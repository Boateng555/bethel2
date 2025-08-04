from django.contrib import admin
from django import forms
from .models import (
    Convention, NewsletterSignup, Hero, HeroMedia
)

class GlobalHeroMediaInline(admin.TabularInline):
    model = HeroMedia
    extra = 3  # Allow adding 3 new media items at once
    max_num = 10  # Maximum 10 media items per hero
    fields = ('image', 'video', 'order')
    verbose_name = "Hero Media Item"
    verbose_name_plural = "Hero Media Items"
    help_text = "Add multiple images and videos for the hero carousel. Images and videos will be displayed in order. You can add up to 10 media items."
    fk_name = 'hero'

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
            from .models import ChurchAdmin
            church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
            if church_admin.role == 'global_admin':
                # Global admins can see all global content
                return qs
        except ChurchAdmin.DoesNotExist:
            pass
            
        # Local admins and regular users can't see global content
        return qs.none()

class GlobalConventionAdmin(GlobalAdminMixin, admin.ModelAdmin):
    """Global convention management"""
    list_display = ['title', 'host_church', 'start_date', 'end_date', 'is_featured', 'is_public', 'created_at']
    list_filter = ['is_featured', 'is_public', 'start_date', 'created_at']
    search_fields = ['title', 'description', 'host_church__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Convention Information', {
            'fields': ('title', 'description', 'host_church', 'participating_churches')
        }),
        ('Event Details', {
            'fields': ('start_date', 'end_date', 'location', 'address')
        }),
        ('Registration', {
            'fields': ('max_attendees', 'registration_deadline', 'registration_fee', 'registration_open')
        }),
        ('Media', {
            'fields': ('banner_image',)
        }),
        ('Status', {
            'fields': ('is_featured', 'is_public')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class GlobalHeroAdmin(GlobalAdminMixin, admin.ModelAdmin):
    """Global hero banners for the main website"""
    list_display = ['title', 'background_type', 'is_active', 'order', 'created_at']
    list_filter = ['background_type', 'is_active', 'created_at']
    search_fields = ['title', 'subtitle']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [GlobalHeroMediaInline]
    
    fieldsets = (
        ('Hero Information', {
            'fields': ('title', 'subtitle')
        }),
        ('Background', {
            'fields': ('background_type', 'background_image', 'background_video')
        }),
        ('Hero Media', {
            'fields': (),  # No direct fields, managed via GlobalHeroMediaInline
            'description': 'Add multiple images and videos for the hero carousel using the "Hero Media Items" section below.'
        }),
        ('Buttons', {
            'fields': ('primary_button_text', 'primary_button_link', 'secondary_button_text', 'secondary_button_link')
        }),
        ('Status', {
            'fields': ('is_active', 'order')
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Only show global hero banners (no church association) and restrict access"""
        qs = super().get_queryset(request)
        
        # Only superusers and global admins can see global heroes
        if request.user.is_superuser:
            return qs.filter(church__isnull=True)
            
        # Check if user is a global admin
        try:
            from .models import ChurchAdmin
            church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
            if church_admin.role == 'global_admin':
                return qs.filter(church__isnull=True)
        except ChurchAdmin.DoesNotExist:
            pass
            
        # Local admins and regular users can't see global heroes
        return qs.none()
    
    def has_add_permission(self, request):
        """Only superusers and global admins can add global heroes"""
        if request.user.is_superuser:
            return True
            
        try:
            from .models import ChurchAdmin
            church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
            return church_admin.role == 'global_admin'
        except ChurchAdmin.DoesNotExist:
            return False
    
    def has_change_permission(self, request, obj=None):
        """Only superusers and global admins can change global heroes"""
        if request.user.is_superuser:
            return True
            
        try:
            from .models import ChurchAdmin
            church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
            return church_admin.role == 'global_admin'
        except ChurchAdmin.DoesNotExist:
            return False
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers and global admins can delete global heroes"""
        if request.user.is_superuser:
            return True
            
        try:
            from .models import ChurchAdmin
            church_admin = ChurchAdmin.objects.get(user=request.user, is_active=True)
            return church_admin.role == 'global_admin'
        except ChurchAdmin.DoesNotExist:
            return False

class GlobalNewsletterSignupAdmin(GlobalAdminMixin, admin.ModelAdmin):
    """Global newsletter signups"""
    list_display = ['first_name', 'last_name', 'email', 'church', 'is_active', 'created_at']
    list_filter = ['is_active', 'wants_global_updates', 'wants_local_updates', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'church__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'church')
        }),
        ('Preferences', {
            'fields': ('wants_global_updates', 'wants_local_updates', 'wants_event_notifications')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Register global admin classes
admin.site.register(Convention, GlobalConventionAdmin)
# admin.site.register(ConventionRegistration, GlobalConventionRegistrationAdmin)
admin.site.register(Hero, GlobalHeroAdmin)
admin.site.register(NewsletterSignup, GlobalNewsletterSignupAdmin) 