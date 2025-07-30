#!/usr/bin/env python3
"""
Test local images to verify they're working properly
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
from PIL import Image
from io import BytesIO
import requests

def test_local_image_quality():
    """Test image quality and dimensions for local images"""
    print("🔍 Testing Local Image Quality")
    print("=" * 50)
    
    # Test HeroMedia images
    print("\n📸 Testing HeroMedia Images")
    hero_media_list = HeroMedia.objects.all()
    for media in hero_media_list:
        if media.image:
            test_local_image(f"HeroMedia ID {media.id}", media.get_image_url())
    
    # Test Church images
    print("\n🏛️ Testing Church Images")
    church_list = Church.objects.all()
    for church in church_list:
        if church.logo:
            test_local_image(f"Church {church.name} - Logo", church.get_logo_url())
        if church.banner_image:
            test_local_image(f"Church {church.name} - Banner", church.get_banner_url())
    
    # Test Ministry images
    print("\n⛪ Testing Ministry Images")
    ministry_list = Ministry.objects.all()
    for ministry in ministry_list:
        if ministry.image:
            test_local_image(f"Ministry {ministry.name}", ministry.get_image_url())
    
    # Test News images
    print("\n📰 Testing News Images")
    news_list = News.objects.all()
    for news in news_list:
        if news.image:
            test_local_image(f"News {news.title}", news.get_image_url())
    
    # Test Sermon images
    print("\n📖 Testing Sermon Images")
    sermon_list = Sermon.objects.all()
    for sermon in sermon_list:
        if sermon.thumbnail:
            test_local_image(f"Sermon {sermon.title}", sermon.get_thumbnail_url())

def test_local_image(description, image_url):
    """Test a single local image for quality and dimensions"""
    try:
        # Handle local URLs
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
            print(f"  ⏭️ {description}: Not a local URL - {image_url}")
            
    except Exception as e:
        print(f"  ❌ {description}: Error - {e}")

def test_storage_configuration():
    """Test the current storage configuration"""
    print("\n⚙️ Testing Storage Configuration")
    print("=" * 50)
    
    try:
        from django.conf import settings
        from django.core.files.storage import default_storage
        
        # Check storage type
        storage_class = default_storage.__class__.__name__
        print(f"Storage class: {storage_class}")
        
        # Check if using local storage
        if 'FileSystem' in storage_class:
            print("✅ Using local file system storage")
            
            # Test a simple upload
            from django.core.files.base import ContentFile
            test_content = ContentFile(b"test", name="test.txt")
            saved_name = default_storage.save('test/local_test.txt', test_content)
            print(f"✅ Test upload successful: {saved_name}")
            
            # Test URL generation
            file_url = default_storage.url(saved_name)
            print(f"✅ Test URL: {file_url}")
            
            # Clean up
            default_storage.delete(saved_name)
            print("✅ Test cleanup successful")
            
        else:
            print("⚠️ Not using local storage")
            
    except Exception as e:
        print(f"❌ Error testing storage: {e}")

if __name__ == "__main__":
    test_storage_configuration()
    test_local_image_quality() 