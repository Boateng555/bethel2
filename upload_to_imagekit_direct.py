#!/usr/bin/env python
"""
Direct upload to ImageKit using requests library
"""
import os
import requests
import base64
import hashlib
import hmac
import time
from pathlib import Path
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.files import File
from core.models import Church, Hero, HeroMedia, News, Ministry, Sermon

def generate_signature(private_key, timestamp):
    """Generate signature for ImageKit API"""
    message = private_key + timestamp
    signature = hmac.new(
        private_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha1
    ).hexdigest()
    return signature

def upload_to_imagekit_direct():
    """
    Upload files directly to ImageKit using their API
    """
    print("🚀 Direct Upload to ImageKit.io...")
    print("=" * 70)
    
    # Configure ImageKit
    public_key = os.environ.get('IMAGEKIT_PUBLIC_KEY')
    private_key = os.environ.get('IMAGEKIT_PRIVATE_KEY')
    url_endpoint = os.environ.get('IMAGEKIT_URL_ENDPOINT')
    
    if not all([public_key, private_key, url_endpoint]):
        print("❌ ImageKit credentials not found!")
        return
    
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
                    # Read file
                    with open(local_path, 'rb') as file:
                        file_content = file.read()
                    
                    # Encode file content
                    file_encoded = base64.b64encode(file_content).decode('utf-8')
                    
                    # Generate timestamp and signature
                    timestamp = str(int(time.time()))
                    signature = generate_signature(private_key, timestamp)
                    
                    # Prepare upload data
                    upload_data = {
                        'file': file_encoded,
                        'fileName': f"church_{church.id}_logo{os.path.splitext(local_path)[1]}",
                        'folder': 'bethel/churches/logos',
                        'useUniqueFileName': False,
                        'publicKey': public_key,
                        'signature': signature,
                        'expire': timestamp
                    }
                    
                    # Upload to ImageKit
                    response = requests.post(
                        'https://upload.imagekit.io/api/v1/files/upload',
                        data=upload_data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if 'url' in result:
                            image_url = result['url']
                            print(f"      ✅ Uploaded: {image_url}")
                            
                            # Update database
                            from django.core.files.base import ContentFile
                            cloudinary_file = ContentFile(file_content, name=os.path.basename(local_path))
                            church.logo.save(os.path.basename(local_path), cloudinary_file, save=True)
                        else:
                            print(f"      ❌ No URL in response: {result}")
                    else:
                        print(f"      ❌ Upload failed: {response.status_code} - {response.text}")
                        
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
                        file_content = file.read()
                    
                    file_encoded = base64.b64encode(file_content).decode('utf-8')
                    timestamp = str(int(time.time()))
                    signature = generate_signature(private_key, timestamp)
                    
                    upload_data = {
                        'file': file_encoded,
                        'fileName': f"news_{news.id}{os.path.splitext(local_path)[1]}",
                        'folder': 'bethel/news',
                        'useUniqueFileName': False,
                        'publicKey': public_key,
                        'signature': signature,
                        'expire': timestamp
                    }
                    
                    response = requests.post(
                        'https://upload.imagekit.io/api/v1/files/upload',
                        data=upload_data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if 'url' in result:
                            image_url = result['url']
                            print(f"      ✅ Uploaded: {image_url}")
                            
                            from django.core.files.base import ContentFile
                            cloudinary_file = ContentFile(file_content, name=os.path.basename(local_path))
                            news.image.save(os.path.basename(local_path), cloudinary_file, save=True)
                        else:
                            print(f"      ❌ No URL in response: {result}")
                    else:
                        print(f"      ❌ Upload failed: {response.status_code} - {response.text}")
                        
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"    ⚠️ Image file missing")
        else:
            print(f"    ❌ No image")
    
    print("\n" + "=" * 70)
    print("🎉 Direct ImageKit upload completed!")
    print("\nNext steps:")
    print("1. Set your ImageKit credentials in Railway environment variables")
    print("2. Deploy to Railway")
    print("3. Check your live site")

if __name__ == "__main__":
    upload_to_imagekit_direct() 