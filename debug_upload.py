#!/usr/bin/env python
"""
Debug script to see exactly what's happening during uploads
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Set ImageKit environment variables
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

from django.core.files.base import ContentFile
from django.conf import settings
from core.models import Church, HeroMedia
from io import BytesIO

def debug_upload_process():
    """Debug the upload process step by step"""
    print("🔍 Debugging upload process...")
    
    try:
        from imagekitio import ImageKit
        
        # Initialize ImageKit
        imagekit = ImageKit(
            public_key=settings.IMAGEKIT_CONFIG['PUBLIC_KEY'],
            private_key=settings.IMAGEKIT_CONFIG['PRIVATE_KEY'],
            url_endpoint=settings.IMAGEKIT_CONFIG['URL_ENDPOINT']
        )
        
        # Test content
        test_content = b"Debug test content"
        test_file = ContentFile(test_content, name='debug_test.jpg')
        
        print(f"Original filename: {test_file.name}")
        
        # Create file object
        file_obj = BytesIO(test_content)
        file_obj.seek(0)
        file_obj.name = os.path.basename('hero/debug_test.jpg')
        
        print(f"File object name: {file_obj.name}")
        
        # Upload to ImageKit
        upload = imagekit.upload_file(
            file=file_obj,
            file_name=os.path.basename('hero/debug_test.jpg')
        )
        
        print(f"Upload response status: {upload.response_metadata.http_status_code}")
        print(f"Uploaded file ID: {upload.file_id}")
        print(f"Uploaded file path: {upload.file_path}")
        print(f"Uploaded file URL: {upload.url}")
        print(f"Uploaded file name: {upload.file_name}")
        
        # Test URL accessibility
        import requests
        try:
            response = requests.head(upload.url, timeout=10)
            print(f"URL accessibility: {response.status_code}")
        except Exception as e:
            print(f"URL accessibility error: {e}")
        
        return upload
        
    except Exception as e:
        print(f"Debug upload failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def debug_django_storage():
    """Debug Django storage upload"""
    print("\n🔍 Debugging Django storage...")
    
    try:
        from django.core.files.storage import default_storage
        
        # Test content
        test_content = b"Django storage debug test"
        test_file = ContentFile(test_content, name='django_debug.jpg')
        
        print(f"Original filename: {test_file.name}")
        
        # Upload using Django storage
        file_path = default_storage.save('hero/django_debug.jpg', test_file)
        file_url = default_storage.url(file_path)
        
        print(f"Returned file path: {file_path}")
        print(f"Generated URL: {file_url}")
        
        # Test URL accessibility
        import requests
        try:
            response = requests.head(file_url, timeout=10)
            print(f"URL accessibility: {response.status_code}")
        except Exception as e:
            print(f"URL accessibility error: {e}")
        
        return file_path, file_url
        
    except Exception as e:
        print(f"Django storage debug failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def check_recent_uploads():
    """Check the most recent uploads in ImageKit"""
    print("\n🔍 Checking recent uploads...")
    
    try:
        from imagekitio import ImageKit
        
        # Initialize ImageKit
        imagekit = ImageKit(
            public_key=settings.IMAGEKIT_CONFIG['PUBLIC_KEY'],
            private_key=settings.IMAGEKIT_CONFIG['PRIVATE_KEY'],
            url_endpoint=settings.IMAGEKIT_CONFIG['URL_ENDPOINT']
        )
        
        # List files
        files = imagekit.list_files()
        
        if files.response_metadata.http_status_code == 200:
            print(f"Total files: {len(files.list)}")
            print("Recent files:")
            for file in files.list[-5:]:  # Last 5 files
                print(f"  - {file.file_path} ({file.size} bytes) - {file.created_at}")
        else:
            print(f"Could not list files: {files.response_metadata.raw}")
            
    except Exception as e:
        print(f"Check recent uploads failed: {e}")

if __name__ == "__main__":
    print("🔍 Upload Debug Tool")
    print("=" * 50)
    
    # Debug direct upload
    upload_result = debug_upload_process()
    
    # Debug Django storage
    django_path, django_url = debug_django_storage()
    
    # Check recent uploads
    check_recent_uploads()
    
    print("\n" + "=" * 50)
    print("📊 DEBUG SUMMARY")
    print("=" * 50)
    
    if upload_result:
        print(f"Direct upload: ✅ {upload_result.file_path}")
    else:
        print("Direct upload: ❌ Failed")
    
    if django_path:
        print(f"Django storage: ✅ {django_path}")
    else:
        print("Django storage: ❌ Failed") 