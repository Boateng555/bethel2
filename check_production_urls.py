#!/usr/bin/env python3
"""
Check current database URLs to debug the image issue
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church, News, Ministry, Sermon, HeroMedia, Event

def check_database_urls():
    """Check what URLs are currently in the database"""
    
    print("🔍 Checking current database URLs...")
    
    # Check Church logos
    print("\n📋 Church logos:")
    churches = Church.objects.all()
    for church in churches:
        if church.logo:
            print(f"  {church.name}: {church.logo}")
        else:
            print(f"  {church.name}: No logo")
    
    # Check News images
    print("\n📋 News images:")
    news_items = News.objects.all()
    for news in news_items:
        if news.image:
            print(f"  {news.title}: {news.image}")
        else:
            print(f"  {news.title}: No image")
    
    # Check HeroMedia images
    print("\n📋 HeroMedia images:")
    hero_media = HeroMedia.objects.all()
    for media in hero_media:
        if media.image:
            print(f"  {media.title}: {media.image}")
        else:
            print(f"  {media.title}: No image")
    
    # Check if any URLs are already Cloudinary URLs
    print("\n🔍 Checking for Cloudinary URLs:")
    cloudinary_count = 0
    local_count = 0
    
    for church in churches:
        if church.logo:
            if str(church.logo).startswith('http'):
                cloudinary_count += 1
            else:
                local_count += 1
    
    for news in news_items:
        if news.image:
            if str(news.image).startswith('http'):
                cloudinary_count += 1
            else:
                local_count += 1
    
    for media in hero_media:
        if media.image:
            if str(media.image).startswith('http'):
                cloudinary_count += 1
            else:
                local_count += 1
    
    print(f"  Cloudinary URLs: {cloudinary_count}")
    print(f"  Local paths: {local_count}")
    
    if local_count > 0:
        print(f"\n❌ Found {local_count} local paths that need to be updated!")
        print("This is why images aren't showing on Railway.")
    else:
        print(f"\n✅ All URLs are already Cloudinary URLs!")

if __name__ == "__main__":
    check_database_urls() 