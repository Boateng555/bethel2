from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib import messages
from rest_framework import generics
from .models import Event, Ministry, News, NewsletterSignup, Hero, Sermon, Church, DonationMethod, ChurchAdmin, Convention, ChurchApplication, Testimony, AboutPage, LeadershipPage, LocalLeadershipPage, LocalAboutPage, EventHighlight
from .serializers import EventSerializer, MinistrySerializer, NewsSerializer, NewsletterSignupSerializer
from datetime import datetime, timedelta, time
from django.utils import timezone
from calendar import monthcalendar, month_name
import calendar
import pytz
from django.db import models
from django.db.models import Q
import requests
import json
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from .forms import TestimonyForm, MinistryJoinRequestForm, EventRegistrationForm
from django.utils.http import urlencode
import qrcode
import io
import base64
from django.core.mail import send_mail
import math

import cloudinary
import cloudinary.uploader
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def get_user_location(request):
    """
    Get user's location based on IP address
    Returns: (country, city) or (None, None) if unable to determine
    """
    try:
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Use ipapi.co for geolocation (free tier)
        response = requests.get(f'https://ipapi.co/{ip}/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            country = data.get('country_name')
            city = data.get('city')
            return country, city
    except Exception as e:
        print(f"Error getting location: {e}")
    
    return None, None

def find_nearest_church(country, city):
    """
    Find the nearest church based on country and city
    Returns: Church object or None
    """
    if not country:
        return None
    
    # First try exact country match
    churches = Church.objects.filter(country__icontains=country)
    if churches.exists():
        # If multiple churches in same country, try city match
        if city:
            city_churches = churches.filter(city__icontains=city)
            if city_churches.exists():
                return city_churches.first()
        # Return first church in country
        return churches.first()
    
    # Try partial country match
    churches = Church.objects.filter(country__icontains=country.split()[0])
    if churches.exists():
        return churches.first()
    
    return None

def home(request):
    # Check if user wants to go to global site (by presence of the parameter)
    go_global = 'global' in request.GET

    # Get all approved and active churches
    churches = Church.objects.filter(is_active=True, is_approved=True)
    church_count = churches.count()

    # If user explicitly wants global site, show it
    if go_global:
        pass  # Continue to show global homepage
    elif church_count == 1:
        # Only one church, redirect to it
        return redirect('church_home', church_id=churches.first().id)
    elif church_count > 1:
        # Multiple churches, show choose your church page
        return redirect('church_list')

    # If no churches, or user chose global, show the global homepage
    # Show the global site with aggregated content from all churches
    
    # Get active hero content (global hero, not church-specific) - RELAXED FILTER
    hero = Hero.objects.filter(
        is_active=True,
        church__isnull=True
    ).prefetch_related('hero_media').order_by('order', '-created_at').first()
    
    # Get public content from all churches for the global site
    # Events, News, Sermons, Ministries appear immediately when public (no approval needed)
    upcoming_events = Event.objects.filter(
        is_public=True,
        start_date__gte=timezone.now()
    ).prefetch_related('hero_media').order_by('start_date')[:6]
    
    featured_events = Event.objects.filter(
        is_public=True,
        is_featured=True
    ).prefetch_related('hero_media').order_by('-start_date')[:3]
    
    public_ministries = Ministry.objects.filter(
        is_public=True
    ).order_by('name')[:6]  # 6 ministries
    
    latest_news = News.objects.filter(
        is_public=True
    ).order_by('-date')[:4]  # 4 latest news articles
    
    latest_sermons = Sermon.objects.filter(
        is_public=True
    ).order_by('-date')[:4]  # 4 latest sermons
    
    # Get user location for display
    country, city = get_user_location(request)
    nearest_church = None
    if country:
        nearest_church = find_nearest_church(country, city)
    
    context = {
        'hero': hero,
        'upcoming_events': upcoming_events,
        'ministries': public_ministries,
        'sermons': latest_sermons,
        'news': latest_news,
        'all_events': Event.objects.filter(is_public=True)[:10],
        'all_ministries': Ministry.objects.filter(is_public=True)[:10],
        'user_country': country,
        'user_city': city,
        'nearest_church': nearest_church,
        'is_global_site': True,
        'recent_testimonies': Testimony.objects.filter(is_approved=True).order_by('-created_at')[:3],
    }
    return render(request, 'core/home.html', context)

def events(request):
    # Show all public events (no approval required)
    all_events = Event.objects.filter(is_public=True).prefetch_related('hero_media')
    featured_events = Event.objects.filter(is_public=True, is_featured=True).prefetch_related('hero_media')[:3]
    all_ministries = Ministry.objects.filter(is_public=True)
    past_highlights = EventHighlight.objects.filter(is_public=True).order_by('-year')[:6]
    context = {
        'all_events': all_events,
        'featured_events': featured_events,
        'all_ministries': all_ministries,
        'past_highlights': past_highlights,
    }
    return render(request, 'core/events.html', context)

def event_detail(request, event_id):
    # Get individual event detail
    event = get_object_or_404(Event.objects.prefetch_related('hero_media'), id=event_id)
    all_events = Event.objects.filter(is_public=True)  # For navigation dropdown
    all_ministries = Ministry.objects.filter(is_public=True)  # For navigation dropdown
    
    # Handle registration form
    registration_success = False
    if request.method == 'POST' and event.requires_registration:
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            registration.church = event.church
            registration.save()
            # Send notification email to church
            church_email = event.church.email or 'CHURCH_EMAIL_HERE'  # Set this to your church email
            send_mail(
                subject=f'New Event Registration: {event.title}',
                message=f'New registration for {event.title}:\n\nName: {registration.first_name} {registration.last_name}\nEmail: {registration.email}\nPhone: {registration.phone}',
                from_email=None,  # Uses DEFAULT_FROM_EMAIL
                recipient_list=[church_email],
                fail_silently=True,
            )
            # Send confirmation email to user
            send_mail(
                subject=f'Thank you for registering for {event.title}',
                message=f'Dear {registration.first_name},\n\nThank you for registering for {event.title} at {event.church.name}. We have received your registration.\n\nEvent Details:\nTitle: {event.title}\nDate: {event.start_date.strftime('%Y-%m-%d %H:%M')}\nLocation: {event.location or event.address}\n\nIf you have any questions, reply to this email.\n\nBlessings,\n{event.church.name}',
                from_email=None,  # Uses DEFAULT_FROM_EMAIL
                recipient_list=[registration.email],
                fail_silently=True,
            )
            registration_success = True
            form = EventRegistrationForm()  # Reset form
    else:
        form = EventRegistrationForm()
    
    # Get past event highlights for this church
    if event.is_big_event:
        past_highlights = EventHighlight.objects.filter(event=event, is_public=True).order_by('-year')
    else:
        past_highlights = EventHighlight.objects.filter(church=event.church, is_public=True).order_by('-year')[:6]  # Get last 6 highlights
    
    # Get registration count if registration is required
    registration_count = None
    if event.requires_registration:
        registration_count = event.registrations.filter(payment_status='paid').count()
    
    # Generate QR code if enabled
    qr_code_base64 = None
    if getattr(event, 'show_qr_code', False):
        qr_url = request.build_absolute_uri()
        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1e3a8a", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    context = {
        'event': event,
        'all_events': all_events,
        'all_ministries': all_ministries,
        'registration_form': form,
        'registration_success': registration_success,
        'past_highlights': past_highlights,
        'registration_count': registration_count,
        'qr_code_base64': qr_code_base64,
    }
    
    # Use big event template if marked as big event
    if event.is_big_event:
        return render(request, 'core/big_event_detail.html', context)
    else:
        return render(request, 'core/event_detail.html', context)

