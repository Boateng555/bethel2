from django.db import models
from django.contrib.auth.models import User, Permission
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from datetime import datetime, timedelta
import requests
from .image_utils import resize_image_field, optimize_image_for_web

# Create your models here.

class Church(models.Model):
    """Represents a Bethel church location"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="URL-friendly name (e.g., 'bremen', 'accra')")
    
    # Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True, null=True)
    shop_url = models.URLField(blank=True, null=True, help_text="Link to church's online store (e.g., Payhip store URL)")
    
    # Church Info
    pastor_name = models.CharField(max_length=100, blank=True)
    denomination = models.CharField(max_length=100, default="Bethel")
    founded_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    
    # Media
    logo = models.ImageField(upload_to='churches/logos/', blank=True, null=True, max_length=500)
    banner_image = models.ImageField(upload_to='churches/banners/', blank=True, null=True, max_length=500)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Churches"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.city}, {self.country}"
    
    def get_full_address(self):
        parts = [self.address, self.city]
        if self.state_province:
            parts.append(self.state_province)
        parts.append(self.country)
        if self.postal_code:
            parts.append(self.postal_code)
        return ", ".join(parts)
    
    def get_logo_url(self):
        """Returns the correct URL for the logo field"""
        if self.logo:
            logo_str = str(self.logo)
            if logo_str.startswith('http'):
                return logo_str
            else:
                return self.logo.url
        return ''
    
    def get_banner_url(self):
        """Returns the correct URL for the banner_image field"""
        if self.banner_image:
            banner_str = str(self.banner_image)
            if banner_str.startswith('http'):
                return banner_str
            else:
                return self.banner_image.url
        return ''
    
    def setup_default_functionality(self):
        """Create default ministries, events, news, sermons, and donation methods for a new church"""
        today = timezone.now().date()
        # Always create events in the future
        next_sunday = today + timedelta(days=(6 - today.weekday() + 1) % 7)
        if next_sunday <= today:
            next_sunday += timedelta(days=7)
        next_wednesday = today + timedelta(days=(2 - today.weekday()) % 7)
        if next_wednesday <= today:
            next_wednesday += timedelta(days=7)
        # Create Sunday Service (always public, always in the future)
        sunday_service = Event.objects.create(
            church=self,
            title='Sunday Service',
            description=f'Join us for our weekly Sunday Service at {self.name}',
            start_date=timezone.make_aware(datetime.combine(next_sunday, datetime.min.time().replace(hour=10, minute=0))),
            end_date=timezone.make_aware(datetime.combine(next_sunday, datetime.min.time().replace(hour=12, minute=0))),
            location=self.name,
            address=self.get_full_address(),
            event_type='service',
            show_qr_code=True,  # Enable QR code by default for new events
            is_public=True
        )
        # Add default related objects for Sunday Service
        from .models import EventSpeaker, EventScheduleItem, EventHighlight, EventRegistration
        speaker = EventSpeaker.objects.create(event=sunday_service, name='Rev. John Doe')
        
        # Create multiple schedule items for Sunday Service
        EventScheduleItem.objects.create(
            event=sunday_service,
            day='Sunday',
            start_time=datetime.min.time().replace(hour=10, minute=0),
            end_time=datetime.min.time().replace(hour=10, minute=15),
            title='Opening Prayer',
            speaker=speaker
        )
        EventScheduleItem.objects.create(
            event=sunday_service,
            day='Sunday',
            start_time=datetime.min.time().replace(hour=10, minute=15),
            end_time=datetime.min.time().replace(hour=10, minute=45),
            title='Worship',
            speaker=speaker
        )
        EventScheduleItem.objects.create(
            event=sunday_service,
            day='Sunday',
            start_time=datetime.min.time().replace(hour=10, minute=45),
            end_time=datetime.min.time().replace(hour=11, minute=30),
            title='Sermon',
            speaker=speaker
        )
        EventScheduleItem.objects.create(
            event=sunday_service,
            day='Sunday',
            start_time=datetime.min.time().replace(hour=11, minute=30),
            end_time=datetime.min.time().replace(hour=12, minute=0),
            title='Closing Prayer & Benediction',
            speaker=speaker
        )
        EventHighlight.objects.create(event=sunday_service, church=self, title='First Sunday Service', description='A blessed time of worship and fellowship.', year=today.year, is_public=True)
        EventRegistration.objects.create(event=sunday_service, church=self, first_name='Jane', last_name='Smith', email='jane@example.com')

        # Create weekly prayer meeting
        prayer_meeting = Event.objects.create(
            church=self,
            title='Prayer Meeting',
            description=f'Join us for our weekly prayer meeting at {self.name}',
            start_date=timezone.make_aware(datetime.combine(next_wednesday, datetime.min.time().replace(hour=19, minute=0))),
            end_date=timezone.make_aware(datetime.combine(next_wednesday, datetime.min.time().replace(hour=20, minute=30))),
            location=self.name,
            address=self.get_full_address(),
            event_type='prayer',
            show_qr_code=True,  # Enable QR code by default for new events
            is_public=True
        )
        # Add default related objects for Prayer Meeting
        speaker2 = EventSpeaker.objects.create(event=prayer_meeting, name='Sister Mary')
        
        # Create multiple schedule items for Prayer Meeting
        EventScheduleItem.objects.create(
            event=prayer_meeting,
            day='Wednesday',
            start_time=datetime.min.time().replace(hour=19, minute=0),
            end_time=datetime.min.time().replace(hour=19, minute=15),
            title='Opening Prayer',
            speaker=speaker2
        )
        EventScheduleItem.objects.create(
            event=prayer_meeting,
            day='Wednesday',
            start_time=datetime.min.time().replace(hour=19, minute=15),
            end_time=datetime.min.time().replace(hour=19, minute=45),
            title='Worship',
            speaker=speaker2
        )
        EventScheduleItem.objects.create(
            event=prayer_meeting,
            day='Wednesday',
            start_time=datetime.min.time().replace(hour=19, minute=45),
            end_time=datetime.min.time().replace(hour=20, minute=15),
            title='Sermon',
            speaker=speaker2
        )
        EventScheduleItem.objects.create(
            event=prayer_meeting,
            day='Wednesday',
            start_time=datetime.min.time().replace(hour=20, minute=15),
            end_time=datetime.min.time().replace(hour=20, minute=30),
            title='Intercessory Prayer',
            speaker=speaker2
        )
        EventHighlight.objects.create(event=prayer_meeting, church=self, title='First Prayer Meeting', description='Powerful time of prayer and intercession.', year=today.year, is_public=True)
        EventRegistration.objects.create(event=prayer_meeting, church=self, first_name='John', last_name='Doe', email='john@example.com')
        
        # Create default ministries if none exist
        if not Ministry.objects.filter(church=self).exists():
            default_ministries = [
                {
                    'name': 'Youth Ministry',
                    'description': 'Engaging young people in faith and fellowship',
                    'ministry_type': 'youth',
                    'leader_name': 'Youth Leader',
                    'is_active': True,
                    'is_public': True
                },
                {
                    'name': 'Women\'s Ministry',
                    'description': 'Supporting and empowering women in their faith journey',
                    'ministry_type': 'women',
                    'leader_name': 'Women\'s Ministry Leader',
                    'is_active': True,
                    'is_public': True
                },
                {
                    'name': 'Men\'s Ministry',
                    'description': 'Building strong men of faith and character',
                    'ministry_type': 'men',
                    'leader_name': 'Men\'s Ministry Leader',
                    'is_active': True,
                    'is_public': True
                },
                {
                    'name': 'Children\'s Ministry',
                    'description': 'Nurturing children in faith and biblical values',
                    'ministry_type': 'children',
                    'leader_name': 'Children\'s Ministry Leader',
                    'is_active': True,
                    'is_public': True
                },
                {
                    'name': 'Music Ministry',
                    'description': 'Leading worship through music and praise',
                    'ministry_type': 'music',
                    'leader_name': 'Music Ministry Leader',
                    'is_active': True,
                    'is_public': True
                },
                {
                    'name': 'Prayer Ministry',
                    'description': 'Intercessory prayer and spiritual support',
                    'ministry_type': 'prayer',
                    'leader_name': 'Prayer Ministry Leader',
                    'is_active': True,
                    'is_public': True
                },
                {
                    'name': 'Outreach Ministry',
                    'description': 'Serving the community and sharing the gospel',
                    'ministry_type': 'outreach',
                    'leader_name': 'Outreach Ministry Leader',
                    'is_active': True,
                    'is_public': True
                }
            ]
            
            for ministry_data in default_ministries:
                Ministry.objects.create(church=self, **ministry_data)
        
        # Create default donation methods if none exist
        if not DonationMethod.objects.filter(church=self).exists():
            default_donations = [
                {
                    'name': 'General Fund',
                    'payment_type': 'other',
                    'account_info': 'Contact the church office for donation information',
                    'description': 'General church fund for operational expenses',
                    'is_active': True,
                    'is_default': True
                },
                {
                    'name': 'Building Fund',
                    'payment_type': 'other',
                    'account_info': 'Contact the church office for building fund donations',
                    'description': 'Fund for church building and maintenance projects',
                    'is_active': True,
                    'is_default': False
                },
                {
                    'name': 'Missions Fund',
                    'payment_type': 'other',
                    'account_info': 'Contact the church office for missions support',
                    'description': 'Supporting local and international missions',
                    'is_active': True,
                    'is_default': False
                }
            ]
            
            for donation_data in default_donations:
                DonationMethod.objects.create(church=self, **donation_data)
        
        # Create default news if none exist
        if not News.objects.filter(church=self).exists():
            News.objects.create(
                church=self,
                title=f'Welcome to {self.name}',
                content=f'''<p>Welcome to {self.name}! We are excited to have you join our church family.</p>
                
                <p>At {self.name}, we are committed to:</p>
                <ul>
                    <li>Sharing the love of Christ with everyone we meet</li>
                    <li>Building a strong community of believers</li>
                    <li>Serving our local community and beyond</li>
                    <li>Growing together in faith and knowledge</li>
                </ul>
                
                <p>We invite you to join us for our weekly services and events. Check out our ministries and get involved in the life of our church!</p>
                
                <p>If you have any questions or would like to learn more about {self.name}, please don't hesitate to contact us.</p>''',
                excerpt=f'Welcome to {self.name}! We are excited to have you join our church family and look forward to growing together in faith.',
                date=today,
                is_public=True,
                is_featured=True
            )
        
        # Create default sermon if none exist
        if not Sermon.objects.filter(church=self).exists():
            Sermon.objects.create(
                church=self,
                title='Welcome Message',
                preacher=self.pastor_name or 'Pastor',
                description=f'A warm welcome message from {self.name}',
                date=today,
                scripture_reference='Psalm 100:4',
                scripture_text='Enter his gates with thanksgiving and his courts with praise; give thanks to him and praise his name.',
                duration='15:00',
                language='English',
                is_public=True,
                is_featured=True
            )
        
        # Create default hero section if none exists
        if not Hero.objects.filter(church=self).exists():
            hero = Hero.objects.create(
                church=self,
                title=f'Welcome to {self.name}',
                subtitle=f'Join us in worship and fellowship in {self.city}, {self.country}',
                background_type='image',
                primary_button_text='Plan Your Visit',
                primary_button_link=f'/church/{self.id}/about/',
                secondary_button_text='Watch Online',
                secondary_button_link=f'/church/{self.id}/sermons/',
                is_active=True,
                order=1
            )
            
            # Create default Hero Media for the hero
            HeroMedia.objects.create(
                hero=hero,
                image=None,  # Will be uploaded by admin
                video=None,  # Will be uploaded by admin
                order=1
            )
        
        # Create welcome news article if none exists
        if not News.objects.filter(church=self).exists():
            News.objects.create(
                church=self,
                title=f'Welcome to {self.name}',
                content=f'We are excited to welcome you to {self.name} in {self.city}, {self.country}. Join us as we grow together in faith and fellowship.',
                excerpt=f'Welcome to {self.name} - a place of worship, community, and spiritual growth.',
                date=today,
                is_public=True
            )
        
        # Create default about page if none exists
        if not hasattr(self, 'about_page'):
            LocalAboutPage.objects.create(
                church=self,
                title=f'About {self.name}',
                intro=f'Welcome to {self.name}, a vibrant community of faith in {self.city}, {self.country}. We are committed to sharing the love of Christ and building strong relationships with God and each other.',
                founding_story=f'{self.name} was established to serve the spiritual needs of our community. We believe in the power of prayer, the importance of fellowship, and the transformative love of Jesus Christ.',
                ministry_today=f'Today, {self.name} continues to grow and serve our community through various ministries, outreach programs, and worship services. We welcome everyone to join us on this journey of faith.',
                quick_facts=f'• Founded: {self.founded_date.year if self.founded_date else "Recently"}\n• Denomination: {self.denomination}\n• Location: {self.city}, {self.country}\n• Pastor: {self.pastor_name or "To be announced"}'
            )
        
        # Create default leadership page if none exists
        if not hasattr(self, 'leadership_page'):
            LocalLeadershipPage.objects.create(
                church=self,
                title=f'Leadership at {self.name}',
                intro=f'The leadership team at {self.name} is dedicated to serving our congregation and community with love, wisdom, and spiritual guidance.',
                current_leadership=f'Our current leadership team works together to ensure that {self.name} continues to be a place of worship, learning, and community service.',
                vision_statement=f'To be a beacon of hope and love in our community, sharing the gospel and making disciples of Jesus Christ.',
                mission_statement=f'To worship God, grow in faith, serve others, and share the love of Christ with everyone we meet.'
            )
        
        return True

    def save(self, *args, **kwargs):
        # Auto-geocode if lat/lon missing and address/city/country present
        if (not self.latitude or not self.longitude) and (self.address and self.city and self.country):
            try:
                query = f"{self.address}, {self.city}, {self.country}"
                url = f"https://nominatim.openstreetmap.org/search"
                params = {
                    'q': query,
                    'format': 'json',
                    'limit': 1
                }
                headers = {'User-Agent': 'bethel-church-directory/1.0'}
                resp = requests.get(url, params=params, headers=headers, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    if data:
                        self.latitude = data[0]['lat']
                        self.longitude = data[0]['lon']
            except Exception as e:
                print(f"Geocoding failed: {e}")
        super().save(*args, **kwargs)

class ChurchAdmin(models.Model):
    """Links users to churches with admin permissions"""
    ROLE_CHOICES = [
        ('local_admin', 'Local Admin'),
        ('global_admin', 'Global Admin'),
        ('moderator', 'Moderator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    church = models.ForeignKey(Church, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='local_admin')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Church Admins"
    
    def __str__(self):
        if self.role == 'global_admin':
            return f"{self.user.username} - Global Admin"
        return f"{self.user.username} - {self.church.name} ({self.role})"

# List of required permissions (codename format: <action>_<model>)
EVENT_PERMS = [
    'add_event', 'change_event', 'delete_event', 'view_event',
    'add_eventspeaker', 'change_eventspeaker', 'delete_eventspeaker', 'view_eventspeaker',
    'add_eventscheduleitem', 'change_eventscheduleitem', 'delete_eventscheduleitem', 'view_eventscheduleitem',
    'add_eventhighlight', 'change_eventhighlight', 'delete_eventhighlight', 'view_eventhighlight',
    'add_eventregistration', 'change_eventregistration', 'delete_eventregistration', 'view_eventregistration',
]

# Patch ChurchAdmin save method to always grant event permissions to local admins
def grant_event_perms_to_local_admin(user):
    app_label = 'core'
    for codename in EVENT_PERMS:
        try:
            perm = Permission.objects.get(codename=codename, content_type__app_label=app_label)
            user.user_permissions.add(perm)
        except Permission.DoesNotExist:
            pass
    user.save()

orig_save = ChurchAdmin.save

def patched_save(self, *args, **kwargs):
    orig_save(self, *args, **kwargs)
    if self.role == 'local_admin' and self.is_active:
        grant_event_perms_to_local_admin(self.user)

ChurchAdmin.save = patched_save

class Event(models.Model):
    """Church events with multi-tenant support"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True)
    
    # Event Details
    event_type = models.CharField(max_length=50, choices=[
        ('service', 'Church Service'),
        ('prayer', 'Prayer Meeting'),
        ('youth', 'Youth Event'),
        ('women', 'Women\'s Fellowship'),
        ('men', 'Men\'s Fellowship'),
        ('convention', 'Convention'),
        ('conference', 'Conference'),
        ('outreach', 'Outreach'),
        ('other', 'Other'),
    ], default='service')
    
    # Registration
    requires_registration = models.BooleanField(default=False)
    max_attendees = models.IntegerField(null=True, blank=True)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    is_big_event = models.BooleanField(default=False, help_text="Use special big event template for this event")
    is_global_featured = models.BooleanField(default=False, help_text="Show this event on the global site if approved")
    global_feature_status = models.CharField(
        max_length=20,
        choices=[('none', 'None'), ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='none',
        help_text="Approval status for global feature request"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # New field
    show_qr_code = models.BooleanField(default=False, help_text="Show QR code for this event on the detail page.")
    
    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.title} - {self.church.name}"
    
    @property
    def card_image(self):
        """Get the first image from Event Hero Media for card display"""
        return next((media.image for media in self.hero_media.all() if media.image), None)

class Ministry(models.Model):
    """Church ministries with multi-tenant support"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    ministry_type = models.CharField(max_length=50, choices=[
        ('youth', 'Youth Ministry'),
        ('women', 'Women\'s Ministry'),
        ('men', 'Men\'s Ministry'),
        ('children', 'Children\'s Ministry'),
        ('music', 'Music Ministry'),
        ('prayer', 'Prayer Ministry'),
        ('outreach', 'Outreach Ministry'),
        ('education', 'Education Ministry'),
        ('other', 'Other'),
    ], default='other')
    
    # Contact
    leader_name = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Media
    image = models.ImageField(upload_to='ministries/', blank=True, null=True, max_length=500)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True, help_text="Show this ministry on the global website")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Ministries"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.church.name}"
    
    def get_image_url(self):
        """Returns the correct URL for the image field"""
        if self.image:
            image_str = str(self.image)
            if image_str.startswith('http'):
                return image_str
            else:
                return self.image.url
        return ''

class News(models.Model):
    """Church news with multi-tenant support"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    excerpt = models.TextField(blank=True, max_length=300)
    date = models.DateField()
    
    # Media
    image = models.ImageField(upload_to='news/', blank=True, null=True, max_length=500)
    
    # Status
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    is_global_featured = models.BooleanField(default=False, help_text="Show this news on the global site if approved")
    global_feature_status = models.CharField(
        max_length=20,
        choices=[('none', 'None'), ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='none',
        help_text="Approval status for global feature request"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "News"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.title} - {self.church.name}"
    
    def get_image_url(self):
        """Returns the correct URL for the image field"""
        if self.image:
            image_str = str(self.image)
            if image_str.startswith('http'):
                return image_str
            else:
                return self.image.url
        return ''

class Sermon(models.Model):
    """Church sermons with multi-tenant support"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    preacher = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    
    # Scripture
    scripture_reference = models.CharField(max_length=200, blank=True, null=True)
    scripture_text = models.TextField(blank=True)
    
    # Media
    audio_file = models.FileField(upload_to='sermons/audio/', blank=True, null=True, max_length=500)
    video_file = models.FileField(upload_to='sermons/video/', blank=True, null=True, max_length=500)
    thumbnail = models.ImageField(upload_to='sermons/thumbnails/', blank=True, null=True, max_length=500)
    link = models.URLField(max_length=500, blank=True, null=True, help_text="External link to sermon (YouTube, Vimeo, etc.)")
    
    # Details
    duration = models.CharField(max_length=20, blank=True, null=True)  # e.g., "45:30"
    language = models.CharField(max_length=50, default='English')
    
    # Status
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.preacher} ({self.date})"
    
    def get_thumbnail_url(self):
        """Returns the correct URL for the thumbnail field"""
        if self.thumbnail:
            thumb_str = str(self.thumbnail)
            if thumb_str.startswith('http'):
                return thumb_str
            else:
                return self.thumbnail.url
        return ''
    
    def get_audio_url(self):
        """Returns the correct URL for the audio_file field"""
        if self.audio_file:
            audio_str = str(self.audio_file)
            if audio_str.startswith('http'):
                return audio_str
            else:
                return self.audio_file.url
        return ''
    
    def get_video_url(self):
        """Returns the correct URL for the video_file field"""
        if self.video_file:
            video_str = str(self.video_file)
            if video_str.startswith('http'):
                return video_str
            else:
                return self.video_file.url
        return ''

class DonationMethod(models.Model):
    """Payment methods for each church"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    
    PAYMENT_TYPES = [
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('gofundme', 'GoFundMe'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100, help_text="e.g., 'General Fund', 'Building Fund'")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    
    # External Link Support
    external_link = models.URLField(blank=True, null=True, help_text="Direct link to PayPal, GoFundMe, etc.")
    account_info = models.TextField(help_text="Account details, email, or payment instructions (if no external link)")
    description = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.church.name}"
    
    def get_donation_url(self):
        """Returns the donation URL - either external link or internal page"""
        if self.external_link:
            return self.external_link
        
        # For PayPal methods, if account_info contains a PayPal.me link, return it
        if self.payment_type == 'paypal' and self.account_info and 'paypal.me' in self.account_info:
            # Check if it's already a full URL
            if self.account_info.startswith('http'):
                return self.account_info
            else:
                # Add https:// if it's just the paypal.me path
                return f"https://{self.account_info}"
        
        # For other methods, return the main church donation page
        return f"/churches/{self.church.id}/donate/"
    
    def is_external_link(self):
        """Check if this donation method uses an external link"""
        return bool(self.external_link)

class Convention(models.Model):
    """Large events/conventions hosted by churches"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host_church = models.ForeignKey(Church, on_delete=models.CASCADE, related_name='hosted_conventions')
    participating_churches = models.ManyToManyField(Church, related_name='participating_conventions', blank=True)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    address = models.TextField()
    
    # Registration
    max_attendees = models.IntegerField(null=True, blank=True)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Media
    banner_image = models.ImageField(upload_to='conventions/', blank=True, null=True, max_length=500)
    
    # Status
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    registration_open = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.title} - {self.host_church.name}"

class NewsletterSignup(models.Model):
    """Newsletter subscriptions per church"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    church = models.ForeignKey(Church, on_delete=models.CASCADE, null=True, blank=True)
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Preferences
    wants_global_updates = models.BooleanField(default=True)
    wants_local_updates = models.BooleanField(default=True)
    wants_event_notifications = models.BooleanField(default=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['email', 'church']
    
    def __str__(self):
        if self.church:
            return f"{self.email} - {self.church.name}"
        return f"{self.email} - Global"

def notify_global_admins_of_request(feature_request):
    """Send email to all global admins when a new global feature request is made."""
    from .models import ChurchAdmin
    global_admins = ChurchAdmin.objects.filter(role='global_admin', is_active=True)
    emails = [ca.user.email for ca in global_admins if ca.user.email]
    if not emails:
        return
    subject = f"[Bethel] New Global Feature Request: {feature_request.title}"
    message = f"A new global feature request has been submitted by {feature_request.requested_by.get_full_name() or feature_request.requested_by.username} for {feature_request.church.name}.\n\nTitle: {feature_request.title}\nDescription: {feature_request.description}\n\nPlease review the request in the admin panel."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, emails, fail_silently=True)

def notify_requester_of_decision(feature_request):
    """Send email to the requester when their global feature request is approved or rejected."""
    if not feature_request.requested_by.email:
        return
    subject = f"[Bethel] Your Global Feature Request: {feature_request.title} was {feature_request.status.title()}"
    if feature_request.status == 'approved':
        message = f"Congratulations! Your request to feature '{feature_request.title}' on the global site has been approved.\n\nApproval Date: {feature_request.approval_date}\nNotes: {feature_request.admin_notes}"
    else:
        message = f"Your request to feature '{feature_request.title}' on the global site was rejected.\n\nNotes: {feature_request.admin_notes}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [feature_request.requested_by.email], fail_silently=True)

class GlobalFeatureRequest(models.Model):
    """Notifications for global feature requests from local admins"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Request Details
    content_type = models.CharField(max_length=20, choices=[
        ('hero', 'Hero Banner'),
        ('event', 'Event'),
        ('news', 'News'),
    ])
    content_id = models.UUIDField(help_text="ID of the content being requested")
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feature_requests_sent')
    
    # Request Info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    
    # Approval Details
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feature_requests_reviewed')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approval_date = models.DateTimeField(null=True, blank=True, help_text="When the content should be featured on global site")
    admin_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Global Feature Request"
        verbose_name_plural = "Global Feature Requests"
    
    def __str__(self):
        return f"{self.title} - {self.church.name} ({self.get_status_display()})"
    
    def get_content_object(self):
        """Get the actual content object being requested"""
        if self.content_type == 'hero':
            return Hero.objects.filter(id=self.content_id).first()
        elif self.content_type == 'event':
            return Event.objects.filter(id=self.content_id).first()
        elif self.content_type == 'news':
            return News.objects.filter(id=self.content_id).first()
        return None

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        old_status = None
        if not is_new:
            old = GlobalFeatureRequest.objects.get(pk=self.pk)
            old_status = old.status
        super().save(*args, **kwargs)
        if is_new:
            notify_global_admins_of_request(self)
        elif old_status and old_status != self.status:
            notify_requester_of_decision(self)

class Hero(models.Model):
    """Hero sections for churches"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    church = models.ForeignKey(Church, on_delete=models.CASCADE, null=True, blank=True)
    
    title = models.CharField(max_length=200)
    subtitle = models.TextField()
    
    # Background
    background_type = models.CharField(
        max_length=10,
        choices=[
            ('image', 'Image'),
            ('video', 'Video'),
        ],
        default='image'
    )
    background_image = models.ImageField(upload_to='hero/', blank=True, null=True, max_length=500)
    background_video = models.FileField(upload_to='hero/videos/', blank=True, null=True, max_length=500)
    
    # Buttons
    primary_button_text = models.CharField(max_length=50, default='Plan Your Visit')
    primary_button_link = models.CharField(max_length=200, default='/visit')
    secondary_button_text = models.CharField(max_length=50, default='Watch Online')
    secondary_button_link = models.CharField(max_length=200, default='/watch')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_global_featured = models.BooleanField(default=False, help_text="Show this hero on the global site if approved")
    global_feature_status = models.CharField(
        max_length=20,
        choices=[('none', 'None'), ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='none',
        help_text="Approval status for global feature request"
    )
    global_feature_date = models.DateTimeField(null=True, blank=True, help_text="When this hero should be featured on the global site")
    order = models.IntegerField(default=1)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        if self.church:
            return f"{self.title} - {self.church.name}"
        return f"{self.title} - Global"

class HeroMedia(models.Model):
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name='hero_media')
    image = models.ImageField(upload_to='hero/', blank=True, null=True, max_length=500)
    video = models.FileField(upload_to='hero/videos/', blank=True, null=True, max_length=500)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Hero Media'
        verbose_name_plural = 'Hero Media'
    
    def __str__(self):
        return f"Hero Media {self.id} - Order {self.order}"
    
    def get_image_url(self):
        """Returns the correct URL for the image field"""
        if self.image:
            image_str = str(self.image)
            if image_str.startswith('http'):
                return image_str
            else:
                return self.image.url
        return ''
    
    def get_video_url(self):
        """Returns the correct URL for the video field"""
        if self.video:
            video_str = str(self.video)
            if video_str.startswith('http'):
                return video_str
            else:
                return self.video.url
        return ''
    
    def save(self, *args, **kwargs):
        # Ensure only one hero media per hero
        if not self.pk:
            HeroMedia.objects.filter(hero=self.hero).delete()
        super().save(*args, **kwargs)

class ChurchApplication(models.Model):
    """Applications for new churches to join the platform"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Church Info
    church_name = models.CharField(max_length=200)
    pastor_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    
    # Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Additional Info
    congregation_size = models.CharField(max_length=50, choices=[
        ('small', 'Small (1-50)'),
        ('medium', 'Medium (51-200)'),
        ('large', 'Large (201-500)'),
        ('very_large', 'Very Large (500+)'),
    ])
    description = models.TextField(help_text="Tell us about your church")
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    
    # Admin Notes
    admin_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.church_name} - {self.city}, {self.country} ({self.status})"

# Signal to automatically set up new churches with default functionality
@receiver(post_save, sender=Church)
def setup_new_church(sender, instance, created, **kwargs):
    """Automatically set up new churches with default functionality"""
    if created:
        # Use the church's setup method
        instance.setup_default_functionality()

@receiver(post_save, sender=ChurchAdmin)
def setup_church_for_local_admin(sender, instance, created, **kwargs):
    """Ensure default functionality is set up when a local admin is assigned to a church."""
    if instance.role == 'local_admin' and instance.church:
        # Setup default functionality
        instance.church.setup_default_functionality()
        
        # Ensure Local Hero exists with Hero Media for local admins
        if not Hero.objects.filter(church=instance.church).exists():
            hero = Hero.objects.create(
                church=instance.church,
                title=f'Welcome to {instance.church.name}',
                subtitle=f'Join us in worship and fellowship in {instance.church.city}, {instance.church.country}',
                background_type='image',
                primary_button_text='Plan Your Visit',
                primary_button_link=f'/church/{instance.church.id}/about/',
                secondary_button_text='Watch Online',
                secondary_button_link=f'/church/{instance.church.id}/sermons/',
                is_active=True,
                order=1
            )
            
            # Create default Hero Media for the hero
            HeroMedia.objects.create(
                hero=hero,
                image=None,  # Will be uploaded by admin
                video=None,  # Will be uploaded by admin
                order=1
            )

@receiver(post_save, sender=ChurchAdmin)
def assign_local_admin_permissions(sender, instance, created, **kwargs):
    if instance.role == 'local_admin':
        from django.contrib.auth.models import Permission
        model_codenames = [
            'ministry', 'event', 'news', 'sermon', 'hero', 'heromedia', 'donationmethod', 'localhero', 'eventheromedia', 'ministryjoinrequest'
        ]
        for codename in model_codenames:
            for action in ['add', 'change', 'delete', 'view']:
                perm_codename = f"{action}_{codename}"
                try:
                    perm = Permission.objects.get(codename=perm_codename)
                    instance.user.user_permissions.add(perm)
                except Permission.DoesNotExist:
                    pass
        instance.user.save()

class LocalHero(Hero):
    """Proxy model for local church heroes"""
    class Meta:
        proxy = True
        verbose_name = "Local Hero"
        verbose_name_plural = "Local Heroes"
    
    def save(self, *args, **kwargs):
        """Ensure local heroes always have a church assigned"""
        if not self.church:
            raise ValueError("Local heroes must have a church assigned")
        super().save(*args, **kwargs)

class Testimony(models.Model):
    """User-submitted testimonies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    church = models.ForeignKey(Church, on_delete=models.CASCADE, null=True, blank=True)
    
    # Testimony Details
    author_name = models.CharField(max_length=100, help_text="Your name (can be anonymous)")
    author_email = models.EmailField(help_text="Your email (will not be displayed publicly)")
    title = models.CharField(max_length=200, help_text="Brief title for your testimony")
    content = models.TextField(help_text="Share your testimony here")
    
    # Optional Details
    location = models.CharField(max_length=100, blank=True, help_text="City, Country (optional)")
    category = models.CharField(max_length=50, choices=[
        ('salvation', 'Salvation Story'),
        ('healing', 'Healing'),
        ('deliverance', 'Deliverance'),
        ('blessing', 'Blessing'),
        ('ministry', 'Ministry Impact'),
        ('family', 'Family'),
        ('other', 'Other'),
    ], default='other')
    
    # Status
    is_approved = models.BooleanField(default=False, help_text="Admin approval required before publishing")
    is_featured = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False, help_text="Hide author name when displaying")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Testimonies"
        ordering = ['-created_at']
    
    def __str__(self):
        if self.is_anonymous:
            return f"Anonymous Testimony - {self.title}"
        return f"{self.author_name} - {self.title}"
    
    def get_display_name(self):
        """Get the name to display (anonymous or real name)"""
        if self.is_anonymous:
            return "Anonymous"
        return self.author_name

class AboutPage(models.Model):
    title = models.CharField(max_length=200, default="About Us")
    intro = models.TextField("Intro/Mission", blank=True)
    founding_story = models.TextField("Founding Story", blank=True)
    timeline = models.TextField("Timeline", blank=True)
    leadership_timeline = models.TextField("Leadership Timeline", blank=True)
    ministry_today = models.TextField("Ministry Today", blank=True)
    quick_facts = models.TextField("Quick Facts", blank=True)
    logo = models.ImageField(upload_to='about/', blank=True, null=True, max_length=500)
    founder_image = models.ImageField(upload_to='about/', blank=True, null=True, max_length=500)
    extra_image = models.ImageField(upload_to='about/', blank=True, null=True, max_length=500)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Page"
        verbose_name_plural = "About Page"

    def __str__(self):
        return self.title

class LeadershipPage(models.Model):
    title = models.CharField(max_length=200, default="Leadership")
    intro = models.TextField("Introduction", blank=True)
    current_leadership = models.TextField("Current Leadership", blank=True)
    board_members = models.TextField("Board Members", blank=True)
    leadership_team = models.TextField("Leadership Team", blank=True)
    vision_statement = models.TextField("Vision Statement", blank=True)
    mission_statement = models.TextField("Mission Statement", blank=True)
    
    # Images
    chairman_image = models.ImageField(upload_to='leadership/', blank=True, null=True, help_text="Photo of the Chairman", max_length=500)
    vice_chairman_image = models.ImageField(upload_to='leadership/', blank=True, null=True, help_text="Photo of the Vice Chairman", max_length=500)
    board_image = models.ImageField(upload_to='leadership/', blank=True, null=True, help_text="Group photo of board members", max_length=500)
    team_image = models.ImageField(upload_to='leadership/', blank=True, null=True, help_text="Group photo of leadership team", max_length=500)
    leadership_photo_1 = models.ImageField(upload_to='leadership/', blank=True, null=True, help_text="Additional leadership photo 1", max_length=500)
    leadership_photo_2 = models.ImageField(upload_to='leadership/', blank=True, null=True, help_text="Additional leadership photo 2", max_length=500)
    leadership_photo_3 = models.ImageField(upload_to='leadership/', blank=True, null=True, help_text="Additional leadership photo 3", max_length=500)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Leadership Page"
        verbose_name_plural = "Leadership Page"
    
    def __str__(self):
        return f"Leadership Page - {self.updated_at.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        # Ensure only one leadership page exists
        if not self.pk:
            LeadershipPage.objects.all().delete()
        super().save(*args, **kwargs)

class LocalLeadershipPage(models.Model):
    """Leadership page for individual churches"""
    church = models.OneToOneField(Church, on_delete=models.CASCADE, related_name='leadership_page')
    title = models.CharField(max_length=200, default="Leadership")
    intro = models.TextField("Introduction", blank=True)
    current_leadership = models.TextField("Current Leadership", blank=True)
    board_members = models.TextField("Board Members", blank=True)
    leadership_team = models.TextField("Leadership Team", blank=True)
    vision_statement = models.TextField("Vision Statement", blank=True)
    mission_statement = models.TextField("Mission Statement", blank=True)
    
    # Images
    pastor_image = models.ImageField(upload_to='leadership/local/', blank=True, null=True, help_text="Photo of the Pastor", max_length=500)
    assistant_pastor_image = models.ImageField(upload_to='leadership/local/', blank=True, null=True, help_text="Photo of the Assistant Pastor", max_length=500)
    board_image = models.ImageField(upload_to='leadership/local/', blank=True, null=True, help_text="Group photo of board members", max_length=500)
    team_image = models.ImageField(upload_to='leadership/local/', blank=True, null=True, help_text="Group photo of leadership team", max_length=500)
    leadership_photo_1 = models.ImageField(upload_to='leadership/local/', blank=True, null=True, help_text="Additional leadership photo 1", max_length=500)
    leadership_photo_2 = models.ImageField(upload_to='leadership/local/', blank=True, null=True, help_text="Additional leadership photo 2", max_length=500)
    leadership_photo_3 = models.ImageField(upload_to='leadership/local/', blank=True, null=True, help_text="Additional leadership photo 3", max_length=500)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Local Leadership Page"
        verbose_name_plural = "Local Leadership Pages"
    
    def __str__(self):
        return f"Leadership - {self.church.name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one leadership page per church
        if not self.pk:
            LocalLeadershipPage.objects.filter(church=self.church).delete()
        super().save(*args, **kwargs)

class LocalAboutPage(models.Model):
    """About page for individual churches"""
    church = models.OneToOneField(Church, on_delete=models.CASCADE, related_name='about_page')
    title = models.CharField(max_length=200, default="About Us")
    intro = models.TextField("Intro/Mission", blank=True)
    founding_story = models.TextField("Founding Story", blank=True)
    timeline = models.TextField("Timeline", blank=True)
    leadership_timeline = models.TextField("Leadership Timeline", blank=True)
    ministry_today = models.TextField("Ministry Today", blank=True)
    quick_facts = models.TextField("Quick Facts", blank=True)
    
    # Images
    logo = models.ImageField(upload_to='about/local/', blank=True, null=True, help_text="Church logo", max_length=500)
    founder_image = models.ImageField(upload_to='about/local/', blank=True, null=True, help_text="Photo of church founder or pastor", max_length=500)
    extra_image = models.ImageField(upload_to='about/local/', blank=True, null=True, help_text="Additional church photo", max_length=500)
    about_photo_1 = models.ImageField(upload_to='about/local/', blank=True, null=True, help_text="Additional about page photo 1", max_length=500)
    about_photo_2 = models.ImageField(upload_to='about/local/', blank=True, null=True, help_text="Additional about page photo 2", max_length=500)
    about_photo_3 = models.ImageField(upload_to='about/local/', blank=True, null=True, help_text="Additional about page photo 3", max_length=500)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Local About Page"
        verbose_name_plural = "Local About Pages"
    
    def __str__(self):
        return f"About - {self.church.name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one about page per church
        if not self.pk:
            LocalAboutPage.objects.filter(church=self.church).delete()
        super().save(*args, **kwargs)

class MinistryJoinRequest(models.Model):
    """User requests to join a ministry"""
    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE, related_name='join_requests')
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ministry Join Request'
        verbose_name_plural = 'Ministry Join Requests'

    def __str__(self):
        return f"{self.name} - {self.ministry.name} ({self.church.name})"

