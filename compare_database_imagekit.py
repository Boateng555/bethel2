#!/usr/bin/env python
"""
Compare database vs ImageKit to see what's different
"""

import os
import django

# Set environment variables
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import News, Church, Ministry, Sermon, Event
from imagekitio import ImageKit

print("🔍 Comparing Database vs ImageKit...")

# Initialize ImageKit
imagekit = ImageKit(
    private_key='private_Dnsrj2VW7uJakaeMaNYaav+P784=',
    public_key='public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=',
    url_endpoint='https://ik.imagekit.io/9buar9mbp'
)

# Get all files in ImageKit
try:
    list_files = imagekit.list_files()
    imagekit_files = [f.name for f in list_files.list]
    print(f"✅ Found {len(imagekit_files)} files in ImageKit")
    
    # Check News items
    print("\n📰 NEWS ITEMS:")
    news_items = News.objects.all()
    for news in news_items:
        print(f"   📰 {news.title}")
        if news.image:
            print(f"      Database: {news.image}")
            print(f"      URL: {news.image.url}")
            if str(news.image) in imagekit_files:
                print(f"      ✅ Found in ImageKit")
            else:
                print(f"      ❌ NOT found in ImageKit")
        else:
            print(f"      📝 No image")
    
    # Check Church items
    print("\n⛪ CHURCH ITEMS:")
    church_items = Church.objects.all()
    for church in church_items:
        print(f"   ⛪ {church.name}")
        if church.logo:
            print(f"      Database: {church.logo}")
            print(f"      URL: {church.logo.url}")
            if str(church.logo) in imagekit_files:
                print(f"      ✅ Found in ImageKit")
            else:
                print(f"      ❌ NOT found in ImageKit")
        else:
            print(f"      📝 No logo")
    
    # Check Ministry items
    print("\n🙏 MINISTRY ITEMS:")
    ministry_items = Ministry.objects.all()
    for ministry in ministry_items:
        print(f"   🙏 {ministry.name}")
        if ministry.image:
            print(f"      Database: {ministry.image}")
            print(f"      URL: {ministry.image.url}")
            if str(ministry.image) in imagekit_files:
                print(f"      ✅ Found in ImageKit")
            else:
                print(f"      ❌ NOT found in ImageKit")
        else:
            print(f"      📝 No image")
    
    # Check Sermon items
    print("\n📖 SERMON ITEMS:")
    sermon_items = Sermon.objects.all()
    for sermon in sermon_items:
        print(f"   📖 {sermon.title}")
        if sermon.thumbnail:
            print(f"      Database: {sermon.thumbnail}")
            print(f"      URL: {sermon.thumbnail.url}")
            if str(sermon.thumbnail) in imagekit_files:
                print(f"      ✅ Found in ImageKit")
            else:
                print(f"      ❌ NOT found in ImageKit")
        else:
            print(f"      📝 No thumbnail")
    
    # Check Event items
    print("\n📅 EVENT ITEMS:")
    event_items = Event.objects.all()
    for event in event_items:
        print(f"   📅 {event.title}")
        if event.image:
            print(f"      Database: {event.image}")
            print(f"      URL: {event.image.url}")
            if str(event.image) in imagekit_files:
                print(f"      ✅ Found in ImageKit")
            else:
                print(f"      ❌ NOT found in ImageKit")
        else:
            print(f"      📝 No image")
    
    print(f"\n📊 SUMMARY:")
    print(f"   ImageKit files: {len(imagekit_files)}")
    print(f"   News items: {news_items.count()}")
    print(f"   Church items: {church_items.count()}")
    print(f"   Ministry items: {ministry_items.count()}")
    print(f"   Sermon items: {sermon_items.count()}")
    print(f"   Event items: {event_items.count()}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n📋 Next steps:")
print("1. Look for items marked with ❌ NOT found in ImageKit")
print("2. These are the items that need to be fixed")
print("3. Run fix_all_broken_images.py to fix them") 