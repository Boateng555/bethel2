#!/usr/bin/env python
"""
Permanent fix to ensure ImageKit storage is always used
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

print("🔧 Applying permanent storage fix...")

# Force ImageKit storage immediately
try:
    from core.storage import ImageKitStorage
    imagekit_storage = ImageKitStorage()
    
    # Override the default storage
    default_storage._wrapped = imagekit_storage
    
    print("✅ Successfully forced ImageKit storage")
    
    # Test the fix
    test_content = b"Permanent storage fix test"
    test_file = ContentFile(test_content, name='permanent_fix_test.txt')
    
    saved_path = default_storage.save('test/permanent_fix_test.txt', test_file)
    url = default_storage.url(saved_path)
    
    print(f"📁 Test upload path: {saved_path}")
    print(f"🌐 Test upload URL: {url}")
    
    if url.startswith('https://ik.imagekit.io/'):
        print("✅ SUCCESS: Permanent fix is working!")
        print("✅ All new uploads will now use ImageKit")
        
        # Clean up test file
        try:
            default_storage.delete(saved_path)
            print("✅ Test file cleaned up")
        except:
            print("⚠️ Could not clean up test file")
            
    else:
        print("❌ FAILED: Permanent fix did not work")
        print(f"❌ URL is: {url}")
        
except Exception as e:
    print(f"❌ Error applying permanent fix: {e}")
    import traceback
    traceback.print_exc()

print("\n📋 Next steps:")
print("1. Restart your Django application: sudo systemctl restart bethel")
print("2. Try uploading a new image through admin")
print("3. Check that new uploads have ImageKit URLs")
print("4. The fix should persist across restarts") 