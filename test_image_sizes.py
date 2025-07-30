#!/usr/bin/env python3
"""
Test script to check image sizes and URLs to diagnose why images appear small
"""

import os
import sys
import django
import requests
from PIL import Image
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import HeroMedia, Hero, Church

def test_image_urls():
    """Test image URLs and their actual sizes"""
    print("🔍 Testing Image URLs and Sizes")
    print("=" * 50)
    
    # Get all hero media
    hero_media_list = HeroMedia.objects.all()
    print(f"Found {hero_media_list.count()} HeroMedia objects")
    
    for media in hero_media_list:
        if media.image:
            print(f"\n📸 HeroMedia ID: {media.id}")
            print(f"   Image field: {media.image}")
            print(f"   Image name: {media.image.name}")
            
            # Get the URL
            image_url = media.get_image_url()
            print(f"   Image URL: {image_url}")
            
            # Check if URL is accessible
            try:
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    print(f"   ✅ URL accessible (Status: {response.status_code})")
                    
                    # Get image size
                    try:
                        img = Image.open(BytesIO(response.content))
                        width, height = img.size
                        print(f"   📏 Image dimensions: {width}x{height} pixels")
                        print(f"   📦 File size: {len(response.content)} bytes")
                        
                        # Check if image is small
                        if width < 800 or height < 600:
                            print(f"   ⚠️  WARNING: Image appears small ({width}x{height})")
                        else:
                            print(f"   ✅ Image size looks good")
                            
                    except Exception as e:
                        print(f"   ❌ Error reading image: {e}")
                else:
                    print(f"   ❌ URL not accessible (Status: {response.status_code})")
                    
            except Exception as e:
                print(f"   ❌ Error accessing URL: {e}")
        else:
            print(f"\n📸 HeroMedia ID: {media.id} - No image")
    
    print("\n" + "=" * 50)
    print("🔍 Testing complete!")

def test_imagekit_urls():
    """Test if ImageKit URLs have any transformation parameters"""
    print("\n🔍 Testing ImageKit URL Structure")
    print("=" * 50)
    
    hero_media_list = HeroMedia.objects.all()
    
    for media in hero_media_list:
        if media.image:
            image_url = media.get_image_url()
            print(f"\n📸 HeroMedia ID: {media.id}")
            print(f"   URL: {image_url}")
            
            # Check if it's an ImageKit URL
            if 'ik.imagekit.io' in image_url:
                print(f"   ✅ ImageKit URL detected")
                
                # Check for transformation parameters
                if 'tr:' in image_url:
                    print(f"   ⚠️  Transformation parameters found in URL")
                    # Extract transformation parameters
                    if '?' in image_url:
                        params = image_url.split('?')[1]
                        print(f"   🔧 Parameters: {params}")
                else:
                    print(f"   ✅ No transformation parameters (original size)")
            else:
                print(f"   ℹ️  Not an ImageKit URL")

if __name__ == "__main__":
    test_image_urls()
    test_imagekit_urls() 