#!/usr/bin/env python3
"""
Update database URLs from local paths to Cloudinary URLs
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church, News, Ministry, Sermon, HeroMedia, Event, EventSpeaker, AboutPage, LeadershipPage

def update_database_urls():
    """Update database URLs to point to Cloudinary"""
    
    print("🔄 Updating database URLs to Cloudinary...")
    
    # Cloudinary base URL
    cloudinary_base = "https://res.cloudinary.com/dhzdusb5k/image/upload/v1752764497/bethel"
    
    # Update Church logos
    print("\n📋 Updating Church logos...")
    churches = Church.objects.all()
    for church in churches:
        if church.logo and str(church.logo) and not str(church.logo).startswith('http'):
            # Extract filename from path
            filename = os.path.basename(str(church.logo))
            new_url = f"{cloudinary_base}/churches/logos/{filename}"
            print(f"  {church.name}: {church.logo} -> {new_url}")
            church.logo = new_url
            church.save()
    
    # Update News images
    print("\n📋 Updating News images...")
    news_items = News.objects.all()
    for news in news_items:
        if news.image and str(news.image) and not str(news.image).startswith('http'):
            filename = os.path.basename(str(news.image))
            new_url = f"{cloudinary_base}/news/{filename}"
            print(f"  {news.title}: {news.image} -> {new_url}")
            news.image = new_url
            news.save()
    
    # Update Ministry images
    print("\n📋 Updating Ministry images...")
    ministries = Ministry.objects.all()
    for ministry in ministries:
        if ministry.image and str(ministry.image) and not str(ministry.image).startswith('http'):
            filename = os.path.basename(str(ministry.image))
            new_url = f"{cloudinary_base}/ministries/{filename}"
            print(f"  {ministry.name}: {ministry.image} -> {new_url}")
            ministry.image = new_url
            ministry.save()
    
    # Update Sermon thumbnails
    print("\n📋 Updating Sermon thumbnails...")
    sermons = Sermon.objects.all()
    for sermon in sermons:
        if sermon.thumbnail and str(sermon.thumbnail) and not str(sermon.thumbnail).startswith('http'):
            filename = os.path.basename(str(sermon.thumbnail))
            new_url = f"{cloudinary_base}/sermons/thumbnails/{filename}"
            print(f"  {sermon.title}: {sermon.thumbnail} -> {new_url}")
            sermon.thumbnail = new_url
            sermon.save()
    
    # Update HeroMedia images
    print("\n📋 Updating HeroMedia images...")
    hero_media = HeroMedia.objects.all()
    for media in hero_media:
        if media.image and str(media.image) and not str(media.image).startswith('http'):
            filename = os.path.basename(str(media.image))
            new_url = f"{cloudinary_base}/hero/{filename}"
            print(f"  {media.title}: {media.image} -> {new_url}")
            media.image = new_url
            media.save()
    
    # Update Event images
    print("\n📋 Updating Event images...")
    events = Event.objects.all()
    for event in events:
        if event.image and str(event.image) and not str(event.image).startswith('http'):
            filename = os.path.basename(str(event.image))
            new_url = f"{cloudinary_base}/events/{filename}"
            print(f"  {event.title}: {event.image} -> {new_url}")
            event.image = new_url
            event.save()
    
    # Update EventSpeaker images
    print("\n📋 Updating EventSpeaker images...")
    speakers = EventSpeaker.objects.all()
    for speaker in speakers:
        if speaker.image and str(speaker.image) and not str(speaker.image).startswith('http'):
            filename = os.path.basename(str(speaker.image))
            new_url = f"{cloudinary_base}/events/speakers/{filename}"
            print(f"  {speaker.name}: {speaker.image} -> {new_url}")
            speaker.image = new_url
            speaker.save()
    
    # Update AboutPage images
    print("\n📋 Updating AboutPage images...")
    about_pages = AboutPage.objects.all()
    for page in about_pages:
        if page.image and str(page.image) and not str(page.image).startswith('http'):
            filename = os.path.basename(str(page.image))
            new_url = f"{cloudinary_base}/about/{filename}"
            print(f"  {page.title}: {page.image} -> {new_url}")
            page.image = new_url
            page.save()
    
    # Update LeadershipPage images
    print("\n📋 Updating LeadershipPage images...")
    leadership_pages = LeadershipPage.objects.all()
    for page in leadership_pages:
        if page.image and str(page.image) and not str(page.image).startswith('http'):
            filename = os.path.basename(str(page.image))
            new_url = f"{cloudinary_base}/leadership/{filename}"
            print(f"  {page.title}: {page.image} -> {new_url}")
            page.image = new_url
            page.save()
    
    print("\n✅ Database URLs updated successfully!")
    print("All media files now point to Cloudinary URLs.")

if __name__ == "__main__":
    update_database_urls() 