def newsletter_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            NewsletterSignup.objects.create(email=email)
            messages.success(request, 'Thank you for subscribing to our newsletter!')
        else:
            messages.error(request, 'Please provide a valid email address.')
    return redirect('home')

def ministries(request):
    # Get all public ministries for the ministries page
    all_ministries = Ministry.objects.filter(is_public=True)
    all_events = Event.objects.filter(is_public=True)  # For navigation dropdown
    
    context = {
        'all_ministries': all_ministries,
        'all_events': all_events,
    }
    return render(request, 'core/ministries.html', context)

def ministry_detail(request, ministry_id):
    ministry = get_object_or_404(Ministry, id=ministry_id)
    all_ministries = Ministry.objects.filter(is_public=True)  # For navigation dropdown
    all_events = Event.objects.filter(is_public=True)  # For navigation dropdown
    join_success = False
    if request.method == 'POST':
        # You can add form validation and saving logic here
        join_success = True
    context = {
        'ministry': ministry,
        'all_ministries': all_ministries,
        'all_events': all_events,
        'join_success': join_success,
    }
    return render(request, 'core/ministry_detail.html', context)

def about(request):
    all_events = Event.objects.filter(is_public=True)
    all_ministries = Ministry.objects.filter(is_public=True)
    about_page = None
    if AboutPage.objects.exists():
        about_page = AboutPage.objects.first()
    context = {
        'all_events': all_events,
        'all_ministries': all_ministries,
        'about_page': about_page,
    }
    return render(request, 'core/about.html', context)

def donation(request):
    all_events = Event.objects.filter(is_public=True)
    all_ministries = Ministry.objects.filter(is_public=True)
    
    # Get churches that have active donation methods
    churches_with_donations = Church.objects.filter(
        is_approved=True, 
        is_active=True,
        donationmethod__is_active=True
    ).distinct().prefetch_related('donationmethod_set')
    
    context = {
        'all_events': all_events,
        'all_ministries': all_ministries,
        'churches_with_donations': churches_with_donations,
    }
    return render(request, 'core/donation.html', context)

def shop(request):
    all_events = Event.objects.filter(is_public=True)
    all_ministries = Ministry.objects.filter(is_public=True)
    
    context = {
        'all_events': all_events,
        'all_ministries': all_ministries,
    }
    return render(request, 'core/shop.html', context)

def watch(request):
    all_events = Event.objects.filter(is_public=True)
    all_ministries = Ministry.objects.filter(is_public=True)
    
    context = {
        'all_events': all_events,
        'all_ministries': all_ministries,
    }
    return render(request, 'core/watch.html', context)

def visit(request):
    all_events = Event.objects.filter(is_public=True)
    all_ministries = Ministry.objects.filter(is_public=True)
    
    context = {
        'all_events': all_events,
        'all_ministries': all_ministries,
    }
    return render(request, 'core/visit.html', context)

def sermon(request):
    all_events = Event.objects.filter(is_public=True)
    all_ministries = Ministry.objects.filter(is_public=True)
    
    # Get filter parameters
    keyword = request.GET.get('keyword', '').strip()
    preacher = request.GET.get('preacher', '').strip()
    date_filter = request.GET.get('date', '').strip()
    
    # Start with all public sermons
    sermons = Sermon.objects.filter(is_public=True)
    
    # Apply keyword filter (search in title and description)
    if keyword:
        sermons = sermons.filter(
            models.Q(title__icontains=keyword) |
            models.Q(description__icontains=keyword) |
            models.Q(scripture_reference__icontains=keyword)
        )
    
    # Apply preacher filter
    if preacher:
        sermons = sermons.filter(preacher__icontains=preacher)
    
    # Apply date filter
    if date_filter:
        try:
            # Convert date string to date object
            from datetime import datetime
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            sermons = sermons.filter(date=filter_date)
        except ValueError:
            # If date format is invalid, ignore the filter
            pass
    
    # Order by date (newest first)
    sermons = sermons.order_by('-date')
    
    context = {
        'all_events': all_events,
        'all_ministries': all_ministries,
        'sermons': sermons,
        'keyword': keyword,  # Pass back to template to preserve form values
        'preacher': preacher,
        'date_filter': date_filter,
    }
    return render(request, 'core/sermon.html', context)

class EventListView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class MinistryListView(generics.ListAPIView):
    queryset = Ministry.objects.all()
    serializer_class = MinistrySerializer

