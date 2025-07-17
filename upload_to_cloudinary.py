#!/usr/bin/env python
"""
Upload all media files to Cloudinary and update database URLs
"""
import os
import sys
import django
import cloudinary
import cloudinary.uploader
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import (
    Church, Ministry, News, Sermon, HeroMedia, EventHighlight, 
    EventSpeaker, Hero, AboutPage, LeadershipPage
)

def upload_to_cloudinary(file_path, folder_name="bethel"):
    """Upload a file to Cloudinary"""
    try:
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
            api_key=os.environ.get('CLOUDINARY_API_KEY'),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET')
        )
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file_path,
            folder=folder_name,
            resource_type="auto"
        )
        
        return result.get('secure_url')
        
    except Exception as e:
        print(f"❌ Error uploading to Cloudinary: {e}")
        return None

def update_database_with_cloudinary_urls():
    """Update all media URLs in the database to use Cloudinary URLs"""
    
    # Check Cloudinary credentials
    required_vars = ['CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your Railway environment.")
        return
    
    print("✅ Cloudinary credentials found")
    
    # Define models and their media fields
    models_to_update = [
        (Church, 'logo', 'churches/logos'),
        (Ministry, 'image', 'ministries'),
        (News, 'image', 'news'),
        (Sermon, 'thumbnail', 'sermons/thumbnails'),
        (HeroMedia, 'image', 'hero'),
        (EventHighlight, 'image', 'event_highlights'),
        (EventSpeaker, 'photo', 'events/speakers'),
        (Hero, 'background_image', 'hero'),
        (AboutPage, 'logo', 'about'),
        (AboutPage, 'founder_image', 'about'),
        (AboutPage, 'extra_image', 'about'),
        (LeadershipPage, 'chairman_image', 'leadership'),
        (LeadershipPage, 'vice_chairman_image', 'leadership'),
        (LeadershipPage, 'board_image', 'leadership'),
        (LeadershipPage, 'team_image', 'leadership'),
        (LeadershipPage, 'leadership_photo_1', 'leadership'),
        (LeadershipPage, 'leadership_photo_2', 'leadership'),
        (LeadershipPage, 'leadership_photo_3', 'leadership'),
    ]
    
    total_uploaded = 0
    total_failed = 0
    
    for model, field_name, folder_name in models_to_update:
        print(f"\n📝 Processing {model.__name__} {field_name}...")
        
        for instance in model.objects.all():
            field = getattr(instance, field_name)
            if not field or not hasattr(field, 'name') or not field.name:
                continue
            
            # Check if already a Cloudinary URL
            if 'res.cloudinary.com' in str(field):
                print(f"  ⏭️  {model.__name__} {instance.id}: Already Cloudinary URL")
                continue
            
            # Get local file path
            local_path = field.path if hasattr(field, 'path') else None
            if not local_path or not os.path.exists(local_path):
                print(f"  ⚠️  {model.__name__} {instance.id}: File not found - {field}")
                continue
            
            # Upload to Cloudinary
            cloudinary_url = upload_to_cloudinary(local_path, folder_name)
            if cloudinary_url:
                # Update the field
                setattr(instance, field_name, cloudinary_url)
                instance.save()
                print(f"  ✅ {model.__name__} {instance.id}: {cloudinary_url}")
                total_uploaded += 1
            else:
                print(f"  ❌ {model.__name__} {instance.id}: Upload failed")
                total_failed += 1
    
    print("\n" + "="*50)
    print(f"🎉 Upload completed!")
    print(f"✅ Successfully uploaded: {total_uploaded}")
    print(f"❌ Failed uploads: {total_failed}")

def main():
    print("🚀 Starting Cloudinary media upload...")
    print("=" * 50)
    
    update_database_with_cloudinary_urls()

if __name__ == '__main__':
    main() 