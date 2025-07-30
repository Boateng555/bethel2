#!/usr/bin/env python3
"""
Fix database paths to match actual ImageKit filenames
"""

import os
import django
import re
from imagekitio import ImageKit

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import HeroMedia, Hero, Church

# ImageKit credentials
PUBLIC_KEY = "public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU="
PRIVATE_KEY = "private_Dnsrj2VW7uJakaeMaNYaav+P784="
URL_ENDPOINT = "https://ik.imagekit.io/9buar9mbp"

def fix_imagekit_paths():
    """Fix database paths to match actual ImageKit filenames"""
    print("🔧 Fixing ImageKit Paths")
    print("=" * 50)
    
    try:
        # Initialize ImageKit
        imagekit = ImageKit(
            private_key=PRIVATE_KEY,
            public_key=PUBLIC_KEY,
            url_endpoint=URL_ENDPOINT
        )
        
        # Get all files from ImageKit
        list_files = imagekit.list_files()
        imagekit_files = {file.name: file for file in list_files.list}
        
        print(f"✅ Found {len(imagekit_files)} files in ImageKit")
        
        # Get all HeroMedia objects
        hero_media_list = HeroMedia.objects.all()
        print(f"📸 Found {hero_media_list.count()} HeroMedia objects")
        
        fixed_count = 0
        
        for media in hero_media_list:
            if media.image:
                current_path = str(media.image.name)
                print(f"\n🔍 HeroMedia ID: {media.id}")
                print(f"   Current path: {current_path}")
                
                # Extract the base filename without path
                base_filename = os.path.basename(current_path)
                print(f"   Base filename: {base_filename}")
                
                # Look for matching file in ImageKit
                matching_file = None
                for imagekit_filename, imagekit_file in imagekit_files.items():
                    # Check if the base filename matches (ignoring the suffix)
                    if base_filename.split('.')[0] in imagekit_filename:
                        matching_file = imagekit_file
                        break
                
                if matching_file:
                    print(f"   ✅ Found matching file: {matching_file.name}")
                    print(f"   📏 Size: {matching_file.size} bytes")
                    
                    # Update the database with the correct path
                    # Remove the leading slash from ImageKit path
                    correct_path = matching_file.file_path.lstrip('/')
                    media.image.name = correct_path
                    media.save()
                    
                    print(f"   🔧 Updated to: {correct_path}")
                    fixed_count += 1
                else:
                    print(f"   ❌ No matching file found in ImageKit")
                    
                    # Check if it's a placeholder file
                    if 'placeholder' in base_filename:
                        print(f"   ℹ️  This appears to be a placeholder file")
                    else:
                        print(f"   ⚠️  This file might be missing from ImageKit")
        
        print(f"\n✅ Fixed {fixed_count} HeroMedia paths")
        
        # Test the fixes
        print(f"\n🧪 Testing fixes...")
        test_fixes()
        
    except Exception as e:
        print(f"❌ Error fixing ImageKit paths: {e}")

def test_fixes():
    """Test if the fixes worked"""
    print("🔍 Testing Image URLs After Fix")
    print("=" * 50)
    
    hero_media_list = HeroMedia.objects.all()
    
    for media in hero_media_list:
        if media.image:
            print(f"\n📸 HeroMedia ID: {media.id}")
            print(f"   Image path: {media.image.name}")
            
            # Get the URL
            image_url = media.get_image_url()
            print(f"   Image URL: {image_url}")
            
            # Test if URL is accessible
            try:
                import requests
                response = requests.head(image_url, timeout=10)
                if response.status_code == 200:
                    print(f"   ✅ URL accessible (Status: {response.status_code})")
                else:
                    print(f"   ❌ URL not accessible (Status: {response.status_code})")
            except Exception as e:
                print(f"   ❌ Error accessing URL: {e}")

if __name__ == "__main__":
    fix_imagekit_paths() 