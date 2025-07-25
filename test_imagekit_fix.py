#!/usr/bin/env python
"""
Simple test to verify ImageKit storage fix
"""

import os
import django
from django.core.files.base import ContentFile

# Set environment variables first
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.files.storage import default_storage

print("🧪 Testing ImageKit storage fix...")

# Test upload
test_content = b"Test file for ImageKit fix verification"
test_file = ContentFile(test_content, name='fix_test.txt')

saved_path = default_storage.save('test/fix_test.txt', test_file)
url = default_storage.url(saved_path)

print(f"Upload path: {saved_path}")
print(f"Upload URL: {url}")

if url.startswith('https://ik.imagekit.io/'):
    print("✅ SUCCESS: ImageKit storage fix is working!")
    print("✅ All admin uploads will now use ImageKit")
else:
    print("❌ FAILED: ImageKit storage fix is not working")
    print(f"❌ URL is: {url}")

# Clean up
try:
    default_storage.delete(saved_path)
    print("✅ Test file cleaned up")
except:
    print("⚠️ Could not clean up test file")

print("\n📋 Next steps:")
print("1. Restart your Django application")
print("2. Try uploading a new image through admin")
print("3. Check that new uploads have ImageKit URLs") 