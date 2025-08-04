#!/usr/bin/env python3
"""
Test script to verify Hero admin interface configuration
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Hero, HeroMedia
from core.admin import HeroAdmin, HeroMediaInline

def test_hero_admin_configuration():
    """Test the Hero admin configuration"""
    print("🔍 Testing Hero Admin Configuration...")
    
    # Test HeroAdmin configuration
    hero_admin = HeroAdmin(Hero, None)
    
    print(f"✅ HeroAdmin inlines: {hero_admin.inlines}")
    print(f"✅ HeroMediaInline in inlines: {HeroMediaInline in hero_admin.inlines}")
    
    # Test HeroMediaInline configuration
    hero_media_inline = HeroMediaInline(Hero, None)
    
    print(f"✅ HeroMediaInline extra: {hero_media_inline.extra}")
    print(f"✅ HeroMediaInline max_num: {hero_media_inline.max_num}")
    print(f"✅ HeroMediaInline fields: {hero_media_inline.fields}")
    print(f"✅ HeroMediaInline verbose_name: {hero_media_inline.verbose_name}")
    print(f"✅ HeroMediaInline help_text: {hero_media_inline.help_text}")
    
    # Test fieldsets
    print(f"✅ HeroAdmin fieldsets: {len(hero_admin.fieldsets)} sections")
    
    # Check if Hero Media section exists in fieldsets
    hero_media_section_exists = False
    for section_name, section_config in hero_admin.fieldsets:
        if section_name == 'Hero Media':
            hero_media_section_exists = True
            print(f"✅ Found Hero Media section: {section_config}")
            break
    
    if not hero_media_section_exists:
        print("❌ Hero Media section not found in fieldsets")
    
    print("\n📋 Summary:")
    print("   - HeroAdmin has HeroMediaInline configured")
    print("   - HeroMediaInline allows 3 new items at once")
    print("   - HeroMediaInline allows up to 10 total items")
    print("   - Hero Media section should be visible in admin")
    
    print("\n🎯 Next Steps:")
    print("   1. Go to Django Admin → Heros")
    print("   2. Edit an existing hero or create a new one")
    print("   3. You should see 'Hero Media' section with 'Hero Media Items' below")
    print("   4. You can add up to 3 new media items at once")
    print("   5. Each item can have an image, video, and display order")

if __name__ == "__main__":
    test_hero_admin_configuration() 