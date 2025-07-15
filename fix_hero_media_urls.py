#!/usr/bin/env python
"""
Script to fix hero media URLs to use Cloudinary
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import HeroMedia
from django.conf import settings

def fix_hero_media_urls():
    """Fix hero media URLs to use Cloudinary"""
    print("🔧 Fixing Hero Media URLs for Cloudinary...")
    print("=" * 60)
    
    # Check if Cloudinary is configured
    if not hasattr(settings, 'CLOUDINARY_STORAGE'):
        print("❌ Cloudinary is not configured!")
        return
    
    hero_media_list = HeroMedia.objects.all()
    fixed_count = 0
    
    for media in hero_media_list:
        print(f"\n📋 Media {media.id}:")
        
        # Check image
        if media.image:
            old_image_url = media.image.url
            print(f"  Image: {old_image_url}")
            
            # If it's a local URL, we need to re-upload to Cloudinary
            if old_image_url.startswith('/media/'):
                print(f"    ⚠️  Local URL detected - needs re-upload to Cloudinary")
                print(f"    💡 You need to re-upload this image in the admin")
        
        # Check video
        if media.video:
            old_video_url = media.video.url
            print(f"  Video: {old_video_url}")
            
            # If it's a local URL, we need to re-upload to Cloudinary
            if old_video_url.startswith('/media/'):
                print(f"    ⚠️  Local URL detected - needs re-upload to Cloudinary")
                print(f"    💡 You need to re-upload this video in the admin")
    
    print("\n" + "=" * 60)
    print("🔧 SOLUTION:")
    print("Your hero media files exist but are using local URLs instead of Cloudinary URLs.")
    print("To fix this:")
    print("1. Go to Django admin: /admin/")
    print("2. Navigate to 'Core' → 'Local heroes'")
    print("3. Edit each church's hero")
    print("4. In the 'Hero Media' section:")
    print("   - Delete the existing media entries")
    print("   - Add new media entries with the same images/videos")
    print("   - This will upload them to Cloudinary with proper URLs")
    print("5. Save the changes")
    print("\nOR use the local admin interface:")
    print("1. Go to your church homepage")
    print("2. Click 'Local Admin' in the navigation")
    print("3. Go to 'Hero Content Management'")
    print("4. Edit the hero and re-upload the media files")

if __name__ == "__main__":
    fix_hero_media_urls() 