from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from rest_framework import generics
from django.contrib.auth.models import User
from .models import Event, Ministry, News, NewsletterSignup, Hero, Sermon, Church, DonationMethod, ChurchAdmin, Convention, ChurchApplication, Testimony, AboutPage, LeadershipPage, LocalLeadershipPage, LocalAboutPage, EventHighlight, GlobalSettings, PrayerRequest, ContactMessage, LiveStreamSettings, EventSpeaker, EventScheduleItem, EventHeroMedia, HeroMedia, MinistryJoinRequest
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
from django.contrib import admin
from django import forms as django_forms
from django.forms import modelform_factory, inlineformset_factory
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseForbidden
from django.core.management import call_command
from .forms import (
    TestimonyForm, MinistryJoinRequestForm, EventRegistrationForm, PrayerRequestForm, ContactMessageForm,
    LocalAdminEventForm, LocalAdminMinistryForm, LocalAdminNewsForm, LocalAdminSermonForm,
    LocalAdminDonationMethodForm, LocalAdminHeroForm,
    LocalAdminEventHeroMediaForm, LocalAdminEventSpeakerForm, LocalAdminEventScheduleItemForm,
    UserAddForm, UserEditForm, SetPasswordFormCustom, MyPasswordChangeForm,
    ChurchMemberAddForm, ChurchMemberEditForm,
)
from django.utils.http import urlencode
import qrcode
import io
import base64
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.core.mail import send_mail
import math
from .event_queries import upcoming_events_cutoff


import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps
import time as time_module
from django.db import connection
from django.db.utils import OperationalError
import threading
import queue
from django.db.models import Count, Avg, Q
from django.db.models.functions import TruncDate, TruncHour
from collections import defaultdict
import json

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
        
        print(f"DEBUG: User IP: {ip}")
        
        # Try ipapi.co first
        try:
            response = requests.get(f'https://ipapi.co/{ip}/json/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                country = data.get('country_name')
                city = data.get('city')
                print(f"DEBUG: ipapi.co result - Country: {country}, City: {city}")
                return country, city
            else:
                print(f"DEBUG: ipapi.co failed with status {response.status_code}")
        except Exception as e:
            print(f"DEBUG: ipapi.co error: {e}")
        
        # Fallback: Try ip-api.com
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    country = data.get('country')
                    city = data.get('city')
                    print(f"DEBUG: ip-api.com result - Country: {country}, City: {city}")
                    return country, city
                else:
                    print(f"DEBUG: ip-api.com failed with status: {data.get('status')}")
        except Exception as e:
            print(f"DEBUG: ip-api.com error: {e}")
        
        # For testing: If localhost, return Germany/Hamburg
        if ip in ['127.0.0.1', 'localhost', '::1']:
            print("DEBUG: Localhost detected, returning Germany/Hamburg for testing")
            return 'Germany', 'Hamburg'
            
    except Exception as e:
        print(f"DEBUG: Error getting location: {e}")
    
    return None, None

def find_nearest_church(country, city):
    """
    Find the nearest church based on country and city
    Returns: Church object or None if no suitable match found
    """
    if not country:
        return None
    
    # Get configuration from GlobalSettings (same instance as full-admin edit)
    try:
        global_settings = GlobalSettings.get_settings()
        min_score = getattr(global_settings, 'local_church_redirect_min_score', 100)
        max_distance_km = getattr(global_settings, 'local_church_redirect_max_distance_km', None)
    except Exception as e:
        print(f"DEBUG: Error getting global settings in find_nearest_church: {e}")
        from django.conf import settings
        min_score = getattr(settings, 'LOCAL_CHURCH_REDIRECT_MIN_SCORE', 100)
        max_distance_km = None
    
    # Get all active and approved churches
    churches = Church.objects.filter(is_active=True, is_approved=True)
    
    if not churches.exists():
        return None
    
    # If only one church exists, return it
    if churches.count() == 1:
        return churches.first()
    
    # Score churches based on location match
    church_scores = []
    
    for church in churches:
        score = 0
        
        # Exact country match (highest priority)
        if church.country and country.lower() in church.country.lower():
            score += 100
        # Partial country match
        elif church.country and country.split()[0].lower() in church.country.lower():
            score += 50
        
        # Exact city match (very high priority)
        if city and church.city and city.lower() in church.city.lower():
            score += 200
        # Partial city match
        elif city and church.city and city.split()[0].lower() in church.city.lower():
            score += 100
        
        # If we have coordinates for the church, we could add distance calculation here
        # max_distance_km from GlobalSettings can be used to filter by distance when user coords available
        church_scores.append((church, score))
    
    # Sort by score (highest first)
    church_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Only return a church if it has a reasonable match score
    # Use the configured minimum score (and max_distance_km when distance logic is used)
    if church_scores and church_scores[0][1] >= min_score:
        best_church = church_scores[0][0]
        best_score = church_scores[0][1]
        
        # Additional check: If we have multiple churches with the same score,
        # prefer the one with better city match
        if best_score >= 100:  # At least partial country match
            # Look for churches with city match
            city_matches = [c for c, s in church_scores if s >= 200]  # Exact city match
            if city_matches:
                return city_matches[0]
            
            partial_city_matches = [c for c, s in church_scores if s >= 150]  # Partial city match
            if partial_city_matches:
                return partial_city_matches[0]
        
        return best_church
    
    # If no good match found, return None instead of forcing a redirect
    return None

def robots_txt(request):
    """Serve robots.txt allowing crawlers and pointing to sitemap (used in core/urls.py for all deployments)."""
    scheme = 'https' if request.is_secure() else 'http'
    host = request.get_host()
    sitemap_url = f"{scheme}://{host}/sitemap.xml"
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /local-admin/",
        "Disallow: /global-admin/",
        "Disallow: /accounts/",
        "Disallow: /api/",
        "",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def smart_home(request):
    """
    Smart home view that redirects users to their nearest church based on location
    """
    try:
        # Get global settings for configuration (same instance as full-admin edit)
        try:
            global_settings = GlobalSettings.get_settings()
            local_redirect_enabled = getattr(global_settings, 'local_church_redirect_enabled', True)
            min_score = getattr(global_settings, 'local_church_redirect_min_score', 100)
        except Exception as e:
            print(f"DEBUG: Error getting global settings: {e}")
            # Fallback to environment variables
            from django.conf import settings
            local_redirect_enabled = getattr(settings, 'LOCAL_CHURCH_REDIRECT_ENABLED', True)
            min_score = getattr(settings, 'LOCAL_CHURCH_REDIRECT_MIN_SCORE', 100)
        
        # Check if local church redirect is enabled
        if not local_redirect_enabled:
            print("DEBUG: Local church redirect disabled, showing church list")
            return redirect('church_list')
        
        # Check if user wants to go to global site (by presence of the parameter)
        go_global = 'global' in request.GET

        # If user explicitly wants global site, redirect to global home
        if go_global:
            return redirect('home')
        
        # Test parameter for manual testing
        test_location = request.GET.get('test_location')
        if test_location:
            print(f"DEBUG: Testing with location: {test_location}")
            if ',' in test_location:
                city, country = test_location.split(',', 1)
                country = country.strip()
                city = city.strip()
            else:
                country = test_location.strip()
                city = None
        else:
            country, city = get_user_location(request)
        
        # Check database availability without blocking
        db_available, db_error = get_database_status()
        
        if not db_available:
            print(f"DEBUG: Database unavailable in smart_home: {db_error}")
            # If database is not available, redirect to global home
            return redirect('home')
        
        # Get all approved and active churches with error handling
        try:
            churches = Church.objects.filter(is_active=True, is_approved=True)
            church_count = churches.count()
            print(f"DEBUG: Found {church_count} active churches")
        except Exception as db_error:
            print(f"DEBUG: Database error in smart_home: {db_error}")
            # If database is not available, redirect to global home
            return redirect('home')
        
        # If no churches, show global site
        if church_count == 0:
            print("DEBUG: No churches found, redirecting to global home")
            return redirect('home')
        
        # If only one church, redirect to location URL so address bar matches the church
        if church_count == 1:
            church = churches.first()
            print(f"DEBUG: Only one church found: {church.name} in {church.city}, {church.country}")
            cslug, cityslug = _location_slugs(church)
            if cslug and cityslug:
                return redirect('church_detail_by_location', country_slug=cslug, city_slug=cityslug)
            return redirect('church_home', church_id=church.id)
        
        print(f"DEBUG: User location detected - Country: {country}, City: {city}")
        
        if country:
            # Try to find nearest church based on location
            nearest_church = find_nearest_church(country, city)
            if nearest_church:
                print(f"DEBUG: Found nearest church: {nearest_church.name} in {nearest_church.city}, {nearest_church.country}")
                
                # Additional check: Only redirect if the match is strong enough
                # This prevents redirecting to churches that are too far away
                match_quality = "good"
                
                # If we have city information, check if it's a strong match
                if city and nearest_church.city:
                    if city.lower() in nearest_church.city.lower() or nearest_church.city.lower() in city.lower():
                        match_quality = "excellent"
                    elif city.split()[0].lower() in nearest_church.city.lower():
                        match_quality = "good"
                    else:
                        match_quality = "country_only"
                
                # Only redirect for good or excellent matches, and only if score meets minimum
                if match_quality in ["good", "excellent"]:
                    print(f"DEBUG: Match quality: {match_quality}, redirecting to {nearest_church.name}")
                    request.session['local_church_redirect'] = True
                    request.session['redirected_church'] = nearest_church.name
                    request.session.modified = True
                    cslug, cityslug = _location_slugs(nearest_church)
                    if cslug and cityslug:
                        return redirect('church_detail_by_location', country_slug=cslug, city_slug=cityslug)
                    return redirect('church_home', church_id=nearest_church.id)
                else:
                    print(f"DEBUG: Match quality too low ({match_quality}), showing church list instead")
            else:
                print(f"DEBUG: No suitable church found for location: {city}, {country}")
        else:
            print("DEBUG: Could not determine user location")
        
        # Try to redirect to main global church as fallback (same instance as full-admin edit)
        try:
            global_settings = GlobalSettings.get_settings()
            if global_settings.main_global_church:
                print(f"DEBUG: No local church found, redirecting to main global church: {global_settings.main_global_church.name}")
                request.session['global_church_fallback'] = True
                request.session['redirected_church'] = global_settings.main_global_church.name
                request.session.modified = True
                ch = global_settings.main_global_church
                cslug, cityslug = _location_slugs(ch)
                if cslug and cityslug:
                    return redirect('church_detail_by_location', country_slug=cslug, city_slug=cityslug)
                return redirect('church_home', church_id=ch.id)
            else:
                print("DEBUG: No main global church configured, showing church list")
                return redirect('church_list')
        except Exception as e:
            print(f"DEBUG: Error getting main global church: {e}")
            return redirect('church_list')
        
    except Exception as e:
        print(f"DEBUG: Unexpected error in smart_home: {e}")
        # Fallback to global home if anything goes wrong
        return redirect('home')

def home(request):
    # Check if user wants to go to global site (by presence of the parameter)
    go_global = 'global' in request.GET

    # Get all approved and active churches with error handling
    try:
        churches = Church.objects.filter(is_active=True, is_approved=True)
        church_count = churches.count()
    except Exception as db_error:
        print(f"DEBUG: Database error in home view: {db_error}")
        # If database is not available, continue to show global homepage
        church_count = 0

    # If user explicitly wants global site, show it
    if go_global:
        pass  # Continue to show global homepage
    elif church_count == 1:
            # Only one church, redirect to it
            try:
                return redirect('church_home', church_id=churches.first().id)
            except Exception as e:
                print(f"DEBUG: Error redirecting to church: {e}")
                pass  # Continue to show global homepage
    elif church_count > 1:
            # Multiple churches, show choose your church page
            return redirect('church_list')

    # If no churches, or user chose global, show the global homepage
    # Show the global site with aggregated content from all churches
    
    # Get global hero and hero settings from GlobalSettings (same instance as full-admin edit)
    try:
        from .models import GlobalSettings
        global_settings = GlobalSettings.get_settings()
        hero = global_settings.global_hero
        if not (hero and hero.is_active):
            # Use fallback hero only when global_hero_fallback_enabled is True
            if getattr(global_settings, 'global_hero_fallback_enabled', True):
                hero = Hero.objects.filter(is_active=True, church__isnull=True).prefetch_related('hero_media').order_by('order', '-created_at').first()
            else:
                hero = None
        hero_rotation_enabled = getattr(global_settings, 'global_hero_rotation_enabled', False)
        hero_rotation_interval = max(3, getattr(global_settings, 'global_hero_rotation_interval', 5))
        hero_fallback_enabled = getattr(global_settings, 'global_hero_fallback_enabled', True)
    except Exception as e:
        print(f"DEBUG: Error getting global hero: {e}")
        hero = None
        hero_rotation_enabled = False
        hero_rotation_interval = 5
        hero_fallback_enabled = True
    
    # Get public content from all churches for the global site
    # Events, News, Sermons, Ministries appear immediately when public (no approval needed)
    try:
        upcoming_events = Event.objects.filter(
            is_public=True,
            end_date__gte=upcoming_events_cutoff(),
        ).prefetch_related('hero_media').order_by('start_date')[:6]
    except Exception as e:
        print(f"DEBUG: Error getting upcoming events: {e}")
        upcoming_events = []
    
    try:
        featured_events = Event.objects.filter(
            is_public=True,
            is_featured=True
        ).prefetch_related('hero_media').order_by('-start_date')[:3]
    except Exception as e:
        print(f"DEBUG: Error getting featured events: {e}")
        featured_events = []
    
    try:
        public_ministries = Ministry.objects.filter(
            is_public=True
        ).order_by('name')[:6]  # 6 ministries
    except Exception as e:
        print(f"DEBUG: Error getting ministries: {e}")
        public_ministries = []
    
    try:
        latest_news = News.objects.filter(
            is_public=True
        ).order_by('-date')[:4]  # 4 latest news articles
    except Exception as e:
        print(f"DEBUG: Error getting news: {e}")
        latest_news = []
    
    try:
        latest_sermons = Sermon.objects.filter(
            is_public=True
        ).order_by('-date')[:4]  # 4 latest sermons
    except Exception as e:
        print(f"DEBUG: Error getting sermons: {e}")
        latest_sermons = []
    
    # Get user location for display
    country, city = get_user_location(request)
    nearest_church = None
    if country:
        try:
            nearest_church = find_nearest_church(country, city)
        except Exception as e:
            print(f"DEBUG: Error finding nearest church: {e}")
    
    try:
        all_events = Event.objects.filter(is_public=True)[:10]
        all_ministries = Ministry.objects.filter(is_public=True)[:10]
        recent_testimonies = Testimony.objects.filter(is_approved=True).order_by('-created_at')[:3]
    except Exception as e:
        print(f"DEBUG: Error getting additional data: {e}")
        all_events = []
        all_ministries = []
        recent_testimonies = []
    
    # SEO: og:image from hero or first hero media
    og_image = None
    if hero:
        first_media = next((m for m in hero.hero_media.all().order_by('order', 'id') if m.image), None)
        if first_media:
            og_image = request.build_absolute_uri(first_media.get_image_url())
        elif getattr(hero, 'background_image', None):
            og_image = request.build_absolute_uri(hero.get_background_image_url())
    context = {
        'hero': hero,
        'hero_rotation_enabled': hero_rotation_enabled,
        'hero_rotation_interval': hero_rotation_interval,
        'hero_fallback_enabled': hero_fallback_enabled,
        'upcoming_events': upcoming_events,
        'ministries': public_ministries,
        'sermons': latest_sermons,
        'news': latest_news,
        'all_events': all_events,
        'all_ministries': all_ministries,
        'user_country': country,
        'user_city': city,
        'nearest_church': nearest_church,
        'is_global_site': go_global,  # Only True if user explicitly requested global site
        'recent_testimonies': recent_testimonies,
        'og_title': None,  # template uses global_settings.site_name
        'og_description': None,  # template uses meta_description from context processor
        'og_image': og_image,
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
        'meta_description': 'Upcoming events at Bethel Prayer Ministry International. Find church events, conferences, and gatherings near you.',
        'og_title': 'Events – Bethel Prayer Ministry International',
    }
    return render(request, 'core/events.html', context)

def _big_event_hero_context(event):
    """Hero buttons: Register before start, View Live after start."""
    now = timezone.now()
    started = bool(event.start_date and now >= event.start_date)
    live_watch_url = reverse('church_watch', args=[event.church_id]) + '#live-stream'
    return {
        'event_has_started': started,
        'live_watch_url': live_watch_url,
        'show_hero_register': bool(event.requires_registration and not started),
        'show_hero_view_live': started,
    }


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
                message=(
                    f"Dear {registration.first_name},\n\nThank you for registering for {event.title} at {event.church.name}. We have received your registration.\n\n"
                    f"Event Details:\nTitle: {event.title}\nDate: {event.start_date.strftime('%Y-%m-%d %H:%M')}\nLocation: {event.location or event.address}\n\n"
                    f"If you have any questions, reply to this email.\n\nBlessings,\n{event.church.name}"
                ),
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
    
    # SEO for event detail
    meta_desc = (event.description or event.title or '')[:160]
    if not meta_desc:
        meta_desc = f"{event.title} at {event.church.name if event.church else 'Bethel'}. Join us."
    og_image = None
    if event.hero_media.exists():
        first_img = next((m for m in event.hero_media.all().order_by('order', 'id') if getattr(m, 'image', None)), None)
        if first_img:
            og_image = request.build_absolute_uri(first_img.get_image_url())
    if not og_image and getattr(event, 'banner_image', None):
        og_image = request.build_absolute_uri(event.banner_image.url)
    context = {
        'event': event,
        'all_events': all_events,
        'all_ministries': all_ministries,
        'registration_form': form,
        'registration_success': registration_success,
        'past_highlights': past_highlights,
        'registration_count': registration_count,
        'qr_code_base64': qr_code_base64,
        'meta_description': meta_desc[:160],
        'og_title': f"{event.title} – Bethel Events",
        'og_description': meta_desc[:160],
        'og_image': og_image,
    }
    if event.is_big_event:
        context.update(_big_event_hero_context(event))
    
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
        'meta_description': 'Explore ministries at Bethel Prayer Ministry International. Get involved in worship, youth, outreach, and more.',
        'og_title': 'Ministries – Bethel Prayer Ministry International',
    }
    return render(request, 'core/ministries.html', context)

