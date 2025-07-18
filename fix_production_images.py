#!/usr/bin/env python
"""
Script to fix image URLs in production database
Converts local file paths to cloud storage URLs
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import (
    Church, Ministry, News, Sermon, Hero, HeroMedia, 
    EventHighlight, EventSpeaker, AboutPage, LeadershipPage,
    LocalLeadershipPage, LocalAboutPage, EventHeroMedia
)

def fix_image_urls():
    """Fix all image URLs in the database"""
    print("🔧 Starting image URL fix...")
    
    # Get the base URL for cloud storage
    if hasattr(settings, 'IMAGEKIT_CONFIG') and all(settings.IMAGEKIT_CONFIG.values()):
        base_url = settings.IMAGEKIT_CONFIG['URL_ENDPOINT']
        print(f"📁 Using ImageKit: {base_url}")
    elif hasattr(settings, 'CLOUDINARY_STORAGE') and all(settings.CLOUDINARY_STORAGE.values()):
        cloud_name = settings.CLOUDINARY_STORAGE['CLOUD_NAME']
        base_url = f"https://res.cloudinary.com/{cloud_name}/image/upload"
        print(f"☁️ Using Cloudinary: {base_url}")
    else:
        print("❌ No cloud storage configured!")
        return
    
    # Models with image fields
    models_to_fix = [
        (Church, ['logo', 'banner_image']),
        (Ministry, ['image']),
        (News, ['image']),
        (Sermon, ['thumbnail']),
        (Hero, ['background_image']),
        (HeroMedia, ['image']),
        (EventHighlight, ['image']),
        (EventSpeaker, ['photo']),
        (AboutPage, ['logo', 'founder_image', 'extra_image']),
        (LeadershipPage, ['chairman_image', 'vice_chairman_image', 'board_image', 'team_image', 'leadership_photo_1', 'leadership_photo_2', 'leadership_photo_3']),
        (LocalLeadershipPage, ['pastor_image', 'assistant_pastor_image', 'board_image', 'team_image', 'leadership_photo_1', 'leadership_photo_2', 'leadership_photo_3']),
        (LocalAboutPage, ['logo', 'founder_image', 'extra_image', 'about_photo_1', 'about_photo_2', 'about_photo_3']),
        (EventHeroMedia, ['image']),
    ]
    
    total_fixed = 0
    
    for model_class, image_fields in models_to_fix:
        print(f"\n📋 Processing {model_class.__name__}...")
        
        for obj in model_class.objects.all():
            updated = False
            
            for field_name in image_fields:
                field = getattr(obj, field_name)
                if field and str(field):
                    field_str = str(field)
                    
                    # Skip if already a full URL
                    if field_str.startswith('http'):
                        continue
                    
                    # Skip if empty
                    if not field_str or field_str == 'None':
                        continue
                    
                    # Convert local path to cloud URL
                    if '/' in field_str:
                        # Remove any leading slashes and clean the path
                        clean_path = field_str.lstrip('/')
                        cloud_url = f"{base_url}/{clean_path}"
                        
                        # Update the field
                        setattr(obj, field_name, cloud_url)
                        updated = True
                        print(f"  ✅ {field_name}: {field_str} → {cloud_url}")
            
            if updated:
                obj.save()
                total_fixed += 1
    
    print(f"\n🎉 Fixed {total_fixed} objects with image URLs")
    print("✅ Image URL fix completed!")

if __name__ == '__main__':
    fix_image_urls() 