class NewsListView(generics.ListAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer

class NewsletterSignupCreateView(generics.CreateAPIView):
    queryset = NewsletterSignup.objects.all()
    serializer_class = NewsletterSignupSerializer

def calendar_view(request):
    # Get current year and month
    now = timezone.now()
    year = request.GET.get('year', now.year)
    month = request.GET.get('month', now.month)
    
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        year = now.year
        month = now.month
    
    # Get all public events for the current month
    events = Event.objects.filter(
        is_public=True,
        start_date__year=year,
        start_date__month=month
    ).order_by('start_date')
    
    # Create calendar data
    cal = monthcalendar(year, month)
    
    # Get month name
    month_name_str = calendar.month_name[month]
    
    # Prepare calendar data with events
    calendar_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'day': '', 'events': []})
            else:
                day_events = events.filter(start_date__day=day)
                week_data.append({
                    'day': day,
                    'events': day_events
                })
        calendar_data.append(week_data)
    
    # Navigation data
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    all_events = Event.objects.filter(is_public=True)  # For navigation dropdown
    all_ministries = Ministry.objects.filter(is_public=True)  # For navigation dropdown
    
    context = {
        'calendar_data': calendar_data,
        'month_name': month_name_str,
        'year': year,
        'month': month,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'all_events': all_events,
        'all_ministries': all_ministries,
        'now': now,  # Pass current date for template comparison
    }
    return render(request, 'core/calendar.html', context)

