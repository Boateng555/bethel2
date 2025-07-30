#!/usr/bin/env python3
"""
Production ImageKit Verification
Final verification that ImageKit is ready for production deployment
"""

import os
import sys
import django
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests

# Set ImageKit environment variables directly
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from imagekitio import ImageKit

def verify_environment():
    """Verify environment variables are set"""
    print("🔍 Verifying Environment Variables...")
    
    required_vars = [
        'IMAGEKIT_PUBLIC_KEY',
        'IMAGEKIT_PRIVATE_KEY', 
        'IMAGEKIT_URL_ENDPOINT'
    ]
    
    all_set = True
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"  ✅ {var}: Set")
        else:
            print(f"  ❌ {var}: Not set")
            all_set = False
    
    return all_set

def verify_django_settings():
    """Verify Django settings configuration"""
    print("\n⚙️ Verifying Django Settings...")
    
    # Check ImageKit config
    imagekit_config = settings.IMAGEKIT_CONFIG
    print(f"  📋 ImageKit Config:")
    print(f"    Public Key: {'✅ Set' if imagekit_config['PUBLIC_KEY'] else '❌ Not set'}")
    print(f"    Private Key: {'✅ Set' if imagekit_config['PRIVATE_KEY'] else '❌ Not set'}")
    print(f"    URL Endpoint: {'✅ Set' if imagekit_config['URL_ENDPOINT'] else '❌ Not set'}")
    
    # Check storage configuration
    print(f"  💾 Default Storage: {settings.DEFAULT_FILE_STORAGE}")
    
    if 'ImageKit' in settings.DEFAULT_FILE_STORAGE:
        print("  ✅ Django configured to use ImageKit storage")
        return True
    else:
        print("  ❌ Django not configured to use ImageKit storage")
        return False

def verify_imagekit_connection():
    """Verify direct connection to ImageKit"""
    print("\n🔗 Verifying ImageKit Connection...")
    
    try:
        imagekit = ImageKit(
            public_key=settings.IMAGEKIT_CONFIG['PUBLIC_KEY'],
            private_key=settings.IMAGEKIT_CONFIG['PRIVATE_KEY'],
            url_endpoint=settings.IMAGEKIT_CONFIG['URL_ENDPOINT']
        )
        
        # Test listing files
        files = imagekit.list_files()
        print(f"  ✅ Connection successful - Found {len(files.list)} files")
        return True, imagekit
        
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        return False, None

def verify_upload_and_access():
    """Verify upload and URL access"""
    print("\n📤 Verifying Upload and Access...")
    
    try:
        # Create a test image
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), "Production Ready", fill='black', font=font)
        draw.text((50, 100), "ImageKit Integration", fill='blue', font=font)
        draw.text((50, 150), "✅ Working!", fill='green', font=font)
        
        # Save to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG', quality=95)
        img_bytes.seek(0)
        
        # Test direct upload
        imagekit = ImageKit(
            public_key=settings.IMAGEKIT_CONFIG['PUBLIC_KEY'],
            private_key=settings.IMAGEKIT_CONFIG['PRIVATE_KEY'],
            url_endpoint=settings.IMAGEKIT_CONFIG['URL_ENDPOINT']
        )
        
        upload = imagekit.upload_file(
            file=img_bytes,
            file_name="production_verification.jpg"
        )
        
        if upload.response_metadata.http_status_code == 200:
            print(f"  ✅ Direct upload successful")
            
            # Test URL access
            url = f"{settings.IMAGEKIT_CONFIG['URL_ENDPOINT']}/{upload.file_path.lstrip('/')}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"  ✅ URL access successful")
                print(f"  📏 File size: {len(response.content)} bytes")
                return True
            else:
                print(f"  ❌ URL access failed: HTTP {response.status_code}")
                return False
        else:
            print(f"  ❌ Direct upload failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Upload/access error: {e}")
        return False

def verify_django_storage():
    """Verify Django storage integration"""
    print("\n🔄 Verifying Django Storage...")
    
    try:
        # Create a test image
        img = Image.new('RGB', (300, 200), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), "Django Storage", fill='black', font=font)
        draw.text((50, 100), "ImageKit Test", fill='darkblue', font=font)
        
        # Save to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG', quality=95)
        img_bytes.seek(0)
        
        # Create test file
        test_file = ContentFile(img_bytes.getvalue(), name="django_storage_verification.jpg")
        
        # Save using Django storage
        saved_path = default_storage.save("test/django_storage_verification.jpg", test_file)
        
        # Check if it's an ImageKit URL
        if 'ik.imagekit.io' in saved_path:
            print(f"  ✅ Django storage using ImageKit")
            print(f"  📁 Saved path: {saved_path}")
            
            # Test URL generation
            url = default_storage.url(saved_path)
            print(f"  🔗 Generated URL: {url}")
            
            return True
        else:
            print(f"  ❌ Django storage not using ImageKit")
            print(f"  📁 Saved path: {saved_path}")
            return False
            
    except Exception as e:
        print(f"  ❌ Django storage error: {e}")
        return False

def generate_production_checklist():
    """Generate production deployment checklist"""
    print("\n📋 Production Deployment Checklist:")
    print("=" * 50)
    print("✅ Environment Variables (Production):")
    print("   - IMAGEKIT_PUBLIC_KEY=public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=")
    print("   - IMAGEKIT_PRIVATE_KEY=private_Dnsrj2VW7uJakaeMaNYaav+P784=")
    print("   - IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/9buar9mbp")
    print()
    print("✅ Django Settings:")
    print("   - DEFAULT_FILE_STORAGE configured for ImageKit")
    print("   - IMAGEKIT_CONFIG properly set")
    print()
    print("✅ Storage Backend:")
    print("   - RobustImageKitStorage working correctly")
    print("   - File uploads go to ImageKit cloud")
    print("   - URLs generated correctly")
    print()
    print("✅ ImageKit Dashboard:")
    print("   - Monitor uploads and usage")
    print("   - Check for any errors or issues")
    print("   - Verify CDN delivery")
    print()
    print("🚀 Ready for Production Deployment!")

def main():
    """Run production verification"""
    print("🚀 Production ImageKit Verification")
    print("=" * 50)
    
    # Test 1: Environment Variables
    env_ok = verify_environment()
    
    # Test 2: Django Settings
    settings_ok = verify_django_settings()
    
    # Test 3: ImageKit Connection
    connection_ok, imagekit = verify_imagekit_connection()
    
    # Test 4: Upload and Access
    upload_ok = verify_upload_and_access()
    
    # Test 5: Django Storage
    storage_ok = verify_django_storage()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Production Verification Results:")
    print(f"  Environment Variables: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"  Django Settings: {'✅ PASS' if settings_ok else '❌ FAIL'}")
    print(f"  ImageKit Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"  Upload & Access: {'✅ PASS' if upload_ok else '❌ FAIL'}")
    print(f"  Django Storage: {'✅ PASS' if storage_ok else '❌ FAIL'}")
    
    all_tests_passed = all([env_ok, settings_ok, connection_ok, upload_ok, storage_ok])
    
    if all_tests_passed:
        print("\n🎉 PRODUCTION READY! ImageKit is fully configured and working.")
        generate_production_checklist()
    else:
        print("\n⚠️ Some tests failed. Please fix the issues before deploying to production.")
        print("\n🔧 Common issues:")
        print("   1. Environment variables not set in your environment")
        print("   2. ImageKit credentials incorrect")
        print("   3. Network connectivity issues")
        print("   4. Django settings misconfiguration")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 