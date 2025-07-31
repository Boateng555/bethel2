# --- Forced clean save to fix inline NameError ---
from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django import forms
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from django.db import models
from .models import (
    Church, ChurchAdmin, Event, Ministry, News, Sermon, 
    DonationMethod, Convention,
    NewsletterSignup, Hero, LocalHero, ChurchApplication, GlobalFeatureRequest, Testimony, AboutPage, LeadershipPage, LocalLeadershipPage, LocalAboutPage, MinistryJoinRequest,
    EventRegistration, EventHighlight, EventSpeaker, EventScheduleItem, EventHeroMedia, HeroMedia, GlobalSettings
)
from django.utils import timezone
from django.core.mail import send_mail
from .admin_utils import EnhancedImagePreviewMixin

from .models import HeroMedia

# Form classes - moved to top to avoid NameError
class ChurchForm(forms.ModelForm):
    class Meta:
        model = Church
        fields = '__all__'
    
    # Temporarily use regular ImageField instead of forms.ImageField
    logo = forms.ImageField(required=False)
    nav_logo = forms.ImageField(required=False)
    banner_image = forms.ImageField(required=False)

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        help_texts = {
            'title': 'Enter the name of your event (e.g., "Sunday Service", "Youth Conference")',
            'description': 'Provide a detailed description of what this event is about, who should attend, and what to expect',
            'start_date': 'When does this event begin? Include both date and time',
            'end_date': 'When does this event end? Include both date and time',
            'location': 'Where is this event taking place? (e.g., "Main Auditorium", "Youth Hall")',
            'address': 'Full address where people can find this event',
            'event_type': 'What type of event is this? Choose the most appropriate category',
            'requires_registration': 'Check this if people need to register before attending',
            'max_attendees': 'Maximum number of people who can attend (leave blank if unlimited)',
            'registration_deadline': 'Last date people can register for this event',
            'registration_fee': 'How much does it cost to attend? (leave blank if free)',
            'is_featured': 'Feature this event prominently on your church website',
            'is_public': 'Show this event to visitors on your website',
            'is_big_event': 'Use special professional template with registration, countdown, and detailed sections',
            'is_global_featured': 'Request to show this event on the global Bethel website',
            'global_feature_status': 'Current status of your global feature request',
            'show_qr_code': 'Display a QR code on the event page for easy sharing',
        }
        labels = {
            'title': 'Event Title',
            'description': 'Event Description',
            'start_date': 'Start Date & Time',
            'end_date': 'End Date & Time',
            'location': 'Event Location',
            'address': 'Full Address',
            'event_type': 'Event Type',
            'requires_registration': 'Requires Registration',
            'max_attendees': 'Maximum Attendees',
            'registration_deadline': 'Registration Deadline',
            'registration_fee': 'Registration Fee',
            'is_featured': 'Featured Event',
            'is_public': 'Public Event',
            'is_big_event': 'Big Event (Professional Template)',
            'is_global_featured': 'Request Global Feature',
            'global_feature_status': 'Global Feature Status',
            'show_qr_code': 'Show QR Code',
        }

class MinistryForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    
    class Meta:
        model = Ministry
        fields = '__all__'
        help_texts = {
            'name': 'Name of your ministry (e.g., "Youth Ministry", "Women\'s Fellowship", "Prayer Team")',
            'description': 'Describe what this ministry does, who it serves, and how people can get involved',
            'ministry_type': 'What type of ministry is this? Choose the most appropriate category',
            'leader_name': 'Who leads this ministry? (e.g., "John Doe", "Sister Mary")',
            'contact_email': 'Email address for ministry inquiries',
            'contact_phone': 'Phone number for ministry inquiries',
            'image': 'Upload a photo representing this ministry (recommended size: 800x600px)',
            'is_active': 'Is this ministry currently active and accepting new members?',
            'is_featured': 'Feature this ministry prominently on your church website',
            'is_public': 'Show this ministry on the global Bethel website',
        }
        labels = {
            'name': 'Ministry Name',
            'description': 'Ministry Description',
            'ministry_type': 'Ministry Type',
            'leader_name': 'Leader Name',
            'contact_email': 'Contact Email',
            'contact_phone': 'Contact Phone',
            'image': 'Ministry Image',
            'is_active': 'Active Ministry',
            'is_featured': 'Featured Ministry',
            'is_public': 'Public Ministry',
        }

class NewsForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    
    class Meta:
        model = News
        fields = '__all__'
        help_texts = {
            'title': 'Headline for your news article (e.g., "New Youth Ministry Launched", "Easter Service Schedule")',
            'content': 'The full news article content. You can include details, quotes, and important information.',
            'excerpt': 'Brief summary of the article (optional). If left blank, the first 300 characters will be used.',
            'date': 'When did this news happen or when should it be published?',
            'image': 'Upload a photo related to this news (recommended size: 1200x800px)',
            'is_featured': 'Feature this news prominently on your church website',
            'is_public': 'Show this news to visitors on your website',
            'is_global_featured': 'Request to show this news on the global Bethel website',
            'global_feature_status': 'Current status of your global feature request',
        }
        labels = {
            'title': 'News Title',
            'content': 'News Content',
            'excerpt': 'News Excerpt',
            'date': 'News Date',
            'image': 'News Image',
            'is_featured': 'Featured News',
            'is_public': 'Public News',
            'is_global_featured': 'Request Global Feature',
            'global_feature_status': 'Global Feature Status',
        }

class SermonForm(forms.ModelForm):
    thumbnail = forms.ImageField(required=False)
    
    class Meta:
        model = Sermon
        fields = '__all__'
        help_texts = {
            'title': 'Title of the sermon (e.g., "Walking in Faith", "The Power of Prayer")',
            'preacher': 'Who preached this sermon? (e.g., "Rev. John Doe", "Pastor Mary Smith")',
            'description': 'Brief description of what the sermon was about',
            'date': 'When was this sermon preached?',
            'scripture_reference': 'Bible passage(s) referenced (e.g., "John 3:16", "Matthew 6:9-13")',
            'scripture_text': 'Full text of the scripture passage(s)',
            'audio_file': 'Upload the audio recording of the sermon (MP3 recommended)',
            'video_file': 'Upload the video recording of the sermon (MP4 recommended)',
            'thumbnail': 'Upload a thumbnail image for the sermon (recommended size: 800x600px)',
            'link': 'External link to the sermon (YouTube, Vimeo, etc.)',
            'duration': 'How long is the sermon? (e.g., "45:30", "1:15:20")',
            'language': 'What language is the sermon in?',
            'is_featured': 'Feature this sermon prominently on your church website',
            'is_public': 'Show this sermon to visitors on your website',
        }
        labels = {
            'title': 'Sermon Title',
            'preacher': 'Preacher',
            'description': 'Sermon Description',
            'date': 'Sermon Date',
            'scripture_reference': 'Scripture Reference',
            'scripture_text': 'Scripture Text',
            'audio_file': 'Audio File',
            'video_file': 'Video File',
            'thumbnail': 'Sermon Thumbnail',
            'link': 'External Link',
            'duration': 'Duration',
            'language': 'Language',
            'is_featured': 'Featured Sermon',
            'is_public': 'Public Sermon',
        }

class HeroMediaForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    
    class Meta:
        model = HeroMedia
        fields = ['image', 'video', 'order']

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')
        if not image and not video:
            raise forms.ValidationError('You must provide at least an image or a video for each Hero Media entry.')
        return cleaned_data

class EventHeroMediaForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    
    class Meta:
        model = EventHeroMedia
        fields = ('image', 'video', 'order')
        help_texts = {
            'image': 'Upload an image for this event (recommended size: 1200x800px). This will be used on event cards and in the hero carousel.',
            'video': 'Upload a video file (MP4 recommended). Videos will appear in the hero carousel and take priority over images.',
            'order': 'Display order (1 = first, 2 = second, etc.). Lower numbers appear first.'
        }
        labels = {
            'image': 'Event Image',
            'video': 'Event Video',
            'order': 'Display Order'
        }

class EventHighlightForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    
    class Meta:
        model = EventHighlight
        fields = '__all__'

class ConventionForm(forms.ModelForm):
    banner_image = forms.ImageField(required=False)
    
    class Meta:
        model = Convention
        fields = '__all__'

class HeroForm(forms.ModelForm):
    background_image = forms.ImageField(required=False)
    
    class Meta:
        model = Hero
        fields = '__all__'

class AboutPageForm(forms.ModelForm):
    logo = forms.ImageField(required=False)
    founder_image = forms.ImageField(required=False)
    extra_image = forms.ImageField(required=False)
    
    class Meta:
        model = AboutPage
        fields = '__all__'

class LeadershipPageForm(forms.ModelForm):
    chairman_image = forms.ImageField(required=False)
    vice_chairman_image = forms.ImageField(required=False)
    board_image = forms.ImageField(required=False)
    team_image = forms.ImageField(required=False)
    leadership_photo_1 = forms.ImageField(required=False)
    leadership_photo_2 = forms.ImageField(required=False)
    leadership_photo_3 = forms.ImageField(required=False)
    
    class Meta:
        model = LeadershipPage
        fields = '__all__'

class LocalLeadershipPageForm(forms.ModelForm):
    pastor_image = forms.ImageField(required=False)
    assistant_pastor_image = forms.ImageField(required=False)
    board_image = forms.ImageField(required=False)
    team_image = forms.ImageField(required=False)
    leadership_photo_1 = forms.ImageField(required=False)
    leadership_photo_2 = forms.ImageField(required=False)
    leadership_photo_3 = forms.ImageField(required=False)
    
    class Meta:
        model = LocalLeadershipPage
        fields = '__all__'

class LocalAboutPageForm(forms.ModelForm):
    logo = forms.ImageField(required=False)
    founder_image = forms.ImageField(required=False)
    extra_image = forms.ImageField(required=False)
    about_photo_1 = forms.ImageField(required=False)
    about_photo_2 = forms.ImageField(required=False)
    about_photo_3 = forms.ImageField(required=False)
    
    class Meta:
        model = LocalAboutPage
        fields = '__all__'

class GlobalSettingsForm(forms.ModelForm):
    global_nav_logo = forms.ImageField(required=False)
    
    class Meta:
        model = GlobalSettings
        fields = '__all__'

# --- CORRECT INLINE DEFINITIONS ---
class EventSpeakerForm(forms.ModelForm):
    photo = forms.ImageField(required=False)
    
    class Meta:
        model = EventSpeaker
        fields = ('name', 'photo', 'title', 'bio')
        help_texts = {
            'name': 'Enter the speaker\'s full name (e.g., "Rev. John Doe")',
            'photo': 'Upload a professional photo of the speaker (recommended size: 400x400px)',
            'title': 'Speaker\'s title or role (e.g., "Senior Pastor", "Guest Speaker", "Youth Minister")',
            'bio': 'Brief biography or description of the speaker (what they do, their background, etc.)'
        }
        labels = {
            'name': 'Speaker Name',
            'photo': 'Speaker Photo',
            'title': 'Speaker Title/Role',
            'bio': 'Speaker Biography'
        }

class EventSpeakerInline(admin.StackedInline):
    model = EventSpeaker
    form = EventSpeakerForm
    extra = 1
    fields = ('name', 'photo', 'title', 'bio')
    verbose_name = "Event Speaker"
    verbose_name_plural = "Event Speakers"
    help_text = "Add speakers for your event. Each speaker can have a name, photo, title/role, and biography."

class EventScheduleItemForm(forms.ModelForm):
    class Meta:
        model = EventScheduleItem
        fields = ('day', 'start_time', 'end_time', 'title', 'description', 'speaker', 'location')
        help_texts = {
            'day': 'Which day of the event? (e.g., "Sunday", "Monday", "Day 1", "Opening Day")',
            'start_time': 'What time does this session/activity start?',
            'end_time': 'What time does this session/activity end?',
            'title': 'Name of this session or activity (e.g., "Opening Prayer", "Main Session", "Break")',
            'description': 'Details about what will happen during this session',
            'speaker': 'Who will be speaking or leading this session? (select from event speakers)',
            'location': 'Where will this session take place? (e.g., "Main Hall", "Room 101", "Outdoor Area")'
        }
        labels = {
            'day': 'Day',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'title': 'Session Title',
            'description': 'Session Description',
            'speaker': 'Speaker/Leader',
            'location': 'Session Location'
        }

class EventScheduleItemInline(admin.StackedInline):
    model = EventScheduleItem
    form = EventScheduleItemForm
    extra = 1
    fields = ('day', 'start_time', 'end_time', 'title', 'description', 'speaker', 'location')
    verbose_name = "Schedule Item"
    verbose_name_plural = "Schedule Items"
    help_text = "Add schedule items for your event. Each item can have a day, time, title, description, speaker, and location."

class EventHighlightForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    
    class Meta:
        model = EventHighlight
        fields = '__all__'

class EventHighlightInline(admin.StackedInline):
    model = EventHighlight
    form = EventHighlightForm
    extra = 1
    fields = ('title', 'description', 'year', 'image', 'video_url', 'attendees_count', 'testimonial', 'testimonial_author', 'is_featured', 'is_public')
    help_texts = {
        'title': 'Required. Short title for the highlight.',
        'description': 'Required. Description of the highlight.',
        'year': 'Required. Year of the event.',
        'image': 'Optional. Upload an image for this highlight.',
        'video_url': 'Optional. If a video is provided, it will be shown as the main media for this highlight. Otherwise, the image will be used. Enter a YouTube or Vimeo URL.',
        'attendees_count': 'Optional. Number of attendees at this event.',
        'testimonial': 'Optional. A testimonial from this event.',
        'testimonial_author': 'Optional. Author of the testimonial.',
        'is_featured': 'Optional. Feature this highlight prominently.',
        'is_public': 'Optional. Show on public site.'
    }
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        
        # Override the save_new method to automatically set the church
        original_save_new = formset.save_new
        
        def save_new(form, *args, **kwargs):
            commit = kwargs.get('commit', True)
            instance = original_save_new(form, commit=False)
            if obj and hasattr(obj, 'church'):
                instance.church = obj.church
            if commit:
                instance.save()
            return instance
        
        formset.save_new = save_new
        
        formset.help_text = mark_safe(
            "<div style='margin:10px 0; color:#1e3a8a; font-weight:bold;'>"
            "If a video is provided, it will be shown as the main media for this highlight. Otherwise, the image will be used."
            "</div>"
        )
        return formset

class GlobalAdminMixin:
    """Mixin for global admin content that's not tied to any church"""
    
    def get_queryset(self, request):
        """Filter queryset based on user role"""
        qs = super().get_queryset(request)
        
        # Superusers and global admins can see everything
        if request.user.is_superuser:
            return qs
            
        # Check if user is a global admin
        try:
            church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
            if church_admin.role == 'global_admin':
                # Global admins can see all global content
                return qs
        except ChurchAdmin.DoesNotExist:
            pass
            
        # Local admins and regular users can't see global content
        return qs.none()