class EventRegistration(models.Model):
    """Event registrations for big events"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    
    # Attendee Info
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Registration Details
    registration_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Special Requirements
    dietary_restrictions = models.TextField(blank=True)
    special_needs = models.TextField(blank=True)
    additional_notes = models.TextField(blank=True)
    
    # Status
    is_confirmed = models.BooleanField(default=False)
    confirmation_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-registration_date']
        verbose_name = 'Event Registration'
        verbose_name_plural = 'Event Registrations'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.event.title}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class EventHighlight(models.Model):
    """Past event highlights and memories"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='highlights', null=True, blank=True)
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    year = models.IntegerField(help_text="Year of the event")
    
    # Media
    image = models.ImageField(upload_to='event_highlights/', blank=True, null=True, max_length=500)
    video_url = models.URLField(blank=True, null=True, help_text="If a video is provided, it will be shown as the main media for this highlight. Otherwise, the image will be used. Enter a YouTube or Vimeo URL.")
    
    # Stats (optional)
    attendees_count = models.IntegerField(null=True, blank=True)
    testimonial = models.TextField(blank=True)
    testimonial_author = models.CharField(max_length=100, blank=True)
    
    # Status
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-year', '-created_at']
        verbose_name = 'Event Highlight'
        verbose_name_plural = 'Event Highlights'
    
    def __str__(self):
        return f"{self.title} ({self.year}) - {self.church.name}"

