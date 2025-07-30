#!/usr/bin/env python3
"""
Test script to verify Django admin images are displaying properly
"""

import os
import django
import requests
from PIL import Image
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import HeroMedia, Church, Ministry, News, Sermon

def test_admin_image_quality():
    """Test image quality and dimensions"""
    print("🔍 Testing Admin Image Quality")
    print("=" * 50)
    
    # Test HeroMedia images
    print("\n📸 Testing HeroMedia Images")
    hero_media_list = HeroMedia.objects.all()
    for media in hero_media_list:
        if media.image:
            test_image_quality(f"HeroMedia ID {media.id}", media.get_image_url())
    
    # Test Church images
    print("\n🏛️ Testing Church Images")
    church_list = Church.objects.all()
    for church in church_list:
        if church.logo:
            test_image_quality(f"Church {church.name} - Logo", church.get_logo_url())
        if church.banner_image:
            test_image_quality(f"Church {church.name} - Banner", church.get_banner_url())
    
    # Test Ministry images
    print("\n⛪ Testing Ministry Images")
    ministry_list = Ministry.objects.all()
    for ministry in ministry_list:
        if ministry.image:
            test_image_quality(f"Ministry {ministry.name}", ministry.get_image_url())
    
    # Test News images
    print("\n📰 Testing News Images")
    news_list = News.objects.all()
    for news in news_list:
        if news.image:
            test_image_quality(f"News {news.title}", news.get_image_url())
    
    # Test Sermon images
    print("\n📖 Testing Sermon Images")
    sermon_list = Sermon.objects.all()
    for sermon in sermon_list:
        if sermon.thumbnail:
            test_image_quality(f"Sermon {sermon.title}", sermon.get_thumbnail_url())

def test_image_quality(description, image_url):
    """Test a single image for quality and dimensions"""
    try:
        # Handle both local and remote URLs
        if image_url.startswith('/media/'):
            # Local file - try to access directly
            try:
                # Convert to absolute path
                local_path = os.path.join(os.getcwd(), image_url.lstrip('/'))
                if os.path.exists(local_path):
                    with open(local_path, 'rb') as f:
                        content = f.read()
                    img = Image.open(BytesIO(content))
                    width, height = img.size
                    file_size = len(content)
                    
                    print(f"  ✅ {description} (Local)")
                    print(f"     Dimensions: {width}x{height} pixels")
                    print(f"     File size: {file_size:,} bytes")
                    
                    # Check if image is reasonable size
                    if file_size < 1000:
                        print(f"     ⚠️  WARNING: Image is very small ({file_size} bytes)")
                    elif width < 100 or height < 100:
                        print(f"     ⚠️  WARNING: Image dimensions are very small ({width}x{height})")
                    else:
                        print(f"     ✅ Image quality looks good")
                else:
                    print(f"  ❌ {description}: Local file not found")
            except Exception as e:
                print(f"  ❌ {description}: Local file error - {e}")
        else:
            # Remote URL (ImageKit or other)
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                # Get image dimensions
                img = Image.open(BytesIO(response.content))
                width, height = img.size
                file_size = len(response.content)
                
                print(f"  ✅ {description} (Remote)")
                print(f"     Dimensions: {width}x{height} pixels")
                print(f"     File size: {file_size:,} bytes")
                
                # Check if image is reasonable size
                if file_size < 1000:
                    print(f"     ⚠️  WARNING: Image is very small ({file_size} bytes)")
                elif width < 100 or height < 100:
                    print(f"     ⚠️  WARNING: Image dimensions are very small ({width}x{height})")
                else:
                    print(f"     ✅ Image quality looks good")
                    
            else:
                print(f"  ❌ {description}: HTTP {response.status_code}")
                
    except Exception as e:
        print(f"  ❌ {description}: Error - {e}")

if __name__ == "__main__":
    test_admin_image_quality() 