#!/usr/bin/env python
"""
Fix Existing Images Script
This script will fix all existing image URLs in the database to use ImageKit
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from django.core.files.base import ContentFile
from core.models import Church, HeroMedia, Event, Ministry, News, Sermon, EventHeroMedia
from imagekitio import ImageKit
from io import BytesIO
import re

def upload_file_to_imagekit(file_path, file_name):
    """Upload a file to ImageKit and return the URL"""
    try:
        # Initialize ImageKit
        imagekit = ImageKit(
            public_key=settings.IMAGEKIT_CONFIG['PUBLIC_KEY'],
            private_key=settings.IMAGEKIT_CONFIG['PRIVATE_KEY'],
            url_endpoint=settings.IMAGEKIT_CONFIG['URL_ENDPOINT']
        )
        
        # Read the file
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Create BytesIO object
        file_obj = BytesIO(file_content)
        file_obj.name = file_name
        
        # Upload to ImageKit
        upload = imagekit.upload_file(
            file=file_obj,
            file_name=file_name
        )
        
        return upload.url
        
    except Exception as e:
        print(f"❌ Failed to upload {file_name}: {e}")
        return None

def fix_model_images(model_class, field_names, media_root):
    """Fix images for a specific model"""
    print(f"\n🔧 Fixing {model_class.__name__} images...")
    
    fixed_count = 0
    error_count = 0
    
    for obj in model_class.objects.all():
        for field_name in field_names:
            if hasattr(obj, field_name):
                field = getattr(obj, field_name)
                if field and field.name:
                    # Check if it's already an ImageKit URL
                    if field.name.startswith('https://ik.imagekit.io/'):
                        print(f"✅ {model_class.__name__} {obj.id} {field_name}: Already ImageKit URL")
                        continue
                    
                    # Check if it's a local path that needs fixing
                    if '/' in field.name and not field.name.startswith('http'):
                        print(f"🔄 {model_class.__name__} {obj.id} {field_name}: {field.name}")
                        
                        # Construct full file path
                        file_path = os.path.join(media_root, field.name)
                        
                        if os.path.exists(file_path):
                            # Upload to ImageKit
                            imagekit_url = upload_file_to_imagekit(file_path, os.path.basename(field.name))
                            
                            if imagekit_url:
                                # Update the field with the new ImageKit URL
                                setattr(obj, field_name, imagekit_url)
                                obj.save()
                                print(f"✅ {model_class.__name__} {obj.id} {field_name}: Updated to {imagekit_url}")
                                fixed_count += 1
                            else:
                                print(f"❌ {model_class.__name__} {obj.id} {field_name}: Failed to upload")
                                error_count += 1
                        else:
                            print(f"⚠️ {model_class.__name__} {obj.id} {field_name}: File not found at {file_path}")
                            # Clear the field if file doesn't exist
                            setattr(obj, field_name, None)
                            obj.save()
                            error_count += 1
    
    return fixed_count, error_count

def main():
    """Main function to fix all existing images"""
    print("🚀 Starting to fix existing images...")
    print("=" * 60)
    
    # Get media root
    media_root = settings.MEDIA_ROOT
    print(f"Media root: {media_root}")
    
    # Define models and their image fields
    models_to_fix = [
        (Church, ['logo', 'nav_logo'], media_root),
        (HeroMedia, ['image', 'video'], media_root),
        (Ministry, ['image'], media_root),
        (News, ['image'], media_root),
        (Sermon, ['thumbnail', 'audio_file', 'video_file'], media_root),
        (EventHeroMedia, ['image', 'video'], media_root),
    ]
    
    total_fixed = 0
    total_errors = 0
    
    for model_class, field_names, media_root in models_to_fix:
        fixed, errors = fix_model_images(model_class, field_names, media_root)
        total_fixed += fixed
        total_errors += errors
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total images fixed: {total_fixed}")
    print(f"Total errors: {total_errors}")
    
    if total_fixed > 0:
        print(f"\n🎉 Successfully fixed {total_fixed} images!")
        print("All existing images should now use ImageKit URLs.")
    else:
        print("\n⚠️ No images were fixed. This might mean:")
        print("- All images are already using ImageKit URLs")
        print("- No local image files were found")
        print("- There were errors during the process")
    
    if total_errors > 0:
        print(f"\n❌ {total_errors} images had errors. Check the logs above.")
    
    print("\n📋 Next Steps:")
    print("1. Refresh your website to see the updated images")
    print("2. Check that images now load from ImageKit URLs")
    print("3. Verify in your ImageKit dashboard that files were uploaded")
    
    return total_fixed > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 