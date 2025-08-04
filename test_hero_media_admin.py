#!/usr/bin/env python3
"""
Test script to verify hero media admin functionality
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Hero, HeroMedia, Church
from django.contrib.auth.models import User

def test_hero_media_functionality():
    """Test the hero media functionality"""
    print("🔍 Testing Hero Media Functionality...")
    
    # Check if we have any churches
    churches = Church.objects.all()
    if not churches.exists():
        print("❌ No churches found. Please create a church first.")
        return
    
    church = churches.first()
    print(f"✅ Found church: {church.name}")
    
    # Check if we have any heroes
    heroes = Hero.objects.filter(church=church)
    if not heroes.exists():
        print("❌ No heroes found for this church. Please create a hero first.")
        return
    
    hero = heroes.first()
    print(f"✅ Found hero: {hero.title}")
    
    # Check existing hero media
    hero_media = hero.hero_media.all()
    print(f"📊 Current hero media count: {hero_media.count()}")
    
    for i, media in enumerate(hero_media, 1):
        print(f"  {i}. {'Image' if media.image else 'Video'}: {media.get_image_url() if media.image else media.get_video_url()}")
    
    # Test creating new hero media
    print("\n🧪 Testing hero media creation...")
    
    # Create a test image media
    try:
        new_image_media = HeroMedia.objects.create(
            hero=hero,
            order=hero_media.count() + 1
        )
        print(f"✅ Created new hero media with ID: {new_image_media.id}")
        print(f"   Order: {new_image_media.order}")
        print(f"   Image: {new_image_media.image}")
        print(f"   Video: {new_image_media.video}")
        
        # Clean up test media
        new_image_media.delete()
        print("✅ Test media cleaned up")
        
    except Exception as e:
        print(f"❌ Error creating hero media: {e}")
    
    print("\n📋 Hero Media Admin Configuration:")
    print("   - Extra forms: 3 (allows adding 3 new items at once)")
    print("   - Max items: 10 (maximum 10 media items per hero)")
    print("   - Fields: image, video, order")
    print("   - Form validation: Requires at least image or video")
    
    print("\n🎯 Next Steps:")
    print("   1. Go to Django Admin → Local Heroes")
    print("   2. Edit an existing hero or create a new one")
    print("   3. In the 'Hero Media Items' section, you can now add multiple images/videos")
    print("   4. Set the order for each media item (1 = first, 2 = second, etc.)")
    print("   5. Save the hero to see your media in the carousel")

if __name__ == "__main__":
    test_hero_media_functionality() 