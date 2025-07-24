#!/usr/bin/env python3
"""
Check Images Script
This script checks what images are in the database and their current paths.
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def check_database_images():
    """Check what images are stored in the database"""
    print("🔍 Checking Database Images")
    print("=" * 50)
    
    from core.models import Church, Event, Ministry, News, Sermon, HeroMedia, EventHeroMedia
    
    models_to_check = [
        (Church, 'logo', 'Church'),
        (Ministry, 'image', 'Ministry'),
        (News, 'image', 'News'),
        (Sermon, 'thumbnail', 'Sermon'),
        (HeroMedia, 'image', 'HeroMedia'),
    ]
    
    total_images = 0
    missing_images = 0
    
    for model, field_name, model_name in models_to_check:
        print(f"\n📋 {model_name} Images:")
        print("-" * 30)
        
        instances = model.objects.all()
        if not instances.exists():
            print(f"  No {model_name} records found")
            continue
        
        for instance in instances:
            field = getattr(instance, field_name)
            if field and hasattr(field, 'name') and field.name:
                total_images += 1
                
                # Get the field value
                field_str = str(field)
                
                # Check if it's a full URL
                if field_str.startswith('http'):
                    print(f"  ✅ {instance}: {field_str[:50]}...")
                else:
                    # Check if file exists
                    if hasattr(field, 'path'):
                        file_path = field.path
                        if os.path.exists(file_path):
                            print(f"  ✅ {instance}: {field_str} (exists)")
                        else:
                            print(f"  ❌ {instance}: {field_str} (missing)")
                            missing_images += 1
                    else:
                        print(f"  ⚠️  {instance}: {field_str} (no path)")
            else:
                print(f"  ⚪ {instance}: No image")
    
    # Check Event Hero Media separately
    print(f"\n📋 Event Hero Media:")
    print("-" * 30)
    
    event_media = EventHeroMedia.objects.all()
    if not event_media.exists():
        print("  No Event Hero Media found")
    else:
        for media in event_media:
            if media.image and hasattr(media.image, 'name') and media.image.name:
                total_images += 1
                field_str = str(media.image)
                
                if field_str.startswith('http'):
                    print(f"  ✅ {media.event.title}: {field_str[:50]}...")
                else:
                    if hasattr(media.image, 'path'):
                        file_path = media.image.path
                        if os.path.exists(file_path):
                            print(f"  ✅ {media.event.title}: {field_str} (exists)")
                        else:
                            print(f"  ❌ {media.event.title}: {field_str} (missing)")
                            missing_images += 1
                    else:
                        print(f"  ⚠️  {media.event.title}: {field_str} (no path)")
            else:
                print(f"  ⚪ {media.event.title}: No image")
    
    print(f"\n📊 Summary:")
    print(f"  Total images in database: {total_images}")
    print(f"  Missing images: {missing_images}")
    print(f"  Available images: {total_images - missing_images}")

def check_media_folders():
    """Check what's in the media folders"""
    print(f"\n📁 Checking Media Folders")
    print("=" * 50)
    
    # Check main media folder
    media_root = settings.MEDIA_ROOT
    print(f"Main media folder: {media_root}")
    
    if os.path.exists(media_root):
        print("✅ Main media folder exists")
        for root, dirs, files in os.walk(media_root):
            level = root.replace(media_root, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:5]:  # Show first 5 files
                print(f"{subindent}{file}")
            if len(files) > 5:
                print(f"{subindent}... and {len(files) - 5} more files")
    else:
        print("❌ Main media folder does not exist")
    
    # Check railway_media folder
    railway_media = os.path.join(settings.BASE_DIR, 'railway_media')
    print(f"\nRailway media folder: {railway_media}")
    
    if os.path.exists(railway_media):
        print("✅ Railway media folder exists")
        for root, dirs, files in os.walk(railway_media):
            level = root.replace(railway_media, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:5]:  # Show first 5 files
                print(f"{subindent}{file}")
            if len(files) > 5:
                print(f"{subindent}... and {len(files) - 5} more files")
    else:
        print("❌ Railway media folder does not exist")

def copy_images_from_railway_media():
    """Copy images from railway_media to media folder"""
    print(f"\n📁 Copying Images from railway_media to media")
    print("=" * 50)
    
    import shutil
    
    railway_media = os.path.join(settings.BASE_DIR, 'railway_media')
    media_root = settings.MEDIA_ROOT
    
    if not os.path.exists(railway_media):
        print("❌ Railway media folder does not exist")
        return
    
    if not os.path.exists(media_root):
        print("✅ Creating media folder")
        os.makedirs(media_root, exist_ok=True)
    
    copied_count = 0
    failed_count = 0
    
    try:
        # Copy all files from railway_media to media
        for root, dirs, files in os.walk(railway_media):
            # Calculate relative path
            rel_path = os.path.relpath(root, railway_media)
            target_dir = os.path.join(media_root, rel_path)
            
            # Create target directory if it doesn't exist
            os.makedirs(target_dir, exist_ok=True)
            
            for file in files:
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_dir, file)
                
                try:
                    shutil.copy2(source_file, target_file)
                    print(f"  ✅ Copied: {os.path.join(rel_path, file)}")
                    copied_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to copy {file}: {e}")
                    failed_count += 1
        
        print(f"\n📊 Copy Summary:")
        print(f"  Files copied: {copied_count}")
        print(f"  Files failed: {failed_count}")
        
        if copied_count > 0:
            print("✅ Images copied successfully!")
            print("   Your images should now be visible on the website")
        
    except Exception as e:
        print(f"❌ Error copying images: {e}")

def suggest_fixes():
    """Suggest fixes for missing images"""
    print(f"\n🔧 Suggested Fixes")
    print("=" * 50)
    
    print("""
If images are missing, here are the solutions:

1. 📁 Copy Images from railway_media to media:
   - Your images are in railway_media/ but Django looks in media/
   - Copy files: railway_media/* → media/

2. 🖼️ Upload Images via Admin:
   - Go to http://localhost:8000/admin/
   - Edit each item and upload images manually

3. 🔄 Update Database Paths:
   - Update database to point to correct image paths
   - Or move images to where database expects them

4. 🚀 Deploy to Production:
   - Set up ImageKit for production
   - Upload images to cloud storage
""")

def main():
    print("🖼️ Image Check Script")
    print("=" * 60)
    
    check_database_images()
    check_media_folders()
    
    # Ask if user wants to copy images
    print(f"\n🤔 Do you want to copy images from railway_media to media?")
    response = input("Type 'yes' to copy images: ").strip().lower()
    
    if response == 'yes':
        copy_images_from_railway_media()
    else:
        suggest_fixes()
    
    print(f"\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("1. Check the output above to see what's missing")
    print("2. Copy images from railway_media to media if needed")
    print("3. Or upload images through Django admin")
    print("4. Test your site to see if images appear")
    print("=" * 60)

if __name__ == "__main__":
    main() 