class LocalAdminMixin:
    """Mixin to restrict local admins to their own church's content"""
    
    def get_queryset(self, request):
        """Filter queryset based on user role"""
        qs = super().get_queryset(request)
        
        # Superusers and global admins can see everything
        if request.user.is_superuser:
            return qs
            
        # Check if user is a local admin
        try:
            church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
            if church_admin.role == 'local_admin' and church_admin.church:
                # Local admin can only see their church's content
                if hasattr(qs.model, 'church'):
                    return qs.filter(church=church_admin.church)
                elif qs.model == ChurchAdmin:
                    return qs.filter(user=request.user)
                else:
                    return qs.none()
        except ChurchAdmin.DoesNotExist:
            pass
            
        return qs
    
    def save_model(self, request, obj, form, change):
        """Auto-assign church for local admins"""
        if not request.user.is_superuser:
            try:
                church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
                if church_admin.role == 'local_admin' and church_admin.church:
                    if hasattr(obj, 'church'):
                        obj.church = church_admin.church
                    elif hasattr(obj, 'user') and obj.user is None:
                        obj.user = request.user
            except ChurchAdmin.DoesNotExist:
                pass
        
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form for local admins"""
        form = super().get_form(request, obj, **kwargs)
        
        if not request.user.is_superuser:
            try:
                church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
                if church_admin.role == 'local_admin' and church_admin.church:
                    # Hide church field for local admins since it's auto-assigned
                    if 'church' in form.base_fields:
                        form.base_fields['church'].widget = forms.HiddenInput()
                        form.base_fields['church'].initial = church_admin.church
            except ChurchAdmin.DoesNotExist:
                pass
        
        return form

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if not request.user.is_superuser and not self.is_global_admin(request.user):
            # Always remove 'global_feature_status' for local admins
            if 'global_feature_status' in fields:
                fields.remove('global_feature_status')
        return fields

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # DEBUG: Show user, role, and church info for local admins
        try:
            church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
            context['debug_local_admin'] = f"User: {request.user.username} | Role: {church_admin.role} | Local Admin Church: {church_admin.church} | Event Church: {getattr(obj, 'church', None)}"
        except ChurchAdmin.DoesNotExist:
            context['debug_local_admin'] = f"User: {request.user.username} | Not a local admin"
        # Existing logic for global feature status
        if obj and not request.user.is_superuser and not self.is_global_admin(request.user):
            status = getattr(obj, 'global_feature_status', None)
            show_send_approval = status is None or status == ''
            if status and status != '':
                context['global_feature_status_text'] = obj.get_global_feature_status_display()
            else:
                context['global_feature_status_text'] = ''
            context['show_send_approval'] = show_send_approval
        return super().render_change_form(request, context, add, change, form_url, obj)

    def is_global_admin(self, user):
        try:
            ca = ChurchAdmin.objects.get(user=user, is_active=True)
            return ca.role == 'global_admin'
        except ChurchAdmin.DoesNotExist:
            return False

class ChurchAdminInline(admin.TabularInline):
    model = ChurchAdmin
    extra = 1
    fields = ('user', 'role', 'is_active')
    autocomplete_fields = ['user']
    show_change_link = True

class HeroInline(admin.StackedInline):
    model = Hero
    extra = 1
    fields = ('title', 'subtitle', 'background_type', 'primary_button_text', 'primary_button_link', 'secondary_button_text', 'secondary_button_link', 'is_active', 'order')
    verbose_name = "Church Hero"
    verbose_name_plural = "Church Heroes"
    help_text = "Configure the hero section for this church's homepage. After saving, you can add multiple hero images/videos by editing the hero in the separate 'Local Heroes' admin section."

class ChurchModelAdmin(EnhancedImagePreviewMixin, admin.ModelAdmin):
    form = ChurchForm
    list_display = ['name', 'city', 'country', 'pastor_name', 'service_times_display', 'is_active', 'is_approved', 'is_featured', 'created_at']
    list_filter = ['is_active', 'is_approved', 'is_featured', 'country', 'created_at']
    search_fields = ['name', 'city', 'country', 'pastor_name', 'email']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at', 'logo_preview', 'nav_logo_preview']
    actions = ['setup_default_functionality', 'add_hero_media_to_churches']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configure enhanced image preview fields
        image_config = [
            {
                'field_name': 'logo',
                'max_width': 400,
                'max_height': 400,
                'title': 'Church Logo Preview'
            },
            {
                'field_name': 'nav_logo',
                'max_width': 300,
                'max_height': 300,
                'is_circular': True,
                'title': 'Navigation Logo Preview'
            },
            {
                'field_name': 'banner_image',
                'max_width': 600,
                'max_height': 300,
                'title': 'Banner Image Preview'
            }
        ]
        
        # Add the enhanced preview fields
        self.add_image_preview_fields(self, image_config)
    
    fieldsets = (
        ('Church Information', {
            'fields': ('name', 'slug', 'description', 'pastor_name', 'email', 'phone', 'logo', 'logo_preview')
        }),
        ('Navigation Logo', {
            'fields': ('nav_logo', 'nav_logo_preview'),
            'description': 'Upload a specific logo for the navigation bar (small, circular format recommended)'
        }),
        ('Service Times', {
            'fields': ('service_times', 'sunday_service_1', 'sunday_service_2', 'wednesday_service', 'friday_service', 'other_services'),
            'description': 'Configure your church service schedule. You can use the text field for custom formats or the time fields for structured data.'
        }),
        ('Location', {
            'fields': ('address', 'city', 'state_province', 'country', 'postal_code', 'latitude', 'longitude')
        }),
        ('Online Presence', {
            'fields': ('website', 'shop_url'),
            'description': 'Configure your church\'s online presence including website and online store.'
        }),
        ('Status', {
            'fields': ('is_active', 'is_approved', 'is_featured')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [ChurchAdminInline, HeroInline]
    
    def setup_default_functionality(self, request, queryset):
        """Setup default functionality for selected churches"""
        for church in queryset:
            church.setup_default_functionality()
            
            # Create a default hero with sample Hero Media if none exists
            if not Hero.objects.filter(church=church).exists():
                hero = Hero.objects.create(
                    church=church,
                    title=f'Welcome to {church.name}',
                    subtitle=f'Join us in worship and fellowship in {church.city}, {church.country}',
                    background_type='image',
                    primary_button_text='Plan Your Visit',
                    primary_button_link=f'/church/{church.id}/about/',
                    secondary_button_text='Watch Online',
                    secondary_button_link=f'/church/{church.id}/sermons/',
                    is_active=True,
                    order=1
                )
                
                # Add a note about Hero Media
                self.message_user(
                    request, 
                    f"Created default hero for {church.name}. "
                    f"To add multiple hero images/videos, edit the hero in the Hero admin section."
                )
        
        self.message_user(request, f"Default functionality setup for {queryset.count()} church(es).")
    setup_default_functionality.short_description = "Setup default functionality (including hero)"
    
    def add_hero_media_to_churches(self, request, queryset):
        """Add Hero Media functionality to selected churches"""
        from core.models import Hero, HeroMedia
        
        updated_count = 0
        
        for church in queryset:
            # Check if church already has hero content
            existing_hero = Hero.objects.filter(church=church).first()
            
            if existing_hero:
                # Update existing hero
                hero = existing_hero
                hero.title = f'Welcome to {church.name}'
                hero.subtitle = f'Join us in worship and fellowship in {church.city}, {church.country}'
                hero.primary_button_link = f'/church/{church.id}/about/'
                hero.secondary_button_link = f'/church/{church.id}/sermons/'
                hero.save()
                
                # Add Hero Media placeholder if none exists
                if not hero.hero_media.exists():
                    HeroMedia.objects.create(
                        hero=hero,
                        image=None,
                        video=None,
                        order=1
                    )
                
                updated_count += 1
            else:
                # Create new hero
                hero = Hero.objects.create(
                    church=church,
                    title=f'Welcome to {church.name}',
                    subtitle=f'Join us in worship and fellowship in {church.city}, {church.country}',
                    background_type='image',
                    primary_button_text='Plan Your Visit',
                    primary_button_link=f'/church/{church.id}/about/',
                    secondary_button_text='Watch Online',
                    secondary_button_link=f'/church/{church.id}/sermons/',
                    is_active=True,
                    order=1
                )
                
                # Create Hero Media placeholder
                HeroMedia.objects.create(
                    hero=hero,
                    image=None,
                    video=None,
                    order=1
                )
                
                updated_count += 1
        
        self.message_user(
            request, 
            f"Successfully added Hero Media functionality to {updated_count} church(es). "
            f"Go to /admin/core/localhero/ to add images/videos."
        )
    add_hero_media_to_churches.short_description = "Add Hero Media functionality"
    
    def get_urls(self):
        """Add custom URLs for setup functionality"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<uuid:church_id>/setup-defaults/',
                self.admin_site.admin_view(self.setup_defaults_view),
                name='church_setup_defaults',
            ),
        ]
        return custom_urls + urls
    
    def setup_defaults_view(self, request, church_id):
        """Handle setup defaults for a specific church"""
        from django.shortcuts import get_object_or_404, redirect
        from django.contrib import messages
        
        church = get_object_or_404(Church, id=church_id)
        church.setup_default_functionality()
        messages.success(request, f"Default functionality setup for {church.name}.")
        return redirect('admin:core_church_change', church_id)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Add setup button to change view"""
        extra_context = extra_context or {}
        extra_context['show_setup_button'] = True
        return super().change_view(request, object_id, form_url, extra_context)
    
    def save_formset(self, request, form, formset, change):
        """Handle formset saving, especially for ChurchAdmin inline"""
        instances = formset.save(commit=False)
        
        # Set the church for new ChurchAdmin instances
        for instance in instances:
            if isinstance(instance, ChurchAdmin) and not instance.church_id:
                instance.church = form.instance
        
        # Save all instances
        for instance in instances:
            instance.save()
        
        # Handle deleted instances
        for obj in formset.deleted_objects:
            obj.delete()
    
    # Preview methods are now handled by EnhancedImagePreviewMixin
    
    def service_times_display(self, obj):
        """Display service times in a readable format"""
        if obj.service_times:
            return obj.service_times
        elif obj.sunday_service_1:
            times = []
            if obj.sunday_service_1:
                times.append(f"Sun {obj.sunday_service_1.strftime('%I:%M %p')}")
            if obj.sunday_service_2:
                times.append(f"Sun {obj.sunday_service_2.strftime('%I:%M %p')}")
            if obj.wednesday_service:
                times.append(f"Wed {obj.wednesday_service.strftime('%I:%M %p')}")
            if obj.friday_service:
                times.append(f"Fri {obj.friday_service.strftime('%I:%M %p')}")
            return " | ".join(times) if times else "No times set"
        return "No times set"
    service_times_display.short_description = "Service Times"

class ChurchAdminModelAdmin(LocalAdminMixin, admin.ModelAdmin):
    list_display = ['user', 'church', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['user__username', 'church__name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Admin Information', {
            'fields': ('user', 'church', 'role')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('System', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

class EventHeroMediaForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    
    class Meta:
        model = EventHeroMedia
        fields = ('image', 'video', 'order')
        help_texts = {
            'image': 'Upload an image for this event (recommended size: 1200x800px). This will be used on event cards and in the hero carousel.',
            'video': 'Upload a video file (MP4 recommended). Videos will appear in the hero carousel and take priority over images.',
            'order': 'Display order (1 = first, 2 = second, etc.). Lower numbers appear first.'
        }
        labels = {
            'image': 'Event Image',
            'video': 'Event Video',
            'order': 'Display Order'
        }

class EventHeroMediaInline(admin.StackedInline):
    model = EventHeroMedia
    form = EventHeroMediaForm
    extra = 1
    fields = ('image', 'video', 'order')
    verbose_name = "Event Media"
    verbose_name_plural = "Event Media"
    help_text = "Add images and videos for your event. Images will be used on event cards and in the hero carousel. Videos will appear in the hero carousel."

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.help_text = self.help_text
        return formset

# Remove @admin.register decorators for these models
# @admin.register(Event)

class EventAdmin(LocalAdminMixin, admin.ModelAdmin):
    form = EventForm
    list_display = ['title', 'church', 'start_date', 'end_date', 'is_big_event', 'is_featured', 'is_global_featured', 'global_feature_status', 'created_at']
    list_filter = ['is_big_event', 'is_featured', 'start_date', 'created_at']
    search_fields = ['title', 'description', 'church__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('church', 'title', 'description'),
            'description': 'Basic information about your event including the title and description that visitors will see.'
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'event_type'),
            'description': 'When your event takes place and what type of event it is.'
        }),
        ('Location', {
            'fields': ('location', 'address'),
            'description': 'Where people can find your event. Include both the venue name and full address.'
        }),
        ('Media', {
            'fields': (),  # No direct fields, managed via EventHeroMediaInline
            'description': 'Add images and videos for your event using the "Event Media" section below.'
        }),
        ('Registration Settings', {
            'fields': ('requires_registration', 'max_attendees', 'registration_deadline', 'registration_fee'),
            'description': 'Configure if people need to register for your event and any associated costs.'
        }),
        ('Event Display', {
            'fields': ('is_featured', 'is_public', 'show_qr_code'),
            'description': 'Control how your event appears on the website and whether to show a QR code for easy sharing.'
        }),
        ('Big Event Template', {
            'fields': ('is_big_event',),
            'description': 'Enable the professional big event template with registration forms, countdown timer, and detailed sections.'
        }),
        ('Global Feature Request', {
            'fields': ('is_global_featured', 'global_feature_status'),
            'description': 'Request to feature this event on the global Bethel website. Only global admins can approve requests.'
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Technical information about this event record.'
        }),
    )

    inlines = [
        EventSpeakerInline,
        EventScheduleItemInline,
        EventHighlightInline,
        EventHeroMediaInline,
    ]

    def save_formset(self, request, form, formset, change):
        """Handle formset saving with proper church filtering"""
        print(f"DEBUG: save_formset called for {formset.model.__name__}")
        print(f"DEBUG: formset.forms: {len(formset.forms)}")
        print(f"DEBUG: formset.is_valid(): {formset.is_valid()}")
        
        if not formset.is_valid():
            print(f"DEBUG: Formset errors: {formset.errors}")
            print(f"DEBUG: Non-form errors: {formset.non_form_errors()}")
        
        # Let Django handle the normal formset saving
        super().save_formset(request, form, formset, change)

    def is_global_admin(self, user):
        try:
            ca = ChurchAdmin.objects.get(user=user, is_active=True)
            return ca.role == 'global_admin'
        except ChurchAdmin.DoesNotExist:
            return False

# @admin.register(Ministry)
class MinistryJoinRequestInline(admin.TabularInline):
    model = MinistryJoinRequest
    extra = 0
    fields = ('name', 'email', 'phone', 'message', 'created_at', 'is_reviewed')
    readonly_fields = ('name', 'email', 'phone', 'message', 'created_at')
    can_delete = False
    show_change_link = True
    verbose_name = 'Join Request'
    verbose_name_plural = 'Join Requests'

class MinistryForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    
    class Meta:
        model = Ministry
        fields = '__all__'
        help_texts = {
            'name': 'Name of your ministry (e.g., "Youth Ministry", "Women\'s Fellowship", "Prayer Team")',
            'description': 'Describe what this ministry does, who it serves, and how people can get involved',
            'ministry_type': 'What type of ministry is this? Choose the most appropriate category',
            'leader_name': 'Who leads this ministry? (e.g., "John Doe", "Sister Mary")',
            'contact_email': 'Email address for ministry inquiries',
            'contact_phone': 'Phone number for ministry inquiries',
            'image': 'Upload a photo representing this ministry (recommended size: 800x600px)',
            'is_active': 'Is this ministry currently active and accepting new members?',
            'is_featured': 'Feature this ministry prominently on your church website',
            'is_public': 'Show this ministry on the global Bethel website',
        }
        labels = {
            'name': 'Ministry Name',
            'description': 'Ministry Description',
            'ministry_type': 'Ministry Type',
            'leader_name': 'Leader Name',
            'contact_email': 'Contact Email',
            'contact_phone': 'Contact Phone',
            'image': 'Ministry Image',
            'is_active': 'Active Ministry',
            'is_featured': 'Featured Ministry',
            'is_public': 'Public Ministry',
        }

class MinistryAdmin(EnhancedImagePreviewMixin, LocalAdminMixin, admin.ModelAdmin):
    form = MinistryForm
    list_display = ['name', 'church', 'leader_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description', 'church__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [MinistryJoinRequestInline]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configure enhanced image preview fields
        image_config = [
            {
                'field_name': 'image',
                'max_width': 500,
                'max_height': 400,
                'title': 'Ministry Image Preview'
            }
        ]
        
        # Add the enhanced preview fields
        self.add_image_preview_fields(self, image_config)

    fieldsets = (
        ('Ministry Information', {
            'fields': ('church', 'name', 'description', 'ministry_type', 'leader_name', 'contact_email', 'contact_phone', 'image')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'is_public')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_global_admin(self, user):
        try:
            ca = ChurchAdmin.objects.get(user=user, is_active=True)
            return ca.role == 'global_admin'
        except ChurchAdmin.DoesNotExist:
            return False

# @admin.register(News)
class NewsForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    
    class Meta:
        model = News
        fields = '__all__'
        help_texts = {
            'title': 'Headline for your news article (e.g., "New Youth Ministry Launched", "Easter Service Schedule")',
            'content': 'The full news article content. You can include details, quotes, and important information.',
            'excerpt': 'Brief summary of the article (optional). If left blank, the first 300 characters will be used.',
            'date': 'When did this news happen or when should it be published?',
            'image': 'Upload a photo related to this news (recommended size: 1200x800px)',
            'is_featured': 'Feature this news prominently on your church website',
            'is_public': 'Show this news to visitors on your website',
            'is_global_featured': 'Request to show this news on the global Bethel website',
            'global_feature_status': 'Current status of your global feature request',
        }
        labels = {
            'title': 'News Title',
            'content': 'News Content',
            'excerpt': 'News Excerpt',
            'date': 'News Date',
            'image': 'News Image',
            'is_featured': 'Featured News',
            'is_public': 'Public News',
            'is_global_featured': 'Request Global Feature',
            'global_feature_status': 'Global Feature Status',
        }

class NewsAdmin(EnhancedImagePreviewMixin, LocalAdminMixin, admin.ModelAdmin):
    form = NewsForm
    list_display = ['title', 'church', 'date', 'is_featured', 'is_global_featured', 'global_feature_status', 'created_at']
    list_filter = ['is_featured', 'date', 'created_at']
    search_fields = ['title', 'content', 'church__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configure enhanced image preview fields
        image_config = [
            {
                'field_name': 'image',
                'max_width': 600,
                'max_height': 400,
                'title': 'News Image Preview'
            }
        ]
        
        # Add the enhanced preview fields
        self.add_image_preview_fields(self, image_config)
    
    fieldsets = (
        ('News Information', {
            'fields': ('title', 'content', 'excerpt', 'date', 'church')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Status', {
            'fields': ('is_featured', 'is_public')
        }),
        ('Global Feature Request', {
            'fields': ('is_global_featured', 'global_feature_status'),
            'description': 'Request to feature this news on the global site. Only global admins can approve requests.'
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_global_admin(self, user):
        try:
            ca = ChurchAdmin.objects.get(user=user, is_active=True)
            return ca.role == 'global_admin'
        except ChurchAdmin.DoesNotExist:
            return False

# @admin.register(Sermon)
class SermonForm(forms.ModelForm):
    thumbnail = forms.ImageField(required=False)
    
    class Meta:
        model = Sermon
        fields = '__all__'
        help_texts = {
            'title': 'Title of the sermon (e.g., "Walking in Faith", "The Power of Prayer")',
            'preacher': 'Who preached this sermon? (e.g., "Rev. John Doe", "Pastor Mary Smith")',
            'description': 'Brief description of what the sermon was about',
            'date': 'When was this sermon preached?',
            'scripture_reference': 'Bible passage(s) referenced (e.g., "John 3:16", "Matthew 6:9-13")',
            'scripture_text': 'Full text of the scripture passage(s)',
            'audio_file': 'Upload the audio recording of the sermon (MP3 recommended)',
            'video_file': 'Upload the video recording of the sermon (MP4 recommended)',
            'thumbnail': 'Upload a thumbnail image for the sermon (recommended size: 800x600px)',
            'link': 'External link to the sermon (YouTube, Vimeo, etc.)',
            'duration': 'How long is the sermon? (e.g., "45:30", "1:15:20")',
            'language': 'What language is the sermon in?',
            'is_featured': 'Feature this sermon prominently on your church website',
            'is_public': 'Show this sermon to visitors on your website',
        }
        labels = {
            'title': 'Sermon Title',
            'preacher': 'Preacher',
            'description': 'Sermon Description',
            'date': 'Sermon Date',
            'scripture_reference': 'Scripture Reference',
            'scripture_text': 'Scripture Text',
            'audio_file': 'Audio File',
            'video_file': 'Video File',
            'thumbnail': 'Sermon Thumbnail',
            'link': 'External Link',
            'duration': 'Duration',
            'language': 'Language',
            'is_featured': 'Featured Sermon',
            'is_public': 'Public Sermon',
        }

class SermonAdmin(EnhancedImagePreviewMixin, LocalAdminMixin, admin.ModelAdmin):
    form = SermonForm
    list_display = ['title', 'church', 'preacher', 'date', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['title', 'description', 'preacher', 'church__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configure enhanced image preview fields
        image_config = [
            {
                'field_name': 'thumbnail',
                'max_width': 500,
                'max_height': 400,
                'title': 'Sermon Thumbnail Preview'
            }
        ]
        
        # Add the enhanced preview fields
        self.add_image_preview_fields(self, image_config)
    
    fieldsets = (
        ('Sermon Information', {
            'fields': ('title', 'preacher', 'description', 'date', 'church')
        }),
        ('Scripture', {
            'fields': ('scripture_reference', 'scripture_text')
        }),
        ('Media', {
            'fields': ('audio_file', 'video_file', 'thumbnail', 'link')
        }),
        ('Details', {
            'fields': ('duration', 'language')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_public')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_global_admin(self, user):
        try:
            ca = ChurchAdmin.objects.get(user=user, is_active=True)
            return ca.role == 'global_admin'
        except ChurchAdmin.DoesNotExist:
            return False

# @admin.register(DonationMethod)
class DonationMethodAdmin(LocalAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'church', 'payment_type', 'is_external_link_display', 'is_active', 'created_at']
    list_filter = ['payment_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'church__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Donation Method Information', {
            'fields': ('name', 'payment_type', 'description', 'church')
        }),
        ('Payment Details', {
            'fields': ('external_link', 'account_info')
        }),
        ('Status', {
            'fields': ('is_active', 'is_default')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_external_link_display(self, obj):
        return "Yes" if obj.is_external_link() else "No"
    is_external_link_display.short_description = "External Link"

    def is_global_admin(self, user):
        try:
            ca = ChurchAdmin.objects.get(user=user, is_active=True)
            return ca.role == 'global_admin'
        except ChurchAdmin.DoesNotExist:
            return False

# Admin site customization
admin.site.site_header = "Bethel Prayer Ministry International"
admin.site.site_title = "Bethel Admin"
admin.site.index_title = "Welcome to Bethel Platform Administration"
admin.site.site_url = "/"  # Link to main site

# Import global admin registrations
from . import global_admin_config

# @admin.register(ChurchApplication)
class ChurchApplicationAdmin(admin.ModelAdmin):
    list_display = ['church_name', 'pastor_name', 'city', 'country', 'status', 'created_at']
    list_filter = ['status', 'country', 'created_at']
    search_fields = ['church_name', 'pastor_name', 'city', 'country', 'contact_email']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_applications', 'reject_applications']

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        # Only superusers or global admins can change status
        if not (request.user.is_superuser or self.is_global_admin(request.user)):
            fields.append('status')
            fields.append('admin_notes')
            fields.append('reviewed_by')
            fields.append('reviewed_at')
        return fields

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Only superusers or global admins can approve/reject
        if not (request.user.is_superuser or self.is_global_admin(request.user)):
            if 'approve_applications' in actions:
                del actions['approve_applications']
            if 'reject_applications' in actions:
                del actions['reject_applications']
        return actions

    def is_global_admin(self, user):
        from .models import ChurchAdmin
        try:
            ca = ChurchAdmin.objects.get(user=user, is_active=True)
            return ca.role == 'global_admin'
        except ChurchAdmin.DoesNotExist:
            return False

    def approve_applications(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} application(s) approved.")
    approve_applications.short_description = "Approve selected applications"

    def reject_applications(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} application(s) rejected.")
    reject_applications.short_description = "Reject selected applications"

class GlobalFeatureRequestAdmin(GlobalAdminMixin, admin.ModelAdmin):
    """Admin for global feature requests from local admins"""
    list_display = ['title', 'church', 'content_type', 'status', 'requested_by', 'created_at']
    list_filter = ['status', 'content_type', 'created_at']
    search_fields = ['title', 'church__name', 'requested_by__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('title', 'description', 'content_type', 'content_id', 'church', 'requested_by')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Review', {
            'fields': ('reviewed_by', 'reviewed_at', 'approval_date', 'admin_notes'),
            'description': 'Set approval date/time for when content should be featured on global site'
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Handle approval workflow"""
        if change and 'status' in form.changed_data:
            # Update the actual content object
            content_obj = obj.get_content_object()
            if content_obj:
                if obj.status == 'approved':
                    content_obj.global_feature_status = 'approved'
                    content_obj.is_global_featured = True
                    if obj.approval_date:
                        content_obj.global_feature_date = obj.approval_date
                elif obj.status == 'rejected':
                    content_obj.global_feature_status = 'rejected'
                    content_obj.is_global_featured = False
                content_obj.save()
            
            # Set review info
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        """Only global admins can add requests"""
        return request.user.is_superuser or self.is_global_admin(request.user)
    
    def is_global_admin(self, user):
        try:
            ca = ChurchAdmin.objects.get(user=user, is_active=True)
            return ca.role == 'global_admin'
        except ChurchAdmin.DoesNotExist:
            return False

