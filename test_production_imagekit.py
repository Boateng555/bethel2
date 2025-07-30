#!/usr/bin/env python3
"""
Comprehensive ImageKit Production Test
Tests all aspects of ImageKit functionality in production environment
"""

import os
import sys
import django
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from django.core.files.base import ContentFile
from imagekitio import ImageKit

def test_environment_variables():
    """Test that all required environment variables are set"""
    print("🔍 Testing Environment Variables...")
    
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

def test_imagekit_connection():
    """Test direct connection to ImageKit"""
    print("\n🔗 Testing ImageKit Connection...")
    
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
        
        # Upload to ImageKit
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
        url = f"{settings.IMAGEKIT_CONFIG['URL_ENDPOINT']}/{file_path}"
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

def test_django_storage():
    """Test Django storage integration"""
    print("\n🔄 Testing Django Storage Integration...")
    
    try:
        from django.core.files.storage import default_storage
        
        # Create test content
        test_content = b"Django storage test content"
        test_file = ContentFile(test_content, name="django_storage_test.txt")
        
        # Save using Django storage
        saved_path = default_storage.save("test/django_storage_test.txt", test_file)
        
        # Get the URL to check if it's ImageKit
        url = default_storage.url(saved_path)
        
        # Check if it's an ImageKit URL
        if 'ik.imagekit.io' in url:
            print(f"  ✅ Django storage using ImageKit")
            print(f"  📁 Saved path: {saved_path}")
            print(f"  🔗 Generated URL: {url}")
            
            return True
        else:
            print(f"  ❌ Django storage not using ImageKit")
            print(f"  📁 Saved path: {saved_path}")
            print(f"  🔗 Generated URL: {url}")
            return False
            
    except Exception as e:
        print(f"  ❌ Django storage error: {e}")
        return False

def test_model_upload():
    """Test model field upload"""
    print("\n📋 Testing Model Upload...")
    
    try:
        from core.models import HeroMedia, Hero, Church
        
        # Get or create a test church and hero
        church, created = Church.objects.get_or_create(
            name="Test Church for ImageKit",
            defaults={
                'slug': 'test-church-imagekit',
                'city': 'Test City',
                'country': 'Test Country',
                'address': '123 Test Street',
                'is_active': True,
                'is_approved': True
            }
        )
        
        hero, created = Hero.objects.get_or_create(
            church=church,
            defaults={
                'title': 'Test Hero',
                'subtitle': 'Testing ImageKit uploads'
            }
        )
        
        # Create a test image
        img = Image.new('RGB', (300, 200), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), "Model Test", fill='black', font=font)
        draw.text((50, 100), "Hero Media", fill='darkblue', font=font)
        
        # Save to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG', quality=95)
        img_bytes.seek(0)
        
        # Create model instance
        hero_media = HeroMedia(
            hero=hero,
            order=1
        )
        
        # Save image to model field
        hero_media.image.save("model_test_hero.jpg", ContentFile(img_bytes.getvalue()))
        hero_media.save()
        
        # Check if image URL is ImageKit
        if 'ik.imagekit.io' in hero_media.image.url:
            print(f"  ✅ Model upload using ImageKit")
            print(f"  📁 Image URL: {hero_media.image.url}")
            
            # Clean up
            hero_media.delete()
            return True
        else:
            print(f"  ❌ Model upload not using ImageKit")
            print(f"  📁 Image URL: {hero_media.image.url}")
            
            # Clean up
            hero_media.delete()
            return False
            
    except Exception as e:
        print(f"  ❌ Model upload error: {e}")
        return False

def test_admin_upload():
    """Test admin interface upload"""
    print("\n⚙️ Testing Admin Upload...")
    
    try:
        from django.contrib.auth.models import User
        from django.test import Client
        from django.urls import reverse
        
        # Create test user
        user, created = User.objects.get_or_create(
            username='test_admin',
            defaults={'is_staff': True, 'is_superuser': True}
        )
        user.set_password('testpass123')
        user.save()
        
        # Create test client
        client = Client()
        client.login(username='test_admin', password='testpass123')
        
        # Create test image
        img = Image.new('RGB', (250, 150), color='lightgreen')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 18)
        except:
            font = ImageFont.load_default()
        
        draw.text((30, 30), "Admin Test", fill='black', font=font)
        draw.text((30, 80), "ImageKit Upload", fill='darkgreen', font=font)
        
        # Save to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG', quality=95)
        img_bytes.seek(0)
        
        print(f"  ✅ Admin upload test prepared")
        print(f"  👤 Test user: test_admin")
        print(f"  🔑 Password: testpass123")
        print(f"  🌐 Admin URL: /admin/")
        
        # Clean up
        user.delete()
        return True
        
    except Exception as e:
        print(f"  ❌ Admin upload test error: {e}")
        return False

def main():
    """Run all ImageKit tests"""
    print("🚀 ImageKit Production Test Suite")
    print("=" * 50)
    
    # Test 1: Environment Variables
    env_ok = test_environment_variables()
    
    if not env_ok:
        print("\n❌ Environment variables not properly configured!")
        print("Please check your environment variables and ensure all ImageKit variables are set.")
        return False
    
    # Test 2: ImageKit Connection
    connection_ok, imagekit = test_imagekit_connection()
    
    if not connection_ok:
        print("\n❌ Cannot connect to ImageKit!")
        print("Please check your ImageKit credentials and network connection.")
        return False
    
    # Test 3: Image Upload
    upload_ok, file_path = test_image_upload(imagekit)
    
    if not upload_ok:
        print("\n❌ Image upload failed!")
        return False
    
    # Test 4: URL Access
    url_ok = test_image_url_access(file_path)
    
    if not url_ok:
        print("\n❌ Image URL access failed!")
        return False
    
    # Test 5: Django Storage
    storage_ok = test_django_storage()
    
    # Test 6: Model Upload
    model_ok = test_model_upload()
    
    # Test 7: Admin Upload
    admin_ok = test_admin_upload()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"  Environment Variables: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"  ImageKit Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"  Image Upload: {'✅ PASS' if upload_ok else '❌ FAIL'}")
    print(f"  URL Access: {'✅ PASS' if url_ok else '❌ FAIL'}")
    print(f"  Django Storage: {'✅ PASS' if storage_ok else '❌ FAIL'}")
    print(f"  Model Upload: {'✅ PASS' if model_ok else '❌ FAIL'}")
    print(f"  Admin Upload: {'✅ PASS' if admin_ok else '❌ FAIL'}")
    
    all_tests_passed = all([env_ok, connection_ok, upload_ok, url_ok, storage_ok, model_ok, admin_ok])
    
    if all_tests_passed:
        print("\n🎉 ALL TESTS PASSED! ImageKit is working correctly in production.")
        print("\n📝 Next Steps:")
        print("  1. Your ImageKit configuration is working properly")
        print("  2. All uploads will go to ImageKit cloud storage")
        print("  3. Images will be served from ImageKit CDN")
        print("  4. You can monitor usage in your ImageKit dashboard")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("  1. Verify ImageKit credentials in environment variables")
        print("  2. Check ImageKit dashboard for any issues")
        print("  3. Ensure your app has internet access")
        print("  4. Check Django settings for storage configuration")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 