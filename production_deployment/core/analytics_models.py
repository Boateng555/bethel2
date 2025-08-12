import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta

# Try to import Church model, but handle gracefully if it doesn't exist
try:
    from .models import Church
except ImportError:
    Church = None

class VisitorSession(models.Model):
    """Track visitor sessions for analytics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Session Info
    session_id = models.CharField(max_length=100, unique=True, help_text="Django session ID")
    ip_address = models.GenericIPAddressField(help_text="Visitor's IP address")
    user_agent = models.TextField(help_text="Browser/device information")
    
    # Geographic Data (privacy-friendly)
    country = models.CharField(max_length=100, blank=True, help_text="Country from IP")
    city = models.CharField(max_length=100, blank=True, help_text="City from IP")
    region = models.CharField(max_length=100, blank=True, help_text="Region/State from IP")
    
    # Device/Browser Info
    device_type = models.CharField(max_length=20, choices=[
        ('desktop', 'Desktop'),
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
        ('other', 'Other'),
    ], default='other')
    browser = models.CharField(max_length=50, blank=True, help_text="Browser name")
    browser_version = models.CharField(max_length=20, blank=True, help_text="Browser version")
    os = models.CharField(max_length=50, blank=True, help_text="Operating system")
    
    # Referrer Info
    referrer = models.URLField(blank=True, help_text="Where visitor came from")
    referrer_domain = models.CharField(max_length=200, blank=True, help_text="Domain of referrer")
    
    # Church Context (if applicable)
    church = models.ForeignKey(Church, on_delete=models.SET_NULL, null=True, blank=True, help_text="Church context if visiting church page") if Church else None
    
    # Session Stats
    page_views_count = models.PositiveIntegerField(default=0, help_text="Number of pages viewed in this session")
    duration = models.PositiveIntegerField(default=0, help_text="Session duration in seconds")
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True, help_text="When session started")
    last_activity = models.DateTimeField(auto_now=True, help_text="Last activity in session")
    ended_at = models.DateTimeField(null=True, blank=True, help_text="When session ended")
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Visitor Session'
        verbose_name_plural = 'Visitor Sessions'
    
    def __str__(self):
        return f"Session {self.session_id[:8]} - {self.ip_address} ({self.started_at.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def is_active(self):
        """Check if session is still active (within 30 minutes)"""
        return self.last_activity > timezone.now() - timedelta(minutes=30)
    
    def end_session(self):
        """Mark session as ended and calculate duration"""
        if not self.ended_at:
            self.ended_at = timezone.now()
            self.duration = int((self.ended_at - self.started_at).total_seconds())
            self.save()


class PageView(models.Model):
    """Track individual page views"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Session Reference
    session = models.ForeignKey(VisitorSession, on_delete=models.CASCADE, related_name='views')
    
    # Page Info
    url = models.URLField(help_text="Full URL visited")
    path = models.CharField(max_length=500, help_text="URL path")
    page_title = models.CharField(max_length=200, blank=True, help_text="Page title")
    view_name = models.CharField(max_length=100, blank=True, help_text="Django view name")
    
    # Church Context
    church = models.ForeignKey(Church, on_delete=models.SET_NULL, null=True, blank=True, help_text="Church context if church page") if Church else None
    
    # Performance
    load_time = models.PositiveIntegerField(null=True, blank=True, help_text="Page load time in milliseconds")
    
    # Timestamp
    viewed_at = models.DateTimeField(auto_now_add=True, help_text="When page was viewed")
    
    class Meta:
        ordering = ['-viewed_at']
        verbose_name = 'Page View'
        verbose_name_plural = 'Page Views'
    
    def __str__(self):
        return f"{self.path} - {self.viewed_at.strftime('%Y-%m-%d %H:%M')}"


class AnalyticsSettings(models.Model):
    """Settings for analytics tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Tracking Settings
    enable_tracking = models.BooleanField(default=True, help_text="Enable visitor tracking")
    track_geolocation = models.BooleanField(default=True, help_text="Track country/city from IP")
    track_user_agent = models.BooleanField(default=True, help_text="Track browser/device info")
    track_referrers = models.BooleanField(default=True, help_text="Track where visitors came from")
    
    # Privacy Settings
    anonymize_ips = models.BooleanField(default=True, help_text="Anonymize IP addresses")
    retention_days = models.PositiveIntegerField(default=365, help_text="Days to keep analytics data")
    
    # Performance Settings
    batch_size = models.PositiveIntegerField(default=100, help_text="Number of records to process in batch")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Analytics Settings'
        verbose_name_plural = 'Analytics Settings'
    
    def __str__(self):
        return f"Analytics Settings (Tracking: {'On' if self.enable_tracking else 'Off'})"
    
    @classmethod
    def get_settings(cls):
        """Get or create analytics settings"""
        settings, created = cls.objects.get_or_create()
        return settings
