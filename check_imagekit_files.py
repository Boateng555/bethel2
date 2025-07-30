#!/usr/bin/env python3
"""
Check existing files in ImageKit account
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Set ImageKit environment variables BEFORE Django setup
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from imagekitio import ImageKit
import requests

def check_imagekit_files():
    """Check existing files in ImageKit account"""
    print("🔍 Checking ImageKit Files")
    print("=" * 50)
    
    # Initialize ImageKit
    imagekit = ImageKit(
        public_key=os.environ['IMAGEKIT_PUBLIC_KEY'],
        private_key=os.environ['IMAGEKIT_PRIVATE_KEY'],
        url_endpoint=os.environ['IMAGEKIT_URL_ENDPOINT']
    )
    
    try:
        # List files
        files = imagekit.list_files()
        print(f"✅ Found {len(files.list)} files in ImageKit account")
        
        # Check files, looking for larger ones
        valid_files = [f for f in files.list if f.size > 1000]
        print(f"✅ Found {len(valid_files)} files larger than 1KB")
        
        if valid_files:
            print(f"\n📁 Valid files (size > 1KB):")
            for i, file in enumerate(valid_files[:3]):
                print(f"\n📁 File {i+1}:")
                print(f"   Name: {file.name}")
                print(f"   Path: {file.file_path}")
                print(f"   Size: {file.size} bytes")
                print(f"   Type: {file.file_type}")
                
                # Try to access the file
                file_url = f"{os.environ['IMAGEKIT_URL_ENDPOINT']}/{file.file_path.lstrip('/')}"
                print(f"   URL: {file_url}")
                
                response = requests.get(file_url, timeout=10)
                print(f"   HTTP Status: {response.status_code}")
                print(f"   Response Size: {len(response.content)} bytes")
                
                if response.status_code == 200 and len(response.content) > 1000:
                    print(f"   ✅ File accessible and looks like an image")
                else:
                    print(f"   ❌ File not accessible or too small")
        else:
            print(f"\n❌ No valid files found. All files are corrupted or too small.")
            
        # Show some examples of the corrupted files
        print(f"\n📁 Examples of corrupted files:")
        for i, file in enumerate(files.list[:3]):
            print(f"\n📁 File {i+1}:")
            print(f"   Name: {file.name}")
            print(f"   Path: {file.file_path}")
            print(f"   Size: {file.size} bytes")
            print(f"   Type: {file.file_type}")
            
            # Try to access the file
            file_url = f"{os.environ['IMAGEKIT_URL_ENDPOINT']}/{file.file_path.lstrip('/')}"
            print(f"   URL: {file_url}")
            
            response = requests.get(file_url, timeout=10)
            print(f"   HTTP Status: {response.status_code}")
            print(f"   Response Size: {len(response.content)} bytes")
            
            if response.status_code == 200 and len(response.content) > 1000:
                print(f"   ✅ File accessible and looks like an image")
            else:
                print(f"   ❌ File not accessible or too small")
                
    except Exception as e:
        print(f"❌ Error listing files: {e}")

if __name__ == "__main__":
    check_imagekit_files() 