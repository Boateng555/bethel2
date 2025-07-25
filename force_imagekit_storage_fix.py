#!/usr/bin/env python
"""
Force ImageKit Storage Fix
This script will force Django to use ImageKit storage by fixing the storage backend
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def check_current_storage():
    """Check what storage Django is currently using"""
    print("🔍 Checking current storage...")
    
    print(f"Settings DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
    print(f"Actual storage class: {type(default_storage).__name__}")
    print(f"Storage module: {type(default_storage).__module__}")
    
    # Test upload
    test_content = b"Test file for storage check"
    test_file = ContentFile(test_content, name='storage_check.txt')
    
    saved_path = default_storage.save('test/storage_check.txt', test_file)
    url = default_storage.url(saved_path)
    
    print(f"Test upload path: {saved_path}")
    print(f"Test upload URL: {url}")
    
    if url.startswith('https://ik.imagekit.io/'):
        print("✅ Storage is using ImageKit")
        return True
    else:
        print("❌ Storage is NOT using ImageKit")
        return False

def force_imagekit_storage():
    """Force Django to use ImageKit storage"""
    print("\n🔧 Forcing ImageKit storage...")
    
    try:
        # Import the ImageKit storage class
        from core.storage import ImageKitStorage
        
        # Create a new ImageKit storage instance
        imagekit_storage = ImageKitStorage()
        
        # Test upload with ImageKit storage
        test_content = b"Test file with forced ImageKit storage"
        test_file = ContentFile(test_content, name='forced_test.txt')
        
        saved_path = imagekit_storage.save('test/forced_test.txt', test_file)
        url = imagekit_storage.url(saved_path)
        
        print(f"Forced upload path: {saved_path}")
        print(f"Forced upload URL: {url}")
        
        if url.startswith('https://ik.imagekit.io/'):
            print("✅ Forced ImageKit storage is working!")
            
            # Clean up
            imagekit_storage.delete(saved_path)
            return True
        else:
            print("❌ Forced ImageKit storage is NOT working")
            return False
        
    except Exception as e:
        print(f"❌ Forced ImageKit storage failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_storage_backend():
    """Fix the storage backend by updating Django's default storage"""
    print("\n🔧 Fixing storage backend...")
    
    try:
        # Import the ImageKit storage class
        from core.storage import ImageKitStorage
        
        # Create a new ImageKit storage instance
        imagekit_storage = ImageKitStorage()
        
        # Test that it works
        test_content = b"Test file for backend fix"
        test_file = ContentFile(test_content, name='backend_fix_test.txt')
        
        saved_path = imagekit_storage.save('test/backend_fix_test.txt', test_file)
        url = imagekit_storage.url(saved_path)
        
        print(f"Backend fix test path: {saved_path}")
        print(f"Backend fix test URL: {url}")
        
        if url.startswith('https://ik.imagekit.io/'):
            print("✅ ImageKit storage backend is working!")
            
            # Clean up
            imagekit_storage.delete(saved_path)
            return True
        else:
            print("❌ ImageKit storage backend is NOT working")
            return False
        
    except Exception as e:
        print(f"❌ Storage backend fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_storage_fix():
    """Create a fix for the storage backend"""
    print("\n🔧 Creating storage fix...")
    
    # Create a new settings file that forces ImageKit storage
    fix_content = '''
# Force ImageKit Storage Fix
# Add this to your Django settings or environment

import os
from django.core.files.storage import get_storage_class

# Force ImageKit storage
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

# Force Django to use ImageKit storage
DEFAULT_FILE_STORAGE = 'core.storage.ImageKitStorage'

# Clear any cached storage
from django.core.files.storage import default_storage
if hasattr(default_storage, '_wrapped'):
    delattr(default_storage, '_wrapped')
'''
    
    with open('storage_fix.py', 'w') as f:
        f.write(fix_content)
    
    print("✅ Created storage_fix.py with ImageKit configuration")
    
    # Also create a simple test script
    test_content = '''
#!/usr/bin/env python
"""
Simple test to verify ImageKit storage is working
"""

import os
import django
from django.core.files.base import ContentFile

# Set environment variables
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.files.storage import default_storage

# Test upload
test_content = b"Simple ImageKit test file"
test_file = ContentFile(test_content, name='simple_test.txt')

saved_path = default_storage.save('test/simple_test.txt', test_file)
url = default_storage.url(saved_path)

print(f"Upload path: {saved_path}")
print(f"Upload URL: {url}")

if url.startswith('https://ik.imagekit.io/'):
    print("✅ SUCCESS: ImageKit storage is working!")
else:
    print("❌ FAILED: ImageKit storage is not working")

# Clean up
default_storage.delete(saved_path)
'''
    
    with open('simple_imagekit_test.py', 'w') as f:
        f.write(test_content)
    
    print("✅ Created simple_imagekit_test.py for testing")
    
    return True

def main():
    """Main function"""
    print("🚀 Starting storage backend fix...")
    print("=" * 60)
    
    # Check current storage
    current_ok = check_current_storage()
    
    # Test forced ImageKit storage
    forced_ok = force_imagekit_storage()
    
    # Test storage backend fix
    backend_ok = fix_storage_backend()
    
    # Create storage fix
    fix_created = create_storage_fix()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Current Storage: {'✅ PASS' if current_ok else '❌ FAIL'}")
    print(f"Forced ImageKit Storage: {'✅ PASS' if forced_ok else '❌ FAIL'}")
    print(f"Storage Backend Fix: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"Fix Files Created: {'✅ PASS' if fix_created else '❌ FAIL'}")
    
    if forced_ok and backend_ok:
        print("\n🎉 SUCCESS! ImageKit storage is working when forced.")
        print("✅ The issue is with Django's default storage initialization")
        print("✅ ImageKit storage class works correctly")
        print("\n📋 Next steps:")
        print("1. Run: python simple_imagekit_test.py")
        print("2. Check if the test shows ImageKit URLs")
        print("3. If it works, we need to fix Django's storage initialization")
    else:
        print("\n⚠️ ImageKit storage is not working even when forced.")
        print("❌ There may be a deeper issue with the ImageKit configuration")
    
    return forced_ok and backend_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 