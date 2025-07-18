#!/usr/bin/env python3
"""
Verify if images are being uploaded correctly
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import HeroMedia, Hero
from django.conf import settings

def verify_uploads():
    """Verify recent uploads"""
    
    print("🔍 Verifying recent uploads...")
    print(f"Environment: {'Production' if not settings.DEBUG else 'Development'}")
    print()
    
    # Check all hero media
    hero_media = HeroMedia.objects.all().order_by('-id')
    print(f"Total Hero Media entries: {hero_media.count()}")
    print()
    
    print("📋 Recent Hero Media (last 10):")
    for media in hero_media[:10]:
        print(f"  ID: {media.id}")
        print(f"  Hero: {media.hero.title if media.hero else 'No hero'}")
        print(f"  Image field: {media.image}")
        if media.image:
            print(f"  Image URL: {media.get_image_url()}")
            print(f"  Is Cloudinary: {'res.cloudinary.com' in str(media.image)}")
            
            # Test if the URL is accessible
            try:
                import requests
                response = requests.head(str(media.image), timeout=5)
                print(f"  URL accessible: {response.status_code == 200}")
            except Exception as e:
                print(f"  URL test failed: {e}")
        else:
            print("  No image")
        print()
    
    # Check for any media without images
    empty_media = HeroMedia.objects.filter(image__isnull=True)
    if empty_media.exists():
        print(f"⚠️  Found {empty_media.count()} Hero Media entries without images:")
        for media in empty_media:
            print(f"  - ID: {media.id}, Hero: {media.hero.title if media.hero else 'No hero'}")
    else:
        print("✅ All Hero Media entries have images")

if __name__ == "__main__":
    verify_uploads() 