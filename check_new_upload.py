#!/usr/bin/env python3
"""
Check for new image uploads and test their accessibility
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import HeroMedia
import requests

def check_new_uploads():
    """Check for new image uploads"""
    
    print("🔍 Checking for new image uploads...")
    
    # Get all Hero Media entries
    hero_media = HeroMedia.objects.all().order_by('-id')
    print(f"Total Hero Media entries: {hero_media.count()}")
    
    print("\n📋 Recent Hero Media entries (last 10):")
    for media in hero_media[:10]:
        print(f"  ID: {media.id}")
        print(f"  Image: {media.image}")
        if media.image:
            # Test if the URL is accessible
            try:
                response = requests.head(str(media.image), timeout=10)
                print(f"  Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"  ✅ Accessible")
                else:
                    print(f"  ❌ Not accessible")
            except Exception as e:
                print(f"  ❌ Error: {e}")
        else:
            print(f"  ❌ No image")
        print()
    
    # Check for any entries with the filename pattern from the debug log
    print("🔍 Looking for entries with recent upload patterns...")
    recent_entries = hero_media.filter(image__icontains='hero_51fd2e79')
    if recent_entries.exists():
        print(f"Found {recent_entries.count()} entries with recent upload pattern:")
        for entry in recent_entries:
            print(f"  ID: {entry.id}, Image: {entry.image}")
    else:
        print("No entries found with recent upload pattern")
    
    # Check for any entries created in the last hour
    from django.utils import timezone
    from datetime import timedelta
    
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_entries = hero_media.filter(created_at__gte=one_hour_ago) if hasattr(HeroMedia, 'created_at') else []
    
    if recent_entries:
        print(f"\n🕐 Found {len(recent_entries)} entries created in the last hour:")
        for entry in recent_entries:
            print(f"  ID: {entry.id}, Image: {entry.image}")
    else:
        print("\n🕐 No entries found created in the last hour")

if __name__ == "__main__":
    check_new_uploads() 