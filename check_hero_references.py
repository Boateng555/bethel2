#!/usr/bin/env python
"""
Script to check hero references and help resolve deletion issues
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import GlobalSettings, Hero, HeroMedia

def check_hero_references(hero_id):
    """Check what's referencing a specific hero"""
    print(f"🔍 Checking References for Hero ID: {hero_id}")
    print("=" * 60)
    
    try:
        hero = Hero.objects.get(id=hero_id)
        print(f"✅ Found Hero: {hero.title}")
        print(f"   Status: {'✅ Active' if hero.is_active else '❌ Inactive'}")
        print(f"   Church: {hero.church.name if hero.church else 'Global Hero'}")
    except Hero.DoesNotExist:
        print(f"❌ Hero with ID {hero_id} not found")
        return
    
    # Check Global Settings references
    try:
        global_settings = GlobalSettings.get_settings()
        if global_settings.global_hero and global_settings.global_hero.id == hero_id:
            print(f"\n🔗 Global Settings Reference:")
            print(f"   ❌ This hero is currently set as the global hero")
            print(f"   Site: {global_settings.site_name}")
            print(f"   You must change the global hero before deleting this one")
        else:
            print(f"\n✅ No Global Settings reference")
    except Exception as e:
        print(f"\n⚠️ Could not check Global Settings: {e}")
    
    # Check Hero Media references
    hero_media = HeroMedia.objects.filter(hero=hero)
    if hero_media.exists():
        print(f"\n📸 Hero Media References:")
        print(f"   ❌ This hero has {hero_media.count()} media items")
        for i, media in enumerate(hero_media, 1):
            print(f"   {i}. {media.image.name if media.image else 'No image'} / {media.video.name if media.video else 'No video'}")
        print(f"   You should delete media items first or they will be deleted automatically")
    else:
        print(f"\n✅ No Hero Media references")
    
    # Check other potential references
    print(f"\n🔍 Other Potential References:")
    
    # Check if this hero is used by any church
    if hero.church:
        print(f"   Church: {hero.church.name}")
    
    # Check if this hero is featured globally
    if hero.is_global_featured:
        print(f"   Global Featured: ✅ Yes")
    
    print(f"\n💡 Solutions:")
    print(f"   1. If this is the global hero:")
    print(f"      - Go to Global Settings")
    print(f"      - Change the global hero to another hero")
    print(f"      - Then try deleting this hero")
    print(f"   2. If this hero has media:")
    print(f"      - Delete the media items first, or")
    print(f"      - They will be deleted automatically when you delete the hero")
    print(f"   3. Alternative: Deactivate instead of delete")
    print(f"      - Set is_active = False instead of deleting")

def list_available_heroes():
    """List all available heroes that could replace the global hero"""
    print(f"\n📋 Available Heroes for Global Settings:")
    print("=" * 60)
    
    heroes = Hero.objects.filter(is_active=True).order_by('title')
    if heroes.exists():
        for i, hero in enumerate(heroes, 1):
            print(f"   {i}. {hero.title} ({hero.id})")
            print(f"      Church: {hero.church.name if hero.church else 'Global'}")
            print(f"      Status: {'✅ Active' if hero.is_active else '❌ Inactive'}")
    else:
        print("   No active heroes found")

def fix_global_hero():
    """Help fix the global hero reference"""
    print(f"\n🔧 Fixing Global Hero Reference:")
    print("=" * 60)
    
    try:
        global_settings = GlobalSettings.get_settings()
        current_hero = global_settings.global_hero
        
        if current_hero:
            print(f"Current Global Hero: {current_hero.title} ({current_hero.id})")
            
            # Find another hero to use
            alternative_hero = Hero.objects.filter(is_active=True).exclude(id=current_hero.id).first()
            
            if alternative_hero:
                print(f"Suggested Alternative: {alternative_hero.title} ({alternative_hero.id})")
                print(f"\nTo fix this:")
                print(f"1. Go to Django Admin: http://127.0.0.1:8000/admin/")
                print(f"2. Navigate to Settings > Global Settings")
                print(f"3. Change the Global Hero to: {alternative_hero.title}")
                print(f"4. Save the settings")
                print(f"5. Then try deleting the original hero")
            else:
                print(f"❌ No alternative heroes available")
                print(f"   You need to create another hero first")
        else:
            print(f"✅ No global hero currently set")
            
    except Exception as e:
        print(f"❌ Error checking global settings: {e}")

if __name__ == "__main__":
    # Check the specific hero that's causing the error
    hero_id = "51fd2e79-1b6b-43ba-ad98-c9b210403cfb"
    check_hero_references(hero_id)
    list_available_heroes()
    fix_global_hero() 