def event_ics(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Convert date to datetime for ICS format
    start_datetime = datetime.combine(event.start_date, time(9, 0))  # Default to 9 AM
    end_datetime = datetime.combine(event.end_date, time(17, 0))    # Default to 5 PM
    
    # Format datetimes for ICS
    start = start_datetime.strftime('%Y%m%dT%H%M%SZ')
    end = end_datetime.strftime('%Y%m%dT%H%M%SZ')
    
    # Clean description for ICS format (remove special characters)
    description = event.description.replace('\n', '\\n').replace('\r', '\\r')
    
    # Include location if available
    location_line = f"LOCATION:{event.location}" if event.location else ""
    
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Bethel Prayer Ministry//EN
BEGIN:VEVENT
UID:{event.id}@bethelprayerministry.com
DTSTAMP:{start}
DTSTART:{start}
DTEND:{end}
SUMMARY:{event.title}
DESCRIPTION:{description}
{location_line}
END:VEVENT
END:VCALENDAR
"""
    response = HttpResponse(ics_content, content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename=event_{event.id}.ics'
    return response

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth (in km)"""
    R = 6371  # Earth radius in kilometers
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    dphi = math.radians(float(lat2) - float(lat1))
    dlambda = math.radians(float(lon2) - float(lon1))
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def church_list(request):
    """Display all churches with search and filter functionality, ordered by proximity if possible"""
    # Get search parameters
    search_query = request.GET.get('search', '')
    country_filter = request.GET.get('country', '')
    city_filter = request.GET.get('city', '')
    
    # Start with all approved churches
    churches = Church.objects.filter(is_approved=True, is_active=True)
    
    # Apply search filter
    if search_query:
        churches = churches.filter(
            models.Q(name__icontains=search_query) |
            models.Q(city__icontains=search_query) |
            models.Q(country__icontains=search_query) |
            models.Q(pastor_name__icontains=search_query)
        )
    
    # Apply country filter
    if country_filter:
        churches = churches.filter(country__icontains=country_filter)
    
    # Apply city filter
    if city_filter:
        churches = churches.filter(city__icontains=city_filter)
    
    # Hardcode user location for testing (Hamburg, Germany)
    user_lat, user_lon = 53.5511, 9.9937
    
    church_distances_dict = {}
    # If we have user lat/lon, order churches by distance
    if user_lat and user_lon:
        church_distances = []
        for church in churches:
            if church.latitude and church.longitude:
                dist = haversine_distance(user_lat, user_lon, church.latitude, church.longitude)
                church_distances.append((dist, church))
                church_distances_dict[church.id] = round(dist, 1)
            else:
                church_distances.append((float('inf'), church))
        church_distances.sort(key=lambda x: x[0])
        churches = [c for d, c in church_distances]
    # Otherwise, fallback to country/city match
    elif user_country:
        def country_city_score(church):
            score = 0
            if church.country and user_country and user_country.lower() in church.country.lower():
                score -= 10
            if church.city and user_city and user_city.lower() in church.city.lower():
                score -= 5
            return score
        churches = sorted(churches, key=country_city_score)
    # Otherwise, keep default ordering
    
    # Get unique countries and cities for filter dropdowns
    countries = Church.objects.filter(is_approved=True, is_active=True).values_list('country', flat=True).distinct().order_by('country')
    cities = Church.objects.filter(is_approved=True, is_active=True).values_list('city', flat=True).distinct().order_by('city')
    
    # Navigation data
    all_events = Event.objects.filter(is_public=True)
    all_ministries = Ministry.objects.filter(is_public=True)
    
    context = {
        'churches': churches,
        'search_query': search_query,
        'country_filter': country_filter,
        'city_filter': city_filter,
        'countries': countries,
        'cities': cities,
        'all_events': all_events,
        'all_ministries': all_ministries,
        'church_distances': church_distances_dict,
    }
    return render(request, 'core/church_list.html', context)

def church_detail(request, church_id):
    """Display detailed information about a specific church"""
    church = get_object_or_404(Church, id=church_id, is_approved=True, is_active=True)
    
    # Get church-specific data - only show future events
    events = Event.objects.filter(
        church=church, 
        is_public=True, 
        start_date__gte=timezone.now()
    ).order_by('start_date')[:5]
    ministries = Ministry.objects.filter(church=church, is_active=True)[:6]
    news = News.objects.filter(church=church, is_public=True).order_by('-date')[:3]
    sermons = Sermon.objects.filter(church=church, is_public=True).order_by('-date')[:3]
    
    # Navigation data
    all_events = Event.objects.filter(is_public=True)
    all_ministries = Ministry.objects.filter(is_public=True)
    
    context = {
        'church': church,
        'events': events,
        'ministries': ministries,
        'news': news,
        'sermons': sermons,
        'all_events': all_events,
        'all_ministries': all_ministries,
    }
    return render(request, 'core/church_detail.html', context)

def church_donation(request, church_id):
    """Display donation methods for a specific church"""
    church = get_object_or_404(Church, id=church_id, is_approved=True, is_active=True)
    
    # Get active donation methods for this church
    donation_methods = DonationMethod.objects.filter(church=church, is_active=True)
    
    # Navigation data
    all_events = Event.objects.filter(is_public=True)
    all_ministries = Ministry.objects.filter(is_public=True)
    
    context = {
        'church': church,
        'donation_methods': donation_methods,
        'all_events': all_events,
        'all_ministries': all_ministries,
    }
    return render(request, 'core/church_donation.html', context)

# Church-specific website views (mirror main site functionality)
def church_home(request, church_id):
    """Church-specific home page with all functionality"""
    church = get_object_or_404(Church, id=church_id, is_approved=True, is_active=True)
    
    # Get church-specific hero (if any) with prefetched hero media
    hero = Hero.objects.filter(church=church, is_active=True).prefetch_related('hero_media').order_by('order', '-created_at').first()
    
    # Show all future public events (not just featured)
    events = Event.objects.filter(
        church=church, 
        is_public=True,
        start_date__gte=timezone.now()
    ).prefetch_related('hero_media').order_by('start_date')[:3]
    all_events = Event.objects.filter(
        church=church, 
        is_public=True,
        start_date__gte=timezone.now()
    )
    ministries = Ministry.objects.filter(church=church, is_active=True)[:6]
    all_ministries = Ministry.objects.filter(church=church, is_active=True)
    news = News.objects.filter(church=church, is_public=True)[:3]
    sermons = Sermon.objects.filter(church=church, is_featured=True, is_public=True)[:3]
    
    context = {
        'church': church,
        'hero': hero,
        'events': events,
        'all_events': all_events,
        'ministries': ministries,
        'all_ministries': all_ministries,
        'news': news,
        'sermons': sermons,
        'is_church_site': True,  # Flag to indicate this is a church-specific page
    }
    return render(request, 'core/church_home.html', context)

def church_events(request, church_id):
    """Church-specific events page"""
    church = get_object_or_404(Church, id=church_id, is_approved=True, is_active=True)
    all_events = Event.objects.filter(church=church, is_public=True).prefetch_related('hero_media')
    featured_events = Event.objects.filter(church=church, is_featured=True, is_public=True).prefetch_related('hero_media')[:3]
    all_ministries = Ministry.objects.filter(church=church, is_active=True)
    
    context = {
        'church': church,
        'all_events': all_events,
        'featured_events': featured_events,
        'all_ministries': all_ministries,
        'is_church_site': True,
    }
    return render(request, 'core/church_events.html', context)

def church_event_detail(request, church_id, event_id):
    """Church-specific event detail page"""
    church = get_object_or_404(Church, id=church_id, is_approved=True, is_active=True)
    event = get_object_or_404(Event.objects.prefetch_related('hero_media'), id=event_id, church=church, is_public=True)
    
    all_events = Event.objects.filter(church=church, is_public=True)
    all_ministries = Ministry.objects.filter(church=church, is_active=True)
    
    # Handle registration form
    registration_success = False
    if request.method == 'POST' and event.requires_registration:
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            registration.church = church
            registration.save()
            # Send notification email to church
            church_email = event.church.email or 'CHURCH_EMAIL_HERE'  # Set this to your church email
            send_mail(
                subject=f'New Event Registration: {event.title}',
                message=f'New registration for {event.title}:\n\nName: {registration.first_name} {registration.last_name}\nEmail: {registration.email}\nPhone: {registration.phone}',
                from_email=None,  # Uses DEFAULT_FROM_EMAIL
                recipient_list=[church_email],
                fail_silently=True,
            )
            # Send confirmation email to user
            send_mail(
                subject=f'Thank you for registering for {event.title}',
                message=f'Dear {registration.first_name},\n\nThank you for registering for {event.title} at {event.church.name}. We have received your registration.\n\nEvent Details:\nTitle: {event.title}\nDate: {event.start_date.strftime('%Y-%m-%d %H:%M')}\nLocation: {event.location or event.address}\n\nIf you have any questions, reply to this email.\n\nBlessings,\n{event.church.name}',
                from_email=None,  # Uses DEFAULT_FROM_EMAIL
                recipient_list=[registration.email],
                fail_silently=True,
            )
            registration_success = True
            form = EventRegistrationForm()  # Reset form
    else:
        form = EventRegistrationForm()
    
    # Get past event highlights for this church
    if event.is_big_event:
        past_highlights = EventHighlight.objects.filter(event=event, is_public=True).order_by('-year')
    else:
        past_highlights = EventHighlight.objects.filter(church=event.church, is_public=True).order_by('-year')[:6]  # Get last 6 highlights
    
    # Get registration count if registration is required
    registration_count = None
    if event.requires_registration:
        registration_count = event.registrations.filter(payment_status='paid').count()
    
    qr_code_base64 = None
    if getattr(event, 'show_qr_code', False):
        qr_url = request.build_absolute_uri()
        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1e3a8a", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    context = {
        'church': church,
        'event': event,
        'all_events': all_events,
        'all_ministries': all_ministries,
        'is_church_site': True,
        'registration_form': form,
        'registration_success': registration_success,
        'past_highlights': past_highlights,
        'registration_count': registration_count,
        'qr_code_base64': qr_code_base64,
    }
    
    # Use big event template if marked as big event
    if event.is_big_event:
        return render(request, 'core/big_event_detail.html', context)
    else:
        return render(request, 'core/church_event_detail.html', context)

def church_ministries(request, church_id):
    """Church-specific ministries page"""
    church = get_object_or_404(Church, id=church_id, is_approved=True, is_active=True)
    
    all_ministries = Ministry.objects.filter(church=church, is_active=True)
    all_events = Event.objects.filter(church=church, is_public=True)
    
    context = {
        'church': church,
        'all_ministries': all_ministries,
        'all_events': all_events,
        'is_church_site': True,
    }
    return render(request, 'core/church_ministries.html', context)

