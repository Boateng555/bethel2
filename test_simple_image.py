#!/usr/bin/env python3
"""
Test simple image creation and upload
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

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

def test_simple_image_creation():
    """Test creating and uploading a simple image"""
    print("🧪 Testing Simple Image Creation")
    print("=" * 50)
    
    # Create a simple image
    img = Image.new('RGB', (400, 400), color=(73, 109, 137))
    draw = ImageDraw.Draw(img)
    
    # Add text
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    draw.text((200, 200), "Test Image", fill=(255, 255, 255), font=font)
    
    # Save to buffer
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    print(f"✅ Image created successfully")
    print(f"   Size: {len(buffer.getvalue())} bytes")
    
    # Test if PIL can read it back
    try:
        test_img = Image.open(buffer)
        print(f"✅ PIL can read the image: {test_img.size}")
    except Exception as e:
        print(f"❌ PIL cannot read the image: {e}")
        return False
    
    # Upload to ImageKit
    try:
        from django.core.files.storage import default_storage
        
        # Create ContentFile
        content_file = ContentFile(buffer.getvalue(), name='test_simple_image.png')
        
        # Upload
        saved_name = default_storage.save('test/simple_test.png', content_file)
        print(f"✅ Uploaded successfully: {saved_name}")
        
        # Get URL
        file_url = default_storage.url(saved_name)
        print(f"✅ File URL: {file_url}")
        
        # Test if the uploaded image is valid
        response = requests.get(file_url, timeout=10)
        if response.status_code == 200:
            try:
                uploaded_img = Image.open(BytesIO(response.content))
                print(f"✅ Uploaded image is valid: {uploaded_img.size}, {len(response.content)} bytes")
                
                # Clean up
                default_storage.delete(saved_name)
                print(f"✅ Cleanup successful")
                return True
            except Exception as e:
                print(f"❌ Uploaded image is corrupted: {e}")
                return False
        else:
            print(f"❌ Upload failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

if __name__ == "__main__":
    test_simple_image_creation() 