#!/usr/bin/env python
"""
Check ImageKit files and verify specific image
"""

import os
import django
from imagekitio import ImageKit

# Set environment variables
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import News

print("🔍 Checking ImageKit files...")

# Initialize ImageKit
imagekit = ImageKit(
    private_key='private_Dnsrj2VW7uJakaeMaNYaav+P784=',
    public_key='public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=',
    url_endpoint='https://ik.imagekit.io/9buar9mbp'
)

# List all files in ImageKit
try:
    list_files = imagekit.list_files()
    print(f"✅ Found {len(list_files.list)} files in ImageKit")
    
    # Check for the specific problematic image
    target_file = "news/Windows Server 2019 Running - Oracle VM VirtualBox 26 04 2024 10 25 40.png"
    found = False
    
    for file in list_files.list:
        print(f"📁 {file.name}")
        if file.name == target_file:
            found = True
            print(f"✅ Found target file: {file.name}")
            print(f"   URL: {file.url}")
            print(f"   Size: {file.size} bytes")
            print(f"   Created: {file.created_at}")
    
    if not found:
        print(f"❌ Target file not found: {target_file}")
        
        # Check what news files exist
        print("\n📰 Checking news files in ImageKit:")
        news_files = [f for f in list_files.list if f.name.startswith('news/')]
        for file in news_files:
            print(f"   📄 {file.name}")
            
except Exception as e:
    print(f"❌ Error listing ImageKit files: {e}")

# Check Django News model
print("\n📰 Checking Django News model...")
try:
    news_items = News.objects.all()
    print(f"Found {news_items.count()} news items in database")
    
    for news in news_items:
        if news.image:
            print(f"📰 {news.title}: {news.image.url}")
            if 'Windows Server' in str(news.image):
                print(f"   ⚠️ This is the problematic image")
                print(f"   Database path: {news.image}")
                print(f"   Generated URL: {news.image.url}")
        else:
            print(f"📰 {news.title}: No image")
            
except Exception as e:
    print(f"❌ Error checking News model: {e}")

print("\n🔧 Next steps:")
print("1. If the file doesn't exist in ImageKit, we need to re-upload it")
print("2. If the file exists but URL is wrong, we need to fix the path")
print("3. If the file exists and URL is correct, there might be a CORS or access issue") 