def ministry_detail(request, ministry_id):
    ministry = get_object_or_404(Ministry, id=ministry_id)
    all_ministries = Ministry.objects.filter(is_public=True)  # For navigation dropdown
    all_events = Event.objects.filter(is_public=True)  # For navigation dropdown
    join_success = False
    if request.method == 'POST':
        join_success = True
    meta_desc = (ministry.description or ministry.name or '')[:160]
    if not meta_desc:
        meta_desc = f"{ministry.name} – Bethel Prayer Ministry International. Get involved."
    og_image = None
    if getattr(ministry, 'image', None) and ministry.image:
        og_image = request.build_absolute_uri(ministry.image.url)
    context = {
        'ministry': ministry,
        'all_ministries': all_ministries,
        'all_events': all_events,
        'join_success': join_success,
        'meta_description': meta_desc[:160],
        'og_title': f"{ministry.name} – Bethel Ministries",
        'og_description': meta_desc[:160],
        'og_image': og_image,
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
    """Watch page - displays sermons and live streams"""
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
    
    # Get featured sermons (for hero section)
    featured_sermons = sermons.filter(is_featured=True)[:3]
    
    # Get recent sermons
    recent_sermons = sermons[:6]
    
    # Get all preachers for filter dropdown
    preachers = Sermon.objects.filter(is_public=True).values_list('preacher', flat=True).distinct()
    
    # Global Watch Online: show only the church whose "Request global live" was approved (everyone gets that same stream)
    live_stream_settings = None
    featured_church = None
    try:
        approved = LiveStreamSettings.objects.filter(
            church__isnull=False,
            global_feature_status='approved'
        ).select_related('church').order_by('-id').first()
        if approved:
            live_stream_settings = approved
            featured_church = approved.church
        is_live = live_stream_settings.get_live_status() if live_stream_settings else False
        next_service = live_stream_settings.get_next_service_time() if live_stream_settings else "No upcoming services"
    except Exception:
        is_live = False
        next_service = "No upcoming services"

    context = {
        'sermons': sermons,
        'featured_sermons': featured_sermons,
        'recent_sermons': recent_sermons,
        'preachers': preachers,
        'live_stream_settings': live_stream_settings,
        'featured_church': featured_church,
        'is_live': is_live,
        'next_service': next_service,
        'keyword': keyword,
        'preacher': preacher,
        'date_filter': date_filter,
    }
    return render(request, 'core/watch.html', context)


def church_watch(request, church_id):
    """Church-specific Watch Online page: sermons, live streams, and spiritual content."""
    church = get_object_or_404(Church, id=church_id, is_approved=True, is_active=True)
    keyword = request.GET.get('keyword', '').strip()
    preacher = request.GET.get('preacher', '').strip()
    date_filter = request.GET.get('date', '').strip()

    sermons = Sermon.objects.filter(church=church, is_public=True)
    if keyword:
        sermons = sermons.filter(
            models.Q(title__icontains=keyword) |
            models.Q(description__icontains=keyword) |
            models.Q(scripture_reference__icontains=keyword)
        )
    if preacher:
        sermons = sermons.filter(preacher__icontains=preacher)
    if date_filter:
        try:
            from datetime import datetime
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            sermons = sermons.filter(date=filter_date)
        except ValueError:
            pass
    sermons = sermons.order_by('-date')
    featured_sermons = sermons.filter(is_featured=True)[:3]
    preachers = Sermon.objects.filter(church=church, is_public=True).values_list('preacher', flat=True).distinct()

    try:
        live_stream_settings = LiveStreamSettings.objects.filter(church=church).first()
        is_live = live_stream_settings.get_live_status() if live_stream_settings else False
        next_service = live_stream_settings.get_next_service_time() if live_stream_settings else "No upcoming services"
    except Exception:
        live_stream_settings = None
        is_live = False
        next_service = "No upcoming services"

    all_events = Event.objects.filter(church=church, is_public=True)
    all_ministries = Ministry.objects.filter(church=church, is_active=True)

    context = {
        'church': church,
        'sermons': sermons,
        'featured_sermons': featured_sermons,
        'preachers': preachers,
        'live_stream_settings': live_stream_settings,
        'is_live': is_live,
        'next_service': next_service,
        'keyword': keyword,
        'preacher': preacher,
        'date_filter': date_filter,
        'all_events': all_events,
        'all_ministries': all_ministries,
        'is_church_site': True,
    }
    return render(request, 'core/church_watch.html', context)


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
        'meta_description': 'Watch and listen to sermons from Bethel Prayer Ministry International. Browse by preacher, date, and topic.',
        'og_title': 'Sermons – Bethel Prayer Ministry International',
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
    
    # Attach absolute image URLs so card images load reliably (relative /media/ can fail depending on host/proxy)
    if not isinstance(churches, list):
        churches = list(churches)
    for church in churches:
        logo_url = church.get_logo_url()
        church.logo_url_absolute = request.build_absolute_uri(logo_url) if logo_url else ''
        banner_url = church.get_banner_url()
        church.banner_url_absolute = request.build_absolute_uri(banner_url) if banner_url else ''
    
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
        'show_logout_success': request.GET.get('logged_out') == '1',
    }
    return render(request, 'core/church_list.html', context)


def _location_slugs(church):
    """Return (country_slug, city_slug) for a church for use in location URLs."""
    def slug(s):
        return (s or '').lower().replace(' ', '-').strip('-')
    return slug(church.country), slug(church.city)


# Country name alternatives for /churches/<country>/ and /churches/<country>/<city>/
COUNTRY_SLUG_ALTERNATIVES = {
    'germany': ('Germany', 'Deutschland', 'DE'),
    'deutschland': ('Germany', 'Deutschland', 'DE'),
    'uk': ('United Kingdom', 'UK', 'England', 'Scotland', 'Wales'),
    'united-kingdom': ('United Kingdom', 'UK', 'England'),
    'usa': ('United States', 'USA', 'US', 'United States of America'),
    'united-states': ('United States', 'USA', 'US'),
    'netherlands': ('Netherlands', 'The Netherlands', 'Holland'),
}


def church_list_by_country(request, country_slug):
    """
    /churches/<country_slug>/ (e.g. /churches/germany/) – list churches in that country.
    Good for Google: "churches in Germany". Uses same list template with country filter.
    """
    country_name = country_slug.replace('-', ' ').title()
    # Try slug in alternatives (e.g. germany -> Deutschland)
    try_names = [country_name]
    if country_slug.lower() in COUNTRY_SLUG_ALTERNATIVES:
        try_names = list(COUNTRY_SLUG_ALTERNATIVES[country_slug.lower()])

    churches = Church.objects.filter(is_approved=True, is_active=True)
    q = models.Q()
    for name in try_names:
        q |= models.Q(country__iexact=name)
    churches = churches.filter(q).order_by('city', 'name')

    countries = Church.objects.filter(is_approved=True, is_active=True).values_list('country', flat=True).distinct().order_by('country')
    cities = Church.objects.filter(is_approved=True, is_active=True).values_list('city', flat=True).distinct().order_by('city')

    for church in churches:
        logo_url = church.get_logo_url()
        church.logo_url_absolute = request.build_absolute_uri(logo_url) if logo_url else ''
        banner_url = church.get_banner_url()
        church.banner_url_absolute = request.build_absolute_uri(banner_url) if banner_url else ''

    display_country = try_names[0] if try_names else country_name
    all_events = Event.objects.filter(is_public=True)
    all_ministries = Ministry.objects.filter(is_public=True)

    context = {
        'churches': churches,
        'search_query': '',
        'country_filter': display_country,
        'city_filter': '',
        'countries': countries,
        'cities': cities,
        'church_distances': {},
        'show_logout_success': False,
        'page_title_override': f'Churches in {display_country}',
    }
    return render(request, 'core/church_list.html', context)


