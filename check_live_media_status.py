#!/usr/bin/env python3
"""
Check the current status of media URLs in the database
"""

import os
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church, News, Ministry, Sermon, HeroMedia, EventHighlight, EventSpeaker
from core.models import AboutPage, LeadershipPage

print("🔍 Checking current media URLs in database...")
print("=" * 60)

# Check Church logos
print("\n📋 CHURCH LOGOS:")
churches = Church.objects.all()
for church in churches:
    if church.logo:
        print(f"  {church.name}: {church.logo}")
        if 'res.cloudinary.com' in str(church.logo):
            print(f"    ✅ Cloudinary URL")
        else:
            print(f"    ❌ Local file path")

# Check News images
print("\n📋 NEWS IMAGES:")
news_items = News.objects.all()
for news in news_items:
    if news.image:
        print(f"  {news.title}: {news.image}")
        if 'res.cloudinary.com' in str(news.image):
            print(f"    ✅ Cloudinary URL")
        else:
            print(f"    ❌ Local file path")

# Check Ministry images
print("\n📋 MINISTRY IMAGES:")
ministries = Ministry.objects.all()
for ministry in ministries:
    if ministry.image:
        print(f"  {ministry.name}: {ministry.image}")
        if 'res.cloudinary.com' in str(ministry.image):
            print(f"    ✅ Cloudinary URL")
        else:
            print(f"    ❌ Local file path")

# Check Sermon thumbnails
print("\n📋 SERMON THUMBNAILS:")
sermons = Sermon.objects.all()
for sermon in sermons:
    if sermon.thumbnail:
        print(f"  {sermon.title}: {sermon.thumbnail}")
        if 'res.cloudinary.com' in str(sermon.thumbnail):
            print(f"    ✅ Cloudinary URL")
        else:
            print(f"    ❌ Local file path")

# Check Hero Media
print("\n📋 HERO MEDIA:")
hero_media = HeroMedia.objects.all()
for hero in hero_media:
    if hero.image:
        print(f"  Hero {hero.id}: {hero.image}")
        if 'res.cloudinary.com' in str(hero.image):
            print(f"    ✅ Cloudinary URL")
        else:
            print(f"    ❌ Local file path")

# Check Event Highlights
print("\n📋 EVENT HIGHLIGHTS:")
highlights = EventHighlight.objects.all()
for highlight in highlights:
    if highlight.video_url:
        print(f"  {highlight.title}: {highlight.video_url}")
        if 'res.cloudinary.com' in str(highlight.video_url):
            print(f"    ✅ Cloudinary URL")
        else:
            print(f"    ❌ Local file path")

# Check Event Speakers
print("\n📋 EVENT SPEAKERS:")
speakers = EventSpeaker.objects.all()
for speaker in speakers:
    if speaker.photo:
        print(f"  {speaker.name}: {speaker.photo}")
        if 'res.cloudinary.com' in str(speaker.photo):
            print(f"    ✅ Cloudinary URL")
        else:
            print(f"    ❌ Local file path")

# Check About Page
print("\n📋 ABOUT PAGE:")
about_pages = AboutPage.objects.all()
for about in about_pages:
    if about.logo:
        print(f"  Logo: {about.logo}")
        if 'res.cloudinary.com' in str(about.logo):
            print(f"    ✅ Cloudinary URL")
        else:
            print(f"    ❌ Local file path")
    
    if about.founder_image:
        print(f"  Founder Image: {about.founder_image}")
        if 'res.cloudinary.com' in str(about.founder_image):
            print(f"    ✅ Cloudinary URL")
        else:
            print(f"    ❌ Local file path")

# Check Leadership Page
print("\n📋 LEADERSHIP PAGE:")
leadership_pages = LeadershipPage.objects.all()
for leadership in leadership_pages:
    if leadership.chairman_image:
        print(f"  Chairman: {leadership.chairman_image}")
        if 'res.cloudinary.com' in str(leadership.chairman_image):
            print(f"    ✅ Cloudinary URL")
        else:
            print(f"    ❌ Local file path")

print("\n" + "=" * 60)
print("💡 SUMMARY:")
print("  - ✅ Cloudinary URLs will work on live site")
print("  - ❌ Local file paths will show broken images")
print("  - If you see mostly ❌, we need to upload to Cloudinary") 