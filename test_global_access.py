#!/usr/bin/env python
"""
Test script to check global website access and hero display
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import GlobalSettings, Hero, Church

def test_global_access():
    """Test global website access and hero configuration"""
    print("🌐 Testing Global Website Access")
    print("=" * 50)
    
    # Check churches
    churches = Church.objects.filter(is_active=True, is_approved=True)
    print(f"Active Churches: {churches.count()}")
    
    if churches.count() == 1:
        print(f"⚠️  Only one church found: {churches.first().name}")
        print("   The site will redirect to this church automatically")
        print("   To see global site, visit: http://127.0.0.1:8000/?global")
    elif churches.count() > 1:
        print(f"⚠️  Multiple churches found: {churches.count()}")
        print("   The site will show church selection page")
        print("   To see global site, visit: http://127.0.0.1:8000/?global")
    else:
        print("✅ No churches found - global site will be shown by default")
        print("   Visit: http://127.0.0.1:8000/")
    
    # Check global hero
    try:
        global_settings = GlobalSettings.get_settings()
        if global_settings.global_hero:
            hero = global_settings.global_hero
            print(f"\n🌟 Global Hero Configuration:")
            print(f"   Title: {hero.title}")
            print(f"   Status: {'✅ Active' if hero.is_active else '❌ Inactive'}")
            print(f"   Background Type: {hero.background_type}")
            
            if hero.background_image:
                print(f"   Background Image: {hero.background_image}")
                print(f"   Image URL: {hero.get_background_image_url()}")
            
            hero_media_count = hero.hero_media.count()
            print(f"   Hero Media Items: {hero_media_count}")
            
            if hero_media_count > 0:
                print("   This hero will show a carousel/slider")
            else:
                print("   This hero will show single background image")
        else:
            print("\n❌ No global hero selected")
            print("   Go to Global Settings and select a global hero")
    except Exception as e:
        print(f"❌ Error checking global hero: {e}")
    
    print(f"\n📝 Access Instructions:")
    print("1. If you see a church site instead of global site:")
    print("   Visit: http://127.0.0.1:8000/?global")
    print("2. If you see a church selection page:")
    print("   Visit: http://127.0.0.1:8000/?global")
    print("3. If you see the global site but no images:")
    print("   - Clear browser cache (Ctrl+F5)")
    print("   - Check browser console for errors")
    print("   - Try incognito/private mode")

if __name__ == "__main__":
    test_global_access() 