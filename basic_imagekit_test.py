#!/usr/bin/env python3
"""
Basic ImageKit Test
Tests ImageKit functionality without Django dependencies
"""

import os
import sys
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests

# Set ImageKit environment variables directly
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

try:
    from imagekitio import ImageKit
    print("✅ ImageKit SDK imported successfully")
except ImportError as e:
    print(f"❌ Failed to import ImageKit SDK: {e}")
    sys.exit(1)

def test_imagekit_connection():
    """Test direct connection to ImageKit"""
    print("\n🔗 Testing ImageKit Connection...")
    
    try:
        imagekit = ImageKit(
            public_key=os.environ['IMAGEKIT_PUBLIC_KEY'],
            private_key=os.environ['IMAGEKIT_PRIVATE_KEY'],
            url_endpoint=os.environ['IMAGEKIT_URL_ENDPOINT']
        )
        
        print("  ✅ ImageKit object created successfully")
        
        # Test listing files
        print("  📁 Listing files...")
        files = imagekit.list_files()
        print(f"  ✅ Connection successful - Found {len(files.list)} files")
        return True, imagekit
        
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        return False, None

def test_image_upload(imagekit):
    """Test uploading an image to ImageKit"""
    print("\n📤 Testing Image Upload...")
    
    try:
        # Create a test image
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add text to the image
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), "Production Test", fill='black', font=font)
        draw.text((50, 100), "ImageKit Upload", fill='blue', font=font)
        draw.text((50, 150), "Success!", fill='green', font=font)
        
        # Save to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG', quality=95)
        img_bytes.seek(0)
        
        print("  🖼️ Test image created successfully")
        
        # Upload to ImageKit
        print("  📤 Uploading to ImageKit...")
        upload = imagekit.upload_file(
            file=img_bytes,
            file_name="production_test_image.jpg"
        )
        
        if upload.response_metadata.http_status_code == 200:
            print(f"  ✅ Upload successful!")
            print(f"  📁 File ID: {upload.file_id}")
            print(f"  📍 File Path: {upload.file_path}")
            print(f"  🔗 URL: {upload.url}")
            return True, upload.file_path
        else:
            print(f"  ❌ Upload failed: {upload.response_metadata.raw}")
            return False, None
            
    except Exception as e:
        print(f"  ❌ Upload error: {e}")
        return False, None

def test_image_url_access(file_path):
    """Test that uploaded image is accessible via URL"""
    print("\n🌐 Testing Image URL Access...")
    
    try:
        url = f"{os.environ['IMAGEKIT_URL_ENDPOINT']}/{file_path}"
        print(f"  🔗 Testing URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"  ✅ Image accessible via URL")
            print(f"  📏 File size: {len(response.content)} bytes")
            return True
        else:
            print(f"  ❌ Image not accessible: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ URL access error: {e}")
        return False

def main():
    """Run ImageKit tests"""
    print("🚀 Basic ImageKit Production Test")
    print("=" * 40)
    
    # Test 1: ImageKit Connection
    connection_ok, imagekit = test_imagekit_connection()
    
    if not connection_ok:
        print("\n❌ Cannot connect to ImageKit!")
        print("\n🔧 Troubleshooting:")
        print("  1. Check your ImageKit credentials")
        print("  2. Verify your internet connection")
        print("  3. Check ImageKit dashboard for any issues")
        return False
    
    # Test 2: Image Upload
    upload_ok, file_path = test_image_upload(imagekit)
    
    if not upload_ok:
        print("\n❌ Image upload failed!")
        return False
    
    # Test 3: URL Access
    url_ok = test_image_url_access(file_path)
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"  ImageKit Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"  Image Upload: {'✅ PASS' if upload_ok else '❌ FAIL'}")
    print(f"  URL Access: {'✅ PASS' if url_ok else '❌ FAIL'}")
    
    all_tests_passed = all([connection_ok, upload_ok, url_ok])
    
    if all_tests_passed:
        print("\n🎉 ALL TESTS PASSED! ImageKit is working correctly.")
        print("\n📝 Your ImageKit configuration is working properly!")
        print("   - Uploads will go to ImageKit cloud storage")
        print("   - Images will be served from ImageKit CDN")
        print("   - You can monitor usage in your ImageKit dashboard")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 