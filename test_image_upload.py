#!/usr/bin/env python3
"""
Test Image Upload Functionality
This script tests image uploads with the current storage configuration.
"""

import os
import django
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def create_test_image():
    """Create a simple SVG test image"""
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1e3a8a;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="300" height="200" fill="url(#grad1)"/>
  <circle cx="150" cy="100" r="60" fill="#ffffff" opacity="0.9"/>
  <text x="150" y="95" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="#3b82f6" text-anchor="middle">BETHEL</text>
  <text x="150" y="115" font-family="Arial, sans-serif" font-size="14" fill="#1e3a8a" text-anchor="middle">CHURCH</text>
  <text x="150" y="135" font-family="Arial, sans-serif" font-size="12" fill="#1e3a8a" text-anchor="middle">TEST</text>
  <text x="150" y="175" font-family="Arial, sans-serif" font-size="10" fill="#ffffff" text-anchor="middle">Upload Test</text>
</svg>'''
    return svg_content.encode('utf-8')

def test_image_upload():
    print("🖼️ Testing Image Upload Functionality")
    print("=" * 50)
    
    try:
        # Create test image
        test_image_data = create_test_image()
        test_image = ContentFile(test_image_data, name="bethel_test_image.svg")
        
        print("✅ Test image created")
        
        # Test upload to different folders
        test_paths = [
            "test/bethel_test.svg",
            "hero/test_hero.svg", 
            "events/test_event.svg",
            "churches/logos/test_logo.svg"
        ]
        
        uploaded_files = []
        
        for path in test_paths:
            try:
                # Save file
                file_path = default_storage.save(path, test_image)
                uploaded_files.append(file_path)
                
                # Check if file exists
                exists = default_storage.exists(file_path)
                
                # Get file URL
                file_url = default_storage.url(file_path)
                
                print(f"✅ Uploaded: {file_path}")
                print(f"   Exists: {exists}")
                print(f"   URL: {file_url}")
                
            except Exception as e:
                print(f"❌ Failed to upload {path}: {e}")
        
        print(f"\n📊 Upload Summary:")
        print(f"   Total files uploaded: {len(uploaded_files)}")
        print(f"   Storage backend: {type(default_storage).__name__}")
        
        # Test file access
        if uploaded_files:
            test_file = uploaded_files[0]
            print(f"\n🔍 Testing file access:")
            print(f"   File: {test_file}")
            print(f"   Exists: {default_storage.exists(test_file)}")
            print(f"   URL: {default_storage.url(test_file)}")
            
            # Try to open the file
            try:
                with default_storage.open(test_file, 'rb') as f:
                    content = f.read()
                    print(f"   Size: {len(content)} bytes")
                    print(f"   ✅ File can be read successfully")
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")
        
        # Clean up test files
        print(f"\n🧹 Cleaning up test files...")
        for file_path in uploaded_files:
            try:
                default_storage.delete(file_path)
                print(f"   ✅ Deleted: {file_path}")
            except Exception as e:
                print(f"   ❌ Failed to delete {file_path}: {e}")
        
        print(f"\n🎉 Image upload test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_model_upload():
    """Test uploading through Django models"""
    print(f"\n🏗️ Testing Model Upload")
    print("=" * 50)
    
    try:
        from core.models import Church, Event, HeroMedia
        from datetime import datetime, timedelta
        
        # Create test image
        test_image_data = create_test_image()
        test_image = ContentFile(test_image_data, name="model_test.svg")
        
        print("✅ Test image created for model upload")
        
        # Test Church model upload
        try:
            church = Church.objects.create(
                name="Test Church",
                description="Test church for upload testing"
            )
            church.logo.save("test_logo.svg", test_image, save=True)
            print(f"✅ Church logo uploaded: {church.logo.url}")
            
            # Clean up
            church.delete()
            print("   🧹 Test church cleaned up")
            
        except Exception as e:
            print(f"❌ Church upload failed: {e}")
        
        # Test Event model upload
        try:
            event = Event.objects.create(
                title="Test Event",
                description="Test event for upload testing",
                start_date=datetime.now() + timedelta(days=7),
                end_date=datetime.now() + timedelta(days=7, hours=2),
                location="Test Location"
            )
            event.image.save("test_event.svg", test_image, save=True)
            print(f"✅ Event image uploaded: {event.image.url}")
            
            # Clean up
            event.delete()
            print("   🧹 Test event cleaned up")
            
        except Exception as e:
            print(f"❌ Event upload failed: {e}")
        
        # Test HeroMedia model upload
        try:
            hero_media = HeroMedia.objects.create(
                title="Test Hero Media",
                description="Test hero media for upload testing"
            )
            hero_media.image.save("test_hero.svg", test_image, save=True)
            print(f"✅ Hero media uploaded: {hero_media.image.url}")
            
            # Clean up
            hero_media.delete()
            print("   🧹 Test hero media cleaned up")
            
        except Exception as e:
            print(f"❌ HeroMedia upload failed: {e}")
        
        print("🎉 Model upload test completed!")
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image_upload()
    test_model_upload() 