#!/usr/bin/env python
"""
Script to migrate Cloudinary URLs to ImageKit URLs
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
from core.models import HeroMedia, Church, News, Ministry, Sermon, Event

def migrate_cloudinary_to_imagekit():
    """Migrate Cloudinary URLs to ImageKit"""
    print("🔄 Migrating Cloudinary URLs to ImageKit")
    print("=" * 60)
    
    # Check if ImageKit is configured
    if not all(settings.IMAGEKIT_CONFIG.values()):
        print("❌ ImageKit not configured!")
        print("Missing values:", [k for k, v in settings.IMAGEKIT_CONFIG.items() if not v])
        return
    
    print("✅ ImageKit configured")
    print(f"📦 Storage Backend: {settings.DEFAULT_FILE_STORAGE}")
    
    # Models to migrate
    models_to_migrate = [
        (HeroMedia, 'image', 'hero'),
        (Church, 'logo', 'churches/logos'),
        (News, 'image', 'news'),
        (Ministry, 'image', 'ministries'),
        (Sermon, 'thumbnail', 'sermons/thumbnails'),
        (Event, 'image', 'events'),
    ]
    
    total_migrated = 0
    total_failed = 0
    
    for model, field_name, folder in models_to_migrate:
        print(f"\n📋 Migrating {model.__name__}.{field_name}...")
        
        instances = model.objects.all()
        print(f"  Found {instances.count()} instances")
        
        for instance in instances:
            field = getattr(instance, field_name)
            if not field:
                print(f"  ⚠️  {instance} - No {field_name}")
                continue
                
            field_str = str(field)
            print(f"  📋 {instance} - Current: {field_str}")
            
            # Skip if already ImageKit URL
            if 'ik.imagekit.io' in field_str:
                print(f"    ✅ Already ImageKit URL")
                continue
                
            # Skip if not Cloudinary URL
            if 'res.cloudinary.com' not in field_str:
                print(f"    ⚠️  Not Cloudinary URL")
                continue
            
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
                
                print(f"      📁 Filename: {filename}")
                
                # Create new file path for ImageKit
                new_path = f"{folder}/{filename}"
                print(f"      🎯 New path: {new_path}")
                
                # Create ContentFile
                content_file = ContentFile(response.content, name=filename)
                
                # Save to ImageKit
                from django.core.files.storage import default_storage
                saved_path = default_storage.save(new_path, content_file)
                print(f"      💾 Saved to: {saved_path}")
                
                # Update the field
                setattr(instance, field_name, saved_path)
                instance.save()
                
                print(f"      ✅ Migrated successfully!")
                total_migrated += 1
                
            except Exception as e:
                print(f"      ❌ Error: {e}")
                import traceback
                traceback.print_exc()
                total_failed += 1
    
    print("\n" + "=" * 60)
    print(f"🎉 Migration completed!")
    print(f"✅ Successfully migrated: {total_migrated}")
    print(f"❌ Failed: {total_failed}")
    
    if total_migrated > 0:
        print("\n🔄 Your images are now stored in ImageKit!")
        print("💡 You can now run in development mode and images will work.")

if __name__ == "__main__":
    migrate_cloudinary_to_imagekit() 