class EventSpeaker(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='speakers')
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='events/speakers/', blank=True, null=True, max_length=500)
    title = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    
    def __str__(self):
        return self.name

class EventScheduleItem(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='schedule_items')
    day = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    speaker = models.ForeignKey(EventSpeaker, on_delete=models.SET_NULL, null=True, blank=True, related_name='schedule_items')
    location = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.day}: {self.title} ({self.start_time}-{self.end_time})"

class EventHeroMedia(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='hero_media')
    image = models.ImageField(upload_to='hero/', blank=True, null=True, max_length=500)
    video = models.FileField(upload_to='hero/videos/', blank=True, null=True, max_length=500)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Media for {self.event.title} ({self.id})"

# Image resizing signals
@receiver(pre_save, sender=Church)
def resize_church_images(sender, instance, **kwargs):
    """Resize church images before saving"""
    if instance.logo and not str(instance.logo).startswith('http'):
        resize_image_field(instance, 'logo', max_width=400, max_height=400, quality=85)
    if instance.banner_image and not str(instance.banner_image).startswith('http'):
        resize_image_field(instance, 'banner_image', max_width=1200, max_height=600, quality=85)



@receiver(pre_save, sender=Ministry)
def resize_ministry_images(sender, instance, **kwargs):
    """Resize ministry images before saving"""
    if instance.image and not str(instance.image).startswith('http'):
        resize_image_field(instance, 'image', max_width=600, max_height=400, quality=85)

