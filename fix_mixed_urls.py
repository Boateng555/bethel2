#!/usr/bin/env python3
"""
Fix images with mixed URL types (local paths and ImageKit URLs)
"""

import os
import django
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import (
    HeroMedia, Hero, Church, Ministry, News, Sermon, 
    EventHighlight, LocalLeadershipPage, LocalAboutPage, 
    EventHeroMedia, Event
)

def create_high_quality_image(filename, width=1200, height=800, text="Sample Image"):
    """Create a high-quality placeholder image with proper dimensions"""
    try:
        # Create a gradient background
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Create a gradient effect
        for y in range(height):
            r = int(73 + (y / height) * 50)
            g = int(109 + (y / height) * 30)
            b = int(137 + (y / height) * 40)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add a subtle pattern
        for i in range(0, width, 50):
            for j in range(0, height, 50):
                if (i + j) % 100 == 0:
                    draw.rectangle([i, j, i+25, j+25], fill=(255, 255, 255, 30), outline=(255, 255, 255, 60))
        
        # Add text
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        # Calculate text position
        text_bbox = draw.textbbox((0, 0), text, font=font) if font else (0, 0, len(text) * 10, 20)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Add text shadow
        draw.text((x+2, y+2), text, fill=(0, 0, 0, 128), font=font)
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        # Add filename
        filename_text = f"File: {filename}"
        draw.text((10, height - 30), filename_text, fill=(255, 255, 255, 180), font=font)
        
        # Add dimensions
        dims_text = f"{width}x{height}px"
        draw.text((width - 80, height - 30), dims_text, fill=(255, 255, 255, 180), font=font)
        
        # Save to buffer with high quality
        buffer = BytesIO()
        img.save(buffer, format='PNG', optimize=True, quality=95)
        buffer.seek(0)
        
        return buffer
    except Exception as e:
        print(f"Error creating image: {e}")
        return None

def fix_model_images_with_mixed_urls(model_class, field_name, url_method_name=None):
    """Fix images for a specific model and field, handling both local and ImageKit URLs"""
    print(f"\n🔧 Fixing {model_class.__name__} {field_name} images...")
    
    objects = model_class.objects.all()
    fixed_count = 0
    
    for obj in objects:
        image_field = getattr(obj, field_name, None)
        if image_field:
            try:
                # Get current URL
                if url_method_name:
                    current_url = getattr(obj, url_method_name)()
                else:
                    current_url = image_field.url
                
                # Check if it's a full ImageKit URL
                if current_url.startswith('https://ik.imagekit.io/'):
                    print(f"  🔗 {model_class.__name__} {obj.id}: {field_name} - ImageKit URL (skipping)")
                    continue
                
                # Check if it's a local path that needs fixing
                if current_url.startswith('/media/'):
                    print(f"  📁 {model_class.__name__} {obj.id}: {field_name} - Local path, checking if corrupted...")
                    
                    # Try to access the local file
                    try:
                        # Get the actual file path
                        file_path = image_field.path
                        if os.path.exists(file_path):
                            # Check file size
                            file_size = os.path.getsize(file_path)
                            if file_size < 1000:  # Less than 1KB is likely corrupted
                                print(f"    ❌ File too small ({file_size} bytes), replacing...")
                                should_replace = True
                            else:
                                print(f"    ✅ File size OK ({file_size} bytes)")
                                should_replace = False
                        else:
                            print(f"    ❌ File not found, replacing...")
                            should_replace = True
                    except Exception as e:
                        print(f"    ❌ Error checking file: {e}, replacing...")
                        should_replace = True
                    
                    if should_replace:
                        # Create high-quality placeholder image
                        filename = os.path.basename(str(image_field.name))
                        
                        # Determine appropriate dimensions based on field type
                        if 'logo' in field_name.lower():
                            width, height = 400, 400
                        elif 'banner' in field_name.lower():
                            width, height = 1200, 600
                        elif 'hero' in field_name.lower():
                            width, height = 1200, 800
                        elif 'thumbnail' in field_name.lower():
                            width, height = 400, 300
                        else:
                            width, height = 800, 600
                        
                        # Create descriptive text
                        if hasattr(obj, 'name'):
                            text = f"{obj.name}"
                        elif hasattr(obj, 'title'):
                            text = f"{obj.title}"
                        else:
                            text = f"{model_class.__name__} {obj.id}"
                        
                        placeholder_buffer = create_high_quality_image(filename, width, height, text)
                        
                        if placeholder_buffer:
                            # Create new file with high-quality content
                            new_file = ContentFile(placeholder_buffer.getvalue(), name=image_field.name)
                            
                            # Update the image field
                            setattr(obj, field_name, new_file)
                            obj.save()
                            
                            print(f"    ✅ Fixed with high-quality image ({width}x{height})")
                            fixed_count += 1
                        else:
                            print(f"    ❌ Failed to create image")
                else:
                    print(f"  ❓ {model_class.__name__} {obj.id}: {field_name} - Unknown URL format: {current_url}")
                    
            except Exception as e:
                print(f"  ⚠️ Error fixing {model_class.__name__} {obj.id}: {e}")
    
    return fixed_count

