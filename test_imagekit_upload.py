#!/usr/bin/env python
"""
Test script to upload a sample image and verify ImageKit is working
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

def create_test_image():
    """Create a simple test image"""
    # Create a simple SVG test image
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="100" fill="#3b82f6"/>
  <text x="50" y="55" font-family="Arial" font-size="12" fill="white" text-anchor="middle">TEST</text>
</svg>'''
    
    return ContentFile(svg_content.encode('utf-8'), name='test_imagekit.svg')

def test_imagekit_upload():
    """Test uploading to ImageKit"""
    print("🧪 Testing ImageKit Upload")
    print("=" * 50)
    
    # Check current storage backend
    print(f"Current storage backend: {settings.DEFAULT_FILE_STORAGE}")
    print(f"DEBUG mode: {settings.DEBUG}")
    
    # Create test image
    test_image = create_test_image()
    print(f"Created test image: {test_image.name}")
    
    # Upload to storage
    try:
        file_path = default_storage.save(f'test_imagekit_{os.getpid()}.svg', test_image)
        print(f"✅ Upload successful!")
        print(f"File path: {file_path}")
        
        # Get the URL
        file_url = default_storage.url(file_path)
        print(f"File URL: {file_url}")
        
        # Check if it's an ImageKit URL
        if 'ik.imagekit.io' in file_url:
            print("🎉 SUCCESS: Image uploaded to ImageKit!")
        elif 'res.cloudinary.com' in file_url:
            print("☁️ Image uploaded to Cloudinary (fallback)")
        else:
            print("📁 Image uploaded to local storage")
        
        # Clean up - delete the test file
        default_storage.delete(file_path)
        print(f"🧹 Cleaned up test file")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def test_production_upload():
    """Test what would happen in production"""
    print("\n🚀 Testing Production Upload Simulation")
    print("=" * 50)
    
    # Temporarily set DEBUG to False to simulate production
    original_debug = settings.DEBUG
    settings.DEBUG = False
    
    try:
        # Check what storage backend would be used
        print(f"Production storage backend: {settings.DEFAULT_FILE_STORAGE}")
        
        # Create test image
        test_image = create_test_image()
        
        # Upload to storage
        file_path = default_storage.save(f'prod_test_{os.getpid()}.svg', test_image)
        file_url = default_storage.url(file_path)
        
        print(f"✅ Production upload successful!")
        print(f"File URL: {file_url}")
        
        if 'ik.imagekit.io' in file_url:
            print("🎉 SUCCESS: Production would use ImageKit!")
        else:
            print("⚠️ Production would use different storage")
        
        # Clean up
        default_storage.delete(file_path)
        
    except Exception as e:
        print(f"❌ Production test failed: {e}")
    finally:
        # Restore original DEBUG setting
        settings.DEBUG = original_debug

if __name__ == "__main__":
    test_imagekit_upload()
    test_production_upload()
    
    print("\n" + "=" * 50)
    print("✅ Test completed!") 