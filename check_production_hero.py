#!/usr/bin/env python3
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/home/testsite.local')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Setup Django
django.setup()

from core.models import GlobalSettings, Hero, HeroMedia

def check_global_hero():
    print("🔍 Checking Global Hero Media...")
    print("=" * 50)
    
    try:
        # Get global settings
        global_settings = GlobalSettings.objects.first()
        if not global_settings:
            print("❌ No GlobalSettings found!")
            return
        
        print(f"✅ GlobalSettings found: {global_settings}")
        
        # Check global hero
        global_hero = global_settings.global_hero
        if not global_hero:
            print("❌ No global hero set in GlobalSettings!")
            return
        
        print(f"✅ Global hero: {global_hero}")
        print(f"   - Title: {global_hero.title}")
        print(f"   - Background video: {global_hero.background_video}")
        
        # Check hero media
        hero_media = global_hero.hero_media.all()
        print(f"✅ Hero media count: {hero_media.count()}")
        
        for i, media in enumerate(hero_media, 1):
            print(f"\n📁 Media {i}:")
            print(f"   - ID: {media.id}")
            print(f"   - Image: {media.image}")
            print(f"   - Video: {media.video}")
            print(f"   - Order: {media.order}")
            
            # Check if files exist
            if media.image:
                image_path = media.image.path
                print(f"   - Image path: {image_path}")
                print(f"   - Image exists: {os.path.exists(image_path)}")
            
            if media.video:
                video_path = media.video.path
                print(f"   - Video path: {video_path}")
                print(f"   - Video exists: {os.path.exists(video_path)}")
        
        # Check background video
        if global_hero.background_video:
            bg_video_path = global_hero.background_video.path
            print(f"\n🎥 Background video:")
            print(f"   - Path: {bg_video_path}")
            print(f"   - Exists: {os.path.exists(bg_video_path)}")
        
        print("\n" + "=" * 50)
        print("✅ Diagnosis complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_global_hero() 