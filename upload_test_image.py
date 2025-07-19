#!/usr/bin/env python
"""
Upload a test image to ImageKit to verify it's working
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
from core.models import Church

def create_test_image():
    """Create a colorful test image"""
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
  <text x="150" y="115" font-family="Arial, sans-serif" font-size="14" fill="#1e3a8a" text-anchor="middle">IMAGEKIT</text>
  <text x="150" y="135" font-family="Arial, sans-serif" font-size="12" fill="#1e3a8a" text-anchor="middle">TEST</text>
  <text x="150" y="175" font-family="Arial, sans-serif" font-size="10" fill="#ffffff" text-anchor="middle">Uploaded via Django</text>
</svg>'''
    
    return ContentFile(svg_content.encode('utf-8'), name='bethel_imagekit_test.svg')

def upload_test_image():
    """Upload a test image to ImageKit"""
    print("🚀 Uploading Test Image to ImageKit")
    print("=" * 50)
    
    # Create test image
    test_image = create_test_image()
    print("✅ Created test image")
    
    try:
        # Upload to ImageKit
        file_path = default_storage.save('bethel/test_image.svg', test_image)
        print(f"✅ Upload successful!")
        print(f"File path: {file_path}")
        
        # Get the URL
        file_url = default_storage.url(file_path)
        print(f"ImageKit URL: {file_url}")
        
        # Check if it's an ImageKit URL
        if 'ik.imagekit.io' in file_url:
            print("🎉 SUCCESS: Image uploaded to ImageKit!")
            print("📱 Check your ImageKit dashboard - you should see this image now!")
            print(f"🔗 Direct link: {file_url}")
            
            # Test if the URL is accessible
            import requests
            try:
                response = requests.head(file_url, timeout=10)
                if response.status_code == 200:
                    print("✅ Image URL is accessible!")
                else:
                    print(f"⚠️ Image URL returned status: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Could not verify image URL: {e}")
            
            return file_url
        else:
            print(f"⚠️ Image uploaded to: {file_url}")
            return None
            
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def update_church_logo():
    """Update a church logo to test ImageKit integration"""
    print("\n🏛️ Testing Church Logo Upload")
    print("=" * 50)
    
    churches = Church.objects.all()
    if churches.exists():
        church = churches.first()
        print(f"Testing with church: {church.name}")
        
        # Create a test logo
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="grad1" cx="50%" cy="50%" r="50%">
      <stop offset="0%" style="stop-color:#1e3a8a;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:1" />
    </radialGradient>
  </defs>
  <rect width="200" height="200" fill="url(#grad1)"/>
  <circle cx="100" cy="100" r="70" fill="#ffffff" opacity="0.9"/>
  <text x="100" y="90" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#1e3a8a" text-anchor="middle">CHURCH</text>
  <text x="100" y="110" font-family="Arial, sans-serif" font-size="14" fill="#1e3a8a" text-anchor="middle">LOGO</text>
  <text x="100" y="130" font-family="Arial, sans-serif" font-size="12" fill="#1e3a8a" text-anchor="middle">IMAGEKIT</text>
  <text x="100" y="180" font-family="Arial, sans-serif" font-size="10" fill="#ffffff" text-anchor="middle">Test Upload</text>
</svg>'''
        
        test_logo = ContentFile(svg_content.encode('utf-8'), name='church_logo_test.svg')
        
        try:
            # Save the logo
            church.logo.save('church_logo_test.svg', test_logo, save=True)
            print(f"✅ Church logo updated successfully!")
            print(f"Logo URL: {church.logo.url}")
            
            if 'ik.imagekit.io' in church.logo.url:
                print("🎉 SUCCESS: Church logo uploaded to ImageKit!")
                print("📱 Check your ImageKit dashboard for the church logo!")
                return church.logo.url
            else:
                print(f"⚠️ Logo uploaded to: {church.logo.url}")
                return None
            
        except Exception as e:
            print(f"❌ Logo update failed: {e}")
            return None
    else:
        print("❌ No churches found in database")
        return None

if __name__ == "__main__":
    print("🧪 ImageKit Upload Test")
    print("=" * 50)
    print("This will upload test images to ImageKit so you can see them in your dashboard.")
    print("Make sure you're in production mode (DEBUG=False) to use ImageKit.")
    print()
    
    # Check current environment
    print(f"Current environment: {'Production' if not settings.DEBUG else 'Development'}")
    print(f"Storage backend: {settings.DEFAULT_FILE_STORAGE}")
    print()
    
    # Upload test image
    image_url = upload_test_image()
    
    # Update church logo
    logo_url = update_church_logo()
    
    print("\n" + "=" * 50)
    if image_url or logo_url:
        print("🎉 Upload test completed!")
        print("📱 Check your ImageKit dashboard at https://imagekit.io/dashboard/media-library")
        print("You should now see the uploaded images!")
    else:
        print("⚠️ No images were uploaded. Check the error messages above.")
    print("✅ Test completed!") 