@receiver(pre_save, sender=News)
def resize_news_images(sender, instance, **kwargs):
    """Resize news images before saving"""
    if instance.image and not str(instance.image).startswith('http'):
        resize_image_field(instance, 'image', max_width=800, max_height=600, quality=85)

@receiver(pre_save, sender=Sermon)
def resize_sermon_images(sender, instance, **kwargs):
    """Resize sermon images before saving"""
    if instance.thumbnail and not str(instance.thumbnail).startswith('http'):
        resize_image_field(instance, 'thumbnail', max_width=400, max_height=300, quality=85)

@receiver(pre_save, sender=Hero)
def resize_hero_images(sender, instance, **kwargs):
    """Resize hero images before saving"""
    if instance.background_image and not str(instance.background_image).startswith('http'):
        resize_image_field(instance, 'background_image', max_width=1920, max_height=1080, quality=85)

@receiver(pre_save, sender=HeroMedia)
def resize_hero_media_images(sender, instance, **kwargs):
    """Resize hero media images before saving"""
    if instance.image and not str(instance.image).startswith('http'):
        resize_image_field(instance, 'image', max_width=1200, max_height=800, quality=85)

@receiver(pre_save, sender=EventHighlight)
def resize_event_highlight_images(sender, instance, **kwargs):
    """Resize event highlight images before saving"""
    if instance.image and not str(instance.image).startswith('http'):
        resize_image_field(instance, 'image', max_width=800, max_height=600, quality=85)

