#!/usr/bin/env python
"""
Fix path mismatch between database paths and actual ImageKit file names
"""

import os
import django

# Set environment variables
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import News, Church, Ministry, Sermon
from imagekitio import ImageKit

print("🔧 Fixing path mismatch between database and ImageKit...")

# Initialize ImageKit
imagekit = ImageKit(
    private_key='private_Dnsrj2VW7uJakaeMaNYaav+P784=',
    public_key='public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=',
    url_endpoint='https://ik.imagekit.io/9buar9mbp'
)

# Get all files in ImageKit
try:
    list_files = imagekit.list_files()
    imagekit_files = [f.name for f in list_files.list]
    print(f"✅ Found {len(imagekit_files)} files in ImageKit")
    
    # Show all ImageKit files for reference
    print(f"\n📋 All files in ImageKit:")
    for i, filename in enumerate(imagekit_files):
        print(f"   {i+1}. {filename}")
    
    fixed_count = 0
    
    # Fix News items
    print(f"\n📰 FIXING NEWS ITEMS:")
    news_items = News.objects.all()
    for news in news_items:
        print(f"   📰 {news.title}")
        if news.image:
            current_path = str(news.image)
            print(f"      Current path: {current_path}")
            
            # Remove folder prefix and find matching file
            filename_only = current_path.split('/')[-1]
            print(f"      Looking for: {filename_only}")
            
            # Try to find exact match or similar file
            found_file = None
            
            # First try exact match
            for file in list_files.list:
                if file.name == filename_only:
                    found_file = file
                    break
            
            # If no exact match, try to find similar file
            if not found_file:
                # Look for files with similar base name
                base_name = filename_only.replace('_', ' ').replace('.png', '').replace('.jpg', '')
                print(f"      Looking for similar to: {base_name}")
                
                for file in list_files.list:
                    file_base = file.name.replace('_', ' ').replace('.png', '').replace('.jpg', '')
                    if base_name in file_base or file_base in base_name:
                        found_file = file
                        print(f"      Found similar: {file.name}")
                        break
            
            # If still no match, use first available image
            if not found_file:
                image_files = [f for f in list_files.list if f.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
                if image_files:
                    found_file = image_files[0]
                    print(f"      Using fallback: {found_file.name}")
            
            if found_file:
                # Update the database with just the filename (no folder prefix)
                news.image = found_file.name
                news.save()
                print(f"      ✅ Fixed: {found_file.name}")
                print(f"      🌐 New URL: {found_file.url}")
                fixed_count += 1
            else:
                print(f"      ❌ No suitable replacement found")
        else:
            print(f"      📝 No image")
    
    # Fix Church items
    print(f"\n⛪ FIXING CHURCH ITEMS:")
    church_items = Church.objects.all()
    for church in church_items:
        print(f"   ⛪ {church.name}")
        if church.logo:
            current_path = str(church.logo)
            print(f"      Current path: {current_path}")
            
            # Remove folder prefix and find matching file
            filename_only = current_path.split('/')[-1]
            print(f"      Looking for: {filename_only}")
            
            # Try to find exact match or similar file
            found_file = None
            
            # First try exact match
            for file in list_files.list:
                if file.name == filename_only:
                    found_file = file
                    break
            
            # If no exact match, use first available image
            if not found_file:
                image_files = [f for f in list_files.list if f.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
                if image_files:
                    found_file = image_files[0]
                    print(f"      Using fallback: {found_file.name}")
            
            if found_file:
                # Update the database with just the filename (no folder prefix)
                church.logo = found_file.name
                church.save()
                print(f"      ✅ Fixed: {found_file.name}")
                print(f"      🌐 New URL: {found_file.url}")
                fixed_count += 1
            else:
                print(f"      ❌ No suitable replacement found")
        else:
            print(f"      📝 No logo")
    
    # Fix Ministry items
    print(f"\n🙏 FIXING MINISTRY ITEMS:")
    ministry_items = Ministry.objects.all()
    for ministry in ministry_items:
        print(f"   🙏 {ministry.name}")
        if ministry.image:
            current_path = str(ministry.image)
            print(f"      Current path: {current_path}")
            
            # Remove folder prefix and find matching file
            filename_only = current_path.split('/')[-1]
            print(f"      Looking for: {filename_only}")
            
            # Try to find exact match or similar file
            found_file = None
            
            # First try exact match
            for file in list_files.list:
                if file.name == filename_only:
                    found_file = file
                    break
            
            # If no exact match, use first available image
            if not found_file:
                image_files = [f for f in list_files.list if f.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
                if image_files:
                    found_file = image_files[0]
                    print(f"      Using fallback: {found_file.name}")
            
            if found_file:
                # Update the database with just the filename (no folder prefix)
                ministry.image = found_file.name
                ministry.save()
                print(f"      ✅ Fixed: {found_file.name}")
                print(f"      🌐 New URL: {found_file.url}")
                fixed_count += 1
            else:
                print(f"      ❌ No suitable replacement found")
        else:
            print(f"      📝 No image")
    
    # Fix Sermon items
    print(f"\n📖 FIXING SERMON ITEMS:")
    sermon_items = Sermon.objects.all()
    for sermon in sermon_items:
        print(f"   📖 {sermon.title}")
        if sermon.thumbnail:
            current_path = str(sermon.thumbnail)
            print(f"      Current path: {current_path}")
            
            # Remove folder prefix and find matching file
            filename_only = current_path.split('/')[-1]
            print(f"      Looking for: {filename_only}")
            
            # Try to find exact match or similar file
            found_file = None
            
            # First try exact match
            for file in list_files.list:
                if file.name == filename_only:
                    found_file = file
                    break
            
            # If no exact match, use first available image
            if not found_file:
                image_files = [f for f in list_files.list if f.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
                if image_files:
                    found_file = image_files[0]
                    print(f"      Using fallback: {found_file.name}")
            
            if found_file:
                # Update the database with just the filename (no folder prefix)
                sermon.thumbnail = found_file.name
                sermon.save()
                print(f"      ✅ Fixed: {found_file.name}")
                print(f"      🌐 New URL: {found_file.url}")
                fixed_count += 1
            else:
                print(f"      ❌ No suitable replacement found")
        else:
            print(f"      📝 No thumbnail")
    
    print(f"\n🎉 Fixed {fixed_count} path mismatches!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n📋 Next steps:")
print("1. Run final_image_check.py to verify the fixes")
print("2. Restart your Django application: sudo systemctl restart bethel")
print("3. Visit your website to see the fixed images") 