def church_ministry_detail(request, church_id, ministry_id):
    """Church-specific ministry detail page"""
    church = get_object_or_404(Church, id=church_id, is_approved=True, is_active=True)
    ministry = get_object_or_404(Ministry, id=ministry_id, church=church, is_active=True)

    join_success = False
    if request.method == 'POST':
        form = MinistryJoinRequestForm(request.POST)
        if form.is_valid():
            join_request = form.save(commit=False)
            join_request.ministry = ministry
            join_request.church = church
            join_request.save()
            join_success = True
            form = MinistryJoinRequestForm()  # Reset form
    else:
        form = MinistryJoinRequestForm()

    all_ministries = Ministry.objects.filter(church=church, is_active=True)
    all_events = Event.objects.filter(church=church, is_public=True)

    context = {
        'church': church,
        'ministry': ministry,
        'all_ministries': all_ministries,
        'all_events': all_events,
        'is_church_site': True,
        'join_form': form,
        'join_success': join_success,
    }
    return render(request, 'core/church_ministry_detail.html', context)

def church_sermons(request, church_id):
    """Church-specific sermons page"""
    church = get_object_or_404(Church, id=church_id, is_approved=True, is_active=True)
    
    # Get filter parameters
    keyword = request.GET.get('keyword', '')
    preacher = request.GET.get('preacher', '')
    date_filter = request.GET.get('date', '')
    
    # Start with all sermons for this church
    sermons = Sermon.objects.filter(church=church, is_public=True)
    
    # Apply filters
    if keyword:
        sermons = sermons.filter(
            Q(title__icontains=keyword) | 
            Q(description__icontains=keyword) |
            Q(preacher__icontains=keyword)
        )
    
    if preacher:
        sermons = sermons.filter(preacher__icontains=preacher)
    
    if date_filter:
        sermons = sermons.filter(date=date_filter)
    
    # Order by date (newest first)
    sermons = sermons.order_by('-date')
    
    all_events = Event.objects.filter(church=church, is_public=True)
    all_ministries = Ministry.objects.filter(church=church, is_active=True)
    
    context = {
        'church': church,
        'all_events': all_events,
        'all_ministries': all_ministries,
        'sermons': sermons,
        'keyword': keyword,
        'preacher': preacher,
        'date_filter': date_filter,
        'is_church_site': True,
    }
    return render(request, 'core/church_sermons.html', context)

def church_news(request, church_id):
    """Church-specific news page"""
    church = get_object_or_404(Church, id=church_id, is_approved=True, is_active=True)
    
    all_events = Event.objects.filter(church=church, is_public=True)
    all_ministries = Ministry.objects.filter(church=church, is_active=True)
    news = News.objects.filter(church=church, is_public=True).order_by('-date')
    
    context = {
        'church': church,
        'all_events': all_events,
        'all_ministries': all_ministries,
        'news': news,
        'is_church_site': True,
    }
    return render(request, 'core/church_news.html', context)

def church_about(request, church_id):
    """Church-specific about page"""
    church = get_object_or_404(Church, id=church_id, is_approved=True, is_active=True)
    
    # Get the church's about page, create one if it doesn't exist
    about_page, created = LocalAboutPage.objects.get_or_create(church=church)
    
    # Get the church's leadership page, create one if it doesn't exist
    from .models import LocalLeadershipPage
    leadership_page, _ = LocalLeadershipPage.objects.get_or_create(church=church)
    
    all_events = Event.objects.filter(church=church, is_public=True)
    all_ministries = Ministry.objects.filter(church=church, is_active=True)
    
    context = {
        'church': church,
        'about_page': about_page,
        'leadership_page': leadership_page,
        'all_events': all_events,
        'all_ministries': all_ministries,
        'is_church_site': True,
    }
    return render(request, 'core/church_about.html', context)

def church_calendar(request, church_id):
    """Church-specific calendar page"""
    church = get_object_or_404(Church, id=church_id, is_approved=True, is_active=True)
    
    # Get current year and month
    now = timezone.now()
    year = request.GET.get('year', now.year)
    month = request.GET.get('month', now.month)
    
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        year = now.year
        month = now.month
    
    # Get church-specific events for the current month
    events = Event.objects.filter(
        church=church,
        is_public=True,
        start_date__year=year,
        start_date__month=month
    ).order_by('start_date')
    
    # Create calendar data
    cal = monthcalendar(year, month)
    
    # Get month name
    month_name_str = calendar.month_name[month]
    
    # Prepare calendar data with events
    calendar_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'day': '', 'events': []})
            else:
                day_events = events.filter(start_date__day=day)
                week_data.append({
                    'day': day,
                    'events': day_events
                })
        calendar_data.append(week_data)
    
    # Navigation data
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    context = {
        'church': church,
        'calendar_data': calendar_data,
        'year': year,
        'month': month,
        'month_name': month_name_str,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'all_events': Event.objects.filter(church=church, is_public=True),
        'all_ministries': Ministry.objects.filter(church=church, is_active=True),
        'is_church_site': True,
    }
    return render(request, 'core/church_calendar.html', context)

def local_admin_dashboard(request):
    """Custom admin dashboard for local church admins"""
    if not request.user.is_authenticated:
        return redirect('admin:login')
    
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
    except ChurchAdmin.DoesNotExist:
        # If user is not a church admin, redirect to regular admin
        return redirect('admin:index')
    
    # Only local admins should access this
    if church_admin.role != 'local_admin' or not church_admin.church:
        return redirect('admin:index')
    
    church = church_admin.church
    
    # Get counts for dashboard
    context = {
        'church': church,
        'church_admin': church_admin,
        'events_count': Event.objects.filter(church=church).count(),
        'ministries_count': Ministry.objects.filter(church=church).count(),
        'news_count': News.objects.filter(church=church).count(),
        'sermons_count': Sermon.objects.filter(church=church).count(),
        'donation_methods_count': DonationMethod.objects.filter(church=church).count(),
        'heroes_count': Hero.objects.filter(church=church).count(),
        'recent_events': Event.objects.filter(church=church).order_by('-created_at')[:5],
        'recent_news': News.objects.filter(church=church).order_by('-created_at')[:5],
        'recent_sermons': Sermon.objects.filter(church=church).order_by('-created_at')[:5],
    }
    
    return render(request, 'core/local_admin_dashboard.html', context)

