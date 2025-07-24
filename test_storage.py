#!/usr/bin/env python3
"""
Test Storage Configuration
This script tests the current storage setup.
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_storage():
    print("🧪 Testing Storage Configuration")
    print("=" * 50)
    
    # Check storage backend
    storage_backend = settings.DEFAULT_FILE_STORAGE
    print(f"Storage Backend: {storage_backend}")
    
    # Check ImageKit configuration
    imagekit_config = settings.IMAGEKIT_CONFIG
    print(f"\nImageKit Configuration:")
    print(f"  Public Key: {'✅ Set' if imagekit_config['PUBLIC_KEY'] else '❌ Not set'}")
    print(f"  Private Key: {'✅ Set' if imagekit_config['PRIVATE_KEY'] else '❌ Not set'}")
    print(f"  URL Endpoint: {'✅ Set' if imagekit_config['URL_ENDPOINT'] else '❌ Not set'}")
    
    # Check media settings
    print(f"\nMedia Settings:")
    print(f"  MEDIA_URL: {settings.MEDIA_URL}")
    print(f"  MEDIA_ROOT: {settings.MEDIA_ROOT}")
    
    # Test storage initialization
    try:
        from django.core.files.storage import default_storage
        print(f"\n✅ Storage initialized successfully!")
        print(f"  Storage Class: {type(default_storage).__name__}")
        
        # Test if we can save a file
        from django.core.files.base import ContentFile
        test_content = b"Test file content"
        test_file = ContentFile(test_content, name="test.txt")
        
        file_path = default_storage.save("test/test_file.txt", test_file)
        print(f"  ✅ Test file saved: {file_path}")
        
        # Check if file exists
        if default_storage.exists(file_path):
            print(f"  ✅ File exists: {file_path}")
        else:
            print(f"  ❌ File does not exist: {file_path}")
        
        # Get file URL
        file_url = default_storage.url(file_path)
        print(f"  📁 File URL: {file_url}")
        
        # Clean up test file
        default_storage.delete(file_path)
        print(f"  🧹 Test file cleaned up")
        
    except Exception as e:
        print(f"❌ Storage test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Conclusion:")
    print("=" * 50)
    
    if 'ImageKitStorage' in str(storage_backend):
        print("🖼️ Using ImageKit for storage")
        print("   - Images will be served via CDN")
        print("   - Better performance for production")
    else:
        print("⚙️ Using local storage")
        print("   - Images saved to local filesystem")
        print("   - Perfect for development")
        print("   - Consider ImageKit for production")

if __name__ == "__main__":
    test_storage() 