@receiver(pre_save, sender=EventSpeaker)
def resize_event_speaker_images(sender, instance, **kwargs):
    """Resize event speaker images before saving"""
    if instance.photo and not str(instance.photo).startswith('http'):
        resize_image_field(instance, 'photo', max_width=300, max_height=300, quality=85)

@receiver(pre_save, sender=AboutPage)
def resize_about_page_images(sender, instance, **kwargs):
    """Resize about page images before saving"""
    for field_name in ['logo', 'founder_image', 'extra_image']:
        field = getattr(instance, field_name)
        if field and not str(field).startswith('http'):
            resize_image_field(instance, field_name, max_width=600, max_height=600, quality=85)

@receiver(pre_save, sender=LeadershipPage)
def resize_leadership_page_images(sender, instance, **kwargs):
    """Resize leadership page images before saving"""
    for field_name in ['chairman_image', 'vice_chairman_image', 'board_image', 'team_image', 
                       'leadership_photo_1', 'leadership_photo_2', 'leadership_photo_3']:
        field = getattr(instance, field_name)
        if field and not str(field).startswith('http'):
            resize_image_field(instance, field_name, max_width=400, max_height=400, quality=85)

@receiver(pre_save, sender=LocalLeadershipPage)
def resize_local_leadership_page_images(sender, instance, **kwargs):
    """Resize local leadership page images before saving"""
    for field_name in ['pastor_image', 'assistant_pastor_image', 'board_image', 'team_image',
                       'leadership_photo_1', 'leadership_photo_2', 'leadership_photo_3']:
        field = getattr(instance, field_name)
        if field and not str(field).startswith('http'):
            resize_image_field(instance, field_name, max_width=400, max_height=400, quality=85)

@receiver(pre_save, sender=LocalAboutPage)
def resize_local_about_page_images(sender, instance, **kwargs):
    """Resize local about page images before saving"""
    for field_name in ['logo', 'founder_image', 'extra_image', 'about_photo_1', 'about_photo_2', 'about_photo_3']:
        field = getattr(instance, field_name)
        if field and not str(field).startswith('http'):
            resize_image_field(instance, field_name, max_width=600, max_height=600, quality=85)

@receiver(pre_save, sender=EventHeroMedia)
def resize_event_hero_media_images(sender, instance, **kwargs):
    """Resize event hero media images before saving"""
    if instance.image and not str(instance.image).startswith('http'):
        resize_image_field(instance, 'image', max_width=1200, max_height=800, quality=85)
