#!/usr/bin/env python
"""
Quick test to verify the storage fix
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

def test_storage_url():
    """Test that storage returns ImageKit URLs"""
    print("🧪 Testing storage URL fix...")
    
    try:
        # Test upload through Django storage
        test_content = b"Test file for URL fix verification"
        test_file = ContentFile(test_content, name='url_fix_test.txt')
        
        saved_path = default_storage.save('test/url_fix_test.txt', test_file)
        print(f"✅ Django storage upload successful! Path: {saved_path}")
        
        # Get URL
        url = default_storage.url(saved_path)
        print(f"✅ Django storage URL: {url}")
        
        # Check if it's an ImageKit URL
        if url.startswith('https://ik.imagekit.io/'):
            print("🎉 SUCCESS: Django storage is returning ImageKit URLs!")
            return True
        else:
            print(f"❌ FAILED: Django storage is returning local URL: {url}")
            return False
        
    except Exception as e:
        print(f"❌ Storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_upload():
    """Test upload through Django models"""
    print("\n🧪 Testing model upload...")
    
    try:
        from core.models import Church, HeroMedia
        
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
        test_content = b"This is a test hero image content for URL fix"
        test_file = ContentFile(test_content, name='model_url_test.jpg')
        
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
            print("🎉 SUCCESS: Model upload is using ImageKit URLs!")
            success = True
        else:
            print(f"❌ FAILED: Model upload is using local URL: {hero_media.image.url}")
            success = False
        
        # Clean up
        hero_media.delete()
        print("✅ Model test cleaned up")
        
        return success
        
    except Exception as e:
        print(f"❌ Model upload test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🚀 Testing storage URL fix...")
    print("=" * 50)
    
    # Test 1: Direct storage
    storage_ok = test_storage_url()
    
    # Test 2: Model upload
    model_ok = test_model_upload()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"Storage URL Test: {'✅ PASS' if storage_ok else '❌ FAIL'}")
    print(f"Model Upload Test: {'✅ PASS' if model_ok else '❌ FAIL'}")
    
    if storage_ok and model_ok:
        print("\n🎉 SUCCESS! Storage URL fix is working.")
        print("✅ Django storage now returns ImageKit URLs")
        print("✅ Model uploads now use ImageKit URLs")
        print("\n📋 Next steps:")
        print("1. Restart your Django application")
        print("2. Try uploading a new image through admin")
        print("3. Check that new uploads have ImageKit URLs")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
    
    return storage_ok and model_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 