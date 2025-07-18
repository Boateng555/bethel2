#!/usr/bin/env python
"""
Script to upload all media files to ImageKit.io using the new storage backend
"""
import os
import django
from pathlib import Path

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from core.models import Church, Hero, HeroMedia, News, Ministry, Sermon, EventSpeaker, EventHighlight, AboutPage, LeadershipPage

def upload_media_to_imagekit():
    """
    Upload all media files to ImageKit.io using the new storage backend
    """
    print("🚀 Uploading Media to ImageKit.io...")
    print("=" * 70)
    
    # Check if ImageKit is configured
    if not all(settings.IMAGEKIT_CONFIG.values()):
        print("❌ ImageKit credentials not found!")
        print("Please set these environment variables:")
        print("  IMAGEKIT_PUBLIC_KEY")
        print("  IMAGEKIT_PRIVATE_KEY")
        print("  IMAGEKIT_URL_ENDPOINT")
        print("\nTo get these credentials:")
        print("1. Go to https://imagekit.io/")
        print("2. Sign up for a free account")
        print("3. Go to Developer Options → API Keys")
        print("4. Copy your Public Key, Private Key, and URL Endpoint")
        return
    
    print("🖼️ ImageKit configured successfully")
    print(f"Using storage: {settings.DEFAULT_FILE_STORAGE}")
    
    # Process Church Logos
    print("\n🏛️ Processing Church Logos...")
    churches = Church.objects.all()
    for church in churches:
        print(f"  📤 {church.name}")
        if church.logo and hasattr(church.logo, 'path'):
            local_path = church.logo.path
            if os.path.exists(local_path):
                print(f"    📸 Uploading logo...")
                try:
                    # Read the file and save using the new storage backend
                    with open(local_path, 'rb') as file:
                        from django.core.files.base import ContentFile
                        content = ContentFile(file.read(), name=os.path.basename(local_path))
                        church.logo.save(os.path.basename(local_path), content, save=True)
                        print(f"      ✅ Uploaded: {church.logo.url}")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"    ⚠️ Logo file missing")
        else:
            print(f"    ❌ No logo")
    
    # Process News Images
    print("\n📰 Processing News Images...")
    news_items = News.objects.all()
    for news in news_items:
        print(f"  📤 {news.title}")
        if news.image and hasattr(news.image, 'path'):
            local_path = news.image.path
            if os.path.exists(local_path):
                print(f"    📸 Uploading image...")
                try:
                    with open(local_path, 'rb') as file:
                        from django.core.files.base import ContentFile
                        content = ContentFile(file.read(), name=os.path.basename(local_path))
                        news.image.save(os.path.basename(local_path), content, save=True)
                        print(f"      ✅ Uploaded: {news.image.url}")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"    ⚠️ Image file missing")
        else:
            print(f"    ❌ No image")
    
    # Process Ministry Images
    print("\n⛪ Processing Ministry Images...")
    ministries = Ministry.objects.all()
    for ministry in ministries:
        print(f"  📤 {ministry.name}")
        if ministry.image and hasattr(ministry.image, 'path'):
            local_path = ministry.image.path
            if os.path.exists(local_path):
                print(f"    📸 Uploading image...")
                try:
                    with open(local_path, 'rb') as file:
                        from django.core.files.base import ContentFile
                        content = ContentFile(file.read(), name=os.path.basename(local_path))
                        ministry.image.save(os.path.basename(local_path), content, save=True)
                        print(f"      ✅ Uploaded: {ministry.image.url}")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"    ⚠️ Image file missing")
        else:
            print(f"    ❌ No image")
    
    # Process Sermon Thumbnails
    print("\n📖 Processing Sermon Thumbnails...")
    sermons = Sermon.objects.all()
    for sermon in sermons:
        print(f"  📤 {sermon.title}")
        if sermon.thumbnail and hasattr(sermon.thumbnail, 'path'):
            local_path = sermon.thumbnail.path
            if os.path.exists(local_path):
                print(f"    📸 Uploading thumbnail...")
                try:
                    with open(local_path, 'rb') as file:
                        from django.core.files.base import ContentFile
                        content = ContentFile(file.read(), name=os.path.basename(local_path))
                        sermon.thumbnail.save(os.path.basename(local_path), content, save=True)
                        print(f"      ✅ Uploaded: {sermon.thumbnail.url}")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"    ⚠️ Thumbnail file missing")
        else:
            print(f"    ❌ No thumbnail")
    
    # Process Hero Media
    print("\n🖼️ Processing Hero Media...")
    heroes = Hero.objects.all()
    for hero in heroes:
        print(f"  📤 {hero.title}")
        hero_media = hero.hero_media.all()
        for media in hero_media:
            if media.image and hasattr(media.image, 'path'):
                local_path = media.image.path
                if os.path.exists(local_path):
                    print(f"    📸 Uploading hero image...")
                    try:
                        with open(local_path, 'rb') as file:
                            from django.core.files.base import ContentFile
                            content = ContentFile(file.read(), name=os.path.basename(local_path))
                            media.image.save(os.path.basename(local_path), content, save=True)
                            print(f"      ✅ Uploaded: {media.image.url}")
                    except Exception as e:
                        print(f"      ❌ Error: {e}")
                else:
                    print(f"    ⚠️ Hero image file missing")
            else:
                print(f"    ❌ No hero image")
    
    # Process Event Speakers
    print("\n🎤 Processing Event Speakers...")
    speakers = EventSpeaker.objects.all()
    for speaker in speakers:
        print(f"  📤 {speaker.name}")
        if speaker.photo and hasattr(speaker.photo, 'path'):
            local_path = speaker.photo.path
            if os.path.exists(local_path):
                print(f"    📸 Uploading speaker photo...")
                try:
                    with open(local_path, 'rb') as file:
                        from django.core.files.base import ContentFile
                        content = ContentFile(file.read(), name=os.path.basename(local_path))
                        speaker.photo.save(os.path.basename(local_path), content, save=True)
                        print(f"      ✅ Uploaded: {speaker.photo.url}")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"    ⚠️ Speaker photo file missing")
        else:
            print(f"    ❌ No speaker photo")
    
    # Process Event Highlights
    print("\n🌟 Processing Event Highlights...")
    highlights = EventHighlight.objects.all()
    for highlight in highlights:
        print(f"  📤 {highlight.title}")
        if highlight.image and hasattr(highlight.image, 'path'):
            local_path = highlight.image.path
            if os.path.exists(local_path):
                print(f"    📸 Uploading highlight image...")
                try:
                    with open(local_path, 'rb') as file:
                        from django.core.files.base import ContentFile
                        content = ContentFile(file.read(), name=os.path.basename(local_path))
                        highlight.image.save(os.path.basename(local_path), content, save=True)
                        print(f"      ✅ Uploaded: {highlight.image.url}")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"    ⚠️ Highlight image file missing")
        else:
            print(f"    ❌ No highlight image")
    
    # Process About Pages
    print("\n📄 Processing About Pages...")
    about_pages = AboutPage.objects.all()
    for page in about_pages:
        print(f"  📤 {page.title}")
        if page.image and hasattr(page.image, 'path'):
            local_path = page.image.path
            if os.path.exists(local_path):
                print(f"    📸 Uploading about page image...")
                try:
                    with open(local_path, 'rb') as file:
                        from django.core.files.base import ContentFile
                        content = ContentFile(file.read(), name=os.path.basename(local_path))
                        page.image.save(os.path.basename(local_path), content, save=True)
                        print(f"      ✅ Uploaded: {page.image.url}")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"    ⚠️ About page image file missing")
        else:
            print(f"    ❌ No about page image")
    
    # Process Leadership Pages
    print("\n👥 Processing Leadership Pages...")
    leadership_pages = LeadershipPage.objects.all()
    for page in leadership_pages:
        print(f"  📤 {page.title}")
        if page.image and hasattr(page.image, 'path'):
            local_path = page.image.path
            if os.path.exists(local_path):
                print(f"    📸 Uploading leadership page image...")
                try:
                    with open(local_path, 'rb') as file:
                        from django.core.files.base import ContentFile
                        content = ContentFile(file.read(), name=os.path.basename(local_path))
                        page.image.save(os.path.basename(local_path), content, save=True)
                        print(f"      ✅ Uploaded: {page.image.url}")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"    ⚠️ Leadership page image file missing")
        else:
            print(f"    ❌ No leadership page image")
    
    print("\n" + "=" * 70)
    print("🎉 ImageKit upload completed!")
    print("\nNext steps:")
    print("1. Set your ImageKit credentials in Railway environment variables")
    print("2. Deploy to Railway")
    print("3. Check your live site")

if __name__ == "__main__":
    upload_media_to_imagekit() 