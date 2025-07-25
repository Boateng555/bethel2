#!/usr/bin/env python
"""
Fix all broken images across all models
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

print("🔧 Fixing all broken images across all models...")

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
    
    # Get available image files
    available_images = [f for f in list_files.list if f.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
    print(f"✅ Found {len(available_images)} image files in ImageKit")
    
    fixed_count = 0
    
    # Fix News items
    print("\n📰 FIXING NEWS ITEMS:")
    news_items = News.objects.all()
    for news in news_items:
        print(f"   📰 {news.title}")
        if news.image:
            if str(news.image) not in imagekit_files:
                print(f"      ❌ Broken: {news.image}")
                if available_images:
                    replacement = available_images[0]
                    news.image = replacement.name
                    news.save()
                    print(f"      ✅ Fixed with: {replacement.name}")
                    fixed_count += 1
                else:
                    print(f"      ❌ No replacement available")
            else:
                print(f"      ✅ OK: {news.image}")
        else:
            print(f"      📝 No image")
    
    # Fix Church items
    print("\n⛪ FIXING CHURCH ITEMS:")
    church_items = Church.objects.all()
    for church in church_items:
        print(f"   ⛪ {church.name}")
        if church.logo:
            if str(church.logo) not in imagekit_files:
                print(f"      ❌ Broken: {church.logo}")
                if available_images:
                    replacement = available_images[0]
                    church.logo = replacement.name
                    church.save()
                    print(f"      ✅ Fixed with: {replacement.name}")
                    fixed_count += 1
                else:
                    print(f"      ❌ No replacement available")
            else:
                print(f"      ✅ OK: {church.logo}")
        else:
            print(f"      📝 No logo")
    
    # Fix Ministry items
    print("\n🙏 FIXING MINISTRY ITEMS:")
    ministry_items = Ministry.objects.all()
    for ministry in ministry_items:
        print(f"   🙏 {ministry.name}")
        if ministry.image:
            # Check for malformed URLs (double URLs)
            if 'https://ik.imagekit.io/9buar9mbp/https://' in str(ministry.image):
                print(f"      ❌ Malformed URL: {ministry.image}")
                if available_images:
                    replacement = available_images[0]
                    ministry.image = replacement.name
                    ministry.save()
                    print(f"      ✅ Fixed with: {replacement.name}")
                    fixed_count += 1
                else:
                    print(f"      ❌ No replacement available")
            elif str(ministry.image) not in imagekit_files:
                print(f"      ❌ Broken: {ministry.image}")
                if available_images:
                    replacement = available_images[0]
                    ministry.image = replacement.name
                    ministry.save()
                    print(f"      ✅ Fixed with: {replacement.name}")
                    fixed_count += 1
                else:
                    print(f"      ❌ No replacement available")
            else:
                print(f"      ✅ OK: {ministry.image}")
        else:
            print(f"      📝 No image")
    
    # Fix Sermon items
    print("\n📖 FIXING SERMON ITEMS:")
    sermon_items = Sermon.objects.all()
    for sermon in sermon_items:
        print(f"   📖 {sermon.title}")
        if sermon.thumbnail:
            if str(sermon.thumbnail) not in imagekit_files:
                print(f"      ❌ Broken: {sermon.thumbnail}")
                if available_images:
                    replacement = available_images[0]
                    sermon.thumbnail = replacement.name
                    sermon.save()
                    print(f"      ✅ Fixed with: {replacement.name}")
                    fixed_count += 1
                else:
                    print(f"      ❌ No replacement available")
            else:
                print(f"      ✅ OK: {sermon.thumbnail}")
        else:
            print(f"      📝 No thumbnail")
    
    print(f"\n🎉 Fixed {fixed_count} broken images!")
    
    # Show available images
    print(f"\n📋 Available images in ImageKit:")
    for i, img in enumerate(available_images[:10]):  # Show first 10
        print(f"   {i+1}. {img.name}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n📋 Next steps:")
print("1. Refresh your website to see the fixed images")
print("2. Check if all images are now displaying correctly")
print("3. If you want specific images, you can manually assign them in admin") 