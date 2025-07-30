#!/usr/bin/env python3
"""
Test ImageKit images with proper environment setup
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Set ImageKit environment variables BEFORE Django setup
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

import requests
from PIL import Image
from io import BytesIO

from core.models import HeroMedia, Church, Ministry, News, Sermon

def test_imagekit_image_quality():
    """Test image quality and dimensions for ImageKit images"""
    print("🔍 Testing ImageKit Admin Image Quality")
    print("=" * 50)
    
    # Test HeroMedia images
    print("\n📸 Testing HeroMedia Images")
    hero_media_list = HeroMedia.objects.all()
    for media in hero_media_list:
        if media.image:
            test_imagekit_image(f"HeroMedia ID {media.id}", media.get_image_url())
    
    # Test Church images
    print("\n🏛️ Testing Church Images")
    church_list = Church.objects.all()
    for church in church_list:
        if church.logo:
            test_imagekit_image(f"Church {church.name} - Logo", church.get_logo_url())
        if church.banner_image:
            test_imagekit_image(f"Church {church.name} - Banner", church.get_banner_url())
    
    # Test Ministry images
    print("\n⛪ Testing Ministry Images")
    ministry_list = Ministry.objects.all()
    for ministry in ministry_list:
        if ministry.image:
            test_imagekit_image(f"Ministry {ministry.name}", ministry.get_image_url())
    
    # Test News images
    print("\n📰 Testing News Images")
    news_list = News.objects.all()
    for news in news_list:
        if news.image:
            test_imagekit_image(f"News {news.title}", news.get_image_url())
    
    # Test Sermon images
    print("\n📖 Testing Sermon Images")
    sermon_list = Sermon.objects.all()
    for sermon in sermon_list:
        if sermon.thumbnail:
            test_imagekit_image(f"Sermon {sermon.title}", sermon.get_thumbnail_url())

def test_imagekit_image(description, image_url):
    """Test a single ImageKit image for quality and dimensions"""
    try:
        # Handle ImageKit URLs
        if image_url.startswith('https://ik.imagekit.io/'):
            # ImageKit URL - test directly
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                # Get image dimensions
                img = Image.open(BytesIO(response.content))
                width, height = img.size
                file_size = len(response.content)
                
                print(f"  ✅ {description} (ImageKit)")
                print(f"     Dimensions: {width}x{height} pixels")
                print(f"     File size: {file_size:,} bytes")
                print(f"     URL: {image_url}")
                
                # Check if image is reasonable size
                if file_size < 1000:
                    print(f"     ⚠️  WARNING: Image is very small ({file_size} bytes)")
                elif width < 100 or height < 100:
                    print(f"     ⚠️  WARNING: Image dimensions are very small ({width}x{height})")
                else:
                    print(f"     ✅ Image quality looks good")
                    
            else:
                print(f"  ❌ {description}: HTTP {response.status_code}")
                print(f"     URL: {image_url}")
                
        elif image_url.startswith('/media/'):
            # Local file - skip for now since we're testing ImageKit
            print(f"  ⏭️ {description}: Local file (skipping)")
            
        else:
            print(f"  ❓ {description}: Unknown URL format: {image_url}")
            
    except Exception as e:
        print(f"  ❌ {description}: Error - {e}")
        if 'image_url' in locals():
            print(f"     URL: {image_url}")

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
        
        # Check environment variables
        public_key = os.environ.get('IMAGEKIT_PUBLIC_KEY')
        private_key = os.environ.get('IMAGEKIT_PRIVATE_KEY')
        url_endpoint = os.environ.get('IMAGEKIT_URL_ENDPOINT')
        
        print(f"ImageKit Public Key: {'✅ Set' if public_key else '❌ Missing'}")
        print(f"ImageKit Private Key: {'✅ Set' if private_key else '❌ Missing'}")
        print(f"ImageKit URL Endpoint: {'✅ Set' if url_endpoint else '❌ Missing'}")
        
        # Test storage functionality
        if 'ImageKit' in storage_class:
            print("✅ Using ImageKit storage")
            
            # Test a simple upload
            from django.core.files.base import ContentFile
            test_content = ContentFile(b"test", name="test.txt")
            saved_name = default_storage.save('test/test.txt', test_content)
            print(f"✅ Test upload successful: {saved_name}")
            
            # Test URL generation
            file_url = default_storage.url(saved_name)
            print(f"✅ Test URL: {file_url}")
            
            # Clean up
            default_storage.delete(saved_name)
            print("✅ Test cleanup successful")
            
        else:
            print("⚠️ Not using ImageKit storage")
            
    except Exception as e:
        print(f"❌ Error testing storage: {e}")

if __name__ == "__main__":
    test_storage_configuration()
    test_imagekit_image_quality() 