#!/usr/bin/env python3
"""
Debug URLs to see what's actually being returned
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import HeroMedia, Church, Ministry, News, Sermon

def debug_urls():
    """Debug URLs to see what's actually being returned"""
    print("🔍 Debugging URLs")
    print("=" * 50)
    
    # Test HeroMedia images
    print("\n📸 Testing HeroMedia Images")
    hero_media_list = HeroMedia.objects.all()[:3]
    for media in hero_media_list:
        if media.image:
            print(f"  HeroMedia {media.id}:")
            print(f"    Direct field: {media.image}")
            print(f"    URL method: {media.get_image_url()}")
            print(f"    Field URL: {media.image.url}")
    
    # Test Church images
    print("\n🏛️ Testing Church Images")
    church_list = Church.objects.all()[:2]
    for church in church_list:
        if church.logo:
            print(f"  Church {church.name} - Logo:")
            print(f"    Direct field: {church.logo}")
            print(f"    URL method: {church.get_logo_url()}")
            print(f"    Field URL: {church.logo.url}")
    
    # Test Ministry images
    print("\n⛪ Testing Ministry Images")
    ministry_list = Ministry.objects.all()[:2]
    for ministry in ministry_list:
        if ministry.image:
            print(f"  Ministry {ministry.name}:")
            print(f"    Direct field: {ministry.image}")
            print(f"    URL method: {ministry.get_image_url()}")
            print(f"    Field URL: {ministry.image.url}")

if __name__ == "__main__":
    debug_urls() 