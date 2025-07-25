#!/usr/bin/env python
"""
Fix the specific news item with broken image
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

print("🔧 Fixing specific news image...")

# Find the news item "sds"
try:
    news_item = News.objects.filter(title="sds").first()
    
    if news_item:
        print(f"📰 Found news item: {news_item.title}")
        print(f"   Current image: {news_item.image}")
        print(f"   Current URL: {news_item.image.url}")
        
        # Check if the original file exists locally
        local_path = Path('media') / str(news_item.image)
        if local_path.exists():
            print(f"✅ Found local file: {local_path}")
            
            # Read the file and re-upload to ImageKit
            with open(local_path, 'rb') as f:
                file_content = f.read()
            
            # Create a new file with the same name
            new_file = ContentFile(file_content, name=news_item.image.name)
            
            # Save using ImageKit storage
            new_path = default_storage.save(news_item.image.name, new_file)
            new_url = default_storage.url(new_path)
            
            print(f"✅ Re-uploaded to ImageKit")
            print(f"   New path: {new_path}")
            print(f"   New URL: {new_url}")
            
            # Update the news item
            news_item.image = new_path
            news_item.save()
            
            print(f"✅ Updated news item in database")
            
        else:
            print(f"❌ Local file not found: {local_path}")
            
            # Try to find a similar file in ImageKit
            print("🔍 Looking for similar files in ImageKit...")
            from imagekitio import ImageKit
            
            imagekit = ImageKit(
                private_key='private_Dnsrj2VW7uJakaeMaNYaav+P784=',
                public_key='public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=',
                url_endpoint='https://ik.imagekit.io/9buar9mbp'
            )
            
            list_files = imagekit.list_files()
            similar_files = [f for f in list_files.list if 'Windows_Server_2019_Running' in f.name]
            
            if similar_files:
                print(f"✅ Found {len(similar_files)} similar files in ImageKit:")
                for file in similar_files:
                    print(f"   📄 {file.name} -> {file.url}")
                
                # Use the first similar file
                best_match = similar_files[0]
                print(f"🎯 Using best match: {best_match.name}")
                
                # Update the news item with the correct path
                news_item.image = best_match.name
                news_item.save()
                
                print(f"✅ Updated news item with ImageKit file: {best_match.name}")
                print(f"   New URL: {best_match.url}")
            else:
                print("❌ No similar files found in ImageKit")
            
    else:
        print("❌ News item 'sds' not found")
        
except Exception as e:
    print(f"❌ Error fixing image: {e}")
    import traceback
    traceback.print_exc()

print("\n📋 Next steps:")
print("1. Check if the image now loads correctly")
print("2. Refresh your website to see the fixed image")
print("3. Verify all other images are working") 