def local_admin_events(request):
    """Local admin events management"""
    if not request.user.is_authenticated:
        return redirect('admin:login')
    
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
    except ChurchAdmin.DoesNotExist:
        return redirect('admin:index')
    
    if church_admin.role != 'local_admin' or not church_admin.church:
        return redirect('admin:index')
    
    church = church_admin.church
    events = Event.objects.filter(church=church).prefetch_related('hero_media').order_by('-start_date')
    past_highlights = EventHighlight.objects.filter(church=church).order_by('-year')[:6]
    
    context = {
        'church': church,
        'events': events,
        'church_admin': church_admin,
        'past_highlights': past_highlights,
    }
    
    return render(request, 'core/local_admin_events.html', context)

def local_admin_ministries(request):
    """Local admin ministries management"""
    if not request.user.is_authenticated:
        return redirect('admin:login')
    
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
    except ChurchAdmin.DoesNotExist:
        return redirect('admin:index')
    
    if church_admin.role != 'local_admin' or not church_admin.church:
        return redirect('admin:index')
    
    church = church_admin.church
    ministries = Ministry.objects.filter(church=church).order_by('name')
    
    context = {
        'church': church,
        'ministries': ministries,
        'church_admin': church_admin,
    }
    
    return render(request, 'core/local_admin_ministries.html', context)

def local_admin_news(request):
    """Local admin news management"""
    if not request.user.is_authenticated:
        return redirect('admin:login')
    
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
    except ChurchAdmin.DoesNotExist:
        return redirect('admin:index')
    
    if church_admin.role != 'local_admin' or not church_admin.church:
        return redirect('admin:index')
    
    church = church_admin.church
    news_list = News.objects.filter(church=church).order_by('-date')
    
    context = {
        'church': church,
        'news_list': news_list,
        'church_admin': church_admin,
    }
    
    return render(request, 'core/local_admin_news.html', context)

def local_admin_sermons(request):
    """Local admin sermons management"""
    if not request.user.is_authenticated:
        return redirect('admin:login')
    
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
    except ChurchAdmin.DoesNotExist:
        return redirect('admin:index')
    
    if church_admin.role != 'local_admin' or not church_admin.church:
        return redirect('admin:index')
    
    church = church_admin.church
    sermons = Sermon.objects.filter(church=church).order_by('-date')
    
    context = {
        'church': church,
        'sermons': sermons,
        'church_admin': church_admin,
    }
    
    return render(request, 'core/local_admin_sermons.html', context)

def local_admin_donations(request):
    """Local admin donation methods management"""
    if not request.user.is_authenticated:
        return redirect('admin:login')
    
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
    except ChurchAdmin.DoesNotExist:
        return redirect('admin:index')
    
    if church_admin.role != 'local_admin' or not church_admin.church:
        return redirect('admin:index')
    
    church = church_admin.church
    donation_methods = DonationMethod.objects.filter(church=church).order_by('name')
    
    # Handle form submissions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            # Add new donation method
            name = request.POST.get('name')
            payment_type = request.POST.get('payment_type')
            external_link = request.POST.get('external_link', '').strip()
            account_info = request.POST.get('account_info')
            description = request.POST.get('description', '').strip()
            is_active = request.POST.get('is_active') == 'on'
            is_default = request.POST.get('is_default') == 'on'
            
            if name and payment_type and account_info:
                # If setting as default, unset other defaults first
                if is_default:
                    DonationMethod.objects.filter(church=church, is_default=True).update(is_default=False)
                
                # Create the donation method
                DonationMethod.objects.create(
                    church=church,
                    name=name,
                    payment_type=payment_type,
                    external_link=external_link if external_link else None,
                    account_info=account_info,
                    description=description,
                    is_active=is_active,
                    is_default=is_default
                )
                
                messages.success(request, f'Donation method "{name}" added successfully!')
            else:
                messages.error(request, 'Please fill in all required fields.')
                
        elif action == 'delete':
            # Delete donation method
            method_id = request.POST.get('method_id')
            try:
                method = DonationMethod.objects.get(id=method_id, church=church)
                method_name = method.name
                method.delete()
                messages.success(request, f'Donation method "{method_name}" deleted successfully!')
            except DonationMethod.DoesNotExist:
                messages.error(request, 'Donation method not found.')
        
        # Redirect to refresh the page
        return redirect('local_admin_donations')
    
    context = {
        'church': church,
        'donation_methods': donation_methods,
        'church_admin': church_admin,
    }
    
    return render(request, 'core/local_admin_donations.html', context)

def local_admin_heroes(request):
    """Local admin hero content management"""
    if not request.user.is_authenticated:
        return redirect('admin:login')
    
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
    except ChurchAdmin.DoesNotExist:
        return redirect('admin:index')
    
    if church_admin.role != 'local_admin' or not church_admin.church:
        return redirect('admin:index')
    
    church = church_admin.church
    heroes = Hero.objects.filter(church=church).order_by('order')
    
    context = {
        'church': church,
        'heroes': heroes,
        'church_admin': church_admin,
    }
    
    return render(request, 'core/local_admin_heroes.html', context)

