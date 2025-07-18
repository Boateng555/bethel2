#!/usr/bin/env python3
"""
Add placeholder images to all empty image fields
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

def add_placeholder_images():
    """Add placeholder images to empty image fields"""
    
    print("🖼️ Adding placeholder images to empty image fields...")
    
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET')
    )
    
    # Create placeholder image
    placeholder_image = create_placeholder_image()
    
    # Models to check for empty images
    models_to_check = [
        (HeroMedia, 'image', 'hero'),
        (Church, 'logo', 'churches/logos'),
        (Church, 'banner_image', 'churches/banners'),
        (News, 'image', 'news'),
        (Ministry, 'image', 'ministries'),
        (Sermon, 'thumbnail', 'sermons'),
    ]
    
    total_added = 0
    
    for model_class, field_name, folder in models_to_check:
        print(f"\n📋 Checking {model_class.__name__}.{field_name}...")
        
        # Get all objects with empty images
        objects = model_class.objects.filter(**{f"{field_name}__isnull": True}) | model_class.objects.filter(**{field_name: ""})
        print(f"Found {objects.count()} objects with empty {field_name}")
        
        added_count = 0
        
        for obj in objects:
            try:
                print(f"  📤 {model_class.__name__} {obj.id}: Adding placeholder...")
                
                # Create unique public_id
                public_id = f"{folder}/placeholder_{obj.id}"
                
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
                
                print(f"  ✅ {model_class.__name__} {obj.id}: Placeholder added successfully")
                print(f"     URL: {upload_result['secure_url']}")
                added_count += 1
                total_added += 1
                
            except Exception as e:
                print(f"  ❌ {model_class.__name__} {obj.id}: Error adding placeholder - {e}")
        
        print(f"  Summary: Added {added_count} placeholders")
    
    print(f"\n🎉 Total placeholders added: {total_added}")
    
    if total_added > 0:
        print("\n💡 Placeholder images have been added to all empty image fields.")
        print("   You can now see these placeholders on your website.")
        print("   Replace them with actual images through the admin interface.")

if __name__ == "__main__":
    add_placeholder_images() 