#!/usr/bin/env python
"""
Fix broken image by re-uploading to ImageKit
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

print("🔧 Fixing broken image...")

# Find the news item with the broken image
try:
    news_items = News.objects.all()
    target_news = None
    
    for news in news_items:
        if news.image and 'Windows Server' in str(news.image):
            target_news = news
            break
    
    if target_news:
        print(f"📰 Found news item: {target_news.title}")
        print(f"   Current image: {target_news.image}")
        print(f"   Current URL: {target_news.image.url}")
        
        # Check if the original file exists locally
        local_path = Path('media') / str(target_news.image)
        if local_path.exists():
            print(f"✅ Found local file: {local_path}")
            
            # Read the file and re-upload to ImageKit
            with open(local_path, 'rb') as f:
                file_content = f.read()
            
            # Create a new file with the same name
            new_file = ContentFile(file_content, name=target_news.image.name)
            
            # Save using ImageKit storage
            new_path = default_storage.save(target_news.image.name, new_file)
            new_url = default_storage.url(new_path)
            
            print(f"✅ Re-uploaded to ImageKit")
            print(f"   New path: {new_path}")
            print(f"   New URL: {new_url}")
            
            # Update the news item
            target_news.image = new_path
            target_news.save()
            
            print(f"✅ Updated news item in database")
            
        else:
            print(f"❌ Local file not found: {local_path}")
            print("   You may need to manually upload the image")
            
    else:
        print("❌ No news item found with the broken image")
        
except Exception as e:
    print(f"❌ Error fixing image: {e}")
    import traceback
    traceback.print_exc()

print("\n📋 Next steps:")
print("1. Check if the image now loads correctly")
print("2. If not, we may need to manually upload the image to ImageKit")
print("3. Verify all other images are working") 