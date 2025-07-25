#!/usr/bin/env python
"""
Check ImageKit files in detail to see why images are showing as icons
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

from imagekitio import ImageKit
import requests

print("🔍 Checking ImageKit files in detail...")

# Initialize ImageKit
imagekit = ImageKit(
    private_key='private_Dnsrj2VW7uJakaeMaNYaav+P784=',
    public_key='public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=',
    url_endpoint='https://ik.imagekit.io/9buar9mbp'
)

try:
    # Get all files in ImageKit
    list_files = imagekit.list_files()
    print(f"✅ Found {len(list_files.list)} files in ImageKit")
    
    # Check each image file
    print(f"\n📋 DETAILED FILE ANALYSIS:")
    
    image_files = [f for f in list_files.list if f.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
    
    for i, file in enumerate(image_files[:10]):  # Check first 10 images
        print(f"\n   {i+1}. {file.name}")
        print(f"      📁 File ID: {file.file_id}")
        print(f"      📏 Size: {file.size} bytes")
        print(f"      📅 Created: {file.created_at}")
        print(f"      🌐 URL: {file.url}")
        
        # Check if the file is accessible
        try:
            response = requests.head(file.url, timeout=10)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'unknown')
                content_length = response.headers.get('content-length', 'unknown')
                print(f"      ✅ Accessible: {content_type} ({content_length} bytes)")
                
                # Check if it's actually an image
                if 'image' in content_type:
                    print(f"      🖼️ Valid image file")
                else:
                    print(f"      ⚠️ Not an image file: {content_type}")
                    
            else:
                print(f"      ❌ Not accessible: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error checking file: {e}")
    
    # Check for very small files (might be corrupted)
    print(f"\n🔍 CHECKING FOR SMALL/CORRUPTED FILES:")
    small_files = [f for f in image_files if f.size < 1000]  # Less than 1KB
    if small_files:
        print(f"   ⚠️ Found {len(small_files)} potentially corrupted files:")
        for file in small_files:
            print(f"      - {file.name}: {file.size} bytes")
    else:
        print(f"   ✅ No suspiciously small files found")
    
    # Check file types
    print(f"\n📊 FILE TYPE BREAKDOWN:")
    file_types = {}
    for file in image_files:
        ext = file.name.lower().split('.')[-1] if '.' in file.name else 'unknown'
        file_types[ext] = file_types.get(ext, 0) + 1
    
    for ext, count in file_types.items():
        print(f"   {ext.upper()}: {count} files")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n📋 RECOMMENDATIONS:")
print(f"1. If files are very small (< 1KB), they might be corrupted")
print(f"2. If content-type is not 'image/*', the files are not valid images")
print(f"3. You may need to re-upload the images properly")
print(f"4. Check if the original image files are valid before uploading") 