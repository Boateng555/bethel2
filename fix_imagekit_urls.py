#!/usr/bin/env python
"""
Script to fix all image URLs to use ImageKit and remove old Cloudinary/local URLs
"""
import os
import django
import requests
from django.core.files.base import ContentFile

# Set production mode to use ImageKit
os.environ['DJANGO_DEBUG'] = 'False'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from core.models import HeroMedia, Church, News, Ministry, Sermon, Event

def fix_all_imagekit_urls():
    """Fix all image URLs to use ImageKit"""
    print("🔧 Fixing All Image URLs to Use ImageKit")
    print("=" * 60)
    
    # Check if ImageKit is configured
    if not all(settings.IMAGEKIT_CONFIG.values()):
        print("❌ ImageKit not configured!")
        return
    
    print("✅ ImageKit configured")
    print(f"📦 Storage Backend: {settings.DEFAULT_FILE_STORAGE}")
    
    # Models to fix
    models_to_fix = [
        (HeroMedia, 'image', 'hero'),
        (Church, 'logo', 'churches/logos'),
        (News, 'image', 'news'),
        (Ministry, 'image', 'ministries'),
        (Sermon, 'thumbnail', 'sermons/thumbnails'),
    ]
    
    total_fixed = 0
    total_errors = 0
    
    for model, field_name, folder in models_to_fix:
        print(f"\n📋 Fixing {model.__name__}.{field_name}...")
        
        instances = model.objects.all()
        print(f"  Found {instances.count()} instances")
        
        for instance in instances:
            field = getattr(instance, field_name)
            if not field:
                continue
                
            field_str = str(field)
            print(f"  📋 {instance} - Current: {field_str}")
            
            # Check if it's already a proper ImageKit path
            if not field_str.startswith('http') and '/' in field_str:
                print(f"    ✅ Already ImageKit path")
                continue
            
            # Check if it's already ImageKit URL
            if 'ik.imagekit.io' in field_str:
                print(f"    ✅ Already ImageKit URL")
                continue
            
            # Handle Cloudinary URLs
            if 'res.cloudinary.com' in field_str:
                try:
                    print(f"    📤 Downloading from Cloudinary...")
                    
                    # Download from Cloudinary
                    response = requests.get(field_str, timeout=30)
                    if response.status_code != 200:
                        print(f"      ❌ Failed to download: {response.status_code}")
                        total_errors += 1
                        continue
                    
                    # Get filename
                    filename = os.path.basename(field_str.split('/')[-1])
                    if '?' in filename:
                        filename = filename.split('?')[0]
                    
                    # Create new file path for ImageKit
                    new_path = f"{folder}/{filename}"
                    
                    # Create ContentFile
                    content_file = ContentFile(response.content, name=filename)
                    
                    # Save to ImageKit
                    from django.core.files.storage import default_storage
                    saved_path = default_storage.save(new_path, content_file)
                    
                    # Update the field
                    setattr(instance, field_name, saved_path)
                    instance.save()
                    
                    print(f"      ✅ Migrated to: {saved_path}")
                    total_fixed += 1
                    
                except Exception as e:
                    print(f"      ❌ Error: {e}")
                    total_errors += 1
            
            # Handle local file paths
            elif field_str.startswith('/media/') or field_str.startswith('media/'):
                try:
                    print(f"    📁 Converting local path...")
                    
                    # Clean the path
                    clean_path = field_str.replace('/media/', '').replace('media/', '')
                    
                    # Create new path in ImageKit folder structure
                    new_path = f"{folder}/{os.path.basename(clean_path)}"
                    
                    # Update the field
                    setattr(instance, field_name, new_path)
                    instance.save()
                    
                    print(f"      ✅ Converted to: {new_path}")
                    total_fixed += 1
                    
                except Exception as e:
                    print(f"      ❌ Error: {e}")
                    total_errors += 1
            
            # Handle other HTTP URLs (not Cloudinary)
            elif field_str.startswith('http'):
                try:
                    print(f"    🌐 Downloading from external URL...")
                    
                    # Download from URL
                    response = requests.get(field_str, timeout=30)
                    if response.status_code != 200:
                        print(f"      ❌ Failed to download: {response.status_code}")
                        total_errors += 1
                        continue
                    
                    # Get filename
                    filename = os.path.basename(field_str.split('/')[-1])
                    if '?' in filename:
                        filename = filename.split('?')[0]
                    
                    # Create new file path for ImageKit
                    new_path = f"{folder}/{filename}"
                    
                    # Create ContentFile
                    content_file = ContentFile(response.content, name=filename)
                    
                    # Save to ImageKit
                    from django.core.files.storage import default_storage
                    saved_path = default_storage.save(new_path, content_file)
                    
                    # Update the field
                    setattr(instance, field_name, saved_path)
                    instance.save()
                    
                    print(f"      ✅ Migrated to: {saved_path}")
                    total_fixed += 1
                    
                except Exception as e:
                    print(f"      ❌ Error: {e}")
                    total_errors += 1
    
    print("\n" + "=" * 60)
    print(f"🎉 URL Fix completed!")
    print(f"✅ Successfully fixed: {total_fixed}")
    print(f"❌ Errors: {total_errors}")
    
    if total_fixed > 0:
        print("\n🔄 All images now use ImageKit!")
        print("💡 Deploy to Railway to see the changes in production.")

if __name__ == "__main__":
    fix_all_imagekit_urls() 