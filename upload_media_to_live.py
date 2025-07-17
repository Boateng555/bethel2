#!/usr/bin/env python
"""
Simple script to upload local media files to the live site
This script will help you get your local images and videos onto the live site
"""
import os
import requests
from pathlib import Path
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.files import File
from core.models import Church, Hero, HeroMedia, News, Ministry, Sermon

def upload_media_to_live():
    """
    Upload local media files to the live site
    """
    print("🚀 Starting media upload to live site...")
    print("=" * 60)
    
    # Check if we're in production mode
    from django.conf import settings
    if settings.DEBUG:
        print("⚠️  WARNING: You're in DEBUG mode (local development)")
        print("   This script will upload to your local database.")
        print("   To upload to the live site, you need to:")
        print("   1. Set DEBUG=False in your environment")
        print("   2. Have Cloudinary credentials configured")
        print("   3. Run this on the production server")
        print()
        
        response = input("Do you want to continue with local upload? (y/n): ")
        if response.lower() != 'y':
            print("❌ Upload cancelled")
            return
    
    # Upload Churches
    print("\n📁 Uploading Church Logos...")
    churches = Church.objects.all()
    for church in churches:
        if church.logo and hasattr(church.logo, 'path'):
            local_path = church.logo.path
            if os.path.exists(local_path):
                print(f"  🏛️  {church.name}: Uploading logo...")
                try:
                    # Re-save to trigger upload
                    church.logo.save(
                        os.path.basename(local_path),
                        File(open(local_path, 'rb')),
                        save=True
                    )
                    print(f"    ✅ Successfully uploaded: {os.path.basename(local_path)}")
                except Exception as e:
                    print(f"    ❌ Error uploading: {e}")
            else:
                print(f"  ⚠️  {church.name}: Logo file missing")
    
    # Upload Heroes and Hero Media
    print("\n🎬 Uploading Hero Media...")
    heroes = Hero.objects.all()
    for hero in heroes:
        print(f"  🌟 {hero.title}")
        hero_media = HeroMedia.objects.filter(hero=hero)
        
        for media in hero_media:
            # Handle images
            if media.image and hasattr(media.image, 'path'):
                local_path = media.image.path
                if os.path.exists(local_path):
                    print(f"    📸 Uploading image: {os.path.basename(local_path)}")
                    try:
                        media.image.save(
                            os.path.basename(local_path),
                            File(open(local_path, 'rb')),
                            save=True
                        )
                        print(f"      ✅ Successfully uploaded")
                    except Exception as e:
                        print(f"      ❌ Error: {e}")
                else:
                    print(f"    ⚠️  Image file missing: {local_path}")
            
            # Handle videos
            if media.video and hasattr(media.video, 'path'):
                local_path = media.video.path
                if os.path.exists(local_path):
                    print(f"    🎥 Uploading video: {os.path.basename(local_path)}")
                    try:
                        media.video.save(
                            os.path.basename(local_path),
                            File(open(local_path, 'rb')),
                            save=True
                        )
                        print(f"      ✅ Successfully uploaded")
                    except Exception as e:
                        print(f"      ❌ Error: {e}")
                else:
                    print(f"    ⚠️  Video file missing: {local_path}")
    
    # Upload News
    print("\n📰 Uploading News Images...")
    news_items = News.objects.all()
    for news in news_items:
        if news.image and hasattr(news.image, 'path'):
            local_path = news.image.path
            if os.path.exists(local_path):
                print(f"  📰 {news.title}: Uploading image...")
                try:
                    news.image.save(
                        os.path.basename(local_path),
                        File(open(local_path, 'rb')),
                        save=True
                    )
                    print(f"    ✅ Successfully uploaded")
                except Exception as e:
                    print(f"    ❌ Error: {e}")
    
    # Upload Ministries
    print("\n⛪ Uploading Ministry Images...")
    ministries = Ministry.objects.all()
    for ministry in ministries:
        if ministry.image and hasattr(ministry.image, 'path'):
            local_path = ministry.image.path
            if os.path.exists(local_path):
                print(f"  ⛪ {ministry.name}: Uploading image...")
                try:
                    ministry.image.save(
                        os.path.basename(local_path),
                        File(open(local_path, 'rb')),
                        save=True
                    )
                    print(f"    ✅ Successfully uploaded")
                except Exception as e:
                    print(f"    ❌ Error: {e}")
    
    # Upload Sermons
    print("\n📖 Uploading Sermon Media...")
    sermons = Sermon.objects.all()
    for sermon in sermons:
        if sermon.thumbnail and hasattr(sermon.thumbnail, 'path'):
            local_path = sermon.thumbnail.path
            if os.path.exists(local_path):
                print(f"  📖 {sermon.title}: Uploading thumbnail...")
                try:
                    sermon.thumbnail.save(
                        os.path.basename(local_path),
                        File(open(local_path, 'rb')),
                        save=True
                    )
                    print(f"    ✅ Successfully uploaded")
                except Exception as e:
                    print(f"    ❌ Error: {e}")
        
        if sermon.video and hasattr(sermon.video, 'path'):
            local_path = sermon.video.path
            if os.path.exists(local_path):
                print(f"  📖 {sermon.title}: Uploading video...")
                try:
                    sermon.video.save(
                        os.path.basename(local_path),
                        File(open(local_path, 'rb')),
                        save=True
                    )
                    print(f"    ✅ Successfully uploaded")
                except Exception as e:
                    print(f"    ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Media upload completed!")
    print("\nNext steps:")
    print("1. If you're in DEBUG mode, your media is now in your local database")
    print("2. To get it on the live site, you need to:")
    print("   - Set DEBUG=False in your environment")
    print("   - Have Cloudinary credentials configured")
    print("   - Run this script on the production server")
    print("3. Or manually upload via the live site admin")
    print("   - Go to: https://web-production-158c.up.railway.app/admin/")

if __name__ == "__main__":
    upload_media_to_live() 