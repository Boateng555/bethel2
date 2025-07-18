#!/usr/bin/env python3
"""
Comprehensive image fix - Check and fix ALL image-related issues
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import (
    Church, News, Ministry, Sermon, HeroMedia, Event, 
    EventSpeaker, AboutPage, LeadershipPage, LocalAboutPage, 
    LocalLeadershipPage, EventHighlight, EventHeroMedia, Hero
)
from django.conf import settings
import cloudinary
import cloudinary.uploader
import requests
from PIL import Image, ImageDraw, ImageFont
import io

def create_placeholder_image(width=400, height=300, text="Image Placeholder"):
    """Create a placeholder image"""
    img = Image.new('RGB', (width, height), color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill='#666666', font=font)
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr.getvalue()

def comprehensive_image_fix():
    """Comprehensive fix for all image issues"""
    
    print("🔧 COMPREHENSIVE IMAGE FIX - Checking and fixing ALL image issues...")
    print(f"Environment: {'Production' if not settings.DEBUG else 'Development'}")
    print(f"Storage: {settings.DEFAULT_FILE_STORAGE}")
    print()
    
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET')
    )
    
    # All models with images to check
    models_to_check = [
        (Church, 'logo', 'churches/logos', 400, 400, 'Church Logo'),
        (Church, 'banner_image', 'churches/banners', 1200, 600, 'Church Banner'),
        (News, 'image', 'news', 800, 600, 'News Image'),
        (Ministry, 'image', 'ministries', 600, 400, 'Ministry Image'),
        (Sermon, 'thumbnail', 'sermons', 400, 300, 'Sermon Thumbnail'),
        (EventSpeaker, 'photo', 'speakers', 300, 300, 'Speaker Photo'),
        (EventHighlight, 'image', 'highlights', 800, 600, 'Event Highlight'),
        (EventHeroMedia, 'image', 'event_hero', 1200, 800, 'Event Hero Image'),
        (HeroMedia, 'image', 'hero', 1200, 800, 'Hero Image'),
    ]
    
    # Page models with multiple image fields
    page_models = [
        (AboutPage, ['logo', 'founder_image', 'extra_image'], 'about', 600, 600),
        (LeadershipPage, ['chairman_image', 'vice_chairman_image', 'board_image', 'team_image', 
                         'leadership_photo_1', 'leadership_photo_2', 'leadership_photo_3'], 'leadership', 400, 400),
        (LocalAboutPage, ['logo', 'founder_image', 'extra_image', 'about_photo_1', 'about_photo_2', 'about_photo_3'], 'local_about', 600, 600),
        (LocalLeadershipPage, ['pastor_image', 'assistant_pastor_image', 'board_image', 'team_image',
                              'leadership_photo_1', 'leadership_photo_2', 'leadership_photo_3'], 'local_leadership', 400, 400),
    ]
    
    total_fixed = 0
    total_checked = 0
    
    # Fix regular models
    for model_class, field_name, folder, width, height, label in models_to_check:
        print(f"\n📋 Checking {model_class.__name__}.{field_name}...")
        
        objects = model_class.objects.all()
        print(f"Found {objects.count()} {model_class.__name__} objects")
        
        fixed_count = 0
        checked_count = 0
        
        for obj in objects:
            checked_count += 1
            total_checked += 1
            
            image_field = getattr(obj, field_name)
            image_url = str(image_field) if image_field else ""
            
            # Skip if no image field
            if not image_field:
                print(f"  ⏭️  {model_class.__name__} {obj.id}: No {field_name}")
                continue
            
            # Check if it's a Cloudinary URL
            if image_url.startswith('http'):
                # Test if the URL is accessible
                try:
                    response = requests.head(image_url, timeout=10)
                    if response.status_code == 200:
                        print(f"  ✅ {model_class.__name__} {obj.id}: {label} is accessible")
                        continue
                    else:
                        print(f"  ❌ {model_class.__name__} {obj.id}: {label} not accessible ({response.status_code})")
                except Exception as e:
                    print(f"  ❌ {model_class.__name__} {obj.id}: Error testing {label} - {e}")
            else:
                print(f"  📁 {model_class.__name__} {obj.id}: {label} is local file")
                continue
            
            # Fix broken image by uploading placeholder
            try:
                print(f"  📤 {model_class.__name__} {obj.id}: Fixing {label}...")
                
                # Create placeholder
                placeholder = create_placeholder_image(width, height, label)
                
                # Create unique public_id
                public_id = f"{folder}/placeholder_{obj.id}"
                
                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    placeholder,
                    folder=folder,
                    public_id=public_id,
                    resource_type="image",
                    format="png",
                    overwrite=True
                )
                
                # Update database
                setattr(obj, field_name, upload_result['secure_url'])
                obj.save()
                
                print(f"  ✅ {model_class.__name__} {obj.id}: {label} fixed")
                print(f"     URL: {upload_result['secure_url']}")
                fixed_count += 1
                total_fixed += 1
                
            except Exception as e:
                print(f"  ❌ {model_class.__name__} {obj.id}: Error fixing {label} - {e}")
        
        print(f"  Summary: Fixed {fixed_count}/{checked_count} {label}s")
    
    # Fix page models with multiple image fields
    for model_class, field_names, folder, width, height in page_models:
        print(f"\n📋 Checking {model_class.__name__}...")
        
        objects = model_class.objects.all()
        print(f"Found {objects.count()} {model_class.__name__} objects")
        
        fixed_count = 0
        checked_count = 0
        
        for obj in objects:
            checked_count += 1
            total_checked += 1
            
            for field_name in field_names:
                image_field = getattr(obj, field_name)
                image_url = str(image_field) if image_field else ""
                
                if not image_field:
                    continue
                
                if image_url.startswith('http'):
                    try:
                        response = requests.head(image_url, timeout=10)
                        if response.status_code == 200:
                            continue
                        else:
                            print(f"  ❌ {model_class.__name__} {obj.id}.{field_name}: Not accessible")
                    except Exception as e:
                        print(f"  ❌ {model_class.__name__} {obj.id}.{field_name}: Error - {e}")
                else:
                    continue
                
                # Fix broken image
                try:
                    print(f"  📤 {model_class.__name__} {obj.id}.{field_name}: Fixing...")
                    
                    placeholder = create_placeholder_image(width, height, f"{model_class.__name__} {field_name}")
                    public_id = f"{folder}/placeholder_{obj.id}_{field_name}"
                    
                    upload_result = cloudinary.uploader.upload(
                        placeholder,
                        folder=folder,
                        public_id=public_id,
                        resource_type="image",
                        format="png",
                        overwrite=True
                    )
                    
                    setattr(obj, field_name, upload_result['secure_url'])
                    obj.save()
                    
                    print(f"  ✅ {model_class.__name__} {obj.id}.{field_name}: Fixed")
                    fixed_count += 1
                    total_fixed += 1
                    
                except Exception as e:
                    print(f"  ❌ {model_class.__name__} {obj.id}.{field_name}: Error - {e}")
        
        print(f"  Summary: Fixed {fixed_count} fields in {checked_count} {model_class.__name__} objects")
    
    # Check for any empty image fields and add placeholders
    print(f"\n🖼️ Adding placeholders to empty image fields...")
    
    for model_class, field_name, folder, width, height, label in models_to_check:
        empty_objects = model_class.objects.filter(**{f"{field_name}__isnull": True}) | model_class.objects.filter(**{field_name: ""})
        
        if empty_objects.exists():
            print(f"  📋 {model_class.__name__}.{field_name}: {empty_objects.count()} empty fields")
            
            for obj in empty_objects:
                try:
                    placeholder = create_placeholder_image(width, height, label)
                    public_id = f"{folder}/placeholder_{obj.id}"
                    
                    upload_result = cloudinary.uploader.upload(
                        placeholder,
                        folder=folder,
                        public_id=public_id,
                        resource_type="image",
                        format="png",
                        overwrite=True
                    )
                    
                    setattr(obj, field_name, upload_result['secure_url'])
                    obj.save()
                    
                    print(f"    ✅ {model_class.__name__} {obj.id}: Added {label}")
                    total_fixed += 1
                    
                except Exception as e:
                    print(f"    ❌ {model_class.__name__} {obj.id}: Error - {e}")
    
    print(f"\n🎉 COMPREHENSIVE IMAGE FIX COMPLETED!")
    print(f"  Total objects checked: {total_checked}")
    print(f"  Total images fixed: {total_fixed}")
    
    if total_fixed > 0:
        print(f"\n💡 All broken images have been replaced with working placeholders.")
        print(f"   You can now see images on your website instead of broken icons.")
        print(f"   Replace placeholders with real images through the admin interface.")
    else:
        print(f"\n✅ All images are working correctly!")

if __name__ == "__main__":
    comprehensive_image_fix() 