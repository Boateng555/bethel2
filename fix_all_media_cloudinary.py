#!/usr/bin/env python
"""
Comprehensive script to fix ALL media files for Cloudinary
"""
import os
import cloudinary
import cloudinary.uploader
from pathlib import Path
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.files import File
from core.models import Church, Hero, HeroMedia, News, Ministry, Sermon

def fix_all_media_cloudinary():
    """
    Upload ALL media files to Cloudinary and update database
    """
    print("🚀 Fixing ALL Media for Cloudinary...")
    print("=" * 70)
    
    # Configure Cloudinary with correct credentials
    cloudinary.config(
        cloud_name="dhzdusb5k",
        api_key="462763744132765",
        api_secret="s-FWNQuY_M40XwHKrskwIh0C-XI"
    )
    
    print("☁️ Cloudinary configured with Root API credentials")
    
    # Process Church Logos
    print("\n🏛️ Processing Church Logos...")
    churches = Church.objects.all()
    for church in churches:
        print(f"  📤 {church.name}")
        if church.logo and hasattr(church.logo, 'path'):
            local_path = church.logo.path
            if os.path.exists(local_path):
                print(f"    📸 Uploading logo...")
                try:
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="bethel/churches/logos",
                        public_id=f"church_{church.id}_logo"
                    )
                    
                    from django.core.files.base import ContentFile
                    import requests
                    
                    response = requests.get(result['secure_url'])
                    if response.status_code == 200:
                        cloudinary_file = ContentFile(response.content, name=os.path.basename(local_path))
                        church.logo.save(os.path.basename(local_path), cloudinary_file, save=True)
                        print(f"      ✅ Uploaded: {result['secure_url']}")
                    else:
                        print(f"      ❌ Failed to download")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"    ⚠️ Logo file missing")
        else:
            print(f"    ❌ No logo")
    
    # Process News Images
    print("\n📰 Processing News Images...")
    news_items = News.objects.all()
    for news in news_items:
        print(f"  📤 {news.title}")
        if news.image and hasattr(news.image, 'path'):
            local_path = news.image.path
            if os.path.exists(local_path):
                print(f"    📸 Uploading image...")
                try:
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="bethel/news",
                        public_id=f"news_{news.id}"
                    )
                    
                    from django.core.files.base import ContentFile
                    import requests
                    
                    response = requests.get(result['secure_url'])
                    if response.status_code == 200:
                        cloudinary_file = ContentFile(response.content, name=os.path.basename(local_path))
                        news.image.save(os.path.basename(local_path), cloudinary_file, save=True)
                        print(f"      ✅ Uploaded: {result['secure_url']}")
                    else:
                        print(f"      ❌ Failed to download")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"    ⚠️ Image file missing")
        else:
            print(f"    ❌ No image")
    
    # Process Ministry Images
    print("\n⛪ Processing Ministry Images...")
    ministries = Ministry.objects.all()
    for ministry in ministries:
        print(f"  📤 {ministry.name}")
        if ministry.image and hasattr(ministry.image, 'path'):
            local_path = ministry.image.path
            if os.path.exists(local_path):
                print(f"    📸 Uploading image...")
                try:
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="bethel/ministries",
                        public_id=f"ministry_{ministry.id}"
                    )
                    
                    from django.core.files.base import ContentFile
                    import requests
                    
                    response = requests.get(result['secure_url'])
                    if response.status_code == 200:
                        cloudinary_file = ContentFile(response.content, name=os.path.basename(local_path))
                        ministry.image.save(os.path.basename(local_path), cloudinary_file, save=True)
                        print(f"      ✅ Uploaded: {result['secure_url']}")
                    else:
                        print(f"      ❌ Failed to download")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"    ⚠️ Image file missing")
        else:
            print(f"    ❌ No image")
    
    # Process Sermon Thumbnails
    print("\n📖 Processing Sermon Thumbnails...")
    sermons = Sermon.objects.all()
    for sermon in sermons:
        print(f"  📤 {sermon.title}")
        if sermon.thumbnail and hasattr(sermon.thumbnail, 'path'):
            local_path = sermon.thumbnail.path
            if os.path.exists(local_path):
                print(f"    📸 Uploading thumbnail...")
                try:
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="bethel/sermons",
                        public_id=f"sermon_{sermon.id}_thumb"
                    )
                    
                    from django.core.files.base import ContentFile
                    import requests
                    
                    response = requests.get(result['secure_url'])
                    if response.status_code == 200:
                        cloudinary_file = ContentFile(response.content, name=os.path.basename(local_path))
                        sermon.thumbnail.save(os.path.basename(local_path), cloudinary_file, save=True)
                        print(f"      ✅ Uploaded: {result['secure_url']}")
                    else:
                        print(f"      ❌ Failed to download")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"    ⚠️ Thumbnail file missing")
        else:
            print(f"    ❌ No thumbnail")
    
    print("\n" + "=" * 70)
    print("🎉 ALL Media Cloudinary fix completed!")
    print("\nNext steps:")
    print("1. Check your live site: https://web-production-158c.up.railway.app/")
    print("2. ALL images should now be visible (church logos, news, ministries, sermons)")
    print("3. If not, clear browser cache and refresh")

if __name__ == "__main__":
    fix_all_media_cloudinary() 