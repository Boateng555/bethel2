#!/usr/bin/env python3
"""
Debug ImageKit upload issues
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
from PIL import Image, ImageDraw
from io import BytesIO
import requests

def debug_imagekit_upload():
    """Debug ImageKit upload directly"""
    print("🔍 Debugging ImageKit Upload")
    print("=" * 50)
    
    # Initialize ImageKit
    imagekit = ImageKit(
        public_key=os.environ['IMAGEKIT_PUBLIC_KEY'],
        private_key=os.environ['IMAGEKIT_PRIVATE_KEY'],
        url_endpoint=os.environ['IMAGEKIT_URL_ENDPOINT']
    )
    
    # Create a simple image
    img = Image.new('RGB', (400, 400), color=(73, 109, 137))
    draw = ImageDraw.Draw(img)
    draw.text((200, 200), "Test", fill=(255, 255, 255))
    
    # Save to buffer
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    print(f"✅ Image created: {len(buffer.getvalue())} bytes")
    
    # Upload directly to ImageKit
    try:
        upload = imagekit.upload_file(
            file=buffer,
            file_name="debug_test.png"
        )
        
        print(f"✅ Upload response status: {upload.response_metadata.http_status_code}")
        print(f"✅ Uploaded file path: {upload.file_path}")
        print(f"✅ Uploaded file ID: {upload.file_id}")
        print(f"✅ Uploaded file name: {upload.name}")
        
        # Test the uploaded file
        file_url = f"{os.environ['IMAGEKIT_URL_ENDPOINT']}/{upload.file_path.lstrip('/')}"
        print(f"✅ File URL: {file_url}")
        
        # Also try the transformation URL
        transform_url = f"{os.environ['IMAGEKIT_URL_ENDPOINT']}/tr:w-400,h-400/{upload.file_path.lstrip('/')}"
        print(f"✅ Transform URL: {transform_url}")
        
        response = requests.get(file_url, timeout=10)
        print(f"✅ HTTP response: {response.status_code}")
        print(f"✅ Response size: {len(response.content)} bytes")
        print(f"✅ Response content: {response.content[:100]}")
        
        if response.status_code == 200:
            try:
                test_img = Image.open(BytesIO(response.content))
                print(f"✅ PIL can read uploaded image: {test_img.size}")
            except Exception as e:
                print(f"❌ PIL cannot read uploaded image: {e}")
        else:
            print(f"❌ HTTP error: {response.text}")
        
        # Try the transform URL
        print(f"\n🔍 Testing transform URL...")
        transform_response = requests.get(transform_url, timeout=10)
        print(f"✅ Transform HTTP response: {transform_response.status_code}")
        print(f"✅ Transform response size: {len(transform_response.content)} bytes")
        
        if transform_response.status_code == 200:
            try:
                transform_img = Image.open(BytesIO(transform_response.content))
                print(f"✅ PIL can read transform image: {transform_img.size}")
            except Exception as e:
                print(f"❌ PIL cannot read transform image: {e}")
        else:
            print(f"❌ Transform HTTP error: {transform_response.text}")
            
    except Exception as e:
        print(f"❌ Upload error: {e}")

if __name__ == "__main__":
    debug_imagekit_upload() 