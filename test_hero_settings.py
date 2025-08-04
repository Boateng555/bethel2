#!/usr/bin/env python
"""
Test script to verify Global Hero Settings functionality
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import GlobalSettings, Hero, Church

def test_hero_settings():
    """Test the hero settings functionality"""
    print("🔍 Testing Global Hero Settings...")
    
    # Get or create global settings
    try:
        settings = GlobalSettings.get_settings()
        print(f"✅ Global Settings found: {settings.site_name}")
    except Exception as e:
        print(f"❌ Error getting global settings: {e}")
        return
    
    # Check if hero fields exist
    print("\n📋 Checking hero fields:")
    hero_fields = [
        'global_hero',
        'global_hero_rotation_enabled', 
        'global_hero_rotation_interval',
        'global_hero_fallback_enabled'
    ]
    
    for field in hero_fields:
        if hasattr(settings, field):
            value = getattr(settings, field)
            print(f"  ✅ {field}: {value}")
        else:
            print(f"  ❌ {field}: Field not found")
    
    # Check for available global heroes
    print("\n🎯 Checking for global heroes:")
    global_heroes = Hero.objects.filter(church__isnull=True)
    print(f"  Found {global_heroes.count()} global heroes:")
    
    for hero in global_heroes:
        status = "✅ Active" if hero.is_active else "❌ Inactive"
        print(f"    - {hero.title} ({status})")
    
    if global_heroes.count() == 0:
        print("  ⚠️  No global heroes found. Create some heroes without church association.")
    
    # Check current global hero
    if settings.global_hero:
        print(f"\n🌟 Current Global Hero: {settings.global_hero.title}")
        print(f"   Status: {'✅ Active' if settings.global_hero.is_active else '❌ Inactive'}")
        print(f"   Background: {settings.global_hero.background_type}")
    else:
        print("\n⚠️  No global hero currently selected")
    
    # Check rotation settings
    print(f"\n⚙️  Hero Rotation Settings:")
    print(f"   Rotation Enabled: {'✅ Yes' if settings.global_hero_rotation_enabled else '❌ No'}")
    print(f"   Rotation Interval: {settings.global_hero_rotation_interval} seconds")
    print(f"   Fallback Enabled: {'✅ Yes' if settings.global_hero_fallback_enabled else '❌ No'}")

def create_sample_global_hero():
    """Create a sample global hero for testing"""
    print("\n🎨 Creating sample global hero...")
    
    # Check if sample hero already exists
    existing_hero = Hero.objects.filter(title="Sample Global Hero", church__isnull=True).first()
    if existing_hero:
        print("  ✅ Sample global hero already exists")
        return existing_hero
    
    # Create new sample hero
    hero = Hero.objects.create(
        title="Sample Global Hero",
        subtitle="This is a sample global hero for testing the hero settings functionality",
        background_type='image',
        primary_button_text="Learn More",
        primary_button_link="/about",
        secondary_button_text="Contact Us", 
        secondary_button_link="/contact",
        is_active=True,
        order=1
    )
    
    print(f"  ✅ Created sample global hero: {hero.title}")
    return hero

if __name__ == "__main__":
    print("🚀 Global Hero Settings Test")
    print("=" * 40)
    
    test_hero_settings()
    
    # Ask if user wants to create sample hero
    print("\n" + "=" * 40)
    response = input("Create a sample global hero for testing? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        create_sample_global_hero()
        print("\n🔄 Re-running tests with new hero...")
        test_hero_settings()
    
    print("\n✅ Test completed!")
    print("\n📝 Next steps:")
    print("1. Go to Django Admin: http://127.0.0.1:8000/admin/")
    print("2. Navigate to Settings > Global Settings")
    print("3. Look for the 'Global Hero Settings' section")
    print("4. Select a global hero and configure settings")
    print("5. Save and test on the main site") 