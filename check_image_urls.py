#!/usr/bin/env python
"""
Check Image URLs Script
This script will check all image URLs in the database to see which ones need fixing
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from core.models import Church, HeroMedia, Event, Ministry, News, Sermon, EventHeroMedia

def check_model_images(model_class, field_names):
    """Check images for a specific model"""
    print(f"\n🔍 Checking {model_class.__name__} images...")
    
    imagekit_count = 0
    local_count = 0
    empty_count = 0
    
    for obj in model_class.objects.all():
        for field_name in field_names:
            if hasattr(obj, field_name):
                field = getattr(obj, field_name)
                if field and field.name:
                    if field.name.startswith('https://ik.imagekit.io/'):
                        print(f"✅ {model_class.__name__} {obj.id} {field_name}: ImageKit URL")
                        imagekit_count += 1
                    elif field.name.startswith('http'):
                        print(f"🌐 {model_class.__name__} {obj.id} {field_name}: External URL")
                    else:
                        print(f"📁 {model_class.__name__} {obj.id} {field_name}: Local path - {field.name}")
                        local_count += 1
                else:
                    empty_count += 1
    
    return imagekit_count, local_count, empty_count

def main():
    """Main function to check all image URLs"""
    print("🔍 Checking all image URLs in database...")
    print("=" * 60)
    
    # Define models and their image fields
    models_to_check = [
        (Church, ['logo', 'nav_logo']),
        (HeroMedia, ['image', 'video']),
        (Ministry, ['image']),
        (News, ['image']),
        (Sermon, ['thumbnail', 'audio_file', 'video_file']),
        (EventHeroMedia, ['image', 'video']),
    ]
    
    total_imagekit = 0
    total_local = 0
    total_empty = 0
    
    for model_class, field_names in models_to_check:
        imagekit, local, empty = check_model_images(model_class, field_names)
        total_imagekit += imagekit
        total_local += local
        total_empty += empty
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"ImageKit URLs: {total_imagekit}")
    print(f"Local paths: {total_local}")
    print(f"Empty fields: {total_empty}")
    
    if total_local > 0:
        print(f"\n⚠️ Found {total_local} images with local paths that need fixing!")
        print("Run fix_existing_images.py to upload them to ImageKit.")
    else:
        print(f"\n✅ All images are already using ImageKit URLs!")
    
    return total_local

if __name__ == "__main__":
    local_count = main()
    sys.exit(0 if local_count == 0 else 1) 