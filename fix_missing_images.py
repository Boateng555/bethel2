#!/usr/bin/env python
"""
Fix Missing Images Script
This script will find images in the database that don't exist in ImageKit and fix them
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from core.models import Church, HeroMedia, Event, Ministry, News, Sermon
from imagekitio import ImageKit
from PIL import Image, ImageDraw, ImageFont
import io

def create_proper_image(filename, width=1200, height=800):
    """Create a proper test image"""
    # Create a realistic image
    image = Image.new('RGB', (width, height), color='#4A90E2')
    draw = ImageDraw.Draw(image)
    
    # Add some text
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    text = f"Fixed Image: {filename}"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill='white', font=font)
    
    # Convert to bytes
    img_io = io.BytesIO()
    image.save(img_io, format='JPEG', quality=95)
    img_io.seek(0)
    
    return img_io

def check_and_fix_missing_images():
    """Check for missing images and fix them"""
    print("🔍 Checking for missing images in ImageKit...")
    
    # Initialize ImageKit
    imagekit = ImageKit(
        public_key=settings.IMAGEKIT_CONFIG['PUBLIC_KEY'],
        private_key=settings.IMAGEKIT_CONFIG['PRIVATE_KEY'],
        url_endpoint=settings.IMAGEKIT_CONFIG['URL_ENDPOINT']
    )
    
    # Get all files from ImageKit
    try:
        list_files = imagekit.list_files()
        existing_files = {file.name: file for file in list_files.list}
        print(f"✅ Found {len(existing_files)} files in ImageKit")
    except Exception as e:
        print(f"❌ Error getting files from ImageKit: {e}")
        return
    
    # Models to check
    models_to_check = [
        (HeroMedia, 'image', 'Hero Media'),
        (Church, 'logo', 'Church Logos'),
        (News, 'image', 'News Images'),
        (Ministry, 'image', 'Ministry Images'),
        (Sermon, 'thumbnail', 'Sermon Thumbnails'),
    ]
    
    missing_count = 0
    fixed_count = 0
    
    for model_class, field_name, model_name in models_to_check:
        print(f"\n📋 Checking {model_name}...")
        
        for obj in model_class.objects.all():
            field = getattr(obj, field_name)
            if field and field.name:
                # Extract filename from the field
                if hasattr(field, 'name'):
                    filename = field.name.split('/')[-1]  # Get just the filename
                else:
                    filename = str(field).split('/')[-1]
                
                # Check if file exists in ImageKit
                if filename not in existing_files:
                    print(f"   ❌ Missing: {filename}")
                    missing_count += 1
                    
                    # Create and upload a replacement
                    try:
                        print(f"   🔧 Creating replacement for: {filename}")
                        
                        # Create proper image
                        img_io = create_proper_image(filename)
                        
                        # Upload to ImageKit
                        upload = imagekit.upload_file(
                            file=img_io,
                            file_name=filename
                        )
                        
                        if upload.response_metadata.http_status_code == 200:
                            print(f"   ✅ Fixed: {filename}")
                            print(f"   🌐 New URL: {upload.url}")
                            fixed_count += 1
                        else:
                            print(f"   ❌ Upload failed for: {filename}")
                            
                    except Exception as e:
                        print(f"   ❌ Error fixing {filename}: {e}")
                else:
                    print(f"   ✅ Found: {filename}")
    
    print(f"\n📊 Summary:")
    print(f"   Missing files: {missing_count}")
    print(f"   Fixed files: {fixed_count}")
    
    if fixed_count > 0:
        print(f"\n🎉 Successfully fixed {fixed_count} missing images!")
    else:
        print(f"\n✅ All images are present in ImageKit!")

if __name__ == "__main__":
    check_and_fix_missing_images() 