class HeroMediaInline(admin.TabularInline):
    model = HeroMedia
    form = HeroMediaForm
    extra = 1
    fields = ('image', 'video', 'order')
    verbose_name_plural = "Hero Media"
    help_text = "Images and videos added here will be used for the homepage hero carousel."
    fk_name = 'hero'  # Explicitly set the FK for proxy model

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            formset.parent_object = obj
        # Patch save_new and save_existing for debug
        orig_save_new = formset.save_new
        orig_save_existing = formset.save_existing
        import sys
        def debug_save_new(*args, **kwargs):
            form = args[0]
            print(f"[DEBUG] HeroMediaInline.save_new: cleaned_data={form.cleaned_data}", file=sys.stderr)
            return orig_save_new(*args, **kwargs)
        def debug_save_existing(*args, **kwargs):
            form = args[0]
            print(f"[DEBUG] HeroMediaInline.save_existing: cleaned_data={form.cleaned_data}", file=sys.stderr)
            return orig_save_existing(*args, **kwargs)
        formset.save_new = debug_save_new
        formset.save_existing = debug_save_existing
        return formset

class LocalHeroAdmin(LocalAdminMixin, admin.ModelAdmin):
    """Local hero banners for individual churches"""
    list_display = ['title', 'church', 'is_active', 'is_global_featured', 'global_feature_status', 'order', 'created_at']
    list_filter = ['background_type', 'is_active', 'created_at']
    search_fields = ['title', 'subtitle']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [HeroMediaInline]

    def get_inline_instances(self, request, obj=None):
        """Get inline instances for the admin"""
        inline_instances = []
        for inline_class in self.inlines:
            inline = inline_class(self.model, self.admin_site)
            # Ensure the inline is properly configured for the proxy model
            if hasattr(inline, 'fk_name') and inline.fk_name == 'hero':
                inline.parent_object = obj
            inline_instances.append(inline)
        return inline_instances

    fieldsets = (
        ('Hero Information', {
            'fields': ('title', 'subtitle', 'church')
        }),
        ('Background', {
            'fields': ('background_type',)
        }),
        ('Buttons', {
            'fields': ('primary_button_text', 'primary_button_link', 'secondary_button_text', 'secondary_button_link')
        }),
        ('Status', {
            'fields': ('is_active', 'order')
        }),
        ('Global Feature Request', {
            'fields': ('is_global_featured', 'global_feature_status'),
            'description': 'Request to feature this hero on the global site. Only global admins can approve requests.'
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Local admins can only see their church's heroes"""
        qs = super().get_queryset(request)
        
        # Superusers can see all local heroes
        if request.user.is_superuser:
            return qs.filter(church__isnull=False)
            
        # Global admins can see all local heroes
        if self.is_global_admin(request.user):
            return qs.filter(church__isnull=False)
        
        # Local admins can only see their church's heroes
        try:
            church_admin = ChurchAdmin.objects.get(user=request.user)
            return qs.filter(church=church_admin.church)
        except ChurchAdmin.DoesNotExist:
            return qs.none()
    
    def has_add_permission(self, request):
        """Local admins can add heroes for their church"""
        if request.user.is_superuser or self.is_global_admin(request.user):
            return True
        return ChurchAdmin.objects.filter(user=request.user).exists()
    
    def has_change_permission(self, request, obj=None):
        """Local admins can edit their church's heroes"""
        if request.user.is_superuser or self.is_global_admin(request.user):
            return True
        if obj:
            try:
                church_admin = ChurchAdmin.objects.get(user=request.user)
                return obj.church == church_admin.church
            except ChurchAdmin.DoesNotExist:
                return False
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Local admins can delete their church's heroes"""
        if request.user.is_superuser or self.is_global_admin(request.user):
            return True
        if obj:
            try:
                church_admin = ChurchAdmin.objects.get(user=request.user)
                return obj.church == church_admin.church
            except ChurchAdmin.DoesNotExist:
                return False
        return True
    
    def save_model(self, request, obj, form, change):
        """Handle global feature requests"""
        if not request.user.is_superuser and not self.is_global_admin(request.user):
            # Local admins can request global features but can't approve them
            if 'is_global_featured' in form.changed_data and obj.is_global_featured:
                obj.global_feature_status = 'pending'
        
        super().save_model(request, obj, form, change)
    
    def get_urls(self):
        """Add custom URLs for approval actions"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<uuid:hero_id>/send-approval/',
                self.admin_site.admin_view(self.send_approval_view),
                name='localhero_send_approval',
            ),
        ]
        return custom_urls + urls
    
    def send_approval_view(self, request, hero_id):
        """Handle sending hero for global approval"""
        from django.http import JsonResponse
        from django.shortcuts import get_object_or_404
        
        try:
            hero = get_object_or_404(LocalHero, id=hero_id)
            
            # Check permissions
            if not request.user.is_superuser and not self.is_global_admin(request.user):
                try:
                    church_admin = ChurchAdmin.objects.get(user=request.user)
                    if hero.church != church_admin.church:
                        return JsonResponse({'success': False, 'message': 'Permission denied'})
                except ChurchAdmin.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Permission denied'})
            
            # Create or update GlobalFeatureRequest
            feature_request, created = GlobalFeatureRequest.objects.get_or_create(
                content_type='hero',
                content_id=hero.id,
                defaults={
                    'church': hero.church,
                    'requested_by': request.user,
                    'title': f"Hero: {hero.title}",
                    'description': f"Request to feature hero '{hero.title}' from {hero.church.name} on the global site.",
                    'status': 'pending'
                }
            )
            
            if not created:
                feature_request.status = 'pending'
                feature_request.save()
            
            # Update hero status
            hero.is_global_featured = True
            hero.global_feature_status = 'pending'
            hero.save()
            
            # Send email notification to global admins
            try:
                notify_global_admins_of_request(feature_request)
            except Exception as e:
                # Log error but don't fail the request
                print(f"Email notification failed: {e}")
            
            return JsonResponse({
                'success': True, 
                'message': 'Request sent successfully! Global admins will be notified.',
                'request_id': str(feature_request.id)
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    def is_global_admin(self, user):
        try:
            ca = ChurchAdmin.objects.get(user=user, is_active=True)
            return ca.role == 'global_admin'
        except ChurchAdmin.DoesNotExist:
            return False
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser and not self.is_global_admin(request.user):
            readonly.append('global_feature_status')
        return readonly
    
    class Media:
        css = {
            'all': ('css/admin-custom.css',)
        }
        js = ('js/localhero_admin.js',)

# Register only the new admin classes that are not registered elsewhere
admin.site.register(Event, EventAdmin)
admin.site.register(Ministry, MinistryAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(Sermon, SermonAdmin)
admin.site.register(DonationMethod, DonationMethodAdmin)
admin.site.register(ChurchApplication, ChurchApplicationAdmin)
# Note: Hero, Convention, ConventionRegistration, and NewsletterSignup are registered in global_admin_config.py

class TestimonyModelAdmin(LocalAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'get_display_name', 'category', 'church', 'is_approved', 'is_featured', 'created_at']
    list_filter = ['is_approved', 'is_featured', 'category', 'church', 'created_at']
    search_fields = ['title', 'content', 'author_name', 'author_email']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_testimonies', 'reject_testimonies', 'feature_testimonies']
    
    fieldsets = (
        ('Testimony Details', {
            'fields': ('title', 'content', 'category')
        }),
        ('Author Information', {
            'fields': ('author_name', 'author_email', 'location', 'is_anonymous')
        }),
        ('Church Association', {
            'fields': ('church',),
            'description': 'Leave blank for global testimonies'
        }),
        ('Status', {
            'fields': ('is_approved', 'is_featured')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def approve_testimonies(self, request, queryset):
        """Approve selected testimonies"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} testimonies have been approved.")
    approve_testimonies.short_description = "Approve selected testimonies"
    
    def reject_testimonies(self, request, queryset):
        """Reject selected testimonies"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} testimonies have been rejected.")
    reject_testimonies.short_description = "Reject selected testimonies"
    
    def feature_testimonies(self, request, queryset):
        """Feature selected testimonies"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} testimonies have been featured.")
    feature_testimonies.short_description = "Feature selected testimonies"
    
    def get_queryset(self, request):
        """Filter queryset based on user role"""
        qs = super().get_queryset(request)
        
        # Superusers can see everything
        if request.user.is_superuser:
            return qs
            
        # Check if user is a local admin
        try:
            church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
            if church_admin.role == 'local_admin' and church_admin.church:
                # Local admin can only see their church's testimonies or global ones
                return qs.filter(models.Q(church=church_admin.church) | models.Q(church__isnull=True))
        except ChurchAdmin.DoesNotExist:
            pass
            
        return qs.none()

# Register Testimony model
admin.site.register(Testimony, TestimonyModelAdmin)

class AboutPageAdmin(admin.ModelAdmin):
    form = AboutPageForm
    list_display = ("title", "updated_at")
    search_fields = ("title",)
    fieldsets = (
        ('About Page Content', {
            'fields': ('title', 'intro', 'founding_story', 'timeline', 'leadership_timeline', 'ministry_today', 'quick_facts')
        }),
        ('Images', {
            'fields': ('logo', 'founder_image', 'extra_image')
        }),
    )

class LeadershipPageAdmin(admin.ModelAdmin):
    form = LeadershipPageForm
    list_display = ("title", "updated_at")
    search_fields = ("title",)
    fieldsets = (
        ('Leadership Page Content', {
            'fields': ('title', 'intro', 'current_leadership', 'board_members', 'leadership_team', 'vision_statement', 'mission_statement')
        }),
        ('Images', {
            'fields': ('chairman_image', 'vice_chairman_image', 'board_image', 'team_image', 'leadership_photo_1', 'leadership_photo_2', 'leadership_photo_3')
        }),
    )

class LocalLeadershipPageAdmin(LocalAdminMixin, admin.ModelAdmin):
    form = LocalLeadershipPageForm
    list_display = ("church", "title", "updated_at")
    list_filter = ("church", "updated_at")
    search_fields = ("church__name", "title")
    readonly_fields = ("pastor_image_preview", "assistant_pastor_image_preview", "board_image_preview", "team_image_preview", "leadership_photo_1_preview", "leadership_photo_2_preview", "leadership_photo_3_preview")
    fieldsets = (
        ('Leadership Page Content', {
            'fields': ('church', 'title', 'intro', 'current_leadership', 'board_members', 'leadership_team', 'vision_statement', 'mission_statement')
        }),
        ('Images', {
            'fields': ('pastor_image', 'pastor_image_preview', 'assistant_pastor_image', 'assistant_pastor_image_preview', 'board_image', 'board_image_preview', 'team_image', 'team_image_preview', 'leadership_photo_1', 'leadership_photo_1_preview', 'leadership_photo_2', 'leadership_photo_2_preview', 'leadership_photo_3', 'leadership_photo_3_preview')
        }),
    )

    def pastor_image_preview(self, obj):
        if obj.pastor_image:
            return format_html(
                '<div style="text-align: center; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">'
                '<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 50%; box-shadow: 0 2px 8px rgba(0,0,0,0.1); object-fit: cover; cursor: pointer;" '
                'onclick="window.open(this.src, \'_blank\')" title="Click to view full size" />'
                '<br><small style="color: #666;">Pastor Photo</small>'
                '</div>', obj.pastor_image.url)
        return ""
    pastor_image_preview.short_description = "Pastor Image Preview"

    def assistant_pastor_image_preview(self, obj):
        if obj.assistant_pastor_image:
            return format_html(
                '<div style="text-align: center; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">'
                '<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 50%; box-shadow: 0 2px 8px rgba(0,0,0,0.1); object-fit: cover; cursor: pointer;" '
                'onclick="window.open(this.src, \'_blank\')" title="Click to view full size" />'
                '<br><small style="color: #666;">Assistant Pastor Photo</small>'
                '</div>', obj.assistant_pastor_image.url)
        return ""
    assistant_pastor_image_preview.short_description = "Assistant Pastor Image Preview"

    def board_image_preview(self, obj):
        if obj.board_image:
            return format_html(
                '<div style="text-align: center; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">'
                '<img src="{}" style="max-width: 200px; max-height: 150px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); object-fit: cover; cursor: pointer;" '
                'onclick="window.open(this.src, \'_blank\')" title="Click to view full size" />'
                '<br><small style="color: #666;">Board Photo</small>'
                '</div>', obj.board_image.url)
        return ""
    board_image_preview.short_description = "Board Image Preview"

    def team_image_preview(self, obj):
        if obj.team_image:
            return format_html(
                '<div style="text-align: center; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">'
                '<img src="{}" style="max-width: 200px; max-height: 150px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); object-fit: cover; cursor: pointer;" '
                'onclick="window.open(this.src, \'_blank\')" title="Click to view full size" />'
                '<br><small style="color: #666;">Team Photo</small>'
                '</div>', obj.team_image.url)
        return ""
    team_image_preview.short_description = "Team Image Preview"

    def leadership_photo_1_preview(self, obj):
        if obj.leadership_photo_1:
            return format_html(
                '<div style="text-align: center; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">'
                '<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); object-fit: cover; cursor: pointer;" '
                'onclick="window.open(this.src, \'_blank\')" title="Click to view full size" />'
                '<br><small style="color: #666;">Leadership Photo 1</small>'
                '</div>', obj.leadership_photo_1.url)
        return ""
    leadership_photo_1_preview.short_description = "Leadership Photo 1 Preview"

    def leadership_photo_2_preview(self, obj):
        if obj.leadership_photo_2:
            return format_html(
                '<div style="text-align: center; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">'
                '<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); object-fit: cover; cursor: pointer;" '
                'onclick="window.open(this.src, \'_blank\')" title="Click to view full size" />'
                '<br><small style="color: #666;">Leadership Photo 2</small>'
                '</div>', obj.leadership_photo_2.url)
        return ""
    leadership_photo_2_preview.short_description = "Leadership Photo 2 Preview"

    def leadership_photo_3_preview(self, obj):
        if obj.leadership_photo_3:
            return format_html(
                '<div style="text-align: center; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">'
                '<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); object-fit: cover; cursor: pointer;" '
                'onclick="window.open(this.src, \'_blank\')" title="Click to view full size" />'
                '<br><small style="color: #666;">Leadership Photo 3</small>'
                '</div>', obj.leadership_photo_3.url)
        return ""
    leadership_photo_3_preview.short_description = "Leadership Photo 3 Preview"

class LocalAboutPageAdmin(LocalAdminMixin, admin.ModelAdmin):
    form = LocalAboutPageForm
    list_display = ("church", "title", "updated_at")
    list_filter = ("church", "updated_at")
    search_fields = ("church__name", "title")
    readonly_fields = ("logo_preview", "founder_image_preview", "extra_image_preview", "about_photo_1_preview", "about_photo_2_preview", "about_photo_3_preview")
    fieldsets = (
        ('About Page Content', {
            'fields': ('church', 'title', 'intro', 'founding_story', 'timeline', 'leadership_timeline', 'ministry_today', 'quick_facts')
        }),
        ('Images', {
            'fields': ('logo', 'logo_preview', 'founder_image', 'founder_image_preview', 'extra_image', 'extra_image_preview', 'about_photo_1', 'about_photo_1_preview', 'about_photo_2', 'about_photo_2_preview', 'about_photo_3', 'about_photo_3_preview')
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<div style="text-align: center; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">'
                '<img src="{}" style="max-width: 200px; max-height: 200px; object-fit: contain; background: #fff; padding: 10px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); cursor: pointer;" '
                'onclick="window.open(this.src, \'_blank\')" title="Click to view full size" />'
                '<br><small style="color: #666;">Church Logo</small>'
                '</div>', obj.logo.url)
        return ""
    logo_preview.short_description = "Logo Preview"

    def founder_image_preview(self, obj):
        if obj.founder_image:
            return format_html(
                '<div style="text-align: center; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">'
                '<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 50%; box-shadow: 0 2px 8px rgba(0,0,0,0.1); object-fit: cover; cursor: pointer;" '
                'onclick="window.open(this.src, \'_blank\')" title="Click to view full size" />'
                '<br><small style="color: #666;">Founder Photo</small>'
                '</div>', obj.founder_image.url)
        return ""
    founder_image_preview.short_description = "Founder Image Preview"

    def extra_image_preview(self, obj):
        if obj.extra_image:
            return format_html(
                '<div style="text-align: center; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">'
                '<img src="{}" style="max-width: 200px; max-height: 150px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); object-fit: cover; cursor: pointer;" '
                'onclick="window.open(this.src, \'_blank\')" title="Click to view full size" />'
                '<br><small style="color: #666;">Extra Photo</small>'
                '</div>', obj.extra_image.url)
        return ""
    extra_image_preview.short_description = "Extra Image Preview"

    def about_photo_1_preview(self, obj):
        if obj.about_photo_1:
            return format_html(
                '<div style="text-align: center; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">'
                '<img src="{}" style="max-width: 200px; max-height: 150px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); object-fit: cover; cursor: pointer;" '
                'onclick="window.open(this.src, \'_blank\')" title="Click to view full size" />'
                '<br><small style="color: #666;">About Photo 1</small>'
                '</div>', obj.about_photo_1.url)
        return ""
    about_photo_1_preview.short_description = "About Photo 1 Preview"

    def about_photo_2_preview(self, obj):
        if obj.about_photo_2:
            return format_html(
                '<div style="text-align: center; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">'
                '<img src="{}" style="max-width: 200px; max-height: 150px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); object-fit: cover; cursor: pointer;" '
                'onclick="window.open(this.src, \'_blank\')" title="Click to view full size" />'
                '<br><small style="color: #666;">About Photo 2</small>'
                '</div>', obj.about_photo_2.url)
        return ""
    about_photo_2_preview.short_description = "About Photo 2 Preview"

    def about_photo_3_preview(self, obj):
        if obj.about_photo_3:
            return format_html(
                '<div style="text-align: center; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">'
                '<img src="{}" style="max-width: 200px; max-height: 150px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); object-fit: cover; cursor: pointer;" '
                'onclick="window.open(this.src, \'_blank\')" title="Click to view full size" />'
                '<br><small style="color: #666;">About Photo 3</small>'
                '</div>', obj.about_photo_3.url)
        return ""
    about_photo_3_preview.short_description = "About Photo 3 Preview"

class HeroAdmin(GlobalAdminMixin, admin.ModelAdmin):
    form = HeroForm
    list_display = ['title', 'is_active', 'is_global_featured', 'order', 'created_at']
    list_filter = ['is_active', 'is_global_featured', 'created_at']
    search_fields = ['title', 'subtitle']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [HeroMediaInline]
    fieldsets = (
        ('Hero Information', {
            'fields': ('title', 'subtitle', 'background_type', 'background_image', 'background_video')
        }),
        ('Buttons', {
            'fields': ('primary_button_text', 'primary_button_link', 'secondary_button_text', 'secondary_button_link')
        }),
        ('Status', {
            'fields': ('is_active', 'is_global_featured', 'global_feature_status', 'global_feature_date', 'order')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class GlobalSettingsAdmin(admin.ModelAdmin):
    form = GlobalSettingsForm
    """Admin for global settings"""
    list_display = ['site_name', 'updated_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'global_nav_logo_preview']
    
    def global_nav_logo_preview(self, obj):
        """Display a preview of the global navigation logo"""
        if obj.global_nav_logo:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 50%; object-fit: cover;" />',
                obj.get_global_nav_logo_url()
            )
        return "No global navigation logo uploaded"
    global_nav_logo_preview.short_description = "Global Navigation Logo Preview"
    
    def has_add_permission(self, request):
        """Only allow one global settings instance"""
        return not GlobalSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of global settings"""
        return False
    
    fieldsets = (
        ('Global Settings', {
            'fields': ('site_name', 'site_description', 'global_contact_email', 'global_contact_phone', 'global_nav_logo', 'global_nav_logo_preview')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )



class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'email', 'phone', 'event', 'registration_date', 'payment_status'
    )
    search_fields = ('first_name', 'last_name', 'email', 'event__title')
    list_filter = ('event', 'payment_status', 'registration_date')

class MinistryJoinRequestAdmin(LocalAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'ministry', 'church', 'created_at', 'is_reviewed']
    list_filter = ['ministry', 'church', 'is_reviewed', 'created_at']
    search_fields = ['name', 'email', 'phone', 'message', 'ministry__name', 'church__name']
    readonly_fields = ['created_at']
    actions = ['mark_as_reviewed']

    def mark_as_reviewed(self, request, queryset):
        for obj in queryset:
            if not obj.is_reviewed:
                # Send email notification
                send_mail(
                    subject='Your Ministry Join Request Has Been Reviewed',
                    message=f"Dear {obj.name},\n\nYour request to join the ministry '{obj.ministry.name}' at {obj.church.name} has been reviewed by our team. We appreciate your interest and will be in touch if any further steps are needed.\n\nGod bless you!\n\nBethel Church Team",
                    from_email=None,  # Use DEFAULT_FROM_EMAIL
                    recipient_list=[obj.email],
                    fail_silently=True,
                )
        queryset.update(is_reviewed=True)

# Register all admin classes (final registration)
admin.site.register(GlobalFeatureRequest, GlobalFeatureRequestAdmin)
admin.site.register(LocalHero, LocalHeroAdmin)
admin.site.register(Church, ChurchModelAdmin)
admin.site.register(ChurchAdmin, ChurchAdminModelAdmin)
admin.site.register(EventRegistration, EventRegistrationAdmin)
admin.site.register(MinistryJoinRequest, MinistryJoinRequestAdmin)
admin.site.register(GlobalSettings, GlobalSettingsAdmin)
admin.site.register(AboutPage, AboutPageAdmin)
admin.site.register(LeadershipPage, LeadershipPageAdmin)
admin.site.register(LocalLeadershipPage, LocalLeadershipPageAdmin)
admin.site.register(LocalAboutPage, LocalAboutPageAdmin)
