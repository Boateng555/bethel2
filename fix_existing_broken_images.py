#!/usr/bin/env python3
"""
Fix existing broken images by re-uploading them to Cloudinary
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import HeroMedia, Church, News, Ministry, Sermon
from django.conf import settings
import cloudinary
import cloudinary.uploader
import requests
from io import BytesIO
import base64

def create_placeholder_image():
    """Create a placeholder image for missing files"""
    # Create a simple 400x300 placeholder image with text
    from PIL import Image, ImageDraw, ImageFont
    import io
    
    # Create a new image with a light gray background
    img = Image.new('RGB', (400, 300), color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Add some text
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except:
        font = None
    
    # Draw text
    text = "Image Placeholder"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (400 - text_width) // 2
    y = (300 - text_height) // 2
    
    draw.text((x, y), text, fill='#666666', font=font)
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr.getvalue()

def fix_broken_images():
    """Fix broken images by re-uploading them to Cloudinary"""
    
    print("🔧 Fixing broken images by re-uploading to Cloudinary...")
    
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET')
    )
    
    # Create placeholder image
    placeholder_image = create_placeholder_image()
    
    # Models to check for broken images
    models_to_check = [
        (HeroMedia, 'image', 'hero'),
        (Church, 'logo', 'churches/logos'),
        (Church, 'banner_image', 'churches/banners'),
        (News, 'image', 'news'),
        (Ministry, 'image', 'ministries'),
        (Sermon, 'thumbnail', 'sermons'),
    ]
    
    total_fixed = 0
    
    for model_class, field_name, folder in models_to_check:
        print(f"\n📋 Checking {model_class.__name__}.{field_name}...")
        
        # Get all objects with images
        objects = model_class.objects.filter(**{f"{field_name}__isnull": False})
        print(f"Found {objects.count()} objects with {field_name}")
        
        fixed_count = 0
        skipped_count = 0
        
        for obj in objects:
            image_field = getattr(obj, field_name)
            image_url = str(image_field)
            
            if not image_url.startswith('http'):
                print(f"  ⏭️  {model_class.__name__} {obj.id}: Not a Cloudinary URL, skipping")
                skipped_count += 1
                continue
            
            # Test if the URL is accessible
            try:
                response = requests.head(image_url, timeout=10)
                if response.status_code == 200:
                    print(f"  ✅ {model_class.__name__} {obj.id}: URL is accessible, skipping")
                    skipped_count += 1
                    continue
                else:
                    print(f"  ❌ {model_class.__name__} {obj.id}: URL not accessible ({response.status_code})")
            except Exception as e:
                print(f"  ❌ {model_class.__name__} {obj.id}: Error testing URL - {e}")
            
            # Try to re-upload the image
            try:
                print(f"  📤 {model_class.__name__} {obj.id}: Re-uploading...")
                
                # Extract filename from URL
                filename = image_url.split('/')[-1]
                # Clean up filename
                clean_filename = filename.split('_')[-1] if '_' in filename else filename
                clean_filename = clean_filename.replace('.jpg', '').replace('.png', '').replace('.jpeg', '')
                
                # Create unique public_id
                public_id = f"{folder}/{clean_filename}_{obj.id}"
                
                # Upload placeholder image to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    placeholder_image,
                    folder=folder,
                    public_id=public_id,
                    resource_type="image",
                    format="png",
                    overwrite=True
                )
                
                # Update the database with the new URL
                setattr(obj, field_name, upload_result['secure_url'])
                obj.save()
                
                print(f"  ✅ {model_class.__name__} {obj.id}: Re-uploaded successfully")
                print(f"     New URL: {upload_result['secure_url']}")
                fixed_count += 1
                total_fixed += 1
                
            except Exception as e:
                print(f"  ❌ {model_class.__name__} {obj.id}: Error re-uploading - {e}")
        
        print(f"  Summary: Fixed {fixed_count}, Skipped {skipped_count}")
    
    print(f"\n🎉 Total images fixed: {total_fixed}")
    
    if total_fixed > 0:
        print("\n💡 The broken images have been replaced with placeholder images.")
        print("   You can now upload the actual images through the admin interface.")
        print("   The placeholder images will be replaced with your real images.")

if __name__ == "__main__":
    fix_broken_images() 