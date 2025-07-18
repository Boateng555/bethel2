#!/usr/bin/env python3
"""
Check the current status of all media files in the database
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import (
    Church, News, Ministry, Sermon, HeroMedia, Event, 
    EventSpeaker, AboutPage, LeadershipPage, LocalAboutPage, 
    LocalLeadershipPage, EventHighlight, EventHeroMedia
)

def check_media_status():
    """Check the status of all media files"""
    
    print("🔍 Checking media status...")
    print(f"Environment: {'Production' if not django.conf.settings.DEBUG else 'Development'}")
    print(f"Storage: {django.conf.settings.DEFAULT_FILE_STORAGE}")
    print()
    
    # Check Church logos
    print("📋 Church Logos:")
    churches = Church.objects.all()
    cloudinary_count = 0
    local_count = 0
    empty_count = 0
    
    for church in churches:
        if church.logo:
            logo_str = str(church.logo)
            if logo_str.startswith('http'):
                cloudinary_count += 1
                print(f"  ✅ {church.name}: Cloudinary URL")
            else:
                local_count += 1
                print(f"  📁 {church.name}: Local file")
        else:
            empty_count += 1
            print(f"  ❌ {church.name}: No logo")
    
    print(f"  Summary: {cloudinary_count} Cloudinary, {local_count} Local, {empty_count} Empty")
    print()
    
    # Check Hero Media
    print("📋 Hero Media:")
    hero_media = HeroMedia.objects.all()
    cloudinary_count = 0
    local_count = 0
    empty_count = 0
    
    for media in hero_media:
        if media.image:
            image_str = str(media.image)
            if image_str.startswith('http'):
                cloudinary_count += 1
                print(f"  ✅ Hero Media {media.id}: Cloudinary URL")
            else:
                local_count += 1
                print(f"  📁 Hero Media {media.id}: Local file")
        else:
            empty_count += 1
            print(f"  ❌ Hero Media {media.id}: No image")
    
    print(f"  Summary: {cloudinary_count} Cloudinary, {local_count} Local, {empty_count} Empty")
    print()
    
    # Check News images
    print("📋 News Images:")
    news_items = News.objects.all()
    cloudinary_count = 0
    local_count = 0
    empty_count = 0
    
    for news in news_items:
        if news.image:
            image_str = str(news.image)
            if image_str.startswith('http'):
                cloudinary_count += 1
                print(f"  ✅ {news.title}: Cloudinary URL")
            else:
                local_count += 1
                print(f"  📁 {news.title}: Local file")
        else:
            empty_count += 1
            print(f"  ❌ {news.title}: No image")
    
    print(f"  Summary: {cloudinary_count} Cloudinary, {local_count} Local, {empty_count} Empty")
    print()
    
    # Test a few Cloudinary URLs
    print("🔗 Testing Cloudinary URLs:")
    test_count = 0
    for church in churches[:3]:  # Test first 3 churches
        if church.logo and str(church.logo).startswith('http'):
            try:
                import requests
                response = requests.head(str(church.logo), timeout=5)
                if response.status_code == 200:
                    print(f"  ✅ {church.name}: URL accessible ({response.status_code})")
                else:
                    print(f"  ❌ {church.name}: URL not accessible ({response.status_code})")
                test_count += 1
            except Exception as e:
                print(f"  ❌ {church.name}: Error testing URL - {e}")
                test_count += 1
    
    if test_count == 0:
        print("  No Cloudinary URLs to test")

if __name__ == "__main__":
    check_media_status() 