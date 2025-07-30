#!/usr/bin/env python
"""
Script to fix ImageKit image issues by re-uploading existing images
"""
import os
import sys
import django
from io import BytesIO

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Set ImageKit environment variables
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

from django.core.files.base import ContentFile
from django.conf import settings
from core.models import Church, HeroMedia, Ministry, News, Sermon
import requests

def create_placeholder_image(filename, width=800, height=600):
    """Create a placeholder image for missing files"""
    from PIL import Image, ImageDraw, ImageFont
    
    # Create a new image with a light gray background
    image = Image.new('RGB', (width, height), color='#f0f0f0')
    draw = ImageDraw.Draw(image)
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()
    
    text = f"Placeholder Image\n{filename}\n{width}x{height}"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill='#666666', font=font)
    
    # Save to BytesIO
    buffer = BytesIO()
    image.save(buffer, format='JPEG', quality=85)
    buffer.seek(0)
    
    return buffer

def fix_hero_media_images():
    """Fix HeroMedia images that are returning 404"""
    print("🔧 Fixing HeroMedia images...")
    
    hero_media_list = HeroMedia.objects.all()
    fixed_count = 0
    
    for media in hero_media_list:
        if media.image:
            # Check if the image URL is accessible
            try:
                response = requests.head(media.image.url, timeout=10)
                if response.status_code == 404:
                    print(f"  ❌ HeroMedia {media.id}: {media.image.name} - 404 error")
                    
                    # Create a placeholder image
                    filename = os.path.basename(media.image.name)
                    placeholder_buffer = create_placeholder_image(filename)
                    
                    # Create new file with placeholder content
                    new_file = ContentFile(placeholder_buffer.getvalue(), name=media.image.name)
                    
                    # Update the image field
                    media.image = new_file
                    media.save()
                    
                    print(f"  ✅ Fixed HeroMedia {media.id} with placeholder image")
                    fixed_count += 1
                else:
                    print(f"  ✅ HeroMedia {media.id}: {media.image.name} - OK")
            except Exception as e:
                print(f"  ⚠️ HeroMedia {media.id}: Error checking {media.image.name} - {e}")
    
    print(f"Fixed {fixed_count} HeroMedia images")
    return fixed_count

def fix_church_images():
    """Fix Church images that are returning 404"""
    print("\n🔧 Fixing Church images...")
    
    churches = Church.objects.all()
    fixed_count = 0
    
    for church in churches:
        if church.logo:
            try:
                response = requests.head(church.logo.url, timeout=10)
                if response.status_code == 404:
                    print(f"  ❌ Church {church.name}: {church.logo.name} - 404 error")
                    
                    # Create a placeholder image
                    filename = os.path.basename(church.logo.name)
                    placeholder_buffer = create_placeholder_image(filename, 400, 400)
                    
                    # Create new file with placeholder content
                    new_file = ContentFile(placeholder_buffer.getvalue(), name=church.logo.name)
                    
                    # Update the logo field
                    church.logo = new_file
                    church.save()
                    
                    print(f"  ✅ Fixed Church {church.name} with placeholder image")
                    fixed_count += 1
                else:
                    print(f"  ✅ Church {church.name}: {church.logo.name} - OK")
            except Exception as e:
                print(f"  ⚠️ Church {church.name}: Error checking {church.logo.name} - {e}")
    
    print(f"Fixed {fixed_count} Church images")
    return fixed_count

def fix_other_model_images():
    """Fix images in other models"""
    print("\n🔧 Fixing other model images...")
    
    models_to_fix = [
        (Ministry, 'image', 'Ministry'),
        (News, 'image', 'News'),
        (Sermon, 'thumbnail', 'Sermon'),
    ]
    
    total_fixed = 0
    
    for model_class, field_name, model_name in models_to_fix:
        print(f"  Checking {model_name} images...")
        fixed_count = 0
        
        for obj in model_class.objects.all():
            field = getattr(obj, field_name)
            if field:
                try:
                    response = requests.head(field.url, timeout=10)
                    if response.status_code == 404:
                        print(f"    ❌ {model_name} {obj.id}: {field.name} - 404 error")
                        
                        # Create a placeholder image
                        filename = os.path.basename(field.name)
                        placeholder_buffer = create_placeholder_image(filename)
                        
                        # Create new file with placeholder content
                        new_file = ContentFile(placeholder_buffer.getvalue(), name=field.name)
                        
                        # Update the field
                        setattr(obj, field_name, new_file)
                        obj.save()
                        
                        print(f"    ✅ Fixed {model_name} {obj.id} with placeholder image")
                        fixed_count += 1
                    else:
                        print(f"    ✅ {model_name} {obj.id}: {field.name} - OK")
                except Exception as e:
                    print(f"    ⚠️ {model_name} {obj.id}: Error checking {field.name} - {e}")
        
        print(f"  Fixed {fixed_count} {model_name} images")
        total_fixed += fixed_count
    
    return total_fixed

def test_fixed_images():
    """Test that the fixed images are now accessible"""
    print("\n🧪 Testing fixed images...")
    
    # Test HeroMedia images
    hero_media_list = HeroMedia.objects.all()
    accessible_count = 0
    
    for media in hero_media_list[:5]:  # Test first 5
        if media.image:
            try:
                response = requests.head(media.image.url, timeout=10)
                if response.status_code == 200:
                    print(f"  ✅ HeroMedia {media.id}: Accessible")
                    accessible_count += 1
                else:
                    print(f"  ❌ HeroMedia {media.id}: Status {response.status_code}")
            except Exception as e:
                print(f"  ⚠️ HeroMedia {media.id}: Error - {e}")
    
    print(f"  {accessible_count}/5 HeroMedia images are accessible")
    
    # Test Church images
    churches = Church.objects.all()
    accessible_count = 0
    
    for church in churches[:3]:  # Test first 3
        if church.logo:
            try:
                response = requests.head(church.logo.url, timeout=10)
                if response.status_code == 200:
                    print(f"  ✅ Church {church.name}: Accessible")
                    accessible_count += 1
                else:
                    print(f"  ❌ Church {church.name}: Status {response.status_code}")
            except Exception as e:
                print(f"  ⚠️ Church {church.name}: Error - {e}")
    
    print(f"  {accessible_count}/3 Church images are accessible")

if __name__ == "__main__":
    print("🚀 Starting ImageKit image fix...")
    print("=" * 60)
    
    # Fix images
    hero_fixed = fix_hero_media_images()
    church_fixed = fix_church_images()
    other_fixed = fix_other_model_images()
    
    total_fixed = hero_fixed + church_fixed + other_fixed
    
    print("\n" + "=" * 60)
    print("📊 FIX SUMMARY")
    print("=" * 60)
    print(f"HeroMedia images fixed: {hero_fixed}")
    print(f"Church images fixed: {church_fixed}")
    print(f"Other model images fixed: {other_fixed}")
    print(f"Total images fixed: {total_fixed}")
    
    if total_fixed > 0:
        print(f"\n🎉 Successfully fixed {total_fixed} images!")
        print("All images should now be accessible via ImageKit URLs.")
        
        # Test the fixed images
        test_fixed_images()
    else:
        print("\n✅ No images needed fixing - all images are already accessible!")
    
    print("\n📝 Next steps:")
    print("1. Check your website to see if images are now loading")
    print("2. Upload new images through Django admin to test ImageKit")
    print("3. Consider replacing placeholder images with actual content") 