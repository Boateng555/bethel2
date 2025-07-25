#!/usr/bin/env python
"""
Comprehensive ImageKit Test and Fix Script
This script will test ImageKit functionality and fix any issues found
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from core.models import Church, HeroMedia, Event, Ministry, News, Sermon
from imagekitio import ImageKit
from io import BytesIO

def test_imagekit_configuration():
    """Test ImageKit configuration"""
    print("🔍 Testing ImageKit Configuration...")
    
    try:
        # Check environment variables
        print(f"IMAGEKIT_PUBLIC_KEY: {'✅ Set' if settings.IMAGEKIT_CONFIG['PUBLIC_KEY'] else '❌ Missing'}")
        print(f"IMAGEKIT_PRIVATE_KEY: {'✅ Set' if settings.IMAGEKIT_CONFIG['PRIVATE_KEY'] else '❌ Missing'}")
        print(f"IMAGEKIT_URL_ENDPOINT: {'✅ Set' if settings.IMAGEKIT_CONFIG['URL_ENDPOINT'] else '❌ Missing'}")
        print(f"Storage backend: {settings.DEFAULT_FILE_STORAGE}")
        
        # Test ImageKit connection
        imagekit = ImageKit(
            public_key=settings.IMAGEKIT_CONFIG['PUBLIC_KEY'],
            private_key=settings.IMAGEKIT_CONFIG['PRIVATE_KEY'],
            url_endpoint=settings.IMAGEKIT_CONFIG['URL_ENDPOINT']
        )
        
        # Test upload
        test_content = b"Test file from comprehensive fix script"
        file_obj = BytesIO(test_content)
        file_obj.name = "comprehensive_test.txt"
        
        upload = imagekit.upload_file(
            file=file_obj,
            file_name="comprehensive_test.txt"
        )
        
        print(f"✅ Direct ImageKit upload successful! URL: {upload.url}")
        
        # Clean up
        imagekit.delete_file(upload.file_id)
        print("✅ Direct ImageKit test file deleted")
        
        return True
        
    except Exception as e:
        print(f"❌ ImageKit configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_django_storage():
    """Test Django storage with ImageKit"""
    print("\n🔍 Testing Django Storage with ImageKit...")
    
    try:
        # Test upload through Django storage
        test_content = b"Test file through Django storage"
        test_file = ContentFile(test_content, name='django_test.txt')
        
        saved_path = default_storage.save('test/django_test.txt', test_file)
        print(f"✅ Django storage upload successful! Path: {saved_path}")
        
        # Get URL
        url = default_storage.url(saved_path)
        print(f"✅ Django storage URL: {url}")
        
        # Check if it's an ImageKit URL
        if url.startswith('https://ik.imagekit.io/'):
            print("🎉 SUCCESS: Django storage is using ImageKit!")
        else:
            print("❌ FAILED: Django storage is not using ImageKit")
        
        # Clean up
        default_storage.delete(saved_path)
        print("✅ Django storage test file deleted")
        
        return True
        
    except Exception as e:
        print(f"❌ Django storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_upload():
    """Test upload through Django models"""
    print("\n🔍 Testing Model Upload...")
    
    try:
        # Get first church
        church = Church.objects.first()
        if not church:
            print("❌ No churches found in database")
            return False
        
        print(f"Testing with church: {church.name}")
        
        # Get or create hero for the church
        hero = church.hero_set.first()
        if not hero:
            print("❌ No hero found for church")
            return False
        
        # Create a test hero media entry
        test_content = b"This is a test hero image content"
        test_file = ContentFile(test_content, name='model_test.jpg')
        
        hero_media = HeroMedia.objects.create(
            hero=hero,
            image=test_file,
            order=999  # High order to avoid conflicts
        )
        
        print(f"✅ Hero media created! ID: {hero_media.id}")
        print(f"Image URL: {hero_media.image.url}")
        print(f"Image path: {hero_media.image.name}")
        
        # Check if it's an ImageKit URL
        if hero_media.image.url.startswith('https://ik.imagekit.io/'):
            print("🎉 SUCCESS: Model upload is using ImageKit!")
        else:
            print("❌ FAILED: Model upload is not using ImageKit")
        
        # Clean up
        hero_media.delete()
        print("✅ Model test cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Model upload test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_existing_media():
    """Fix existing media files that might be causing 404 errors"""
    print("\n🔧 Fixing existing media files...")
    
    try:
        # List all models that have media fields
        models_with_media = [
            (Church, ['logo', 'nav_logo']),
            (HeroMedia, ['image', 'video']),
            (Ministry, ['image']),
            (News, ['image']),
            (Sermon, ['thumbnail', 'audio_file', 'video_file']),
        ]
        
        fixed_count = 0
        
        for model, fields in models_with_media:
            print(f"Processing {model.__name__}...")
            for obj in model.objects.all():
                for field_name in fields:
                    if hasattr(obj, field_name):
                        field = getattr(obj, field_name)
                        if field and field.name:
                            try:
                                # Try to get the URL - this will trigger ImageKit lookup
                                url = field.url
                                if url.startswith('https://ik.imagekit.io/'):
                                    print(f"✅ {model.__name__} {obj.id} {field_name}: ImageKit URL")
                                else:
                                    print(f"⚠️ {model.__name__} {obj.id} {field_name}: Non-ImageKit URL")
                            except Exception as e:
                                print(f"❌ {model.__name__} {obj.id} {field_name}: {e}")
                                # Clear the field if it doesn't exist
                                setattr(obj, field_name, None)
                                obj.save()
                                fixed_count += 1
        
        print(f"✅ Fixed {fixed_count} media files")
        return True
        
    except Exception as e:
        print(f"❌ Media fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_test_upload():
    """Create a test upload that you can see in admin"""
    print("\n🔧 Creating test upload for admin verification...")
    
    try:
        # Get first church
        church = Church.objects.first()
        if not church:
            print("❌ No churches found")
            return False
        
        # Get or create hero
        hero = church.hero_set.first()
        if not hero:
            print("❌ No hero found")
            return False
        
        # Create a test hero media with recognizable content
        test_content = b"This is a test image uploaded by the fix script on " + str.encode(str(django.utils.timezone.now()))
        test_file = ContentFile(test_content, name='fix_script_test.jpg')
        
        hero_media = HeroMedia.objects.create(
            hero=hero,
            image=test_file,
            order=1
        )
        
        print(f"✅ Test upload created!")
        print(f"ID: {hero_media.id}")
        print(f"Image URL: {hero_media.image.url}")
        print(f"Image path: {hero_media.image.name}")
        
        if hero_media.image.url.startswith('https://ik.imagekit.io/'):
            print("🎉 SUCCESS: Test upload is in ImageKit!")
            print("You can now check your ImageKit dashboard to see this file.")
        else:
            print("❌ FAILED: Test upload is not in ImageKit")
        
        return hero_media
        
    except Exception as e:
        print(f"❌ Test upload failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function to run all tests and fixes"""
    print("🚀 Starting comprehensive ImageKit test and fix...")
    print("=" * 60)
    
    # Test 1: ImageKit configuration
    config_ok = test_imagekit_configuration()
    
    # Test 2: Django storage
    storage_ok = test_django_storage()
    
    # Test 3: Model upload
    model_ok = test_model_upload()
    
    # Fix 4: Fix existing media
    media_fixed = fix_existing_media()
    
    # Test 5: Create test upload
    test_upload = create_test_upload()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"ImageKit Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Django Storage: {'✅ PASS' if storage_ok else '❌ FAIL'}")
    print(f"Model Upload: {'✅ PASS' if model_ok else '❌ FAIL'}")
    print(f"Media Fix: {'✅ PASS' if media_fixed else '❌ FAIL'}")
    print(f"Test Upload: {'✅ PASS' if test_upload else '❌ FAIL'}")
    
    if test_upload:
        print(f"\n🔍 Test upload details:")
        print(f"ID: {test_upload.id}")
        print(f"URL: {test_upload.image.url}")
        print(f"Path: {test_upload.image.name}")
    
    print("\n📋 Next Steps:")
    print("1. Check your ImageKit dashboard for the test file")
    print("2. Try uploading a new image through Django admin")
    print("3. Verify that new uploads have ImageKit URLs")
    print("4. Check that images load properly on your website")
    
    if all([config_ok, storage_ok, model_ok, media_fixed, test_upload]):
        print("\n🎉 ALL TESTS PASSED! ImageKit is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
    
    return all([config_ok, storage_ok, model_ok, media_fixed, test_upload])

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 