def church_detail_by_location(request, country_slug, city_slug):
    """
    Resolve /churches/<country_slug>/<city_slug>/ (e.g. /churches/ghana/accra/,
    /churches/germany/hamburg/) to the canonical church detail URL.
    Tries country+city, then country alternatives (e.g. Germany/Deutschland), then city only.
    """
    # Convert slug to display name (e.g. "ghana" -> "Ghana", "new-york" -> "New York")
    country_name = country_slug.replace('-', ' ').title()
    city_name = city_slug.replace('-', ' ').title()

    def query_churches(country_filter, city_filter):
        return Church.objects.filter(
            is_active=True,
            is_approved=True,
            **country_filter,
            **city_filter,
        ).order_by('name')

    # 1) Try exact country + city
    churches = query_churches(
        {'country__iexact': country_name},
        {'city__iexact': city_name},
    )

    # 2) If no match, try country alternatives (e.g. germany -> Deutschland)
    if not churches.exists() and country_slug.lower() in COUNTRY_SLUG_ALTERNATIVES:
        for alt in COUNTRY_SLUG_ALTERNATIVES[country_slug.lower()]:
            churches = query_churches(
                {'country__iexact': alt},
                {'city__iexact': city_name},
            )
            if churches.exists():
                break

    # 3) Fallback: match by city only (so e.g. Hamburg works even if country differs)
    if not churches.exists():
        churches = Church.objects.filter(
            is_active=True,
            is_approved=True,
            city__iexact=city_name,
        ).order_by('name')

    if not churches.exists():
        raise Http404("No church found for this location.")

    # Show the church welcome/home page at this URL so the address bar matches the message
    # "We've automatically redirected you to [Church Name]"
    church = churches.first()

    # Same context as church_home so the page looks identical (welcome, Plan Your Visit, etc.)
    heroes = list(Hero.objects.filter(church=church, is_active=True).prefetch_related('hero_media').order_by('order', '-created_at'))
    hero = heroes[0] if heroes else None
    events = Event.objects.filter(
        church=church,
        is_public=True,
        end_date__gte=upcoming_events_cutoff(),
    ).prefetch_related('hero_media').order_by('start_date')[:3]
    all_events = Event.objects.filter(
        church=church,
        is_public=True,
        end_date__gte=upcoming_events_cutoff(),
    )
    ministries = Ministry.objects.filter(church=church, is_active=True)[:6]
    all_ministries = Ministry.objects.filter(church=church, is_active=True)
    news = News.objects.filter(church=church, is_public=True)[:3]
    sermons = Sermon.objects.filter(church=church, is_featured=True, is_public=True)[:3]
    country, city = get_user_location(request)
    nearest_church = None
    if country:
        try:
            nearest_church = find_nearest_church(country, city)
        except Exception:
            pass
    if request.session.get('local_church_redirect'):
        request.session['clear_redirect_notification'] = True

    context = {
        'church': church,
        'hero': hero,
        'heroes': heroes,
        'events': events,
        'all_events': all_events,
        'ministries': ministries,
        'all_ministries': all_ministries,
        'news': news,
        'sermons': sermons,
        'is_church_site': True,
        'user_country': country,
        'user_city': city,
        'nearest_church': nearest_church,
        'show_logout_success': request.GET.get('logged_out') == '1',
    }
    return render(request, 'core/church_home.html', context)


def church_detail(request, church_id):
    """Display detailed information about a specific church"""
    church = get_object_or_404(Church, id=church_id, is_approved=True, is_active=True)
    
    # Events still visible for one week after they end
    events = Event.objects.filter(
        church=church,
        is_public=True,
        end_date__gte=upcoming_events_cutoff(),
    ).order_by('start_date')[:5]
    ministries = Ministry.objects.filter(church=church, is_active=True)[:6]
    news = News.objects.filter(church=church, is_public=True).order_by('-date')[:3]
    sermons = Sermon.objects.filter(church=church, is_public=True).order_by('-date')[:3]
    
    # Navigation data
    all_events = Event.objects.filter(is_public=True)
    all_ministries = Ministry.objects.filter(is_public=True)

    # SEO: meta description and Open Graph (crawlable, indexable)
    location = f"{church.city}, {church.country}"
    if church.description and church.description.strip():
        meta_desc = church.description.strip()[:157] + ("…" if len(church.description) > 160 else "")
    else:
        meta_desc = f"{church.name} in {location}. Services, events, ministries. Bethel Prayer Ministry International."
    meta_desc = meta_desc[:160]
    og_image = None
    if church.logo:
        og_image = request.build_absolute_uri(church.get_logo_url())
    elif church.banner_image:
        og_image = request.build_absolute_uri(church.get_banner_url())
    
    context = {
        'church': church,
        'events': events,
        'ministries': ministries,
        'news': news,
        'sermons': sermons,
        'all_events': all_events,
        'all_ministries': all_ministries,
        'meta_description': meta_desc,
        'og_title': f"{church.name} - Bethel Church",
        'og_description': meta_desc,
        'og_image': og_image,
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
    
    # Get all active church heroes (for carousel) with prefetched hero media
    heroes = list(Hero.objects.filter(church=church, is_active=True).prefetch_related('hero_media').order_by('order', '-created_at'))
    hero = heroes[0] if heroes else None  # first hero for backward compatibility in template
    
    # Show public events until one week after they end
    events = Event.objects.filter(
        church=church,
        is_public=True,
        end_date__gte=upcoming_events_cutoff(),
    ).prefetch_related('hero_media').order_by('start_date')[:3]
    all_events = Event.objects.filter(
        church=church,
        is_public=True,
        end_date__gte=upcoming_events_cutoff(),
    )
    ministries = Ministry.objects.filter(church=church, is_active=True)[:6]
    all_ministries = Ministry.objects.filter(church=church, is_active=True)
    news = News.objects.filter(church=church, is_public=True)[:3]
    sermons = Sermon.objects.filter(church=church, is_featured=True, is_public=True)[:3]
    
    # Get user location for location detection banner
    country, city = get_user_location(request)
    nearest_church = None
    if country:
        try:
            nearest_church = find_nearest_church(country, city)
        except Exception as e:
            print(f"DEBUG: Error finding nearest church: {e}")
    
    # Clear the redirect notification after displaying it
    if request.session.get('local_church_redirect'):
        # Keep the data for this request, but mark it for removal
        request.session['clear_redirect_notification'] = True
    
    context = {
        'church': church,
        'hero': hero,
        'heroes': heroes,
        'events': events,
        'all_events': all_events,
        'ministries': ministries,
        'all_ministries': all_ministries,
        'news': news,
        'sermons': sermons,
        'is_church_site': True,  # Flag to indicate this is a church-specific page
        'user_country': country,
        'user_city': city,
        'nearest_church': nearest_church,
        'show_logout_success': request.GET.get('logged_out') == '1',
    }
    return render(request, 'core/church_home.html', context)

def church_events(request, church_id):
    """Church-specific events page"""
    church = get_object_or_404(Church, id=church_id, is_approved=True, is_active=True)
    all_events = Event.objects.filter(church=church, is_public=True).prefetch_related('hero_media')
    featured_events = Event.objects.filter(church=church, is_featured=True, is_public=True).prefetch_related('hero_media')[:3]
    all_ministries = Ministry.objects.filter(church=church, is_active=True)
    
    # Get user location for location detection banner
    country, city = get_user_location(request)
    nearest_church = None
    if country:
        try:
            nearest_church = find_nearest_church(country, city)
        except Exception as e:
            print(f"DEBUG: Error finding nearest church: {e}")
    
    context = {
        'church': church,
        'all_events': all_events,
        'featured_events': featured_events,
        'all_ministries': all_ministries,
        'is_church_site': True,
        'user_country': country,
        'user_city': city,
        'nearest_church': nearest_church,
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
                message=(
                    f"Dear {registration.first_name},\n\nThank you for registering for {event.title} at {event.church.name}. We have received your registration.\n\n"
                    f"Event Details:\nTitle: {event.title}\nDate: {event.start_date.strftime('%Y-%m-%d %H:%M')}\nLocation: {event.location or event.address}\n\n"
                    f"If you have any questions, reply to this email.\n\nBlessings,\n{event.church.name}"
                ),
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
    
    # Get user location for location detection banner
    country, city = get_user_location(request)
    nearest_church = None
    if country:
        try:
            nearest_church = find_nearest_church(country, city)
        except Exception as e:
            print(f"DEBUG: Error finding nearest church: {e}")
    
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
        'user_country': country,
        'user_city': city,
        'nearest_church': nearest_church,
    }
    if event.is_big_event:
        context.update(_big_event_hero_context(event))
    
    # Use big event template if marked as big event
    if event.is_big_event:
        return render(request, 'core/big_event_detail.html', context)
    else:
        return render(request, 'core/church_event_detail.html', context)

def church_ministries(request, church_id):
    """Church-specific ministries page"""
    church = get_object_or_404(Church, id=church_id, is_approved=True, is_active=True)
    
    ministries = Ministry.objects.filter(church=church, is_active=True)
    all_events = Event.objects.filter(church=church, is_public=True)
    
    context = {
        'church': church,
        'ministries': ministries,
        'all_ministries': ministries,
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


def logout_view(request):
    """Log out the user, then redirect to their church page (or home) with a success message."""
    church_id = request.session.get('logout_redirect_church_id')
    logout(request)
    if church_id:
        try:
            return redirect(reverse('church_home', kwargs={'church_id': church_id}) + '?logged_out=1')
        except Exception:
            pass
    return redirect(reverse('church_list') + '?logged_out=1')


def local_admin_login(request):
    """Custom login for local admin: password then optional TOTP verify."""
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('local_admin_dashboard')
    if request.user.is_authenticated:
        return redirect(next_url)
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
            if device:
                request.session['pending_mfa_user_id'] = user.pk
                request.session['pending_mfa_backend'] = user.backend
                request.session['pending_mfa_next'] = next_url
                return redirect(reverse('local_admin_login_verify'))
            login(request, user)
            return redirect(next_url)
    else:
        form = AuthenticationForm(request)
    return render(request, 'core/local_admin_login.html', {'form': form, 'next': next_url or reverse('local_admin_dashboard')})


def local_admin_login_verify(request):
    """Verify TOTP code after password for users who have MFA enabled."""
    user_id = request.session.get('pending_mfa_user_id')
    backend = request.session.get('pending_mfa_backend')
    next_url = request.session.get('pending_mfa_next', reverse('local_admin_dashboard'))
    if not user_id or not backend:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': next_url}))
    user = get_object_or_404(User, pk=user_id)
    device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
    if not device:
        for k in ('pending_mfa_user_id', 'pending_mfa_backend', 'pending_mfa_next'):
            request.session.pop(k, None)
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': next_url}))
    if request.method == 'POST':
        token = (request.POST.get('token') or '').strip().replace(' ', '')
        if token and device.verify_token(token):
            user.backend = backend
            login(request, user)
            for k in ('pending_mfa_user_id', 'pending_mfa_backend', 'pending_mfa_next'):
                request.session.pop(k, None)
            return redirect(next_url)
        messages.error(request, 'Invalid or expired code. Please try again.')
    return render(request, 'core/local_admin_login_verify.html', {'next': next_url})


def church_admin_entry(request):
    """
    Simple page for church staff: only "Go to Church Admin Dashboard".
    Keeps them away from the Django/admin database interface. Used when they hit /admin/
    or when they don't have Local Admin role yet.
    """
    if not request.user.is_authenticated:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_dashboard')}))
    # If they are a Local Admin, send them straight to the dashboard
    try:
        ca = ChurchAdmin.objects.get(user=request.user, is_active=True)
        if ca.role == 'local_admin' and ca.church_id:
            return redirect('local_admin_dashboard')
    except ChurchAdmin.DoesNotExist:
        pass
    return render(request, 'core/church_admin_entry.html')


def local_admin_dashboard(request):
    """Custom admin dashboard for local church admins (or minimal dashboard for superusers)"""
    if not request.user.is_authenticated:
        login_url = reverse('local_admin_login')
        next_url = reverse('local_admin_dashboard')
        return redirect(login_url + '?' + urlencode({'next': next_url}))
    
    church_admin = None
    church = None
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
        if church_admin.role == 'local_admin' and church_admin.church:
            church = church_admin.church
    except ChurchAdmin.DoesNotExist:
        pass
    
    # Allow superusers even without a church (minimal dashboard for user management)
    if not church and not request.user.is_superuser:
        messages.warning(
            request,
            'You need Local Admin role for a church to use the Church Admin Dashboard. '
            'Ask a superadmin to add you as a member with Local Admin role.'
        )
        return redirect('church_admin_entry')
    
    # Remember which church to return to after logout (session is read before logout)
    if church:
        request.session['logout_redirect_church_id'] = str(church.id)
    
    if church:
        pending_requests_qs = MinistryJoinRequest.objects.filter(church=church, is_reviewed=False).order_by('-created_at')
        context = {
            'church': church,
            'church_admin': church_admin,
            'events_count': Event.objects.filter(church=church).count(),
            'ministries_count': Ministry.objects.filter(church=church).count(),
            'news_count': News.objects.filter(church=church).count(),
            'sermons_count': Sermon.objects.filter(church=church).count(),
            'donation_methods_count': DonationMethod.objects.filter(church=church).count(),
            'heroes_count': Hero.objects.filter(church=church).count(),
            'pending_requests_count': pending_requests_qs.count(),
            'pending_requests': pending_requests_qs[:15],
            'recent_events': Event.objects.filter(church=church).order_by('-created_at')[:5],
            'recent_news': News.objects.filter(church=church).order_by('-created_at')[:5],
            'recent_sermons': Sermon.objects.filter(church=church).order_by('-created_at')[:5],
        }
    else:
        context = {
            'church': None,
            'church_admin': None,
            'events_count': 0,
            'ministries_count': 0,
            'news_count': 0,
            'sermons_count': 0,
            'donation_methods_count': 0,
            'heroes_count': 0,
            'pending_requests_count': 0,
            'pending_requests': [],
            'recent_events': [],
            'recent_news': [],
            'recent_sermons': [],
        }
    if request.user.is_superuser:
        context['pending_global_live_count'] = LiveStreamSettings.objects.filter(
            church__isnull=False, global_feature_status='pending'
        ).count()
    else:
        context['pending_global_live_count'] = 0

    # Website visitors count (last 30 days) for analytics card
    try:
        from .analytics_models import VisitorSession
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        context['website_visitors_count'] = VisitorSession.objects.filter(started_at__gte=start_date).count()
    except Exception:
        context['website_visitors_count'] = 0

    return render(request, 'core/local_admin_dashboard.html', context)


def local_admin_requests(request):
    """List ministry join requests: per church for local admins, or all for superusers. Stays in Bethel Admin."""
    if not request.user.is_authenticated:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    church = None
    church_admin = None
    show_all_churches = False
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
        if church_admin.role == 'local_admin' and church_admin.church:
            church = church_admin.church
    except ChurchAdmin.DoesNotExist:
        pass
    if not church and request.user.is_superuser:
        show_all_churches = True

    if not church and not show_all_churches:
        messages.info(request, 'Requests are managed per church. Add yourself as a Local Admin for a church, or use a superadmin account to see all requests.')
        return redirect('local_admin_dashboard')

    status_filter = request.GET.get('status', 'all')  # all | pending | reviewed
    if church:
        qs = MinistryJoinRequest.objects.filter(church=church).order_by('-created_at')
        pending_count = MinistryJoinRequest.objects.filter(church=church, is_reviewed=False).count()
    else:
        qs = MinistryJoinRequest.objects.select_related('church', 'ministry').order_by('-created_at')
        pending_count = MinistryJoinRequest.objects.filter(is_reviewed=False).count()
    if status_filter == 'pending':
        qs = qs.filter(is_reviewed=False)
    elif status_filter == 'reviewed':
        qs = qs.filter(is_reviewed=True)

    context = {
        'church': church,
        'church_admin': church_admin,
        'requests': qs,
        'status_filter': status_filter,
        'pending_requests_count': pending_count,
        'show_all_churches': show_all_churches,
    }
    return render(request, 'core/local_admin_requests.html', context)


def local_admin_ministry_request_respond(request, request_id):
    """Accept or decline a ministry join request. Local admins only their church; superusers any request. Stays in Bethel Admin."""
    if not request.user.is_authenticated:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    church = None
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
        if church_admin.role == 'local_admin' and church_admin.church:
            church = church_admin.church
    except ChurchAdmin.DoesNotExist:
        pass
    if church:
        join_request = get_object_or_404(MinistryJoinRequest, id=request_id, church=church)
    elif request.user.is_superuser:
        join_request = get_object_or_404(MinistryJoinRequest, id=request_id)
    else:
        messages.info(request, 'You need Local Admin role for a church or superadmin to respond to requests.')
        return redirect('local_admin_dashboard')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ('accept', 'decline'):
            join_request.is_reviewed = True
            join_request.save()
            if action == 'accept':
                messages.success(request, f'Accepted request from {join_request.name} to join {join_request.ministry.name}.')
            else:
                messages.success(request, f'Declined request from {join_request.name}.')
    return redirect('local_admin_requests')


# --- Full in-dashboard admin (no Django admin redirect) - superuser only ---
def _get_full_admin_models():
    """Return list of (model, model_admin, app_label, model_name, verbose_name_plural) for models registered in admin."""
    result = []
    for model, model_admin in admin.site._registry.items():
        if model._meta.app_label != 'core':
            continue
        result.append({
            'model': model,
            'model_admin': model_admin,
            'app_label': model._meta.app_label,
            'model_name': model._meta.model_name,
            'verbose_name_plural': model._meta.verbose_name_plural or model._meta.model_name,
        })
    return sorted(result, key=lambda x: x['verbose_name_plural'].lower())


def _get_full_admin_model(app_label, model_name):
    """Get model and admin class; return (model, model_admin) or (None, None)."""
    if app_label != 'core':
        return None, None
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        return None, None
    if model not in admin.site._registry:
        return None, None
    return model, admin.site._registry[model]


def _build_model_form(model, request=None, instance=None):
    """Build a ModelForm for the model with file fields optional and basic styling."""
    pk_name = model._meta.pk.name
    field_names = [
        f.name for f in list(model._meta.fields) + list(model._meta.many_to_many)
        if f.name != pk_name
        and not getattr(f, 'auto_created', False)
        and getattr(f, 'editable', True)
    ]
    if not field_names:
        field_names = [f.name for f in model._meta.fields if f.name != pk_name and getattr(f, 'editable', True)]
    if not field_names:
        form_class = modelform_factory(model, fields='__all__', exclude=[pk_name])
    else:
        form_class = modelform_factory(model, fields=field_names)
    input_class = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#1e3a8a] text-gray-900'
    for name, field in form_class.base_fields.items():
        if hasattr(field, 'required') and isinstance(field, (django_forms.FileField, django_forms.ImageField)):
            field.required = False
        if hasattr(field, 'widget') and field.widget and hasattr(field.widget, 'attrs'):
            field.widget.attrs.setdefault('class', input_class)
    return form_class


def full_admin_home(request):
    """Full admin home: list all models to manage (in-dashboard, no Django admin)."""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    models_list = _get_full_admin_models()
    context = {
        'models_list': models_list,
        'church': None,
        'church_admin': None,
    }
    return render(request, 'core/full_admin_home.html', context)


def full_admin_list(request, app_label, model_name):
    """List objects for a model."""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    model, _ = _get_full_admin_model(app_label, model_name)
    if not model:
        raise Http404
    qs = model.objects.all()
    try:
        qs = qs.order_by('-pk')
    except Exception:
        qs = qs.order_by('pk')
    paginator = Paginator(qs, 50)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(int(page))
    except (ValueError, PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)
    context = {
        'model': model,
        'model_name': model_name,
        'app_label': app_label,
        'verbose_name': model._meta.verbose_name or model_name,
        'verbose_name_plural': model._meta.verbose_name_plural or model_name,
        'object_list': page_obj,
        'page_obj': page_obj,
        'church': None,
        'church_admin': None,
    }
    return render(request, 'core/full_admin_list.html', context)


def full_admin_add(request, app_label, model_name):
    """Add new object."""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    model, _ = _get_full_admin_model(app_label, model_name)
    if not model:
        raise Http404
    FormClass = _build_model_form(model)
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f'Added {model._meta.verbose_name}.')
            return redirect('full_admin_list', app_label=app_label, model_name=model_name)
    else:
        form = FormClass()
    context = {
        'model': model,
        'model_name': model_name,
        'app_label': app_label,
        'form': form,
        'verbose_name': model._meta.verbose_name or model_name,
        'verbose_name_plural': model._meta.verbose_name_plural or model_name,
        'is_edit': False,
        'church': None,
        'church_admin': None,
    }
    return render(request, 'core/full_admin_form.html', context)


def full_admin_edit(request, app_label, model_name, pk):
    """Edit object."""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    model, _ = _get_full_admin_model(app_label, model_name)
    if not model:
        raise Http404
    obj = get_object_or_404(model, pk=pk)
    FormClass = _build_model_form(model)
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated {model._meta.verbose_name}.')
            return redirect('full_admin_list', app_label=app_label, model_name=model_name)
    else:
        form = FormClass(instance=obj)
    context = {
        'model': model,
        'model_name': model_name,
        'app_label': app_label,
        'form': form,
        'obj': obj,
        'verbose_name': model._meta.verbose_name or model_name,
        'verbose_name_plural': model._meta.verbose_name_plural or model_name,
        'is_edit': True,
        'church': None,
        'church_admin': None,
    }
    # For Global Settings edit: add hero media link and preview
    if model_name == 'globalsettings' and hasattr(obj, 'global_hero'):
        hero = getattr(obj, 'global_hero', None)
        context['hero_media_url'] = reverse('full_admin_hero_media', args=[str(obj.pk)]) if obj.pk else None
        context['global_hero'] = hero
        context['global_hero_media_list'] = list(hero.hero_media.all().order_by('order', 'id')[:12]) if hero else []
    return render(request, 'core/full_admin_form.html', context)


@require_POST
def full_admin_delete(request, app_label, model_name, pk):
    """Delete object."""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_dashboard')}))
    model, _ = _get_full_admin_model(app_label, model_name)
    if not model:
        raise Http404
    obj = get_object_or_404(model, pk=pk)
    obj.delete()
    messages.success(request, f'Deleted {model._meta.verbose_name}.')
    return redirect('full_admin_list', app_label=app_label, model_name=model_name)


class FullAdminHeroMediaForm(django_forms.ModelForm):
    """Hero media form for full-admin; allows empty image/video for extra formset rows."""
    image = django_forms.ImageField(required=False)
    video = django_forms.FileField(required=False)

    class Meta:
        model = HeroMedia
        fields = ['image', 'video', 'order']

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')
        if not image and not video and self.instance and self.instance.pk:
            if not (getattr(self.instance, 'image', None) or getattr(self.instance, 'video', None)):
                raise django_forms.ValidationError('Provide at least an image or a video, or delete this row.')
        return cleaned_data


def full_admin_hero_media(request, pk):
    """Edit the selected global hero's pictures and videos (full-admin)."""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    obj = get_object_or_404(GlobalSettings, pk=pk)
    hero = obj.global_hero
    edit_url = reverse('full_admin_edit', args=['core', 'globalsettings', pk])
    if not hero:
        messages.warning(request, 'Save and select a global hero first, then you can edit its pictures and videos.')
        return redirect(edit_url)
    HeroMediaFormSet = inlineformset_factory(Hero, HeroMedia, form=FullAdminHeroMediaForm, extra=2, can_delete=True, max_num=20)
    if request.method == 'POST':
        formset = HeroMediaFormSet(request.POST, request.FILES, instance=hero)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Hero pictures and videos saved.')
            return redirect('full_admin_hero_media', pk=pk)
    else:
        formset = HeroMediaFormSet(instance=hero)
    context = {
        'obj': obj,
        'hero': hero,
        'formset': formset,
        'back_url': edit_url,
        'church': None,
        'church_admin': None,
    }
    return render(request, 'core/full_admin_hero_media.html', context)


def local_admin_events(request):
    """Local admin events management"""
    if not request.user.is_authenticated:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
    except ChurchAdmin.DoesNotExist:
        return redirect('admin:index')
    
    if church_admin.role != 'local_admin' or not church_admin.church:
        return redirect('admin:index')
    
    church = church_admin.church
    events = Event.objects.filter(church=church).prefetch_related('hero_media').order_by('-start_date')
    past_highlights = EventHighlight.objects.filter(church=church).order_by('-year')[:6]
    now = timezone.now()
    
    context = {
        'church': church,
        'events': events,
        'church_admin': church_admin,
        'past_highlights': past_highlights,
        'public_events_count': events.filter(is_public=True).count(),
        'upcoming_events_count': events.filter(end_date__gte=upcoming_events_cutoff()).count(),
        'featured_events_count': events.filter(is_featured=True).count(),
    }
    
    return render(request, 'core/local_admin_events.html', context)

def local_admin_ministries(request):
    """Local admin ministries management"""
    if not request.user.is_authenticated:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    
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
        'public_ministries_count': ministries.filter(is_public=True).count(),
        'active_ministries_count': ministries.filter(is_active=True).count(),
    }
    
    return render(request, 'core/local_admin_ministries.html', context)

