#!/usr/bin/env python
"""
Final test to verify ImageKit storage is working correctly
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
from django.core.files.base import ContentFile

print("🧪 Final Storage Test...")

# Test storage with a new file
try:
    test_content = b"Final storage test - this should go to ImageKit"
    test_file = ContentFile(test_content, name='final_test.txt')
    
    saved_path = default_storage.save('test/final_test.txt', test_file)
    url = default_storage.url(saved_path)
    
    print(f"📁 Upload path: {saved_path}")
    print(f"🌐 Upload URL: {url}")
    
    if url.startswith('https://ik.imagekit.io/'):
        print("✅ SUCCESS: Storage is using ImageKit!")
        print("✅ All new uploads will go to ImageKit cloud")
        
        # Clean up test file
        try:
            default_storage.delete(saved_path)
            print("✅ Test file cleaned up")
        except:
            print("⚠️ Could not clean up test file")
            
    else:
        print("❌ FAILED: Storage is NOT using ImageKit")
        print(f"❌ URL is: {url}")
        print("❌ New uploads will still go to local storage")
        
except Exception as e:
    print(f"❌ Error testing storage: {e}")
    import traceback
    traceback.print_exc()

print("\n📋 Next steps:")
print("1. Restart your Django application: sudo systemctl restart bethel")
print("2. Try uploading a new image through admin")
print("3. Check that new uploads have ImageKit URLs")
print("4. Your website should now display all images correctly") 