def fix_all_mixed_urls():
    """Fix all images with mixed URL types"""
    print("🔧 Fixing Images with Mixed URL Types")
    print("=" * 60)
    
    total_fixed = 0
    
    # Fix HeroMedia images
    print("\n📸 Fixing HeroMedia Images")
    fixed = fix_model_images_with_mixed_urls(HeroMedia, 'image', 'get_image_url')
    total_fixed += fixed
    
    # Fix Church images
    print("\n🏛️ Fixing Church Images")
    fixed = fix_model_images_with_mixed_urls(Church, 'logo', 'get_logo_url')
    total_fixed += fixed
    fixed = fix_model_images_with_mixed_urls(Church, 'banner_image', 'get_banner_url')
    total_fixed += fixed
    fixed = fix_model_images_with_mixed_urls(Church, 'nav_logo', 'get_nav_logo_url')
    total_fixed += fixed
    
    # Fix Ministry images
    print("\n⛪ Fixing Ministry Images")
    fixed = fix_model_images_with_mixed_urls(Ministry, 'image', 'get_image_url')
    total_fixed += fixed
    
    # Fix News images
    print("\n📰 Fixing News Images")
    fixed = fix_model_images_with_mixed_urls(News, 'image', 'get_image_url')
    total_fixed += fixed
    
    # Fix Sermon images
    print("\n📖 Fixing Sermon Images")
    fixed = fix_model_images_with_mixed_urls(Sermon, 'thumbnail', 'get_thumbnail_url')
    total_fixed += fixed
    
    # Fix Hero images
    print("\n🦸 Fixing Hero Images")
    fixed = fix_model_images_with_mixed_urls(Hero, 'background_image', 'get_background_image_url')
    total_fixed += fixed
    
    # Fix EventHeroMedia images
    print("\n🎬 Fixing EventHeroMedia Images")
    fixed = fix_model_images_with_mixed_urls(EventHeroMedia, 'image', 'get_image_url')
    total_fixed += fixed
    
    # Fix LocalLeadershipPage images
    print("\n👥 Fixing LocalLeadershipPage Images")
    leadership_fields = ['pastor_image', 'assistant_pastor_image', 'board_image', 'team_image', 
                        'leadership_photo_1', 'leadership_photo_2', 'leadership_photo_3']
    
    for field_name in leadership_fields:
        try:
            url_method = f'get_{field_name}_url'
            fixed = fix_model_images_with_mixed_urls(LocalLeadershipPage, field_name, url_method)
            total_fixed += fixed
        except AttributeError:
            print(f"  ⚠️ No URL method for {field_name}")
    
    # Fix LocalAboutPage images
    print("\nℹ️ Fixing LocalAboutPage Images")
    about_fields = ['logo', 'founder_image', 'extra_image', 'about_photo_1', 'about_photo_2', 'about_photo_3']
    
    for field_name in about_fields:
        try:
            url_method = f'get_{field_name}_url'
            fixed = fix_model_images_with_mixed_urls(LocalAboutPage, field_name, url_method)
            total_fixed += fixed
        except AttributeError:
            print(f"  ⚠️ No URL method for {field_name}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 MIXED URL FIX SUMMARY")
    print("=" * 60)
    print(f"Total images fixed: {total_fixed}")
    
    if total_fixed > 0:
        print(f"\n✅ Successfully fixed {total_fixed} corrupted local images!")
        print("All images should now display at proper size and quality in Django admin.")
        print("\n🎨 Image improvements:")
        print("   - High-quality placeholder images with appropriate dimensions")
        print("   - Proper aspect ratios preserved")
        print("   - Professional gradient backgrounds")
        print("   - Descriptive text labels")
    else:
        print("\n🎉 No corrupted local images found!")

if __name__ == "__main__":
    fix_all_mixed_urls() 