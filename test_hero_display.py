#!/usr/bin/env python
"""
Test script to verify hero display configuration
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import GlobalSettings, Hero

def test_hero_display():
    """Test hero display configuration"""
    print("🎨 Testing Hero Display Configuration")
    print("=" * 50)
    
    # Get global settings
    try:
        settings = GlobalSettings.get_settings()
        print(f"✅ Global Settings: {settings.site_name}")
    except Exception as e:
        print(f"❌ Error getting global settings: {e}")
        return
    
    # Check global hero
    if not settings.global_hero:
        print("❌ No global hero selected")
        return
    
    hero = settings.global_hero
    print(f"\n🌟 Global Hero: {hero.title}")
    print(f"   Status: {'✅ Active' if hero.is_active else '❌ Inactive'}")
    print(f"   Background Type: {hero.background_type}")
    
    # Check background configuration
    if hero.background_type == 'image':
        if hero.background_image:
            print(f"   ✅ Background Image: {hero.background_image.name}")
            print(f"   Image URL: {hero.get_background_image_url()}")
        else:
            print("   ❌ Background type is 'image' but no image uploaded")
    elif hero.background_type == 'video':
        if hero.background_video:
            print(f"   ✅ Background Video: {hero.background_video.name}")
        else:
            print("   ❌ Background type is 'video' but no video uploaded")
    else:
        print(f"   ⚠️ Unknown background type: {hero.background_type}")
    
    # Check hero media
    hero_media = hero.hero_media.all()
    if hero_media.exists():
        print(f"\n📸 Hero Media: {hero_media.count()} items")
        for i, media in enumerate(hero_media, 1):
            print(f"   {i}. Order: {media.order}")
            if media.image:
                print(f"      Image: {media.image.name}")
            if media.video:
                print(f"      Video: {media.video.name}")
    else:
        print("\n📸 Hero Media: No media items")
    
    # Template logic check
    print(f"\n🔍 Template Logic Check:")
    print(f"   Hero has media: {hero_media.exists()}")
    print(f"   Background type == 'image': {hero.background_type == 'image'}")
    print(f"   Background image exists: {bool(hero.background_image)}")
    print(f"   Background type == 'video': {hero.background_type == 'video'}")
    print(f"   Background video exists: {bool(hero.background_video)}")
    
    # Determine what should display
    if hero_media.exists():
        print(f"\n🎯 Expected Display: Hero Media Carousel ({hero_media.count()} items)")
    elif hero.background_type == 'video' and hero.background_video:
        print(f"\n🎯 Expected Display: Background Video")
    elif hero.background_type == 'image' and hero.background_image:
        print(f"\n🎯 Expected Display: Background Image")
    else:
        print(f"\n🎯 Expected Display: Gray Fallback Background")
    
    print(f"\n✅ Test completed!")
    print(f"📝 Next steps:")
    print(f"   1. Refresh your browser (Ctrl+F5)")
    print(f"   2. Visit: http://127.0.0.1:8000/?global")
    print(f"   3. You should now see the background image!")

if __name__ == "__main__":
    test_hero_display() 