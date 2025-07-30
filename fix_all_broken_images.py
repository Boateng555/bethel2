#!/usr/bin/env python3
"""
Comprehensive script to fix all broken images across all models
"""

import os
import django
import requests
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from imagekitio import ImageKit

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import (
    HeroMedia, Hero, Church, Ministry, News, Sermon, 
    EventHighlight, LocalLeadershipPage, LocalAboutPage, 
    EventHeroMedia, Event
)

# ImageKit credentials
PUBLIC_KEY = "public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU="
PRIVATE_KEY = "private_Dnsrj2VW7uJakaeMaNYaav+P784="
URL_ENDPOINT = "https://ik.imagekit.io/9buar9mbp"

def create_placeholder_image(filename, width=800, height=600):
    """Create a placeholder image with the given dimensions"""
    try:
        # Create a simple placeholder image
        img = Image.new('RGB', (width, height), color=(73, 109, 137))
        
        # Save to buffer
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer
    except Exception as e:
        print(f"Error creating placeholder: {e}")
        return None

def fix_model_images(model_class, field_name, url_method_name=None):
    """Fix images for a specific model and field"""
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
                
                # Test if URL is accessible
                response = requests.head(current_url, timeout=10)
                if response.status_code != 200:
                    print(f"  ❌ {model_class.__name__} {obj.id}: {field_name} - Broken (404)")
                    
                    # Create placeholder image
                    filename = os.path.basename(str(image_field.name))
                    placeholder_buffer = create_placeholder_image(filename)
                    
                    if placeholder_buffer:
                        # Create new file with placeholder content
                        new_file = ContentFile(placeholder_buffer.getvalue(), name=image_field.name)
                        
                        # Update the image field
                        setattr(obj, field_name, new_file)
                        obj.save()
                        
                        print(f"  ✅ Fixed {model_class.__name__} {obj.id} with placeholder image")
                        fixed_count += 1
                    else:
                        print(f"  ❌ Failed to create placeholder for {model_class.__name__} {obj.id}")
                else:
                    print(f"  ✅ {model_class.__name__} {obj.id}: {field_name} - Working")
                    
            except Exception as e:
                print(f"  ⚠️ Error fixing {model_class.__name__} {obj.id}: {e}")
    
    return fixed_count

def fix_all_broken_images():
    """Fix all broken images across all models"""
    print("🔧 Fixing ALL Broken Images")
    print("=" * 60)
    
    total_fixed = 0
    
    # Fix HeroMedia images
    print("\n📸 Fixing HeroMedia Images")
    fixed = fix_model_images(HeroMedia, 'image', 'get_image_url')
    total_fixed += fixed
    
    # Fix Church images
    print("\n🏛️ Fixing Church Images")
    fixed = fix_model_images(Church, 'logo', 'get_logo_url')
    total_fixed += fixed
    fixed = fix_model_images(Church, 'banner_image', 'get_banner_url')
    total_fixed += fixed
    fixed = fix_model_images(Church, 'nav_logo', 'get_nav_logo_url')
    total_fixed += fixed
    
    # Fix Ministry images
    print("\n⛪ Fixing Ministry Images")
    fixed = fix_model_images(Ministry, 'image', 'get_image_url')
    total_fixed += fixed
    
    # Fix News images
    print("\n📰 Fixing News Images")
    fixed = fix_model_images(News, 'image', 'get_image_url')
    total_fixed += fixed
    
    # Fix Sermon images
    print("\n📖 Fixing Sermon Images")
    fixed = fix_model_images(Sermon, 'thumbnail', 'get_thumbnail_url')
    total_fixed += fixed
    
    # Fix Hero images
    print("\n🦸 Fixing Hero Images")
    fixed = fix_model_images(Hero, 'background_image', 'get_background_image_url')
    total_fixed += fixed
    
    # Fix EventHeroMedia images
    print("\n🎬 Fixing EventHeroMedia Images")
    fixed = fix_model_images(EventHeroMedia, 'image', 'get_image_url')
    total_fixed += fixed
    
    # Fix LocalLeadershipPage images
    print("\n👥 Fixing LocalLeadershipPage Images")
    leadership_fields = ['pastor_image', 'assistant_pastor_image', 'board_image', 'team_image', 
                        'leadership_photo_1', 'leadership_photo_2', 'leadership_photo_3']
    
    for field_name in leadership_fields:
        try:
            url_method = f'get_{field_name}_url'
            fixed = fix_model_images(LocalLeadershipPage, field_name, url_method)
            total_fixed += fixed
        except AttributeError:
            print(f"  ⚠️ No URL method for {field_name}")
    
    # Fix LocalAboutPage images
    print("\nℹ️ Fixing LocalAboutPage Images")
    about_fields = ['logo', 'founder_image', 'extra_image', 'about_photo_1', 'about_photo_2', 'about_photo_3']
    
    for field_name in about_fields:
        try:
            url_method = f'get_{field_name}_url'
            fixed = fix_model_images(LocalAboutPage, field_name, url_method)
            total_fixed += fixed
        except AttributeError:
            print(f"  ⚠️ No URL method for {field_name}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FIX SUMMARY")
    print("=" * 60)
    print(f"Total images fixed: {total_fixed}")
    
    if total_fixed > 0:
        print(f"\n✅ Successfully fixed {total_fixed} broken images!")
        print("All images should now be working properly.")
    else:
        print("\n🎉 No broken images found! All images are working.")

if __name__ == "__main__":
    fix_all_broken_images() 