def local_admin_church_settings(request):
    """Local admin church settings"""
    if not request.user.is_authenticated:
        return redirect('admin:login')
    
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
    except ChurchAdmin.DoesNotExist:
        return redirect('admin:index')
    
    if church_admin.role != 'local_admin' or not church_admin.church:
        return redirect('admin:index')
    
    church = church_admin.church
    
    # Handle form submissions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_settings':
            # Update church settings
            shop_url = request.POST.get('shop_url', '').strip()
            website = request.POST.get('website', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            
            # Update the church
            church.shop_url = shop_url if shop_url else None
            church.website = website if website else None
            church.email = email if email else None
            church.phone = phone if phone else None
            church.save()
            
            messages.success(request, 'Church settings updated successfully!')
            return redirect('local_admin_church_settings')
    
    context = {
        'church': church,
        'church_admin': church_admin,
    }
    
    return render(request, 'core/local_admin_church_settings.html', context)

def global_admin_dashboard(request):
    """Global admin dashboard for managing global content"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Check if user is a global admin or superuser
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
        if church_admin.role != 'global_admin' and not request.user.is_superuser:
            messages.error(request, "You don't have permission to access the global admin dashboard.")
            return redirect('home')
    except ChurchAdmin.DoesNotExist:
        if not request.user.is_superuser:
            messages.error(request, "You don't have permission to access the global admin dashboard.")
            return redirect('home')
    
    # Get global content counts
    context = {
        'conventions_count': Convention.objects.count(),
        'convention_registrations_count': ConventionRegistration.objects.count(),
        'newsletter_signups_count': NewsletterSignup.objects.count(),
        'global_heroes_count': Hero.objects.filter(church__isnull=True).count(),
        'churches_count': Church.objects.filter(is_approved=True).count(),
        'pending_applications_count': ChurchApplication.objects.filter(status='pending').count(),
        'pending_event_requests_count': Event.objects.filter(global_feature_status='pending').count(),
        'pending_hero_requests_count': Hero.objects.filter(global_feature_status='pending').count(),
        'pending_news_requests_count': News.objects.filter(global_feature_status='pending').count(),
    }
    
    return render(request, 'core/global_admin_dashboard.html', context)

@require_POST
def request_global_event_feature(request, event_id):
    if not request.user.is_authenticated:
        return redirect('admin:login')
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
    except ChurchAdmin.DoesNotExist:
        return redirect('admin:index')
    if church_admin.role != 'local_admin' or not church_admin.church:
        return redirect('admin:index')
    try:
        event = Event.objects.get(id=event_id, church=church_admin.church)
    except Event.DoesNotExist:
        messages.error(request, 'Event not found.')
        return redirect('local_admin_events')
    event.global_feature_status = 'pending'
    event.save()
    messages.success(request, 'Global feature request submitted for this event!')
    return redirect('local_admin_events')

@staff_member_required
def global_event_feature_requests(request):
    pending_events = Event.objects.filter(global_feature_status='pending').order_by('-created_at')
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        action = request.POST.get('action')
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            messages.error(request, 'Event not found.')
            return redirect('global_event_feature_requests')
        if action == 'approve':
            event.global_feature_status = 'approved'
            event.is_global_featured = True
            event.save()
            messages.success(request, f'Event "{event.title}" approved for global feature.')
        elif action == 'reject':
            event.global_feature_status = 'rejected'
            event.is_global_featured = False
            event.save()
            messages.success(request, f'Event "{event.title}" rejected for global feature.')
        return redirect('global_event_feature_requests')
    context = {'pending_events': pending_events}
    return render(request, 'core/global_event_feature_requests.html', context)

@require_POST
def request_global_hero_feature(request, hero_id):
    if not request.user.is_authenticated:
        return redirect('admin:login')
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
    except ChurchAdmin.DoesNotExist:
        return redirect('admin:index')
    if church_admin.role != 'local_admin' or not church_admin.church:
        return redirect('admin:index')
    try:
        hero = Hero.objects.get(id=hero_id, church=church_admin.church)
    except Hero.DoesNotExist:
        messages.error(request, 'Hero content not found.')
        return redirect('local_admin_heroes')
    hero.global_feature_status = 'pending'
    hero.save()
    messages.success(request, 'Global feature request submitted for this hero content!')
    return redirect('local_admin_heroes')

@require_POST
def request_global_news_feature(request, news_id):
    if not request.user.is_authenticated:
        return redirect('admin:login')
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
    except ChurchAdmin.DoesNotExist:
        return redirect('admin:index')
    if church_admin.role != 'local_admin' or not church_admin.church:
        return redirect('admin:index')
    try:
        news = News.objects.get(id=news_id, church=church_admin.church)
    except News.DoesNotExist:
        messages.error(request, 'News article not found.')
        return redirect('local_admin_news')
    news.global_feature_status = 'pending'
    news.save()
    messages.success(request, 'Global feature request submitted for this news article!')
    return redirect('local_admin_news')

@staff_member_required
def global_hero_feature_requests(request):
    pending_heroes = Hero.objects.filter(global_feature_status='pending').order_by('-created_at')
    if request.method == 'POST':
        hero_id = request.POST.get('hero_id')
        action = request.POST.get('action')
        try:
            hero = Hero.objects.get(id=hero_id)
        except Hero.DoesNotExist:
            messages.error(request, 'Hero content not found.')
            return redirect('global_hero_feature_requests')
        if action == 'approve':
            hero.global_feature_status = 'approved'
            hero.is_global_featured = True
            hero.save()
            messages.success(request, f'Hero "{hero.title}" approved for global feature.')
        elif action == 'reject':
            hero.global_feature_status = 'rejected'
            hero.is_global_featured = False
            hero.save()
            messages.success(request, f'Hero "{hero.title}" rejected for global feature.')
        return redirect('global_hero_feature_requests')
    context = {'pending_heroes': pending_heroes}
    return render(request, 'core/global_hero_feature_requests.html', context)

@staff_member_required
def global_news_feature_requests(request):
    pending_news = News.objects.filter(global_feature_status='pending').order_by('-created_at')
    if request.method == 'POST':
        news_id = request.POST.get('news_id')
        action = request.POST.get('action')
        try:
            news = News.objects.get(id=news_id)
        except News.DoesNotExist:
            messages.error(request, 'News article not found.')
            return redirect('global_news_feature_requests')
        if action == 'approve':
            news.global_feature_status = 'approved'
            news.is_global_featured = True
            news.save()
            messages.success(request, f'News "{news.title}" approved for global feature.')
        elif action == 'reject':
            news.global_feature_status = 'rejected'
            news.is_global_featured = False
            news.save()
            messages.success(request, f'News "{news.title}" rejected for global feature.')
        return redirect('global_news_feature_requests')
    context = {'pending_news': pending_news}
    return render(request, 'core/global_news_feature_requests.html', context)

def privacy(request):
    """Privacy Policy page"""
    return render(request, 'core/privacy_policy.html')

def terms(request):
    """Terms of Service page"""
    return render(request, 'core/terms_of_service.html')

def cookies(request):
    """Cookie Policy page"""
    return render(request, 'core/cookies.html')

def leadership(request):
    all_events = Event.objects.filter(is_public=True)
    all_ministries = Ministry.objects.filter(is_public=True)
    leadership_page = None
    if LeadershipPage.objects.exists():
        leadership_page = LeadershipPage.objects.first()
    context = {
        'all_events': all_events,
        'all_ministries': all_ministries,
        'leadership_page': leadership_page,
    }
    return render(request, 'core/leadership.html', context)

def resources(request):
    """Resources page with placeholder data"""
    resources = [
        {'title': 'Church Handbook', 'url': '#', 'description': 'A comprehensive guide to church life, ministry, and community involvement.'},
        {'title': 'Prayer Guide', 'url': '#', 'description': 'Daily prayers, devotionals, and spiritual growth resources.'},
        {'title': 'Bible Study Materials', 'url': '#', 'description': 'Weekly Bible study guides and discussion questions.'},
        {'title': 'Ministry Resources', 'url': '#', 'description': 'Tools and materials for various ministry activities.'},
    ]
    return render(request, 'core/resources.html', {'resources': resources})

def testimonies(request):
    """Testimonies page with user submission form and approved testimonies"""
    if request.method == 'POST':
        form = TestimonyForm(request.POST)
        if form.is_valid():
            testimony = form.save(commit=False)
            # Auto-assign church if user is on a church-specific page
            if hasattr(request, 'church'):
                testimony.church = request.church
            testimony.save()
            messages.success(request, 'Thank you for sharing your testimony! It will be reviewed and published soon.')
            return redirect('testimonies')
    else:
        form = TestimonyForm()
    
    # Get approved testimonies
    approved_testimonies = Testimony.objects.filter(is_approved=True).order_by('-created_at')
    
    context = {
        'testimonies': approved_testimonies,
        'form': form,
    }
    return render(request, 'core/testimonies.html', context)

def church_leadership(request, church_id):
    """Leadership page for individual churches"""
    try:
        church = Church.objects.get(id=church_id, is_approved=True)
    except Church.DoesNotExist:
        raise Http404("Church not found")
    
    # Get church-specific leadership page
    leadership_page = None
    if LocalLeadershipPage.objects.filter(church=church).exists():
        leadership_page = LocalLeadershipPage.objects.get(church=church)
    
    # Get church content
    events = Event.objects.filter(church=church, is_public=True)[:5]
    ministries = Ministry.objects.filter(church=church, is_public=True, is_active=True)[:5]
    
    context = {
        'church': church,
        'leadership_page': leadership_page,
        'events': events,
        'ministries': ministries,
    }
    return render(request, 'core/church_leadership.html', context)

def event_highlight_detail(request, highlight_id):
    highlight = get_object_or_404(EventHighlight, id=highlight_id)
    return render(request, 'core/past_event_detail.html', {'highlight': highlight})

def event_speakers(request, event_id):
    from .models import Event
    event = Event.objects.get(id=event_id)
    speakers = event.speakers.all()
    return render(request, 'core/event_speakers.html', {'event': event, 'speakers': speakers})

def all_event_highlights(request):
    highlights = EventHighlight.objects.all().order_by('-year')
    return render(request, 'core/all_event_highlights.html', {'highlights': highlights})

def news_detail(request, news_id):
    """Display individual news article detail"""
    news = get_object_or_404(News, id=news_id, is_public=True)
    
    # Get navigation data
    all_events = Event.objects.filter(is_public=True)
    all_ministries = Ministry.objects.filter(is_public=True)
    
    # Get related news from the same church
    related_news = News.objects.filter(
        church=news.church, 
        is_public=True
    ).exclude(id=news.id).order_by('-date')[:3]
    
    context = {
        'news': news,
        'all_events': all_events,
        'all_ministries': all_ministries,
        'related_news': related_news,
        'church': news.church,
    }
    
    return render(request, 'core/news_detail.html', context)

@csrf_exempt
def trigger_media_upload(request):
    """
    Temporary view to trigger media upload to Cloudinary
    Only accessible via direct URL
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
        )
        
        success_count = 0
        error_count = 0
        results = []
        
        # Upload Church logos
        churches = Church.objects.all()
        for church in churches:
            if church.logo and not 'res.cloudinary.com' in str(church.logo):
                try:
                    local_path = str(church.logo)
                    
                    # Upload to Cloudinary
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="churches/logos",
                        public_id=f"church_{church.id}_logo",
                        overwrite=True
                    )
                    
                    # Update database
                    church.logo = result['secure_url']
                    church.save()
                    
                    results.append(f"✅ {church.name}: {result['secure_url']}")
                    success_count += 1
                    
                except Exception as e:
                    results.append(f"❌ {church.name}: Error - {e}")
                    error_count += 1
        
        # Upload Hero Media
        hero_media = HeroMedia.objects.all()
        for hero in hero_media:
            if hero.image and not 'res.cloudinary.com' in str(hero.image):
                try:
                    local_path = str(hero.image)
                    
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="hero",
                        public_id=f"hero_{hero.id}",
                        overwrite=True
                    )
                    
                    hero.image = result['secure_url']
                    hero.save()
                    
                    results.append(f"✅ Hero {hero.id}: {result['secure_url']}")
                    success_count += 1
                    
                except Exception as e:
                    results.append(f"❌ Hero {hero.id}: Error - {e}")
                    error_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Upload completed! Success: {success_count}, Errors: {error_count}',
            'results': results
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
