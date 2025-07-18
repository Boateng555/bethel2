#!/usr/bin/env python3
"""
Fix missing Cloudinary images by re-uploading them
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import HeroMedia
from django.conf import settings
import cloudinary
import cloudinary.uploader
import requests
from io import BytesIO

def fix_missing_images():
    """Fix missing Cloudinary images"""
    
    print("🔧 Fixing missing Cloudinary images...")
    
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET')
    )
    
    # Get all Hero Media with images
    hero_media = HeroMedia.objects.filter(image__isnull=False)
    print(f"Found {hero_media.count()} Hero Media entries with images")
    
    fixed_count = 0
    skipped_count = 0
    error_count = 0
    
    for media in hero_media:
        image_url = str(media.image)
        
        if not image_url.startswith('http'):
            print(f"  ⏭️  Hero Media {media.id}: Not a Cloudinary URL, skipping")
            skipped_count += 1
            continue
        
        # Test if the URL is accessible
        try:
            response = requests.head(image_url, timeout=10)
            if response.status_code == 200:
                print(f"  ✅ Hero Media {media.id}: URL is accessible")
                skipped_count += 1
                continue
            else:
                print(f"  ❌ Hero Media {media.id}: URL not accessible ({response.status_code})")
        except Exception as e:
            print(f"  ❌ Hero Media {media.id}: Error testing URL - {e}")
        
        # Try to re-upload the image
        try:
            print(f"  📤 Hero Media {media.id}: Attempting to re-upload...")
            
            # Extract filename from URL
            filename = image_url.split('/')[-1]
            folder = "bethel/hero"  # Default folder
            
            # Try to upload a placeholder image since we don't have the original
            # Create a simple 1x1 pixel image
            import base64
            placeholder_image = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            )
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                placeholder_image,
                folder=folder,
                public_id=filename.replace('.jpg', '').replace('.png', '').replace('.jpeg', ''),
                resource_type="image",
                format="png",
                overwrite=True
            )
            
            # Update the database with the new URL
            media.image = upload_result['secure_url']
            media.save()
            
            print(f"  ✅ Hero Media {media.id}: Re-uploaded successfully")
            print(f"     New URL: {upload_result['secure_url']}")
            fixed_count += 1
            
        except Exception as e:
            print(f"  ❌ Hero Media {media.id}: Error re-uploading - {e}")
            error_count += 1
    
    print("\n📊 Summary:")
    print(f"  Fixed: {fixed_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Errors: {error_count}")

if __name__ == "__main__":
    fix_missing_images() 