def local_admin_news(request):
    """Local admin news management"""
    if not request.user.is_authenticated:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    
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
        'news': news_list,
        'news_list': news_list,
        'church_admin': church_admin,
    }
    
    return render(request, 'core/local_admin_news.html', context)

def local_admin_sermons(request):
    """Local admin sermons management"""
    if not request.user.is_authenticated:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    
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
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    
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
        
        return redirect('local_admin_donations')
    
    context = {
        'church': church,
        'donation_methods': donation_methods,
        'church_admin': church_admin,
    }
    
    return render(request, 'core/local_admin_donations.html', context)


@require_POST
def local_admin_donation_delete(request, method_id):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_donations')}))
        return redirect('admin:index')
    church_admin, church = church_data
    method = get_object_or_404(DonationMethod, id=method_id, church=church)
    name = method.name
    method.delete()
    messages.success(request, f'Donation method "{name}" was deleted.')
    return redirect('local_admin_donations')


@require_POST
def local_admin_donation_bulk_delete(request):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_donations')}))
        return redirect('admin:index')
    church_admin, church = church_data
    ids = request.POST.getlist('donation_method_ids')
    if ids:
        deleted = DonationMethod.objects.filter(id__in=ids, church=church).delete()
        count = deleted[0] if isinstance(deleted, tuple) else len(ids)
        messages.success(request, f'{count} donation method{"s" if count != 1 else ""} deleted.')
    return redirect('local_admin_donations')


def local_admin_heroes(request):
    """Local admin hero content management"""
    if not request.user.is_authenticated:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    
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
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    
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


