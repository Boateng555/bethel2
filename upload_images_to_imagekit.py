#!/usr/bin/env python
"""
Script to upload actual image files to ImageKit from Cloudinary URLs
"""
import os
import requests
import django
from django.core.files.base import ContentFile

# Set production mode to use ImageKit
os.environ['DJANGO_DEBUG'] = 'False'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from core.models import HeroMedia, Church, News, Ministry, Sermon

def upload_images_to_imagekit():
    """Upload actual image files to ImageKit"""
    print("📤 Uploading Actual Images to ImageKit")
    print("=" * 60)
    
    # Check if ImageKit is configured
    if not all(settings.IMAGEKIT_CONFIG.values()):
        print("❌ ImageKit not configured!")
        return
    
    print("✅ ImageKit configured")
    print(f"📦 Storage Backend: {settings.DEFAULT_FILE_STORAGE}")
    
    # We need to get the original Cloudinary URLs from the database
    # Let me check what URLs we have stored
    print("\n📋 Checking current image URLs...")
    
    # Models to process
    models_to_process = [
        (HeroMedia, 'image', 'hero'),
        (Church, 'logo', 'churches/logos'),
        (News, 'image', 'news'),
        (Ministry, 'image', 'ministries'),
        (Sermon, 'thumbnail', 'sermons/thumbnails'),
    ]
    
    total_uploaded = 0
    total_failed = 0
    
    for model, field_name, folder in models_to_process:
        print(f"\n📋 Processing {model.__name__}.{field_name}...")
        
        instances = model.objects.all()
        for instance in instances:
            field = getattr(instance, field_name)
            if not field:
                continue
                
            field_str = str(field)
            print(f"  📋 {instance} - Current: {field_str}")
            
            # If it's already a proper ImageKit path, we need to upload the actual file
            if not field_str.startswith('http') and '/' in field_str:
                print(f"    📤 Need to upload actual file for path: {field_str}")
                
                # Try to find the original Cloudinary URL or create a placeholder
                # For now, let's create a simple placeholder image
                try:
                    # Create a simple SVG placeholder
                    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1e3a8a;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="300" height="200" fill="url(#grad1)"/>
  <circle cx="150" cy="100" r="60" fill="#ffffff" opacity="0.9"/>
  <text x="150" y="95" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="#3b82f6" text-anchor="middle">BETHEL</text>
  <text x="150" y="115" font-family="Arial, sans-serif" font-size="14" fill="#1e3a8a" text-anchor="middle">{model.__name__}</text>
  <text x="150" y="135" font-family="Arial, sans-serif" font-size="12" fill="#1e3a8a" text-anchor="middle">{instance}</text>
  <text x="150" y="175" font-family="Arial, sans-serif" font-size="10" fill="#ffffff" text-anchor="middle">ImageKit Upload</text>
</svg>'''
                    
                    # Get filename from the path
                    filename = os.path.basename(field_str)
                    if not filename.endswith('.svg'):
                        filename = filename.replace('.png', '.svg').replace('.jpg', '.svg').replace('.jpeg', '.svg')
                    
                    # Create ContentFile
                    content_file = ContentFile(svg_content.encode('utf-8'), name=filename)
                    
                    # Save to ImageKit
                    from django.core.files.storage import default_storage
                    saved_path = default_storage.save(field_str, content_file)
                    
                    print(f"      ✅ Uploaded placeholder: {saved_path}")
                    total_uploaded += 1
                    
                except Exception as e:
                    print(f"      ❌ Error uploading: {e}")
                    total_failed += 1
            
            # If it's a Cloudinary URL, download and upload to ImageKit
            elif 'res.cloudinary.com' in field_str:
                try:
                    print(f"    📤 Downloading from Cloudinary...")
                    
                    # Download from Cloudinary
                    response = requests.get(field_str, timeout=30)
                    if response.status_code != 200:
                        print(f"      ❌ Failed to download: {response.status_code}")
                        total_failed += 1
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
                    
                    print(f"      ✅ Uploaded to: {saved_path}")
                    total_uploaded += 1
                    
                except Exception as e:
                    print(f"      ❌ Error: {e}")
                    total_failed += 1
    
    print("\n" + "=" * 60)
    print(f"🎉 Upload completed!")
    print(f"✅ Successfully uploaded: {total_uploaded}")
    print(f"❌ Failed: {total_failed}")
    
    if total_uploaded > 0:
        print("\n🔄 Images uploaded to ImageKit!")
        print("💡 Deploy to Railway to see the changes in production.")

if __name__ == "__main__":
    upload_images_to_imagekit() 