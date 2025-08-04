#!/usr/bin/env python
"""
Script to automatically fix hero deletion issues by changing global hero references
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import GlobalSettings, Hero, HeroMedia

def fix_hero_deletion(hero_id_to_delete):
    """Fix hero deletion by changing global hero reference"""
    print(f"🔧 Fixing Hero Deletion for ID: {hero_id_to_delete}")
    print("=" * 60)
    
    try:
        # Get the hero to be deleted
        hero_to_delete = Hero.objects.get(id=hero_id_to_delete)
        print(f"✅ Found Hero to Delete: {hero_to_delete.title}")
        print(f"   Status: {'✅ Active' if hero_to_delete.is_active else '❌ Inactive'}")
        print(f"   Church: {hero_to_delete.church.name if hero_to_delete.church else 'Global Hero'}")
    except Hero.DoesNotExist:
        print(f"❌ Hero with ID {hero_id_to_delete} not found")
        return False
    
    # Check if this hero is the global hero
    try:
        global_settings = GlobalSettings.get_settings()
        if global_settings.global_hero and global_settings.global_hero.id == hero_id_to_delete:
            print(f"\n🔗 This hero is currently the Global Hero")
            print(f"   Site: {global_settings.site_name}")
            
            # Find an alternative hero
            alternative_hero = Hero.objects.filter(
                is_active=True
            ).exclude(id=hero_id_to_delete).first()
            
            if alternative_hero:
                print(f"\n🔄 Changing Global Hero to: {alternative_hero.title}")
                print(f"   Alternative Hero ID: {alternative_hero.id}")
                
                # Update global settings
                global_settings.global_hero = alternative_hero
                global_settings.save()
                
                print(f"✅ Successfully changed global hero to: {alternative_hero.title}")
                print(f"   You can now delete the original hero")
                return True
            else:
                print(f"❌ No alternative heroes available")
                print(f"   You need to create another hero first")
                return False
        else:
            print(f"\n✅ This hero is not the global hero")
            print(f"   You should be able to delete it directly")
            return True
            
    except Exception as e:
        print(f"❌ Error checking/updating global settings: {e}")
        return False

def delete_hero_media(hero_id):
    """Delete hero media items for a specific hero"""
    print(f"\n📸 Deleting Hero Media for Hero ID: {hero_id}")
    print("=" * 60)
    
    try:
        hero = Hero.objects.get(id=hero_id)
        hero_media = HeroMedia.objects.filter(hero=hero)
        
        if hero_media.exists():
            print(f"Found {hero_media.count()} media items to delete:")
            for i, media in enumerate(hero_media, 1):
                print(f"   {i}. {media.image.name if media.image else 'No image'} / {media.video.name if media.video else 'No video'}")
            
            # Delete media items
            deleted_count = hero_media.delete()[0]
            print(f"✅ Deleted {deleted_count} media items")
            return True
        else:
            print("✅ No media items to delete")
            return True
            
    except Hero.DoesNotExist:
        print(f"❌ Hero with ID {hero_id} not found")
        return False
    except Exception as e:
        print(f"❌ Error deleting media: {e}")
        return False

def safe_delete_hero(hero_id):
    """Safely delete a hero by handling all references"""
    print(f"🗑️ Safe Delete Hero ID: {hero_id}")
    print("=" * 60)
    
    try:
        hero = Hero.objects.get(id=hero_id)
        print(f"Hero to delete: {hero.title}")
        
        # Step 1: Fix global hero reference if needed
        if not fix_hero_deletion(hero_id):
            print("❌ Cannot proceed with deletion - global hero reference issue")
            return False
        
        # Step 2: Delete hero media (optional - will be deleted automatically)
        # delete_hero_media(hero_id)
        
        # Step 3: Delete the hero
        print(f"\n🗑️ Deleting hero: {hero.title}")
        hero.delete()
        print(f"✅ Successfully deleted hero: {hero.title}")
        return True
        
    except Hero.DoesNotExist:
        print(f"❌ Hero with ID {hero_id} not found")
        return False
    except Exception as e:
        print(f"❌ Error deleting hero: {e}")
        return False

def list_all_heroes():
    """List all heroes for reference"""
    print(f"\n📋 All Heroes:")
    print("=" * 60)
    
    heroes = Hero.objects.all().order_by('title')
    if heroes.exists():
        for i, hero in enumerate(heroes, 1):
            print(f"   {i}. {hero.title} ({hero.id})")
            print(f"      Church: {hero.church.name if hero.church else 'Global'}")
            print(f"      Status: {'✅ Active' if hero.is_active else '❌ Inactive'}")
            print(f"      Media: {hero.hero_media.count()} items")
    else:
        print("   No heroes found")

if __name__ == "__main__":
    # The hero ID that's causing the deletion error
    hero_id = "51fd2e79-1b6b-43ba-ad98-c9b210403cfb"
    
    print("🔍 Hero Deletion Fix Tool")
    print("=" * 60)
    
    # List all heroes first
    list_all_heroes()
    
    # Try to safely delete the hero
    success = safe_delete_hero(hero_id)
    
    if success:
        print(f"\n🎉 Hero deletion completed successfully!")
        print(f"📝 You can now:")
        print(f"   1. Go to Django Admin: http://127.0.0.1:8000/admin/")
        print(f"   2. Navigate to Core > Heroes")
        print(f"   3. The hero should no longer be there")
    else:
        print(f"\n❌ Hero deletion failed")
        print(f"📝 Please check the error messages above") 