#!/usr/bin/env python
"""
Debug hero media issues on live site
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Hero, HeroMedia, Church
from django.conf import settings

def debug_hero_media():
    """Debug hero media issues"""
    print("🔍 Debugging Hero Media Issues...")
    print("=" * 60)
    
    # Check Cloudinary configuration
    print("📋 Cloudinary Configuration:")
    if hasattr(settings, 'CLOUDINARY_STORAGE'):
        print("✅ Cloudinary is configured")
        print(f"   Cloud Name: {settings.CLOUDINARY_STORAGE['CLOUD_NAME']}")
        print(f"   Storage: {settings.DEFAULT_FILE_STORAGE}")
    else:
        print("❌ Cloudinary is NOT configured")
        print(f"   Storage: {settings.DEFAULT_FILE_STORAGE}")
    
    # Check churches and their hero media
    churches = Church.objects.filter(is_active=True, is_approved=True)
    print(f"\n📋 Found {churches.count()} active churches:")
    
    for church in churches:
        print(f"\n🏛️  {church.name} (ID: {church.id}):")
        
        hero = Hero.objects.filter(church=church).first()
        if not hero:
            print("   ❌ No hero found")
            continue
            
        print(f"   ✅ Hero: {hero.title}")
        
        hero_media = hero.hero_media.all()
        if not hero_media.exists():
            print("   ❌ No hero media found")
            continue
            
        print(f"   📸 Found {hero_media.count()} hero media items:")
        
        for i, media in enumerate(hero_media, 1):
            print(f"      {i}. Media ID: {media.id}")
            
            if media.image:
                image_url = media.image.url
                print(f"         Image: {image_url}")
                if image_url.startswith('/media/'):
                    print(f"         ⚠️  Local URL - needs Cloudinary")
                elif 'cloudinary.com' in image_url:
                    print(f"         ✅ Cloudinary URL")
                else:
                    print(f"         ❓ Unknown URL format")
            else:
                print(f"         Image: None")
                
            if media.video:
                video_url = media.video.url
                print(f"         Video: {video_url}")
                if video_url.startswith('/media/'):
                    print(f"         ⚠️  Local URL - needs Cloudinary")
                elif 'cloudinary.com' in video_url:
                    print(f"         ✅ Cloudinary URL")
                else:
                    print(f"         ❓ Unknown URL format")
            else:
                print(f"         Video: None")
    
    print("\n" + "=" * 60)
    print("🔧 NEXT STEPS:")
    print("1. If you see 'Local URL - needs Cloudinary':")
    print("   - Go to Django admin: /admin/")
    print("   - Navigate to Core → Local heroes")
    print("   - Edit each church's hero")
    print("   - Delete existing media and re-upload")
    print("2. If you see 'Cloudinary URL':")
    print("   - The URLs are correct, check browser console for errors")
    print("3. If you see 'No hero media found':")
    print("   - Add hero media through the admin interface")

if __name__ == "__main__":
    debug_hero_media() 