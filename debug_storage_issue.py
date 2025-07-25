#!/usr/bin/env python
"""
Debug why new uploads are still going to local storage instead of ImageKit
"""

import os
import django

# Set environment variables
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile

print("🔍 Debugging Storage Issue...")

# Check current storage configuration
print(f"\n📋 CURRENT STORAGE CONFIGURATION:")
print(f"   DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')}")
print(f"   MEDIA_ROOT: {getattr(settings, 'MEDIA_ROOT', 'Not set')}")
print(f"   STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', 'Not set')}")

# Check ImageKit configuration
print(f"\n📋 IMAGEKIT CONFIGURATION:")
if hasattr(settings, 'IMAGEKIT_CONFIG'):
    print(f"   IMAGEKIT_CONFIG: {settings.IMAGEKIT_CONFIG}")
    print(f"   PUBLIC_KEY: {settings.IMAGEKIT_CONFIG.get('PUBLIC_KEY', 'Not set')}")
    print(f"   PRIVATE_KEY: {settings.IMAGEKIT_CONFIG.get('PRIVATE_KEY', 'Not set')}")
    print(f"   URL_ENDPOINT: {settings.IMAGEKIT_CONFIG.get('URL_ENDPOINT', 'Not set')}")
else:
    print(f"   ❌ IMAGEKIT_CONFIG not found in settings")

# Check environment variables
print(f"\n📋 ENVIRONMENT VARIABLES:")
print(f"   IMAGEKIT_PUBLIC_KEY: {os.environ.get('IMAGEKIT_PUBLIC_KEY', 'Not set')}")
print(f"   IMAGEKIT_PRIVATE_KEY: {os.environ.get('IMAGEKIT_PRIVATE_KEY', 'Not set')}")
print(f"   IMAGEKIT_URL_ENDPOINT: {os.environ.get('IMAGEKIT_URL_ENDPOINT', 'Not set')}")

# Check current default storage
print(f"\n📋 CURRENT DEFAULT STORAGE:")
print(f"   Storage class: {type(default_storage).__name__}")
print(f"   Storage module: {default_storage.__class__.__module__}")

# Try to import storage override
print(f"\n📋 STORAGE OVERRIDE CHECK:")
try:
    import core.storage_override
    print(f"   ✅ core.storage_override imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import core.storage_override: {e}")

# Test storage with a new file
print(f"\n📋 TESTING STORAGE WITH NEW FILE:")
try:
    test_content = b"Test file for storage debugging"
    test_file = ContentFile(test_content, name='debug_test.txt')
    
    saved_path = default_storage.save('test/debug_test.txt', test_file)
    url = default_storage.url(saved_path)
    
    print(f"   Upload path: {saved_path}")
    print(f"   Upload URL: {url}")
    
    if url.startswith('https://ik.imagekit.io/'):
        print(f"   ✅ SUCCESS: Storage is using ImageKit!")
    else:
        print(f"   ❌ FAILED: Storage is NOT using ImageKit")
        print(f"   ❌ URL is: {url}")
    
    # Clean up test file
    try:
        default_storage.delete(saved_path)
        print(f"   ✅ Test file cleaned up")
    except:
        print(f"   ⚠️ Could not clean up test file")
        
except Exception as e:
    print(f"   ❌ Error testing storage: {e}")
    import traceback
    traceback.print_exc()

# Check if storage override is working
print(f"\n📋 STORAGE OVERRIDE STATUS:")
try:
    # Check if default_storage was overridden
    if hasattr(default_storage, '_wrapped'):
        print(f"   Storage has _wrapped attribute")
        print(f"   Wrapped storage: {type(default_storage._wrapped).__name__}")
    else:
        print(f"   Storage does NOT have _wrapped attribute")
    
    # Try to force the override again
    print(f"\n📋 FORCING STORAGE OVERRIDE:")
    try:
        from core.storage import ImageKitStorage
        imagekit_storage = ImageKitStorage()
        default_storage._wrapped = imagekit_storage
        print(f"   ✅ Manually forced ImageKit storage")
        
        # Test again
        test_content2 = b"Test file after manual override"
        test_file2 = ContentFile(test_content2, name='debug_test2.txt')
        
        saved_path2 = default_storage.save('test/debug_test2.txt', test_file2)
        url2 = default_storage.url(saved_path2)
        
        print(f"   Upload path: {saved_path2}")
        print(f"   Upload URL: {url2}")
        
        if url2.startswith('https://ik.imagekit.io/'):
            print(f"   ✅ SUCCESS: Manual override worked!")
        else:
            print(f"   ❌ FAILED: Manual override did not work")
        
        # Clean up
        try:
            default_storage.delete(saved_path2)
            print(f"   ✅ Test file 2 cleaned up")
        except:
            print(f"   ⚠️ Could not clean up test file 2")
            
    except Exception as e:
        print(f"   ❌ Error with manual override: {e}")
        
except Exception as e:
    print(f"   ❌ Error checking storage override: {e}")

print(f"\n📋 RECOMMENDATIONS:")
print(f"1. Check if core/storage_override.py exists and is correct")
print(f"2. Verify that backend/settings.py imports the override")
print(f"3. Restart the Django application completely")
print(f"4. Check if there are any import errors in the logs") 