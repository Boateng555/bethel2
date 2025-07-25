#!/usr/bin/env python
"""
Simple script to fix corrupted media files by deleting them and creating proper test images
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
from PIL import Image, ImageDraw, ImageFont
import io

print("🔧 Simple media fix - creating proper test images...")

# Initialize ImageKit
imagekit = ImageKit(
    private_key='private_Dnsrj2VW7uJakaeMaNYaav+P784=',
    public_key='public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=',
    url_endpoint='https://ik.imagekit.io/9buar9mbp'
)

def create_test_image(filename, text="Test Image"):
    """Create a proper test image"""
    width, height = 400, 300
    image = Image.new('RGB', (width, height), color='white')
    
    # Draw gradient background
    for y in range(height):
        for x in range(width):
            r = int((x / width) * 255)
            g = int((y / height) * 255)
            b = 128
            image.putpixel((x, y), (r, g, b))
    
    # Add text
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 120), text, fill='black', font=font)
    draw.text((50, 150), filename, fill='blue', font=font)
    
    # Save to bytes
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return img_buffer.getvalue()

try:
    # Get all files in ImageKit
    print("📁 Getting files from ImageKit...")
    list_files = imagekit.list_files()
    print(f"Found {len(list_files.list)} files")
    
    # Delete all corrupted files (smaller than 1KB)
    print("\n🗑️ Deleting corrupted files...")
    deleted_count = 0
    
    for file in list_files.list:
        if file.size < 1000:  # Less than 1KB
            try:
                print(f"   Deleting: {file.name} ({file.size} bytes)")
                imagekit.delete_file(file.file_id)
                deleted_count += 1
            except Exception as e:
                print(f"   Error deleting {file.name}: {e}")
    
    print(f"✅ Deleted {deleted_count} corrupted files")
    
    # Create new proper test images
    print("\n📝 Creating proper test images...")
    
    test_images = [
        ("hero_banner.jpg", "Hero Banner"),
        ("church_logo.png", "Church Logo"),
        ("event_image.jpg", "Event Image"),
        ("sermon_thumbnail.jpg", "Sermon Thumbnail"),
        ("ministry_image.jpg", "Ministry Image"),
        ("news_image.jpg", "News Image"),
        ("leadership_photo.jpg", "Leadership Photo"),
        ("about_image.jpg", "About Page Image"),
        ("default-image.jpg", "Default Image"),
    ]
    
    created_count = 0
    for filename, description in test_images:
        try:
            print(f"   Creating: {filename}")
            new_image_data = create_test_image(filename, description)
            
            upload = imagekit.upload_file(
                file=new_image_data,
                file_name=filename
            )
            print(f"   ✅ Created: {filename}")
            created_count += 1
            
        except Exception as e:
            print(f"   ❌ Error creating {filename}: {e}")
    
    print(f"\n✅ Successfully created {created_count} proper test images")
    print("📋 Your ImageKit should now show real image previews instead of generic icons")
    print("🌐 Your website should display proper images instead of broken icons")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 