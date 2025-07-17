#!/usr/bin/env python
"""
Script to properly upload hero media files to Cloudinary and update database
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

def fix_hero_media_cloudinary():
    """
    Upload hero media files to Cloudinary and update database correctly
    """
    print("🚀 Fixing Hero Media for Cloudinary...")
    print("=" * 70)
    
    # Configure Cloudinary with correct credentials
    cloudinary.config(
        cloud_name="dhzdusb5k",
        api_key="462763744132765",
        api_secret="s-FWNQuY_M40XwHKrskwIh0C-XI"
    )
    
    print("☁️ Cloudinary configured with Root API credentials")
    
    # Process Hero Media
    print("\n🌟 Processing Hero Media...")
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
                        # Upload to Cloudinary
                        result = cloudinary.uploader.upload(
                            local_path,
                            folder="bethel/heroes",
                            public_id=f"hero_{hero.id}_image_{media.id}"
                        )
                        
                        # Create a new file object with the Cloudinary URL
                        from django.core.files.base import ContentFile
                        import requests
                        
                        # Download the file from Cloudinary
                        response = requests.get(result['secure_url'])
                        if response.status_code == 200:
                            # Create a new file with the Cloudinary content
                            cloudinary_file = ContentFile(response.content, name=os.path.basename(local_path))
                            
                            # Update the media object
                            media.image.save(os.path.basename(local_path), cloudinary_file, save=True)
                            print(f"      ✅ Uploaded and updated: {result['secure_url']}")
                        else:
                            print(f"      ❌ Failed to download from Cloudinary")
                            
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
                        # Upload to Cloudinary
                        result = cloudinary.uploader.upload(
                            local_path,
                            folder="bethel/heroes",
                            resource_type="video",
                            public_id=f"hero_{hero.id}_video_{media.id}"
                        )
                        
                        # Create a new file object with the Cloudinary URL
                        from django.core.files.base import ContentFile
                        import requests
                        
                        # Download the file from Cloudinary
                        response = requests.get(result['secure_url'])
                        if response.status_code == 200:
                            # Create a new file with the Cloudinary content
                            cloudinary_file = ContentFile(response.content, name=os.path.basename(local_path))
                            
                            # Update the media object
                            media.video.save(os.path.basename(local_path), cloudinary_file, save=True)
                            print(f"      ✅ Uploaded and updated: {result['secure_url']}")
                        else:
                            print(f"      ❌ Failed to download from Cloudinary")
                            
                    except Exception as e:
                        print(f"      ❌ Error: {e}")
                else:
                    print(f"    ⚠️ Video file missing")
    
    print("\n" + "=" * 70)
    print("🎉 Hero Media Cloudinary fix completed!")
    print("\nNext steps:")
    print("1. Check your live site: https://web-production-158c.up.railway.app/")
    print("2. Hero images and videos should now be visible")
    print("3. If not, clear browser cache and refresh")

if __name__ == "__main__":
    fix_hero_media_cloudinary() 