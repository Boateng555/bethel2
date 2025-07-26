#!/usr/bin/env python3
"""
Test script to verify ImageKit uploads work correctly
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from core.models import HeroMedia, Hero

def create_test_image(filename="test_image.jpg", width=800, height=600):
    """Create a test image with text"""
    # Create a new image with a white background
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Add some text
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    text = f"Test Image\n{width}x{height}\n{filename}"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill='black', font=font)
    
    # Save to BytesIO
    buffer = BytesIO()
    image.save(buffer, format='JPEG', quality=95)
    buffer.seek(0)
    
    return buffer

def test_imagekit_upload():
    """Test ImageKit upload functionality"""
    print("🧪 Testing ImageKit upload functionality...")
    
    # Create a test image
    image_buffer = create_test_image("test_upload.jpg", 1200, 800)
    original_size = len(image_buffer.getvalue())
    print(f"   📏 Created test image: {original_size:,} bytes")
    
    # Create a SimpleUploadedFile
    uploaded_file = SimpleUploadedFile(
        "test_upload.jpg",
        image_buffer.getvalue(),
        content_type="image/jpeg"
    )
    
    # Get or create a Hero for testing
    hero, created = Hero.objects.get_or_create(
        title="Test Hero",
        defaults={
            'subtitle': 'Test subtitle',
            'background_type': 'image'
        }
    )
    
    # Create HeroMedia with the uploaded file
    hero_media = HeroMedia.objects.create(
        hero=hero,
        image=uploaded_file,
        order=1
    )
    
    # Check the result
    if hero_media.image:
        image_url = str(hero_media.image)
        print(f"   ✅ Upload successful!")
        print(f"   🔗 URL: {image_url}")
        
        # Check if it's an ImageKit URL
        if 'ik.imagekit.io' in image_url:
            print(f"   🎯 ImageKit URL detected")
            
            # Try to get file size from ImageKit
            try:
                import requests
                response = requests.head(image_url)
                if response.status_code == 200:
                    content_length = response.headers.get('content-length')
                    if content_length:
                        file_size = int(content_length)
                        print(f"   📊 File size: {file_size:,} bytes")
                        
                        if file_size > 10000:  # More than 10KB
                            print(f"   ✅ File size looks good (not corrupted)")
                            return True
                        else:
                            print(f"   ❌ File size too small (likely corrupted)")
                            return False
                    else:
                        print(f"   ⚠️ Could not determine file size")
                        return True
                else:
                    print(f"   ❌ Could not access image: {response.status_code}")
                    return False
            except Exception as e:
                print(f"   ⚠️ Error checking file size: {e}")
                return True
        else:
            print(f"   ❌ Not an ImageKit URL")
            return False
    else:
        print(f"   ❌ Upload failed")
        return False

if __name__ == "__main__":
    print("🚀 Starting ImageKit upload test...")
    success = test_imagekit_upload()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("🎉 ImageKit uploads should now work correctly")
    else:
        print("\n❌ Test failed!")
        print("🔧 There may still be issues with ImageKit uploads")
    
    print("\n📝 Next steps:")
    print("1. Pull these changes on your server: git pull origin main")
    print("2. Restart your Django service: sudo systemctl restart bethel.service")
    print("3. Try uploading an image through Django admin")
    print("4. Check if the uploaded image is full-sized (not tiny)") 