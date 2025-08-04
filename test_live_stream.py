#!/usr/bin/env python
"""
Script to test LiveStreamSettings functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import LiveStreamSettings, Church
from django.utils import timezone

def main():
    print("=== Testing LiveStreamSettings Functionality ===\n")
    
    # Check if any LiveStreamSettings exist
    settings = LiveStreamSettings.objects.first()
    
    if not settings:
        print("❌ No LiveStreamSettings found!")
        print("\n📝 To create LiveStreamSettings:")
        print("1. Go to Django Admin: http://127.0.0.1:8000/admin/")
        print("2. Navigate to 'Core' → 'Live Stream Settings'")
        print("3. Click 'Add Live Stream Settings'")
        print("4. Configure your platform settings")
        print("5. Set your service schedule")
        print("6. Save the settings")
        return
    
    print(f"✅ Found LiveStreamSettings: {settings}")
    print(f"   Platform: {settings.platform}")
    print(f"   Church: {settings.church.name if settings.church else 'Global'}")
    print(f"   Is Live: {settings.is_live}")
    print(f"   Auto Detect: {settings.auto_detect_live}")
    
    # Test live status
    is_live = settings.get_live_status()
    print(f"\n🔴 Live Status: {'🟢 LIVE' if is_live else '🔴 OFFLINE'}")
    
    # Test next service time
    next_service = settings.get_next_service_time()
    print(f"⏰ Next Service: {next_service}")
    
    # Test embed code
    embed_code = settings.get_embed_code()
    if "No embed code available" not in embed_code:
        print(f"📺 Embed Code: Available")
        print(f"   Width: {settings.embed_width}%")
        print(f"   Height: {settings.embed_height}px")
        print(f"   Autoplay: {'✅ Enabled' if settings.autoplay else '❌ Disabled'}")
    else:
        print(f"📺 Embed Code: Not configured")
    
    # Show platform-specific settings
    print(f"\n🔧 Platform Settings:")
    if settings.platform == 'youtube':
        print(f"   YouTube Channel ID: {settings.youtube_channel_id or 'Not set'}")
        print(f"   YouTube Stream Key: {'✅ Set' if settings.youtube_stream_key else '❌ Not set'}")
        print(f"   YouTube Live URL: {settings.youtube_live_url or 'Not set'}")
    elif settings.platform == 'facebook':
        print(f"   Facebook Page ID: {settings.facebook_page_id or 'Not set'}")
        print(f"   Facebook Live URL: {settings.facebook_live_url or 'Not set'}")
    
    # Show service schedule
    print(f"\n⏰ Service Schedule:")
    print(f"   Sunday Morning: {settings.sunday_morning_time}")
    print(f"   Sunday Evening: {settings.sunday_evening_time}")
    print(f"   Wednesday: {settings.wednesday_time}")
    print(f"   Friday: {settings.friday_time}")
    
    # Show current time for comparison
    now = timezone.now()
    print(f"\n🕐 Current Time: {now.strftime('%A, %B %d, %Y at %I:%M %p')}")
    
    print(f"\n✅ LiveStreamSettings test completed!")
    print(f"\n🌐 To view the live stream page:")
    print(f"   http://127.0.0.1:8000/watch/")

if __name__ == "__main__":
    main() 