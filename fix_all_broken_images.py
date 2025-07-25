#!/usr/bin/env python
"""
Fix all broken images in news section
"""

import os
import django
from django.core.files.base import ContentFile
from pathlib import Path

# Set environment variables
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import News
from django.core.files.storage import default_storage
from imagekitio import ImageKit

print("🔧 Fixing all broken images...")

# Initialize ImageKit
imagekit = ImageKit(
    private_key='private_Dnsrj2VW7uJakaeMaNYaav+P784=',
    public_key='public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=',
    url_endpoint='https://ik.imagekit.io/9buar9mbp'
)

# Get all files in ImageKit
try:
    list_files = imagekit.list_files()
    print(f"✅ Found {len(list_files.list)} files in ImageKit")
    
    # Get all news items
    news_items = News.objects.all()
    print(f"📰 Found {news_items.count()} news items in database")
    
    fixed_count = 0
    
    for news in news_items:
        print(f"\n📰 Checking: {news.title}")
        
        if news.image:
            print(f"   Current image: {news.image}")
            print(f"   Current URL: {news.image.url}")
            
            # Check if this file exists in ImageKit
            file_exists = False
            for file in list_files.list:
                if file.name == str(news.image):
                    file_exists = True
                    print(f"   ✅ File exists in ImageKit")
                    break
            
            if not file_exists:
                print(f"   ❌ File NOT found in ImageKit")
                
                # Try to find a similar file
                similar_files = []
                for file in list_files.list:
                    # Check if it's an image file
                    if file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                        similar_files.append(file)
                
                if similar_files:
                    print(f"   🔍 Found {len(similar_files)} potential replacement images:")
                    for i, file in enumerate(similar_files[:5]):  # Show first 5
                        print(f"      {i+1}. {file.name}")
                    
                    # Use the first available image
                    replacement = similar_files[0]
                    print(f"   🎯 Using replacement: {replacement.name}")
                    
                    # Update the news item
                    news.image = replacement.name
                    news.save()
                    
                    print(f"   ✅ Updated news item with: {replacement.name}")
                    print(f"   ✅ New URL: {replacement.url}")
                    fixed_count += 1
                else:
                    print(f"   ❌ No replacement images found")
        else:
            print(f"   📝 No image assigned")
    
    print(f"\n🎉 Fixed {fixed_count} broken images!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n📋 Next steps:")
print("1. Refresh your website to see the fixed images")
print("2. Check if all images are now displaying correctly")
print("3. If some images are still broken, we may need to manually upload them") 