def local_admin_live_stream(request):
    """Local admin: configure live stream for the church's Watch Online page. Stays in Bethel Admin."""
    if not request.user.is_authenticated:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
    except ChurchAdmin.DoesNotExist:
        messages.info(request, 'Live stream is configured per church. Add yourself as a Local Admin for a church to use this page.')
        return redirect('local_admin_dashboard')
    if church_admin.role != 'local_admin' or not church_admin.church:
        messages.info(request, 'Live stream is configured per church. You need Local Admin role for a church to edit it here.')
        return redirect('local_admin_dashboard')
    church = church_admin.church

    settings_obj, _ = LiveStreamSettings.objects.get_or_create(
        church=church,
        defaults={'platform': 'youtube'}
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'request_global':
            settings_obj.is_global_featured = True
            settings_obj.global_feature_status = 'pending'
            settings_obj.save()
            messages.success(request, 'Request sent to feature this live stream on the global Watch Online page. A global admin will review it.')
            return redirect('local_admin_live_stream')
        settings_obj.platform = request.POST.get('platform', 'youtube')
        settings_obj.youtube_channel_id = (request.POST.get('youtube_channel_id') or '').strip()
        settings_obj.facebook_live_url = (request.POST.get('facebook_live_url') or '').strip()
        settings_obj.red5_stream_url = (request.POST.get('red5_stream_url') or '').strip()
        settings_obj.is_live = request.POST.get('is_live') == 'on'
        settings_obj.autoplay = request.POST.get('autoplay') == 'on'
        settings_obj.save()
        messages.success(request, 'Live stream settings saved.')
        return redirect('local_admin_live_stream')

    context = {
        'church': church,
        'church_admin': church_admin,
        'settings': settings_obj,
    }
    return render(request, 'core/local_admin_live_stream.html', context)


def local_admin_global_live_requests(request):
    """List churches that requested their live stream on the global Watch Online page. Superuser only. Approve/reject here — no Django admin."""
    if not request.user.is_authenticated:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    if not request.user.is_superuser:
        messages.info(request, 'Only superadmins can approve global live requests.')
        return redirect('local_admin_dashboard')
    pending = LiveStreamSettings.objects.filter(
        church__isnull=False,
        global_feature_status='pending'
    ).select_related('church').order_by('-id')
    context = {
        'church': None,
        'church_admin': None,
        'pending_global_live': pending,
        'pending_global_live_count': pending.count(),
    }
    return render(request, 'core/local_admin_global_live_requests.html', context)


@require_POST
def local_admin_global_live_respond(request, settings_id):
    """Approve or reject a church's request to feature their live stream on the global Watch Online page. Superuser only."""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('local_admin_dashboard')
    settings_obj = get_object_or_404(LiveStreamSettings, id=settings_id)
    action = request.POST.get('action')
    if action == 'approve':
        settings_obj.global_feature_status = 'approved'
        settings_obj.is_global_featured = True
        settings_obj.save()
        church_name = settings_obj.church.name if settings_obj.church else 'Church'
        messages.success(request, f'Approved global live request for {church_name}. Their stream can now appear on the global Watch Online page.')
    elif action == 'reject':
        settings_obj.global_feature_status = 'rejected'
        settings_obj.is_global_featured = False
        settings_obj.save()
        church_name = settings_obj.church.name if settings_obj.church else 'Church'
        messages.success(request, f'Rejected global live request for {church_name}.')
    return redirect('local_admin_global_live_requests')


def _get_local_admin_church(request):
    """Return (church_admin, church) for local admin or None (caller should redirect)."""
    if not request.user.is_authenticated:
        return None
    try:
        church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
    except ChurchAdmin.DoesNotExist:
        return None
    if church_admin.role != 'local_admin' or not church_admin.church:
        return None
    return (church_admin, church_admin.church)


def local_admin_event_add(request):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_event_add')}))
        return redirect('admin:index')
    church_admin, church = church_data
    if request.method == 'POST':
        form = LocalAdminEventForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.church = church
            obj.save()
            messages.success(request, f'Event "{obj.title}" created.')
            return redirect('local_admin_events')
    else:
        form = LocalAdminEventForm()
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Add Event', 'obj': None, 'list_url': reverse('local_admin_events')}
    return render(request, 'core/local_admin_event_form.html', context)


def local_admin_event_edit(request, event_id):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
        return redirect('admin:index')
    church_admin, church = church_data
    event = get_object_or_404(Event, id=event_id, church=church)
    if request.method == 'POST':
        form = LocalAdminEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f'Event "{event.title}" updated.')
            return redirect('local_admin_events')
    else:
        form = LocalAdminEventForm(instance=event)
        dt_format = '%Y-%m-%dT%H:%M'
        for field_name, dt in [('start_date', event.start_date), ('end_date', event.end_date), ('registration_deadline', getattr(event, 'registration_deadline', None))]:
            if dt and field_name in form.fields:
                if timezone.is_aware(dt):
                    dt = timezone.localtime(dt)
                form.fields[field_name].initial = dt.strftime(dt_format)
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Edit Event', 'obj': event, 'list_url': reverse('local_admin_events')}
    return render(request, 'core/local_admin_event_form.html', context)


@require_POST
def local_admin_event_delete(request, event_id):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_events')}))
        return redirect('admin:index')
    church_admin, church = church_data
    event = get_object_or_404(Event, id=event_id, church=church)
    name = event.title
    event.delete()
    messages.success(request, f'Event "{name}" was deleted.')
    return redirect('local_admin_events')


@require_POST
def local_admin_event_bulk_delete(request):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_events')}))
        return redirect('admin:index')
    church_admin, church = church_data
    ids = request.POST.getlist('event_ids')
    if ids:
        deleted = Event.objects.filter(id__in=ids, church=church).delete()
        count = deleted[0] if isinstance(deleted, tuple) else len(ids)
        messages.success(request, f'{count} event{"s" if count != 1 else ""} deleted.')
    return redirect('local_admin_events')


def _get_event_for_local_admin(request, event_id):
    """Return (church_admin, church, event) or None if not allowed."""
    church_data = _get_local_admin_church(request)
    if not church_data:
        return None
    church_admin, church = church_data
    event = get_object_or_404(Event, id=event_id, church=church)
    return (church_admin, church, event)


def local_admin_event_hero_media(request, event_id):
    data = _get_event_for_local_admin(request, event_id)
    if not data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
        return redirect('admin:index')
    church_admin, church, event = data
    if request.method == 'POST':
        if request.POST.get('delete_id'):
            media = get_object_or_404(EventHeroMedia, id=request.POST['delete_id'], event=event)
            media.delete()
            messages.success(request, 'Hero media removed.')
            return redirect('local_admin_event_hero_media', event_id=event_id)
        form = LocalAdminEventHeroMediaForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.event = event
            obj.save()
            messages.success(request, 'Hero image/video added.')
            return redirect('local_admin_event_hero_media', event_id=event_id)
    else:
        form = LocalAdminEventHeroMediaForm()
    media_list = event.hero_media.all().order_by('order', 'id')
    context = {'event': event, 'church': church, 'church_admin': church_admin, 'form': form, 'media_list': media_list, 'list_url': reverse('local_admin_event_edit', args=[event_id])}
    return render(request, 'core/local_admin_event_hero_media.html', context)


def local_admin_event_speakers(request, event_id):
    data = _get_event_for_local_admin(request, event_id)
    if not data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
        return redirect('admin:index')
    church_admin, church, event = data
    speakers = event.speakers.all().order_by('name')
    context = {'event': event, 'church': church, 'church_admin': church_admin, 'speakers': speakers, 'list_url': reverse('local_admin_event_edit', args=[event_id])}
    return render(request, 'core/local_admin_event_speakers.html', context)


def local_admin_event_speaker_add(request, event_id):
    data = _get_event_for_local_admin(request, event_id)
    if not data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
        return redirect('admin:index')
    church_admin, church, event = data
    if request.method == 'POST':
        form = LocalAdminEventSpeakerForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.event = event
            obj.save()
            messages.success(request, f'Speaker "{obj.name}" added.')
            return redirect('local_admin_event_speakers', event_id=event_id)
    else:
        form = LocalAdminEventSpeakerForm()
    context = {'event': event, 'church': church, 'church_admin': church_admin, 'form': form, 'list_url': reverse('local_admin_event_speakers', args=[event_id])}
    return render(request, 'core/local_admin_event_speaker_form.html', context)


def local_admin_event_speaker_edit(request, event_id, speaker_id):
    data = _get_event_for_local_admin(request, event_id)
    if not data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
        return redirect('admin:index')
    church_admin, church, event = data
    speaker = get_object_or_404(EventSpeaker, id=speaker_id, event=event)
    if request.method == 'POST':
        form = LocalAdminEventSpeakerForm(request.POST, request.FILES, instance=speaker)
        if form.is_valid():
            form.save()
            messages.success(request, f'Speaker "{speaker.name}" updated.')
            return redirect('local_admin_event_speakers', event_id=event_id)
    else:
        form = LocalAdminEventSpeakerForm(instance=speaker)
    context = {'event': event, 'church': church, 'church_admin': church_admin, 'form': form, 'obj': speaker, 'list_url': reverse('local_admin_event_speakers', args=[event_id])}
    return render(request, 'core/local_admin_event_speaker_form.html', context)


@require_POST
def local_admin_event_speaker_delete(request, event_id, speaker_id):
    data = _get_event_for_local_admin(request, event_id)
    if not data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_event_speakers', args=[event_id])}))
        return redirect('admin:index')
    church_admin, church, event = data
    speaker = get_object_or_404(EventSpeaker, id=speaker_id, event=event)
    name = speaker.name
    speaker.delete()
    messages.success(request, f'Speaker "{name}" removed.')
    return redirect('local_admin_event_speakers', event_id=event_id)


def local_admin_event_schedule(request, event_id):
    data = _get_event_for_local_admin(request, event_id)
    if not data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
        return redirect('admin:index')
    church_admin, church, event = data
    items = event.schedule_items.all().order_by('day', 'start_time')
    context = {'event': event, 'church': church, 'church_admin': church_admin, 'items': items, 'list_url': reverse('local_admin_event_edit', args=[event_id])}
    return render(request, 'core/local_admin_event_schedule.html', context)


def local_admin_event_schedule_add(request, event_id):
    data = _get_event_for_local_admin(request, event_id)
    if not data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
        return redirect('admin:index')
    church_admin, church, event = data
    if request.method == 'POST':
        form = LocalAdminEventScheduleItemForm(request.POST, event=event)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.event = event
            obj.save()
            messages.success(request, f'Schedule item "{obj.title}" added.')
            return redirect('local_admin_event_schedule', event_id=event_id)
    else:
        form = LocalAdminEventScheduleItemForm(event=event)
    context = {'event': event, 'church': church, 'church_admin': church_admin, 'form': form, 'list_url': reverse('local_admin_event_schedule', args=[event_id])}
    return render(request, 'core/local_admin_event_schedule_form.html', context)


