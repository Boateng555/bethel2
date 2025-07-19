#!/usr/bin/env python
"""
Script to verify that images are working correctly in production
"""
import os
import requests
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import HeroMedia, Church, News, Ministry, Sermon

def verify_production_images():
    """Verify that images are working in production"""
    print("🔍 Verifying Production Images")
    print("=" * 50)
    
    # Production URL
    production_url = "https://web-production-158c.up.railway.app"
    
    print(f"🌐 Production URL: {production_url}")
    
    # Test production site accessibility
    try:
        response = requests.get(production_url, timeout=10)
        if response.status_code == 200:
            print("✅ Production site is accessible")
        else:
            print(f"❌ Production site returned status: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot access production site: {e}")
        return
    
    # Check model images
    models_to_check = [
        (HeroMedia, 'image', 'Hero Media'),
        (Church, 'logo', 'Church Logos'),
        (News, 'image', 'News Images'),
        (Ministry, 'image', 'Ministry Images'),
        (Sermon, 'thumbnail', 'Sermon Thumbnails'),
    ]
    
    total_images = 0
    working_images = 0
    broken_images = 0
    
    for model, field_name, model_name in models_to_check:
        print(f"\n📋 Checking {model_name}...")
        
        instances = model.objects.all()
        for instance in instances:
            field = getattr(instance, field_name)
            if not field:
                continue
            
            total_images += 1
            field_str = str(field)
            
            # Generate the full URL
            if 'ik.imagekit.io' in field_str:
                # Already a full ImageKit URL
                image_url = field_str
            elif field_str.startswith('http'):
                # Already a full URL
                image_url = field_str
            else:
                # ImageKit path - construct URL
                imagekit_endpoint = "https://ik.imagekit.io/144671b7r"
                image_url = f"{imagekit_endpoint}/{field_str}"
            
            print(f"  📸 {instance}: {image_url}")
            
            # Test if image is accessible
            try:
                img_response = requests.head(image_url, timeout=10)
                if img_response.status_code == 200:
                    print(f"    ✅ Image accessible")
                    working_images += 1
                else:
                    print(f"    ❌ Image not accessible (Status: {img_response.status_code})")
                    broken_images += 1
            except Exception as e:
                print(f"    ❌ Image error: {e}")
                broken_images += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Image Status Summary:")
    print(f"  Total Images: {total_images}")
    print(f"  ✅ Working: {working_images}")
    print(f"  ❌ Broken: {broken_images}")
    
    if working_images > 0:
        print(f"\n🎉 {working_images} images are working correctly!")
        print(f"💡 Visit {production_url} to see your images in action.")
    
    if broken_images > 0:
        print(f"\n⚠️  {broken_images} images need attention.")
        print(f"🔧 Check the ImageKit dashboard for any issues.")

if __name__ == "__main__":
    verify_production_images() 