#!/usr/bin/env python
"""
Script to check Hero Media files and provide fix instructions
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Hero, HeroMedia, Church

def check_hero_media_files():
    """Check Hero Media files and provide fix instructions"""
    print("🔍 Checking Hero Media files...")
    print("=" * 60)
    
    churches = Church.objects.filter(is_active=True, is_approved=True)
    
    for church in churches:
        hero = Hero.objects.filter(church=church).first()
        if not hero:
            print(f"❌ {church.name} - NO HERO")
            continue
            
        hero_media = hero.hero_media.all()
        if not hero_media.exists():
            print(f"❌ {church.name} - NO HERO MEDIA")
            continue
            
        print(f"\n📋 {church.name}:")
        for media in hero_media:
            has_image = bool(media.image)
            has_video = bool(media.video)
            image_url = media.image.url if media.image else "None"
            video_url = media.video.url if media.video else "None"
            
            print(f"  Media {media.id}:")
            print(f"    Image: {'✅' if has_image else '❌'} {image_url}")
            print(f"    Video: {'✅' if has_video else '❌'} {video_url}")
            
            if not has_image and not has_video:
                print(f"    ⚠️  This media has no files uploaded!")
    
    print("\n" + "=" * 60)
    print("🔧 TO FIX THE MISSING IMAGES/VIDEOS:")
    print("1. Go to your Django admin: /admin/")
    print("2. Navigate to 'Core' → 'Local heroes'")
    print("3. Edit each church's hero")
    print("4. In the 'Hero Media' section, upload images/videos")
    print("5. Save the changes")
    print("\nOR use the local admin interface:")
    print("1. Go to your church homepage")
    print("2. Click 'Local Admin' in the navigation")
    print("3. Go to 'Hero Content Management'")
    print("4. Edit the hero and upload media files")

if __name__ == "__main__":
    check_hero_media_files() 