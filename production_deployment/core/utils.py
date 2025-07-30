import os
import base64
import hashlib
import hmac
import time
import requests
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def upload_to_imagekit(file_path, folder_name="bethel"):
    """
    Upload a file to ImageKit using direct HTTP requests
    """
    try:
        # Read the file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Get file name
        file_name = os.path.basename(file_path)
        
        # Prepare the upload data
        upload_data = {
            'file': (file_name, file_data),
            'fileName': file_name,
            'folder': folder_name,
        }
        
        # Get ImageKit credentials
        public_key = os.environ.get('IMAGEKIT_PUBLIC_KEY')
        private_key = os.environ.get('IMAGEKIT_PRIVATE_KEY')
        url_endpoint = os.environ.get('IMAGEKIT_URL_ENDPOINT')
        
        if not all([public_key, private_key, url_endpoint]):
            print("❌ ImageKit credentials not found")
            return None
        
        # Create signature
        timestamp = str(int(time.time()))
        signature = create_signature(private_key, timestamp)
        
        # Prepare headers
        headers = {
            'Authorization': f'Basic {base64.b64encode(f"{public_key}:{signature}".encode()).decode()}',
            'x-ik-timestamp': timestamp,
        }
        
        # Upload to ImageKit
        response = requests.post(
            'https://upload.imagekit.io/api/v1/files/upload',
            files=upload_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('url')
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error uploading to ImageKit: {e}")
        return None

def create_signature(private_key, timestamp):
    """
    Create signature for ImageKit API
    """
    message = private_key + timestamp
    signature = hmac.new(
        private_key.encode(),
        message.encode(),
        hashlib.sha1
    ).hexdigest()
    return signature

def update_media_urls_in_database():
    """
    Update all media URLs in the database to use ImageKit URLs
    """
    from .models import Church, Event, Ministry, News, Sermon, HeroMedia
    
    models_to_update = [
        (Church, 'logo'),
        (Event, 'image'),
        (Ministry, 'image'),
        (News, 'image'),
        (Sermon, 'thumbnail'),
        (HeroMedia, 'image'),
    ]
    
    for model, field_name in models_to_update:
        print(f"📝 Updating {model.__name__} {field_name} URLs...")
        
        for instance in model.objects.all():
            field = getattr(instance, field_name)
            if field and hasattr(field, 'name') and field.name:
                # Check if it's already an ImageKit URL
                if 'imagekit.io' in str(field):
                    continue
                
                # Get local file path
                local_path = field.path if hasattr(field, 'path') else None
                if local_path and os.path.exists(local_path):
                    # Upload to ImageKit
                    imagekit_url = upload_to_imagekit(local_path)
                    if imagekit_url:
                        # Update the field
                        setattr(instance, field_name, imagekit_url)
                        instance.save()
                        print(f"✅ Updated {model.__name__} {instance.id}: {imagekit_url}")
                    else:
                        print(f"❌ Failed to upload {local_path}")
                else:
                    print(f"⚠️ File not found: {field}")
    
    print("🎉 Database update complete!")

def get_imagekit_url(local_path, folder_name="bethel"):
    """
    Get ImageKit URL for a local file, upload if needed
    """
    if not local_path or not os.path.exists(local_path):
        return None
    
    # Check if we're in production
    if not settings.DEBUG:
        # Upload to ImageKit and return URL
        return upload_to_imagekit(local_path, folder_name)
    else:
        # In development, return local path
        return f"/media/{os.path.basename(local_path)}" 