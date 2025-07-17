#!/usr/bin/env python
"""
Fixed script to upload all media files to ImageKit.io
"""
import os
import imagekitio
from pathlib import Path
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.files import File
from core.models import Church, Hero, HeroMedia, News, Ministry, Sermon

def upload_media_to_imagekit():
    """
    Upload all media files to ImageKit.io
    """
    print("🚀 Uploading Media to ImageKit.io...")
    print("=" * 70)
    
    # Configure ImageKit
    public_key = os.environ.get('IMAGEKIT_PUBLIC_KEY')
    private_key = os.environ.get('IMAGEKIT_PRIVATE_KEY')
    url_endpoint = os.environ.get('IMAGEKIT_URL_ENDPOINT')
    
    if not all([public_key, private_key, url_endpoint]):
        print("❌ ImageKit credentials not found!")
        print("Please set these environment variables:")
        print("  IMAGEKIT_PUBLIC_KEY")
        print("  IMAGEKIT_PRIVATE_KEY")
        print("  IMAGEKIT_URL_ENDPOINT")
        return
    
    # Initialize ImageKit
    imagekit = imagekitio.ImageKit(
        public_key=public_key,
        private_key=private_key,
        url_endpoint=url_endpoint
    )
    
    print("🖼️ ImageKit configured successfully")
    
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
                    # Upload to ImageKit
                    with open(local_path, 'rb') as file:
                        result = imagekit.upload_file(
                            file=file,
                            file_name=f"church_{church.id}_logo{os.path.splitext(local_path)[1]}",
                            options={
                                "folder": "bethel/churches/logos",
                                "use_unique_file_name": False
                            }
                        )
                    
                    # Check if upload was successful
                    if hasattr(result, 'response_metadata') and result.response_metadata.http_status_code == 200:
                        # Get the URL from the response
                        image_url = result.response_metadata.raw.url
                        
                        # Update database with ImageKit URL
                        from django.core.files.base import ContentFile
                        import requests
                        
                        response = requests.get(image_url)
                        if response.status_code == 200:
                            cloudinary_file = ContentFile(response.content, name=os.path.basename(local_path))
                            church.logo.save(os.path.basename(local_path), cloudinary_file, save=True)
                            print(f"      ✅ Uploaded: {image_url}")
                        else:
                            print(f"      ❌ Failed to download")
                    else:
                        print(f"      ❌ Upload failed: {result}")
                        
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
                    with open(local_path, 'rb') as file:
                        result = imagekit.upload_file(
                            file=file,
                            file_name=f"news_{news.id}{os.path.splitext(local_path)[1]}",
                            options={
                                "folder": "bethel/news",
                                "use_unique_file_name": False
                            }
                        )
                    
                    if hasattr(result, 'response_metadata') and result.response_metadata.http_status_code == 200:
                        image_url = result.response_metadata.raw.url
                        
                        from django.core.files.base import ContentFile
                        import requests
                        
                        response = requests.get(image_url)
                        if response.status_code == 200:
                            cloudinary_file = ContentFile(response.content, name=os.path.basename(local_path))
                            news.image.save(os.path.basename(local_path), cloudinary_file, save=True)
                            print(f"      ✅ Uploaded: {image_url}")
                        else:
                            print(f"      ❌ Failed to download")
                    else:
                        print(f"      ❌ Upload failed: {result}")
                        
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
                    with open(local_path, 'rb') as file:
                        result = imagekit.upload_file(
                            file=file,
                            file_name=f"ministry_{ministry.id}{os.path.splitext(local_path)[1]}",
                            options={
                                "folder": "bethel/ministries",
                                "use_unique_file_name": False
                            }
                        )
                    
                    if hasattr(result, 'response_metadata') and result.response_metadata.http_status_code == 200:
                        image_url = result.response_metadata.raw.url
                        
                        from django.core.files.base import ContentFile
                        import requests
                        
                        response = requests.get(image_url)
                        if response.status_code == 200:
                            cloudinary_file = ContentFile(response.content, name=os.path.basename(local_path))
                            ministry.image.save(os.path.basename(local_path), cloudinary_file, save=True)
                            print(f"      ✅ Uploaded: {image_url}")
                        else:
                            print(f"      ❌ Failed to download")
                    else:
                        print(f"      ❌ Upload failed: {result}")
                        
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
                    with open(local_path, 'rb') as file:
                        result = imagekit.upload_file(
                            file=file,
                            file_name=f"sermon_{sermon.id}_thumb{os.path.splitext(local_path)[1]}",
                            options={
                                "folder": "bethel/sermons",
                                "use_unique_file_name": False
                            }
                        )
                    
                    if hasattr(result, 'response_metadata') and result.response_metadata.http_status_code == 200:
                        image_url = result.response_metadata.raw.url
                        
                        from django.core.files.base import ContentFile
                        import requests
                        
                        response = requests.get(image_url)
                        if response.status_code == 200:
                            cloudinary_file = ContentFile(response.content, name=os.path.basename(local_path))
                            sermon.thumbnail.save(os.path.basename(local_path), cloudinary_file, save=True)
                            print(f"      ✅ Uploaded: {image_url}")
                        else:
                            print(f"      ❌ Failed to download")
                    else:
                        print(f"      ❌ Upload failed: {result}")
                        
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"    ⚠️ Thumbnail file missing")
        else:
            print(f"    ❌ No thumbnail")
    
    print("\n" + "=" * 70)
    print("🎉 ImageKit upload completed!")
    print("\nNext steps:")
    print("1. Set your ImageKit credentials in Railway environment variables")
    print("2. Deploy to Railway")
    print("3. Check your live site")

if __name__ == "__main__":
    upload_media_to_imagekit() 