def local_admin_event_schedule_edit(request, event_id, item_id):
    data = _get_event_for_local_admin(request, event_id)
    if not data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
        return redirect('admin:index')
    church_admin, church, event = data
    item = get_object_or_404(EventScheduleItem, id=item_id, event=event)
    if request.method == 'POST':
        form = LocalAdminEventScheduleItemForm(request.POST, event=event, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule item updated.')
            return redirect('local_admin_event_schedule', event_id=event_id)
    else:
        form = LocalAdminEventScheduleItemForm(event=event, instance=item)
    context = {'event': event, 'church': church, 'church_admin': church_admin, 'form': form, 'obj': item, 'list_url': reverse('local_admin_event_schedule', args=[event_id])}
    return render(request, 'core/local_admin_event_schedule_form.html', context)


@require_POST
def local_admin_event_schedule_delete(request, event_id, item_id):
    data = _get_event_for_local_admin(request, event_id)
    if not data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_event_schedule', args=[event_id])}))
        return redirect('admin:index')
    church_admin, church, event = data
    item = get_object_or_404(EventScheduleItem, id=item_id, event=event)
    item.delete()
    messages.success(request, 'Schedule item removed.')
    return redirect('local_admin_event_schedule', event_id=event_id)


def local_admin_ministry_add(request):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_ministry_add')}))
        return redirect('admin:index')
    church_admin, church = church_data
    if request.method == 'POST':
        form = LocalAdminMinistryForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.church = church
            obj.save()
            messages.success(request, f'Ministry "{obj.name}" created.')
            return redirect('local_admin_ministries')
    else:
        form = LocalAdminMinistryForm()
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Add Ministry', 'list_url': reverse('local_admin_ministries')}
    return render(request, 'core/local_admin_form.html', context)


def local_admin_ministry_edit(request, ministry_id):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
        return redirect('admin:index')
    church_admin, church = church_data
    ministry = get_object_or_404(Ministry, id=ministry_id, church=church)
    if request.method == 'POST':
        form = LocalAdminMinistryForm(request.POST, request.FILES, instance=ministry)
        if form.is_valid():
            form.save()
            messages.success(request, f'Ministry "{ministry.name}" updated.')
            return redirect('local_admin_ministries')
    else:
        form = LocalAdminMinistryForm(instance=ministry)
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Edit Ministry', 'obj': ministry, 'list_url': reverse('local_admin_ministries')}
    return render(request, 'core/local_admin_form.html', context)


@require_POST
def local_admin_ministry_delete(request, ministry_id):
    """Delete a single ministry (church must match)."""
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_ministries')}))
        return redirect('admin:index')
    church_admin, church = church_data
    ministry = get_object_or_404(Ministry, id=ministry_id, church=church)
    name = ministry.name
    ministry.delete()
    messages.success(request, f'Ministry "{name}" was deleted.')
    return redirect('local_admin_ministries')


@require_POST
def local_admin_ministry_bulk_delete(request):
    """Delete selected ministries (by checkbox)."""
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_ministries')}))
        return redirect('admin:index')
    church_admin, church = church_data
    ids = request.POST.getlist('ministry_ids')
    if ids:
        deleted = Ministry.objects.filter(id__in=ids, church=church).delete()
        count = deleted[0] if isinstance(deleted, tuple) else len(ids)
        messages.success(request, f'{count} ministr{"y" if count == 1 else "ies"} deleted.')
    return redirect('local_admin_ministries')


def local_admin_news_add(request):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_news_add')}))
        return redirect('admin:index')
    church_admin, church = church_data
    if request.method == 'POST':
        form = LocalAdminNewsForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.church = church
            obj.save()
            messages.success(request, f'News "{obj.title}" created.')
            return redirect('local_admin_news')
    else:
        form = LocalAdminNewsForm()
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Add News', 'list_url': reverse('local_admin_news')}
    return render(request, 'core/local_admin_form.html', context)


def local_admin_news_edit(request, news_id):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
        return redirect('admin:index')
    church_admin, church = church_data
    news_item = get_object_or_404(News, id=news_id, church=church)
    if request.method == 'POST':
        form = LocalAdminNewsForm(request.POST, request.FILES, instance=news_item)
        if form.is_valid():
            form.save()
            messages.success(request, f'News "{news_item.title}" updated.')
            return redirect('local_admin_news')
    else:
        form = LocalAdminNewsForm(instance=news_item)
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Edit News', 'obj': news_item, 'list_url': reverse('local_admin_news')}
    return render(request, 'core/local_admin_form.html', context)


@require_POST
def local_admin_news_delete(request, news_id):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_news')}))
        return redirect('admin:index')
    church_admin, church = church_data
    news_item = get_object_or_404(News, id=news_id, church=church)
    name = news_item.title
    news_item.delete()
    messages.success(request, f'News "{name}" was deleted.')
    return redirect('local_admin_news')


@require_POST
def local_admin_news_bulk_delete(request):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_news')}))
        return redirect('admin:index')
    church_admin, church = church_data
    ids = request.POST.getlist('news_ids')
    if ids:
        deleted = News.objects.filter(id__in=ids, church=church).delete()
        count = deleted[0] if isinstance(deleted, tuple) else len(ids)
        messages.success(request, f'{count} article{"s" if count != 1 else ""} deleted.')
    return redirect('local_admin_news')


def local_admin_sermon_add(request):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_sermon_add')}))
        return redirect('admin:index')
    church_admin, church = church_data
    if request.method == 'POST':
        form = LocalAdminSermonForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.church = church
            obj.save()
            messages.success(request, f'Sermon "{obj.title}" created.')
            return redirect('local_admin_sermons')
    else:
        form = LocalAdminSermonForm()
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Add Sermon', 'list_url': reverse('local_admin_sermons')}
    return render(request, 'core/local_admin_form.html', context)


def local_admin_sermon_edit(request, sermon_id):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
        return redirect('admin:index')
    church_admin, church = church_data
    sermon_obj = get_object_or_404(Sermon, id=sermon_id, church=church)
    if request.method == 'POST':
        form = LocalAdminSermonForm(request.POST, request.FILES, instance=sermon_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Sermon "{sermon_obj.title}" updated.')
            return redirect('local_admin_sermons')
    else:
        form = LocalAdminSermonForm(instance=sermon_obj)
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Edit Sermon', 'obj': sermon_obj, 'list_url': reverse('local_admin_sermons')}
    return render(request, 'core/local_admin_form.html', context)


@require_POST
def local_admin_sermon_delete(request, sermon_id):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_sermons')}))
        return redirect('admin:index')
    church_admin, church = church_data
    sermon_obj = get_object_or_404(Sermon, id=sermon_id, church=church)
    name = sermon_obj.title
    sermon_obj.delete()
    messages.success(request, f'Sermon "{name}" was deleted.')
    return redirect('local_admin_sermons')


@require_POST
def local_admin_sermon_bulk_delete(request):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_sermons')}))
        return redirect('admin:index')
    church_admin, church = church_data
    ids = request.POST.getlist('sermon_ids')
    if ids:
        deleted = Sermon.objects.filter(id__in=ids, church=church).delete()
        count = deleted[0] if isinstance(deleted, tuple) else len(ids)
        messages.success(request, f'{count} sermon{"s" if count != 1 else ""} deleted.')
    return redirect('local_admin_sermons')


def local_admin_donation_edit(request, method_id):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
        return redirect('admin:index')
    church_admin, church = church_data
    method = get_object_or_404(DonationMethod, id=method_id, church=church)
    if request.method == 'POST':
        form = LocalAdminDonationMethodForm(request.POST, instance=method)
        if form.is_valid():
            form.save()
            messages.success(request, f'Donation method "{method.name}" updated.')
            return redirect('local_admin_donations')
    else:
        form = LocalAdminDonationMethodForm(instance=method)
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Edit Donation Method', 'obj': method, 'list_url': reverse('local_admin_donations')}
    return render(request, 'core/local_admin_form.html', context)


def local_admin_hero_add(request):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_hero_add')}))
        return redirect('admin:index')
    church_admin, church = church_data
    if request.method == 'POST':
        form = LocalAdminHeroForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.church = church
            obj.save()
            messages.success(request, f'Hero "{obj.title}" created.')
            return redirect('local_admin_heroes')
    else:
        form = LocalAdminHeroForm()
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Add Hero', 'list_url': reverse('local_admin_heroes')}
    return render(request, 'core/local_admin_form.html', context)


def local_admin_hero_edit(request, hero_id):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
        return redirect('admin:index')
    church_admin, church = church_data
    hero = get_object_or_404(Hero, id=hero_id, church=church)
    if request.method == 'POST':
        form = LocalAdminHeroForm(request.POST, request.FILES, instance=hero)
        if form.is_valid():
            form.save()
            messages.success(request, f'Hero "{hero.title}" updated. Your changes are saved.')
            return redirect('local_admin_heroes')
        else:
            messages.error(request, 'Please fix the errors below. If you changed the image or video, select the file again and save.')
    else:
        form = LocalAdminHeroForm(instance=hero)
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Edit Hero', 'obj': hero, 'list_url': reverse('local_admin_heroes')}
    return render(request, 'core/local_admin_form.html', context)


@require_POST
def local_admin_hero_delete(request, hero_id):
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_heroes')}))
        return redirect('admin:index')
    church_admin, church = church_data
    hero = get_object_or_404(Hero, id=hero_id, church=church)
    name = hero.title
    hero.delete()
    messages.success(request, f'Hero "{name}" was deleted.')
    return redirect('local_admin_heroes')


# --- Church members: add/remove members and assign rights (for local admins of this church) ---
def local_admin_members(request):
    """List members (ChurchAdmin) for the current church. Local admin only."""
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_members')}))
        return redirect('admin:index')
    church_admin, church = church_data
    members = ChurchAdmin.objects.filter(church=church).select_related('user').order_by('user__username')
    context = {'members': members, 'church': church, 'church_admin': church_admin}
    return render(request, 'core/local_admin_members.html', context)


def local_admin_member_add(request):
    """Add a new member to this church (create User + ChurchAdmin)."""
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_member_add')}))
        return redirect('admin:index')
    church_admin, church = church_data
    if request.method == 'POST':
        form = ChurchMemberAddForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            user.is_staff = True
            user.email = form.cleaned_data.get('email', '') or ''
            user.first_name = form.cleaned_data.get('first_name', '') or ''
            user.last_name = form.cleaned_data.get('last_name', '') or ''
            user.save()
            role = form.cleaned_data.get('role', 'local_admin')
            ChurchAdmin.objects.create(user=user, church=church, role=role, is_active=True)
            messages.success(request, f'Member "{user.username}" added. They can now log in and manage this church.')
            return redirect('local_admin_members')
    else:
        form = ChurchMemberAddForm()
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Add member'}
    return render(request, 'core/local_admin_member_form.html', context)


def local_admin_member_edit(request, user_id):
    """Edit a member's role and active status."""
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
        return redirect('admin:index')
    church_admin, church = church_data
    target_user = get_object_or_404(User, id=user_id)
    ca = get_object_or_404(ChurchAdmin, user=target_user, church=church)
    if request.method == 'POST':
        form = ChurchMemberEditForm(request.POST)
        if form.is_valid():
            ca.role = form.cleaned_data['role']
            ca.is_active = form.cleaned_data['is_active']
            ca.save()
            messages.success(request, f'Member "{target_user.username}" updated.')
            return redirect('local_admin_members')
    else:
        form = ChurchMemberEditForm(initial={'role': ca.role, 'is_active': ca.is_active})
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Edit member', 'obj': target_user, 'member': ca}
    return render(request, 'core/local_admin_member_form.html', context)


@require_POST
def local_admin_member_remove(request, user_id):
    """Remove member's access (set is_active=False)."""
    church_data = _get_local_admin_church(request)
    if not church_data:
        return redirect('admin:index')
    church_admin, church = church_data
    target_user = get_object_or_404(User, id=user_id)
    ca = ChurchAdmin.objects.filter(user=target_user, church=church).first()
    if ca:
        ca.is_active = False
        ca.save()
        messages.success(request, f'Access removed for "{target_user.username}". They can no longer log in to this church dashboard.')
    return redirect('local_admin_members')


@require_POST
def local_admin_member_bulk_remove(request):
    """Remove selected members' access (set is_active=False)."""
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': reverse('local_admin_members')}))
        return redirect('admin:index')
    church_admin, church = church_data
    user_ids = request.POST.getlist('member_user_ids')
    if user_ids:
        count = ChurchAdmin.objects.filter(church=church, user_id__in=user_ids).update(is_active=False)
        messages.success(request, f'Access removed for {count} member{"s" if count != 1 else ""}.')
    return redirect('local_admin_members')


def local_admin_member_set_password(request, user_id):
    """Set password for a church member (local admin only)."""
    church_data = _get_local_admin_church(request)
    if not church_data:
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
        return redirect('admin:index')
    church_admin, church = church_data
    target_user = get_object_or_404(User, id=user_id)
    get_object_or_404(ChurchAdmin, user=target_user, church=church)
    if request.method == 'POST':
        form = SetPasswordFormCustom(target_user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Password set for "{target_user.username}".')
            return redirect('local_admin_members')
    else:
        form = SetPasswordFormCustom(target_user)
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Set password', 'obj': target_user}
    return render(request, 'core/local_admin_user_password.html', context)


def _superuser_required(view_func):
    """Decorator: redirect to dashboard if not superuser."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
        if not request.user.is_superuser:
            messages.error(request, 'Only superadmins can manage users.')
            return redirect('local_admin_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@_superuser_required
def local_admin_users(request):
    """List users (superuser only)."""
    users = User.objects.all().order_by('username')
    church_admins_map = {ca.user_id: ca for ca in ChurchAdmin.objects.select_related('church').all()}
    users_with_roles = [{'user': u, 'church_admin': church_admins_map.get(u.id)} for u in users]
    church_data = _get_local_admin_church(request)
    church = church_data[1] if church_data else None
    church_admin = church_data[0] if church_data else None
    context = {
        'users_with_roles': users_with_roles,
        'church': church,
        'church_admin': church_admin,
    }
    return render(request, 'core/local_admin_users.html', context)


@_superuser_required
def local_admin_user_add(request):
    """Add user (superuser only)."""
    church_data = _get_local_admin_church(request)
    church = church_data[1] if church_data else None
    church_admin = church_data[0] if church_data else None
    if request.method == 'POST':
        form = UserAddForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            role = form.cleaned_data.get('role')
            church_obj = form.cleaned_data.get('church')
            if role and church_obj:
                ChurchAdmin.objects.create(user=user, church=church_obj, role=role, is_active=True)
            elif role and role.strip():
                ChurchAdmin.objects.create(user=user, church=None, role=role, is_active=True)
            messages.success(request, f'User "{user.username}" created.')
            return redirect('local_admin_users')
    else:
        form = UserAddForm()
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Add User'}
    return render(request, 'core/local_admin_user_form.html', context)


@_superuser_required
def local_admin_user_edit(request, user_id):
    """Edit user permissions and church role (superuser only)."""
    church_data = _get_local_admin_church(request)
    church = church_data[1] if church_data else None
    church_admin = church_data[0] if church_data else None
    target_user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, user=target_user)
        if form.is_valid():
            target_user.is_staff = form.cleaned_data['is_staff']
            target_user.is_superuser = form.cleaned_data['is_superuser']
            target_user.is_active = form.cleaned_data['is_active']
            target_user.save()
            role = form.cleaned_data.get('role')
            church_obj = form.cleaned_data.get('church')
            ca = ChurchAdmin.objects.filter(user=target_user).first()
            if role and role.strip():
                if ca:
                    ca.role = role
                    ca.church = church_obj
                    ca.is_active = form.cleaned_data['is_active']
                    ca.save()
                else:
                    ChurchAdmin.objects.create(user=target_user, church=church_obj, role=role, is_active=True)
            else:
                if ca:
                    ca.delete()
            messages.success(request, f'User "{target_user.username}" updated.')
            return redirect('local_admin_users')
    else:
        form = UserEditForm(user=target_user)
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Edit User', 'obj': target_user}
    return render(request, 'core/local_admin_user_form.html', context)


@_superuser_required
def local_admin_user_change_password(request, user_id):
    """Set password for a user (superuser only)."""
    church_data = _get_local_admin_church(request)
    church = church_data[1] if church_data else None
    church_admin = church_data[0] if church_data else None
    target_user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = SetPasswordFormCustom(target_user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Password updated for "{target_user.username}".')
            return redirect('local_admin_users')
    else:
        form = SetPasswordFormCustom(target_user)
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Set password', 'obj': target_user}
    return render(request, 'core/local_admin_user_password.html', context)


def local_admin_my_password_change(request):
    """Change own password (any logged-in admin)."""
    if not request.user.is_authenticated:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    church_data = _get_local_admin_church(request)
    church = church_data[1] if church_data else None
    church_admin = church_data[0] if church_data else None
    if request.method == 'POST':
        form = MyPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was changed.')
            return redirect('local_admin_dashboard')
    else:
        form = MyPasswordChangeForm(request.user)
    context = {'form': form, 'church': church, 'church_admin': church_admin, 'title': 'Change my password'}
    return render(request, 'core/local_admin_my_password.html', context)


def local_admin_mfa_security(request):
    """Enable or disable two-factor authentication (TOTP) for the current user."""
    if not request.user.is_authenticated:
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
    church_data = _get_local_admin_church(request)
    church = church_data[1] if church_data else None
    church_admin = church_data[0] if church_data else None
    confirmed_device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()
    unconfirmed_device = TOTPDevice.objects.filter(user=request.user, confirmed=False).first()

    # Disable: require password and delete device
    if request.method == 'POST' and request.POST.get('action') == 'disable':
        from django.contrib.auth import authenticate
        password = request.POST.get('password', '')
        if authenticate(username=request.user.username, password=password):
            TOTPDevice.objects.filter(user=request.user).delete()
            messages.success(request, 'Two-factor authentication has been disabled.')
            return redirect('local_admin_dashboard')
        messages.error(request, 'Incorrect password.')
        return redirect('local_admin_mfa_security')

    # Confirm setup: user entered code to verify
    if request.method == 'POST' and request.POST.get('action') == 'confirm' and unconfirmed_device:
        token = (request.POST.get('token') or '').strip().replace(' ', '')
        if token and unconfirmed_device.verify_token(token):
            unconfirmed_device.confirmed = True
            unconfirmed_device.save()
            messages.success(request, 'Two-factor authentication is now enabled.')
            return redirect('local_admin_dashboard')
        messages.error(request, 'Invalid or expired code. Please try again.')

    # Start setup: create unconfirmed device
    if request.method == 'POST' and request.POST.get('action') == 'enable' and not confirmed_device:
        if unconfirmed_device:
            unconfirmed_device.delete()
        TOTPDevice.objects.create(user=request.user, name='default', confirmed=False)
        return redirect('local_admin_mfa_security')

    # Build QR for unconfirmed device (base64 data URL for img src)
    qr_data_url = None
    if unconfirmed_device:
        try:
            url = unconfirmed_device.config_url
            img = qrcode.make(url, version=1, box_size=4, border=2)
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            qr_data_url = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
        except Exception:
            pass

    context = {
        'church': church,
        'church_admin': church_admin,
        'title': 'Security & two-factor authentication',
        'has_mfa': bool(confirmed_device),
        'unconfirmed_device': unconfirmed_device,
        'qr_data_url': qr_data_url,
    }
    return render(request, 'core/local_admin_mfa_security.html', context)


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
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
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
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
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
        return redirect(reverse('local_admin_login') + '?' + urlencode({'next': request.get_full_path()}))
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

def volunteer(request):
    """Volunteer page - shows all ministries and allows joining"""
    # Get all active ministries from all churches
    ministries = Ministry.objects.filter(is_active=True, is_public=True).select_related('church')
    
    # Group ministries by church
    churches_with_ministries = {}
    for ministry in ministries:
        church = ministry.church
        if church not in churches_with_ministries:
            churches_with_ministries[church] = []
        churches_with_ministries[church].append(ministry)
    
    # Handle ministry join requests
    join_success = False
    selected_ministry = None
    
    if request.method == 'POST':
        form = MinistryJoinRequestForm(request.POST)
        if form.is_valid():
            ministry_id = request.POST.get('ministry_id')
            try:
                ministry = Ministry.objects.get(id=ministry_id, is_active=True)
                join_request = form.save(commit=False)
                join_request.ministry = ministry
                join_request.church = ministry.church
                join_request.save()
                join_success = True
                selected_ministry = ministry
                form = MinistryJoinRequestForm()  # Reset form
            except Ministry.DoesNotExist:
                pass
    else:
        form = MinistryJoinRequestForm()
    
    context = {
        'churches_with_ministries': churches_with_ministries,
        'join_form': form,
        'join_success': join_success,
        'selected_ministry': selected_ministry,
    }
    return render(request, 'core/volunteer.html', context)

def prayer_request(request):
    """Prayer requests page - submit and view prayer requests"""
    # Handle prayer request submission
    submit_success = False
    
    if request.method == 'POST':
        form = PrayerRequestForm(request.POST)
        if form.is_valid():
            prayer_request = form.save(commit=False)
            # Auto-assign church if user is on a church-specific page
            if hasattr(request, 'church'):
                prayer_request.church = request.church
            prayer_request.save()
            messages.success(request, 'Thank you for your prayer request! It will be reviewed and published soon.')
            return redirect('prayer_request')
    else:
        form = PrayerRequestForm()
    
    # Get approved prayer requests
    prayer_requests = PrayerRequest.objects.filter(
        is_approved=True, 
        is_public=True
    ).order_by('-created_at')
    
    # Filter by category if requested
    category_filter = request.GET.get('category', '')
    if category_filter:
        prayer_requests = prayer_requests.filter(category=category_filter)
    
    # Get answered prayers
    answered_prayers = PrayerRequest.objects.filter(
        is_approved=True,
        is_public=True,
        is_answered=True
    ).order_by('-answered_date')
    
    context = {
        'form': form,
        'prayer_requests': prayer_requests,
        'answered_prayers': answered_prayers,
        'category_filter': category_filter,
        'submit_success': submit_success,
    }
    return render(request, 'core/prayer_request.html', context)

def contact(request):
    """Contact page - allows users to send messages"""
    # Get global settings for contact info
    try:
        global_settings = GlobalSettings.get_settings()
    except:
        global_settings = None
    
    # Handle contact form submissions
    contact_success = False
    
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            # Auto-assign church if user is on a church-specific page
            if hasattr(request, 'church'):
                contact_message.church = request.church
            contact_message.save()
            contact_success = True
            form = ContactMessageForm()  # Reset form
    else:
        form = ContactMessageForm()
    
    context = {
        'form': form,
        'contact_success': contact_success,
        'global_settings': global_settings,
    }
    return render(request, 'core/contact.html', context)

def services(request):
    """Services page - showcases church services and ministries"""
    # Get global settings for contact info
    try:
        global_settings = GlobalSettings.get_settings()
    except:
        global_settings = None
    
    # Get all active ministries from all churches
    ministries = Ministry.objects.filter(is_active=True, is_public=True).select_related('church')
    
    # Group ministries by type
    ministry_types = {}
    for ministry in ministries:
        ministry_type = ministry.ministry_type
        if ministry_type not in ministry_types:
            ministry_types[ministry_type] = []
        ministry_types[ministry_type].append(ministry)
    
    # Define service categories
    service_categories = [
        {
            'title': 'Worship Services',
            'description': 'Join us for inspiring worship services where we come together to praise, pray, and grow in faith.',
            'icon': '🎵',
            'services': [
                'Sunday Services',
                'Wednesday Prayer Meetings',
                'Special Worship Events',
                'Praise and Worship Ministry'
            ]
        },
        {
            'title': 'Children & Youth',
            'description': 'Nurturing the next generation through age-appropriate programs and activities.',
            'icon': '👶',
            'services': [
                'Sunday School',
                'Youth Ministry',
                'Children\'s Church',
                'Vacation Bible School'
            ]
        },
        {
            'title': 'Community Outreach',
            'description': 'Serving our community through various outreach programs and initiatives.',
            'icon': '🤝',
            'services': [
                'Food Bank Ministry',
                'Homeless Outreach',
                'Community Service Projects',
                'Mission Trips'
            ]
        },
        {
            'title': 'Spiritual Growth',
            'description': 'Deepen your faith through Bible study, discipleship, and spiritual development programs.',
            'icon': '📖',
            'services': [
                'Bible Study Groups',
                'Discipleship Classes',
                'Prayer Ministry',
                'Counseling Services'
            ]
        },
        {
            'title': 'Family & Support',
            'description': 'Supporting families and individuals through life\'s challenges and celebrations.',
            'icon': '👨‍👩‍👧‍👦',
            'services': [
                'Marriage Counseling',
                'Family Ministry',
                'Grief Support',
                'Addiction Recovery'
            ]
        },
        {
            'title': 'Special Events',
            'description': 'Join us for special events, conferences, and celebrations throughout the year.',
            'icon': '🎉',
            'services': [
                'Annual Conferences',
                'Revival Services',
                'Holiday Celebrations',
                'Community Events'
            ]
        }
    ]
    
    context = {
        'service_categories': service_categories,
        'ministry_types': ministry_types,
        'global_settings': global_settings,
    }
    return render(request, 'core/services.html', context)

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
    
    # SEO
    meta_desc = (news.excerpt or news.content or news.title or '')[:160]
    if not meta_desc:
        meta_desc = f"{news.title} – {news.church.name}. Bethel Prayer Ministry International."
    og_image = None
    if getattr(news, 'image', None) and news.image:
        og_image = request.build_absolute_uri(news.get_image_url() if hasattr(news, 'get_image_url') else news.image.url)
    
    context = {
        'news': news,
        'all_events': all_events,
        'all_ministries': all_ministries,
        'related_news': related_news,
        'church': news.church,
        'meta_description': meta_desc[:160],
        'og_title': f"{news.title} – Bethel",
        'og_description': meta_desc[:160],
        'og_image': og_image,
    }
    
    return render(request, 'core/news_detail.html', context)



def debug_urls(request):
    """Debug view to show current database URLs"""
    try:
        from core.models import Church, News, Ministry, Sermon, HeroMedia
        
        output = []
        output.append("<h1>🔍 Database URL Debug</h1>")
        
        # Check Church logos
        output.append("<h2>📋 Church Logos:</h2>")
        churches = Church.objects.all()
        for church in churches:
            if church.logo:
                output.append(f"<p><strong>{church.name}:</strong> {church.logo}</p>")
            else:
                output.append(f"<p><strong>{church.name}:</strong> No logo</p>")
        
        # Check News images
        output.append("<h2>📋 News Images:</h2>")
        news_items = News.objects.all()
        for news in news_items:
            if news.image:
                output.append(f"<p><strong>{news.title}:</strong> {news.image}</p>")
            else:
                output.append(f"<p><strong>{news.title}:</strong> No image</p>")
        
        # Check HeroMedia images
        output.append("<h2>📋 HeroMedia Images:</h2>")
        hero_media = HeroMedia.objects.all()
        for media in hero_media:
            if media.image:
                output.append(f"<p><strong>{media.title}:</strong> {media.image}</p>")
            else:
                output.append(f"<p><strong>{media.title}:</strong> No image</p>")
        
        # Count local vs ImageKit URLs
        local_count = 0
        local_count = 0
        
        for church in churches:
            if church.logo:
                if not str(church.logo).startswith('http'):
                    local_count += 1
        
        for news in news_items:
            if news.image:
                if not str(news.image).startswith('http'):
                    local_count += 1
        
        for media in hero_media:
            if media.image:
                if not str(media.image).startswith('http'):
                    local_count += 1
        
        output.append(f"<h2>📊 Summary:</h2>")
        output.append(f"<p><strong>Local media files:</strong> {local_count}</p>")
        output.append(f"<p><strong>External URLs:</strong> {len(churches) + len(news_items) + len(hero_media) - local_count}</p>")
        
        if local_count > 0:
            output.append(f"<p style='color: green;'><strong>✅ Found {local_count} local media files!</strong></p>")
        else:
            output.append(f"<p style='color: blue;'><strong>ℹ️ All media files are external URLs!</strong></p>")
        
        return HttpResponse("".join(output))
        
    except Exception as e:
        return HttpResponse(f"❌ Error: {str(e)}")

def check_production_status(request):
    """Check production environment status"""
    
    status = {
        'environment': {
            'DEBUG': settings.DEBUG,
            'DEFAULT_FILE_STORAGE': settings.DEFAULT_FILE_STORAGE,
            'MEDIA_URL': settings.MEDIA_URL,
        },
        'storage_config': {
            'using_local_storage': 'django.core.files.storage.FileSystemStorage' in str(settings.DEFAULT_FILE_STORAGE),
            'media_url': settings.MEDIA_URL,
            'media_root': str(settings.MEDIA_ROOT),
        },
        'sample_media': {}
    }
    
    # Test local storage
    try:
        from django.core.files.storage import default_storage
        test_file = default_storage.save('test.txt', ContentFile(b'test'))
        default_storage.delete(test_file)
        status['storage_test'] = 'Working'
    except Exception as e:
        status['storage_test'] = f'Error: {str(e)}'
    
    # Check sample media URLs
    if Event.objects.exists():
        event = Event.objects.first()
        status['sample_media']['event'] = {
            'title': event.title,
            'image_field': str(event.image) if event.image else None,
            'get_url_method': event.get_image_url() if hasattr(event, 'get_image_url') else 'No method',
        }
    
    return JsonResponse(status)

def debug_env(request):
    """Debug endpoint to check environment variables"""
    return JsonResponse({
        'debug': settings.DEBUG,
        'storage_backend': str(settings.DEFAULT_FILE_STORAGE),
        'media_url': settings.MEDIA_URL,
        'media_root': str(settings.MEDIA_ROOT),
        'using_local_storage': 'django.core.files.storage.FileSystemStorage' in str(settings.DEFAULT_FILE_STORAGE),
    })

def test_local_upload_endpoint(request):
    """Test endpoint to upload an image to local storage"""
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    from django.http import JsonResponse
    
    try:
        # Create a test image
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1e3a8a;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="300" height="200" fill="url(#grad1)"/>
  <circle cx="150" cy="100" r="60" fill="#ffffff" opacity="0.9"/>
  <text x="150" y="95" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="#3b82f6" text-anchor="middle">BETHEL</text>
  <text x="150" y="115" font-family="Arial, sans-serif" font-size="14" fill="#1e3a8a" text-anchor="middle">LOCAL</text>
  <text x="150" y="135" font-family="Arial, sans-serif" font-size="12" fill="#1e3a8a" text-anchor="middle">TEST</text>
  <text x="150" y="175" font-family="Arial, sans-serif" font-size="10" fill="#ffffff" text-anchor="middle">Uploaded via Django</text>
</svg>'''
        
        test_image = ContentFile(svg_content.encode('utf-8'), name='bethel_local_test.svg')
        
        # Upload to local storage
        file_path = default_storage.save('bethel/test_image.svg', test_image)
        file_url = default_storage.url(file_path)
        
        return JsonResponse({
            'success': True,
            'file_path': file_path,
            'file_url': file_url,
            'storage_backend': str(settings.DEFAULT_FILE_STORAGE),
            'message': 'Image uploaded successfully to local storage!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'storage_backend': str(settings.DEFAULT_FILE_STORAGE)
        }, status=500)

@csrf_exempt
def upload_test_endpoint(request):
    """Local file upload endpoint"""
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    from django.views.decorators.http import require_http_methods
    from django.core.files.storage import default_storage
    import os
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        # Get the uploaded file
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image file provided'}, status=400)
        
        uploaded_file = request.FILES['image']
        
        # Save the file to local storage
        file_path = default_storage.save(f'uploads/{uploaded_file.name}', uploaded_file)
        file_url = default_storage.url(file_path)
        
        return JsonResponse({
            'success': True,
            'message': 'File uploaded successfully to local storage!',
            'file_name': uploaded_file.name,
            'file_path': file_path,
            'url': file_url,
            'size': uploaded_file.size
        })
            
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc(),
            'message': 'Upload failed due to an error',
            'imagekit_config': {
                'has_public_key': bool(settings.IMAGEKIT_CONFIG.get('PUBLIC_KEY')),
                'has_private_key': bool(settings.IMAGEKIT_CONFIG.get('PRIVATE_KEY')),
                'has_url_endpoint': bool(settings.IMAGEKIT_CONFIG.get('URL_ENDPOINT')),
            }
        }, status=500)

def health_check(request):
    """Health check endpoint to diagnose database and application status"""
    from django.http import JsonResponse
    from django.db import connection
    
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'database': {
            'connected': False,
            'error': None
        },
        'models': {
            'churches': 0,
            'events': 0,
            'ministries': 0
        }
    }
    
    # Test database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status['database']['connected'] = True
            
            # Test model queries
            try:
                health_status['models']['churches'] = Church.objects.count()
            except Exception as e:
                health_status['models']['churches'] = f"Error: {str(e)}"
            
            try:
                health_status['models']['events'] = Event.objects.count()
            except Exception as e:
                health_status['models']['events'] = f"Error: {str(e)}"
            
            try:
                health_status['models']['ministries'] = Ministry.objects.count()
            except Exception as e:
                health_status['models']['ministries'] = f"Error: {str(e)}"
                
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['database']['error'] = str(e)
    
    return JsonResponse(health_status)

def retry_database_operation(operation, max_retries=3, delay=1):
    """
    Retry a database operation with exponential backoff
    """
    for attempt in range(max_retries):
        try:
            return operation()
        except OperationalError as e:
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                if attempt < max_retries - 1:
                    print(f"DEBUG: Database connection attempt {attempt + 1} failed, retrying in {delay} seconds...")
                    time_module.sleep(delay)
                    delay *= 2  # Exponential backoff
                    continue
                else:
                    print(f"DEBUG: Database connection failed after {max_retries} attempts: {e}")
                    raise
            else:
                raise
    return None

def static_fallback(request):
    """Static fallback page when database is unavailable"""
    from django.http import HttpResponse
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bethel Prayer Ministry International</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .logo { font-size: 2em; color: #1e3a8a; font-weight: bold; margin-bottom: 10px; }
            .subtitle { color: #666; margin-bottom: 20px; }
            .message { background: #f0f9ff; border: 1px solid #0ea5e9; padding: 20px; border-radius: 5px; margin-bottom: 30px; }
            .contact { background: #fef3c7; border: 1px solid #f59e0b; padding: 20px; border-radius: 5px; }
            .contact h3 { margin-top: 0; color: #92400e; }
            .contact p { margin: 5px 0; }
            .refresh-btn { background: #1e3a8a; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            .refresh-btn:hover { background: #1e40af; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🏛️ Bethel Prayer Ministry International</div>
                <div class="subtitle">Connecting believers worldwide through prayer and fellowship</div>
            </div>
            
            <div class="message">
                <h3>🔄 Service Temporarily Unavailable</h3>
                <p>We're currently experiencing technical difficulties with our database connection. Our team is working to restore full service as quickly as possible.</p>
                <p>Please try refreshing the page in a few moments, or contact us if you need immediate assistance.</p>
            </div>
            
            <div class="contact">
                <h3>📞 Contact Information</h3>
                <p><strong>Email:</strong> members@gmail.com</p>
                <p><strong>Emergency Contact:</strong> Available through our prayer network</p>
                <p><strong>Prayer Requests:</strong> We're still accepting prayer requests via email</p>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <button class="refresh-btn" onclick="window.location.reload()">🔄 Refresh Page</button>
            </div>
            
            <div style="text-align: center; margin-top: 20px; color: #666; font-size: 14px;">
                <p>© 2026 Bethel. All rights reserved.</p>
            </div>
        </div>
        
        <script>
            // Auto-refresh every 30 seconds
            setTimeout(function() {
                window.location.reload();
            }, 30000);
        </script>
    </body>
    </html>
    """
    
    return HttpResponse(html_content, content_type='text/html')

def startup_health_check(request):
    """Lightweight health check for startup - no database required"""
    import os
    
    health_status = {
        'status': 'healthy',
        'timestamp': time_module.time(),
        'environment': os.environ.get('ENVIRONMENT', 'development'),
        'database_independent_mode': os.environ.get('DATABASE_INDEPENDENT_MODE', '0') == '1',
        'services': {
            'application': 'running',
            'database': 'unknown',  # Will be checked separately
            'storage': 'configured',
        },
        'message': 'Application is starting up'
    }
    
    # Check database status in background (non-blocking)
    try:
        db_available, db_error = get_database_status()
        health_status['services']['database'] = 'available' if db_available else 'unavailable'
        if not db_available:
            health_status['message'] = f'Database unavailable: {db_error}'
    except Exception as e:
        health_status['services']['database'] = 'error'
        health_status['message'] = f'Database check failed: {str(e)}'
    
    return JsonResponse(health_status)

def is_database_available():
    """Check if database is available without blocking"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return True
    except Exception:
        return False

def get_database_status():
    """Get database status with timeout"""
    import threading
    import queue
    
    result_queue = queue.Queue()
    
    def check_db():
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result_queue.put(('success', None))
        except Exception as e:
            result_queue.put(('error', str(e)))
    
    # Start database check in a separate thread
    thread = threading.Thread(target=check_db)
    thread.daemon = True
    thread.start()
    
    # Wait for result with timeout
    try:
        thread.join(timeout=5)  # 5 second timeout
        if thread.is_alive():
            return False, "Database check timed out"
        
        status, error = result_queue.get_nowait()
        return status == 'success', error
    except queue.Empty:
        return False, "Database check failed"

@require_POST
def clear_redirect_notification(request):
    """Clear the redirect notification session variables"""
    try:
        # Clear the session variables
        if 'local_church_redirect' in request.session:
            del request.session['local_church_redirect']
        if 'global_church_fallback' in request.session:
            del request.session['global_church_fallback']
        if 'redirected_church' in request.session:
            del request.session['redirected_church']
        if 'clear_redirect_notification' in request.session:
            del request.session['clear_redirect_notification']
        
        request.session.modified = True
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def analytics_dashboard(request):
    """Analytics dashboard for staff and church admins"""
    if not request.user.is_authenticated:
        return redirect('admin:login')
    # Allow staff or any active church admin (local admin dashboard user)
    try:
        from .models import ChurchAdmin
        is_church_admin = ChurchAdmin.objects.filter(user=request.user, is_active=True).exists()
    except Exception:
        is_church_admin = False
    if not (request.user.is_staff or is_church_admin):
        return redirect('admin:login')
    
    from .analytics_models import VisitorSession, PageView, AnalyticsSettings
    
    # Get date range (last 30 days by default)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Get analytics settings
    settings = AnalyticsSettings.get_settings()
    
    # Basic stats
    total_sessions = VisitorSession.objects.filter(started_at__gte=start_date).count()
    total_page_views = PageView.objects.filter(viewed_at__gte=start_date).count()
    unique_visitors = VisitorSession.objects.filter(started_at__gte=start_date).values('ip_address').distinct().count()
    
    # Average session duration
    completed_sessions = VisitorSession.objects.filter(
        started_at__gte=start_date,
        ended_at__isnull=False
    )
    avg_duration = completed_sessions.aggregate(avg_duration=Avg('duration'))['avg_duration'] or 0
    
    # Device breakdown
    device_stats = VisitorSession.objects.filter(started_at__gte=start_date).values('device_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Browser breakdown
    browser_stats = VisitorSession.objects.filter(
        started_at__gte=start_date,
        browser__isnull=False
    ).exclude(browser='').values('browser').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Top countries
    country_stats = VisitorSession.objects.filter(
        started_at__gte=start_date,
        country__isnull=False
    ).exclude(country='').values('country').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Top pages
    page_stats = PageView.objects.filter(viewed_at__gte=start_date).values('path').annotate(
        views=Count('id')
    ).order_by('-views')[:10]
    
    # Daily visitors chart data
    daily_visitors = VisitorSession.objects.filter(
        started_at__gte=start_date
    ).annotate(
        date=TruncDate('started_at')
    ).values('date').annotate(
        visitors=Count('id')
    ).order_by('date')
    
    # Hourly activity
    hourly_activity = VisitorSession.objects.filter(
        started_at__gte=start_date
    ).annotate(
        hour=TruncHour('started_at')
    ).values('hour').annotate(
        sessions=Count('id')
    ).order_by('hour')
    
    # Top referrers
    referrer_stats = VisitorSession.objects.filter(
        started_at__gte=start_date,
        referrer_domain__isnull=False
    ).exclude(referrer_domain='').values('referrer_domain').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Church-specific stats (if applicable)
    church_stats = None
    if request.user.is_superuser:
        church_stats = VisitorSession.objects.filter(
            started_at__gte=start_date,
            church__isnull=False
        ).values('church__name').annotate(
            sessions=Count('id'),
            page_views=Count('page_views_count')
        ).order_by('-sessions')[:10]
    
    # Get visitor sessions for map (with coordinates)
    visitor_sessions = VisitorSession.objects.filter(
        started_at__gte=start_date,
        country__isnull=False
    ).exclude(country='').values('country', 'city').annotate(
        count=Count('id')
    ).order_by('-count')[:20]
    
    # Add sample coordinates for countries (you can enhance this with a proper geocoding service)
    country_coordinates = {
        'United States': {'lat': 39.8283, 'lng': -98.5795},
        'Germany': {'lat': 51.1657, 'lng': 10.4515},
        'United Kingdom': {'lat': 55.3781, 'lng': -3.4360},
        'Canada': {'lat': 56.1304, 'lng': -106.3468},
        'Australia': {'lat': -25.2744, 'lng': 133.7751},
        'France': {'lat': 46.2276, 'lng': 2.2137},
        'Netherlands': {'lat': 52.1326, 'lng': 5.2913},
        'Sweden': {'lat': 60.1282, 'lng': 18.6435},
        'Norway': {'lat': 60.4720, 'lng': 8.4689},
        'Denmark': {'lat': 56.2639, 'lng': 9.5018},
    }
    
    # Add coordinates to visitor sessions
    for session in visitor_sessions:
        if session['country'] in country_coordinates:
            session.update(country_coordinates[session['country']])
        else:
            session.update({'lat': 0, 'lng': 0})
    
    # JSON-serialized for chart JS (dates and querysets need default=str)
    context = {
        'total_sessions': total_sessions,
        'total_page_views': total_page_views,
        'unique_visitors': unique_visitors,
        'avg_duration': int(avg_duration),
        'device_stats': device_stats,
        'browser_stats': browser_stats,
        'country_stats': country_stats,
        'page_stats': page_stats,
        'referrer_stats': referrer_stats,
        'church_stats': church_stats,
        'visitor_sessions': list(visitor_sessions),
        'daily_visitors': list(daily_visitors),
        'hourly_activity': list(hourly_activity),
        'daily_visitors_json': json.dumps(list(daily_visitors), default=str),
        'device_stats_json': json.dumps(list(device_stats), default=str),
        'browser_stats_json': json.dumps(list(browser_stats), default=str),
        'country_stats_json': json.dumps(list(country_stats), default=str),
        'start_date': start_date,
        'end_date': end_date,
        'settings': settings,
    }
    
    return render(request, 'core/analytics_dashboard.html', context)

def _get_footer_context():
    """Get footer_copyright and footer_links for error pages (no request context)."""
    try:
        gs = GlobalSettings.get_settings()
        footer_copyright = getattr(gs, 'footer_copyright', '© 2026 Bethel')
        if isinstance(footer_copyright, str) and '2025' in footer_copyright:
            footer_copyright = footer_copyright.replace('2025', '2026')
        if not isinstance(footer_copyright, str):
            footer_copyright = '© 2026 Bethel'
        footer_links = gs.get_footer_links() if hasattr(gs, 'get_footer_links') else []
        if not isinstance(footer_links, list):
            footer_links = []
    except Exception:
        footer_copyright = '© 2026 Bethel'
        footer_links = []
    return {'footer_copyright': footer_copyright, 'footer_links': footer_links}


def custom_error_500(request):
    """Custom 500 handler so footer comes from admin."""
    context = _get_footer_context()
    return render(request, '500.html', context, status=500)


def custom_error_404(request, exception):
    """Custom 404 handler so footer comes from admin."""
    context = _get_footer_context()
    return render(request, '404.html', context, status=404)


def custom_error_403(request, exception):
    """Custom 403 handler so footer comes from admin."""
    context = _get_footer_context()
    return render(request, '403.html', context, status=403)


def custom_error_400(request, exception):
    """Custom 400 handler so footer comes from admin."""
    context = _get_footer_context()
    return render(request, '400.html', context, status=400)


@login_required
def user_profile(request):
    """User profile page"""
    user = request.user
    context = {
        'user': user,
        'title': 'User Profile',
    }
    return render(request, 'core/user_profile.html', context)
