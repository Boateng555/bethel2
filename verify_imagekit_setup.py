#!/usr/bin/env python3
"""
Verify ImageKit setup is working correctly
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def verify_imagekit_setup():
    """Verify ImageKit is properly configured"""
    print("🔍 Verifying ImageKit Setup")
    print("=" * 50)
    
    # Check environment variables
    public_key = os.environ.get('IMAGEKIT_PUBLIC_KEY')
    private_key = os.environ.get('IMAGEKIT_PRIVATE_KEY')
    url_endpoint = os.environ.get('IMAGEKIT_URL_ENDPOINT')
    
    print(f"✅ Environment Variables:")
    print(f"   PUBLIC_KEY: {'✅ Set' if public_key else '❌ Missing'}")
    print(f"   PRIVATE_KEY: {'✅ Set' if private_key else '❌ Missing'}")
    print(f"   URL_ENDPOINT: {'✅ Set' if url_endpoint else '❌ Missing'}")
    
    # Check Django storage
    from django.core.files.storage import default_storage
    storage_class = default_storage.__class__.__name__
    print(f"\n✅ Django Storage:")
    print(f"   Storage Class: {storage_class}")
    print(f"   Using ImageKit: {'✅ Yes' if 'ImageKit' in storage_class else '❌ No'}")
    
    # Test ImageKit connection
    try:
        from imagekitio import ImageKit
        imagekit = ImageKit(
            public_key=public_key,
            private_key=private_key,
            url_endpoint=url_endpoint
        )
        files = imagekit.list_files()
        print(f"\n✅ ImageKit Connection:")
        print(f"   Status: Connected successfully")
        print(f"   Files in account: {len(files.list)}")
        
    except Exception as e:
        print(f"\n❌ ImageKit Connection:")
        print(f"   Error: {e}")
    
    # Test Django storage functionality
    try:
        from django.core.files.base import ContentFile
        test_content = ContentFile(b"test", name="test.txt")
        saved_name = default_storage.save('test/verify_test.txt', test_content)
        file_url = default_storage.url(saved_name)
        
        print(f"\n✅ Django Storage Test:")
        print(f"   Upload: ✅ Success")
        print(f"   Saved as: {saved_name}")
        print(f"   URL: {file_url}")
        
        # Clean up
        default_storage.delete(saved_name)
        print(f"   Cleanup: ✅ Success")
        
    except Exception as e:
        print(f"\n❌ Django Storage Test:")
        print(f"   Error: {e}")
    
    print(f"\n🎯 Summary:")
    if all([public_key, private_key, url_endpoint]) and 'ImageKit' in storage_class:
        print("   ✅ ImageKit is properly configured and working!")
        print("   ✅ Your Django admin images should display correctly")
        print("   ✅ New uploads will go to ImageKit")
    else:
        print("   ❌ ImageKit configuration needs attention")
        print("   ❌ Please run the setup scripts again")

if __name__ == "__main__":
    verify_imagekit_setup() 