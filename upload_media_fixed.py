#!/usr/bin/env python
"""
Working script to upload all local media to Cloudinary with correct API secrets
"""
import os
import cloudinary
import cloudinary.uploader
from pathlib import Path
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.files import File
from core.models import Church, Hero, HeroMedia, News, Ministry, Sermon

def upload_all_media():
    """
    Upload all local media files to Cloudinary with correct credentials
    """
    print("🚀 Starting media upload to Cloudinary with correct credentials...")
    print("=" * 70)
    
    # Configure Cloudinary with correct credentials
    cloudinary.config(
        cloud_name="dhzdusb5k",
        api_key="462763744132765",
        api_secret="s-FWNQuY_M40XwHKrskwIh0C-XI"  # Root API secret
    )
    
    print("☁️ Cloudinary configured with Root API credentials")
    
    # Upload Churches
    print("\n🏛️ Uploading Church Logos...")
    churches = Church.objects.all()
    for church in churches:
        if church.logo and hasattr(church.logo, 'path'):
            local_path = church.logo.path
            if os.path.exists(local_path):
                print(f"  📤 {church.name}: Uploading logo...")
                try:
                    # Upload to Cloudinary
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="bethel/churches",
                        public_id=f"church_{church.id}_logo"
                    )
                    
                    # Update database with Cloudinary URL
                    church.logo_url = result['secure_url']
                    church.save()
                    
                    print(f"    ✅ Uploaded: {result['secure_url']}")
                except Exception as e:
                    print(f"    ❌ Error: {e}")
            else:
                print(f"  ⚠️ {church.name}: Logo file missing")
    
    # Upload Heroes and Hero Media
    print("\n🌟 Uploading Hero Media...")
    heroes = Hero.objects.all()
    for hero in heroes:
        print(f"  📤 {hero.title}")
        hero_media = HeroMedia.objects.filter(hero=hero)
        
        for media in hero_media:
            # Handle images
            if media.image and hasattr(media.image, 'path'):
                local_path = media.image.path
                if os.path.exists(local_path):
                    print(f"    📸 Uploading image...")
                    try:
                        result = cloudinary.uploader.upload(
                            local_path,
                            folder="bethel/heroes",
                            public_id=f"hero_{hero.id}_image_{media.id}"
                        )
                        
                        # Update database
                        media.image_url = result['secure_url']
                        media.save()
                        
                        print(f"      ✅ Uploaded: {result['secure_url']}")
                    except Exception as e:
                        print(f"      ❌ Error: {e}")
                else:
                    print(f"    ⚠️ Image file missing")
            
            # Handle videos
            if media.video and hasattr(media.video, 'path'):
                local_path = media.video.path
                if os.path.exists(local_path):
                    print(f"    🎥 Uploading video...")
                    try:
                        result = cloudinary.uploader.upload(
                            local_path,
                            folder="bethel/heroes",
                            resource_type="video",
                            public_id=f"hero_{hero.id}_video_{media.id}"
                        )
                        
                        # Update database
                        media.video_url = result['secure_url']
                        media.save()
                        
                        print(f"      ✅ Uploaded: {result['secure_url']}")
                    except Exception as e:
                        print(f"      ❌ Error: {e}")
                else:
                    print(f"    ⚠️ Video file missing")
    
    # Upload News
    print("\n📰 Uploading News Images...")
    news_items = News.objects.all()
    for news in news_items:
        if news.image and hasattr(news.image, 'path'):
            local_path = news.image.path
            if os.path.exists(local_path):
                print(f"  📤 {news.title}: Uploading image...")
                try:
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="bethel/news",
                        public_id=f"news_{news.id}"
                    )
                    
                    # Update database
                    news.image_url = result['secure_url']
                    news.save()
                    
                    print(f"    ✅ Uploaded: {result['secure_url']}")
                except Exception as e:
                    print(f"    ❌ Error: {e}")
    
    # Upload Ministries
    print("\n⛪ Uploading Ministry Images...")
    ministries = Ministry.objects.all()
    for ministry in ministries:
        if ministry.image and hasattr(ministry.image, 'path'):
            local_path = ministry.image.path
            if os.path.exists(local_path):
                print(f"  📤 {ministry.name}: Uploading image...")
                try:
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="bethel/ministries",
                        public_id=f"ministry_{ministry.id}"
                    )
                    
                    # Update database
                    ministry.image_url = result['secure_url']
                    ministry.save()
                    
                    print(f"    ✅ Uploaded: {result['secure_url']}")
                except Exception as e:
                    print(f"    ❌ Error: {e}")
    
    # Upload Sermons
    print("\n📖 Uploading Sermon Media...")
    sermons = Sermon.objects.all()
    for sermon in sermons:
        if sermon.thumbnail and hasattr(sermon.thumbnail, 'path'):
            local_path = sermon.thumbnail.path
            if os.path.exists(local_path):
                print(f"  📤 {sermon.title}: Uploading thumbnail...")
                try:
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="bethel/sermons",
                        public_id=f"sermon_{sermon.id}_thumb"
                    )
                    
                    # Update database
                    sermon.thumbnail_url = result['secure_url']
                    sermon.save()
                    
                    print(f"    ✅ Uploaded: {result['secure_url']}")
                except Exception as e:
                    print(f"    ❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("🎉 All media upload completed!")
    print("\nNext steps:")
    print("1. Check your live site: https://web-production-158c.up.railway.app/")
    print("2. Images and videos should now be visible")
    print("3. If not, clear browser cache and refresh")
    print("4. The media is now stored on Cloudinary and will work on the live site!")

if __name__ == "__main__":
    upload_all_media() 