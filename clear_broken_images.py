#!/usr/bin/env python3
"""
Clear broken Cloudinary images from the database
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import HeroMedia
import requests

def clear_broken_images():
    """Clear broken Cloudinary images"""
    
    print("🧹 Clearing broken Cloudinary images...")
    
    # Get all Hero Media with images
    hero_media = HeroMedia.objects.filter(image__isnull=False)
    print(f"Found {hero_media.count()} Hero Media entries with images")
    
    cleared_count = 0
    kept_count = 0
    
    for media in hero_media:
        image_url = str(media.image)
        
        if not image_url.startswith('http'):
            print(f"  ⏭️  Hero Media {media.id}: Not a Cloudinary URL, keeping")
            kept_count += 1
            continue
        
        # Test if the URL is accessible
        try:
            response = requests.head(image_url, timeout=10)
            if response.status_code == 200:
                print(f"  ✅ Hero Media {media.id}: URL is accessible, keeping")
                kept_count += 1
                continue
            else:
                print(f"  ❌ Hero Media {media.id}: URL not accessible ({response.status_code}), clearing")
                # Clear the broken image
                media.image = None
                media.save()
                cleared_count += 1
        except Exception as e:
            print(f"  ❌ Hero Media {media.id}: Error testing URL - {e}, clearing")
            # Clear the broken image
            media.image = None
            media.save()
            cleared_count += 1
    
    print("\n📊 Summary:")
    print(f"  Cleared: {cleared_count}")
    print(f"  Kept: {kept_count}")
    print(f"  Total: {cleared_count + kept_count}")
    
    if cleared_count > 0:
        print("\n💡 Next steps:")
        print("  1. Go to the admin interface")
        print("  2. Re-upload the images that were cleared")
        print("  3. The images should now work properly")

if __name__ == "__main__":
    clear_broken_images() 