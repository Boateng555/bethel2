#!/usr/bin/env python
"""
Script to test ImageKit configuration and verify uploads are working
"""
import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from core.storage import ImageKitStorage
from django.core.files.base import ContentFile
import tempfile

def test_imagekit_config():
    """Test ImageKit configuration and upload"""
    print("🔍 Testing ImageKit Configuration...")
    
    # Check environment variables
    print(f"IMAGEKIT_PUBLIC_KEY: {'✅ Set' if settings.IMAGEKIT_CONFIG['PUBLIC_KEY'] else '❌ Missing'}")
    print(f"IMAGEKIT_PRIVATE_KEY: {'✅ Set' if settings.IMAGEKIT_CONFIG['PRIVATE_KEY'] else '❌ Missing'}")
    print(f"IMAGEKIT_URL_ENDPOINT: {'✅ Set' if settings.IMAGEKIT_CONFIG['URL_ENDPOINT'] else '❌ Missing'}")
    
    # Check storage backend
    print(f"Current storage backend: {settings.DEFAULT_FILE_STORAGE}")
    
    # Test if all ImageKit config values are present
    all_config_present = all(settings.IMAGEKIT_CONFIG.values())
    print(f"All ImageKit config present: {'✅ Yes' if all_config_present else '❌ No'}")
    
    if not all_config_present:
        print("\n❌ ImageKit configuration is incomplete!")
        print("Please set the following environment variables:")
        print("- IMAGEKIT_PUBLIC_KEY")
        print("- IMAGEKIT_PRIVATE_KEY") 
        print("- IMAGEKIT_URL_ENDPOINT")
        return False
    
    # Test ImageKit connection
    try:
        storage = ImageKitStorage()
        print("\n🔄 Testing ImageKit connection...")
        
        # Create a test file
        test_content = b"This is a test file for ImageKit upload"
        test_file = ContentFile(test_content, name='test.txt')
        
        # Try to upload
        filename = storage._save('test/test_upload.txt', test_file)
        print(f"✅ Upload successful! File saved as: {filename}")
        
        # Test URL generation
        url = storage.url(filename)
        print(f"✅ URL generated: {url}")
        
        # Test file existence
        exists = storage.exists(filename)
        print(f"✅ File exists check: {exists}")
        
        # Clean up - delete test file
        deleted = storage.delete(filename)
        print(f"✅ Test file deleted: {deleted}")
        
        print("\n🎉 ImageKit is working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ ImageKit test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_imagekit_config()
    sys.exit(0 if success else 1) 