#!/usr/bin/env python
"""
Update database URLs from local paths to Cloudinary URLs
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import (
    Church, News, Ministry, Sermon, HeroMedia, Event, 
    EventSpeaker, AboutPage, LeadershipPage, LocalAboutPage, 
    LocalLeadershipPage, EventHighlight, EventHeroMedia
)

def update_database_urls():
    """Update database URLs to point to Cloudinary"""
    
    print("🔄 Updating database URLs to Cloudinary...")
    
    # Your Cloudinary base URL
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
    
    # Update Hero Media
    print("\n📋 Updating Hero Media...")
    hero_media = HeroMedia.objects.all()
    for media in hero_media:
        if media.image and str(media.image) and not str(media.image).startswith('http'):
            filename = os.path.basename(str(media.image))
            new_url = f"{cloudinary_base}/hero/{filename}"
            print(f"  Hero Media {media.id}: {media.image} -> {new_url}")
            media.image = new_url
            media.save()
    
    # Update Event Highlights
    print("\n📋 Updating Event Highlights...")
    highlights = EventHighlight.objects.all()
    for highlight in highlights:
        if highlight.image and str(highlight.image) and not str(highlight.image).startswith('http'):
            filename = os.path.basename(str(highlight.image))
            new_url = f"{cloudinary_base}/event_highlights/{filename}"
            print(f"  {highlight.title}: {highlight.image} -> {new_url}")
            highlight.image = new_url
            highlight.save()
    
    # Update Event Speakers
    print("\n📋 Updating Event Speakers...")
    speakers = EventSpeaker.objects.all()
    for speaker in speakers:
        if speaker.photo and str(speaker.photo) and not str(speaker.photo).startswith('http'):
            filename = os.path.basename(str(speaker.photo))
            new_url = f"{cloudinary_base}/events/speakers/{filename}"
            print(f"  {speaker.name}: {speaker.photo} -> {new_url}")
            speaker.photo = new_url
            speaker.save()
    
    # Update About Page
    print("\n📋 Updating About Page...")
    about_pages = AboutPage.objects.all()
    for about in about_pages:
        for field_name in ['logo', 'founder_image', 'extra_image']:
            field = getattr(about, field_name)
            if field and str(field) and not str(field).startswith('http'):
                filename = os.path.basename(str(field))
                new_url = f"{cloudinary_base}/about/{filename}"
                print(f"  About {field_name}: {field} -> {new_url}")
                setattr(about, field_name, new_url)
        about.save()
    
    # Update Leadership Page
    print("\n📋 Updating Leadership Page...")
    leadership_pages = LeadershipPage.objects.all()
    for leadership in leadership_pages:
        for field_name in ['chairman_image', 'vice_chairman_image', 'board_image', 'team_image', 
                          'leadership_photo_1', 'leadership_photo_2', 'leadership_photo_3']:
            field = getattr(leadership, field_name)
            if field and str(field) and not str(field).startswith('http'):
                filename = os.path.basename(str(field))
                new_url = f"{cloudinary_base}/leadership/{filename}"
                print(f"  Leadership {field_name}: {field} -> {new_url}")
                setattr(leadership, field_name, new_url)
        leadership.save()
    
    # Update Local About Page
    print("\n📋 Updating Local About Page...")
    local_about_pages = LocalAboutPage.objects.all()
    for about in local_about_pages:
        for field_name in ['logo', 'founder_image', 'extra_image', 'about_photo_1', 'about_photo_2', 'about_photo_3']:
            field = getattr(about, field_name)
            if field and str(field) and not str(field).startswith('http'):
                filename = os.path.basename(str(field))
                new_url = f"{cloudinary_base}/about/local/{filename}"
                print(f"  Local About {field_name}: {field} -> {new_url}")
                setattr(about, field_name, new_url)
        about.save()
    
    # Update Local Leadership Page
    print("\n📋 Updating Local Leadership Page...")
    local_leadership_pages = LocalLeadershipPage.objects.all()
    for leadership in local_leadership_pages:
        for field_name in ['pastor_image', 'assistant_pastor_image', 'board_image', 'team_image',
                          'leadership_photo_1', 'leadership_photo_2', 'leadership_photo_3']:
            field = getattr(leadership, field_name)
            if field and str(field) and not str(field).startswith('http'):
                filename = os.path.basename(str(field))
                new_url = f"{cloudinary_base}/leadership/local/{filename}"
                print(f"  Local Leadership {field_name}: {field} -> {new_url}")
                setattr(leadership, field_name, new_url)
        leadership.save()
    
    # Update Event Hero Media
    print("\n📋 Updating Event Hero Media...")
    event_hero_media = EventHeroMedia.objects.all()
    for media in event_hero_media:
        if media.image and str(media.image) and not str(media.image).startswith('http'):
            filename = os.path.basename(str(media.image))
            new_url = f"{cloudinary_base}/hero/{filename}"
            print(f"  Event Hero Media {media.id}: {media.image} -> {new_url}")
            media.image = new_url
            media.save()
    
    print("\n🎉 Database update completed!")
    print("📝 All image URLs have been updated to use Cloudinary")
    print("🌐 Your images should now be visible on the live site")

if __name__ == "__main__":
    update_database_urls() 