#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import GlobalSettings, Hero

def debug_global_hero():
    print("=== Global Hero Debug ===")
    
    # Get global settings
    gs = GlobalSettings.get_settings()
    hero = gs.global_hero
    
    if not hero:
        print("❌ No global hero set")
        return
    
    print(f"✅ Global Hero: {hero.title}")
    print(f"✅ Is Active: {hero.is_active}")
    print(f"✅ Background Type: {hero.background_type}")
    print(f"✅ Background Video: {hero.background_video}")
    print(f"✅ Video URL: {hero.get_background_video_url()}")
    print(f"✅ Video exists: {hero.background_video.storage.exists(hero.background_video.name) if hero.background_video else False}")
    print(f"✅ Hero Media Count: {hero.hero_media.count()}")
    
    # Check template logic
    print("\n=== Template Logic ===")
    if hero.hero_media.all():
        print("🔴 Template will use hero_media carousel (not background video)")
        for i, media in enumerate(hero.hero_media.all()):
            print(f"  Media {i+1}: Image={bool(media.image)}, Video={bool(media.video)}")
    elif hero.background_type == 'video' and hero.background_video:
        print("✅ Template will use background video")
        print(f"  Video source: {hero.get_background_video_url()}")
    elif hero.background_type == 'image' and hero.background_image:
        print("🟡 Template will use background image")
        print(f"  Image source: {hero.get_background_image_url()}")
    else:
        print("🔴 Template will show gray fallback")
    
    # Test video file
    if hero.background_video:
        print(f"\n=== Video File Test ===")
        video_path = hero.background_video.path
        print(f"Video path: {video_path}")
        print(f"File exists: {os.path.exists(video_path)}")
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            print(f"File size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    debug_global_hero() 