#!/usr/bin/env python
"""
Simple script to test and fix ImageKit uploads
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
import requests

def test_direct_imagekit_upload():
    """Test direct ImageKit upload using the ImageKit SDK"""
    print("🧪 Testing direct ImageKit upload...")
    
    try:
        from imagekitio import ImageKit
        
        # Initialize ImageKit
        imagekit = ImageKit(
            public_key=settings.IMAGEKIT_CONFIG['PUBLIC_KEY'],
            private_key=settings.IMAGEKIT_CONFIG['PRIVATE_KEY'],
            url_endpoint=settings.IMAGEKIT_CONFIG['URL_ENDPOINT']
        )
        
        # Create test content
        test_content = b"This is a test image content for direct ImageKit upload"
        
        # Upload directly to ImageKit
        upload = imagekit.upload_file(
            file=test_content,
            file_name="direct_test.jpg"
        )
        
        if upload.response_metadata.http_status_code == 200:
            print("✅ Direct ImageKit upload successful!")
            print(f"File ID: {upload.file_id}")
            print(f"File URL: {upload.url}")
            print(f"File Path: {upload.file_path}")
            
            # Test the URL
            try:
                response = requests.head(upload.url, timeout=10)
                if response.status_code == 200:
                    print("✅ Uploaded file is accessible!")
                    return True
                else:
                    print(f"⚠️ Uploaded file returned status: {response.status_code}")
                    return False
            except Exception as e:
                print(f"⚠️ Could not verify uploaded file: {e}")
                return False
        else:
            print(f"❌ Direct ImageKit upload failed: {upload.response_metadata.raw}")
            return False
            
    except Exception as e:
        print(f"❌ Direct ImageKit upload test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_django_storage_upload():
    """Test Django storage upload"""
    print("\n🧪 Testing Django storage upload...")
    
    try:
        from django.core.files.storage import default_storage
        
        # Create test content
        test_content = b"This is a test image content for Django storage upload"
        test_file = ContentFile(test_content, name='django_test.jpg')
        
        # Upload using Django storage
        file_path = default_storage.save('hero/django_test.jpg', test_file)
        file_url = default_storage.url(file_path)
        
        print(f"✅ Django storage upload successful!")
        print(f"File path: {file_path}")
        print(f"File URL: {file_url}")
        
        # Test the URL
        try:
            response = requests.head(file_url, timeout=10)
            if response.status_code == 200:
                print("✅ Uploaded file is accessible!")
                return True
            else:
                print(f"⚠️ Uploaded file returned status: {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠️ Could not verify uploaded file: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Django storage upload test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_upload():
    """Test model upload"""
    print("\n🧪 Testing model upload...")
    
    try:
        # Get first church and hero
        church = Church.objects.first()
        if not church:
            print("❌ No churches found")
            return False
        
        hero = church.hero_set.first()
        if not hero:
            print("❌ No hero found")
            return False
        
        # Create test content
        test_content = b"This is a test image content for model upload"
        test_file = ContentFile(test_content, name='model_test.jpg')
        
        # Create hero media
        hero_media = HeroMedia.objects.create(
            hero=hero,
            image=test_file,
            order=999
        )
        
        print(f"✅ Model upload successful!")
        print(f"Image URL: {hero_media.image.url}")
        print(f"Image path: {hero_media.image.name}")
        
        # Test the URL
        try:
            response = requests.head(hero_media.image.url, timeout=10)
            if response.status_code == 200:
                print("✅ Uploaded image is accessible!")
                success = True
            else:
                print(f"⚠️ Uploaded image returned status: {response.status_code}")
                success = False
        except Exception as e:
            print(f"⚠️ Could not verify uploaded image: {e}")
            success = False
        
        # Clean up
        hero_media.delete()
        print("✅ Test cleaned up")
        
        return success
        
    except Exception as e:
        print(f"❌ Model upload test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_imagekit_dashboard():
    """Check what files exist in ImageKit dashboard"""
    print("\n🔍 Checking ImageKit dashboard...")
    
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
            print(f"✅ Found {len(files.list)} files in ImageKit dashboard:")
            for file in files.list[:10]:  # Show first 10 files
                print(f"  - {file.file_path} ({file.size} bytes)")
            
            if len(files.list) > 10:
                print(f"  ... and {len(files.list) - 10} more files")
        else:
            print(f"❌ Could not list files: {files.response_metadata.raw}")
            
    except Exception as e:
        print(f"❌ Could not check ImageKit dashboard: {e}")

if __name__ == "__main__":
    print("🔍 ImageKit Upload Diagnostic")
    print("=" * 50)
    
    # Test different upload methods
    direct_ok = test_direct_imagekit_upload()
    django_ok = test_django_storage_upload()
    model_ok = test_model_upload()
    
    # Check dashboard
    check_imagekit_dashboard()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS")
    print("=" * 50)
    print(f"Direct ImageKit upload: {'✅ Working' if direct_ok else '❌ Failed'}")
    print(f"Django storage upload: {'✅ Working' if django_ok else '❌ Failed'}")
    print(f"Model upload: {'✅ Working' if model_ok else '❌ Failed'}")
    
    if direct_ok and not (django_ok and model_ok):
        print("\n🔧 ISSUE IDENTIFIED:")
        print("Direct ImageKit uploads work, but Django storage uploads don't.")
        print("This suggests an issue with the Django storage configuration.")
    elif not direct_ok:
        print("\n🔧 ISSUE IDENTIFIED:")
        print("Direct ImageKit uploads don't work. Check your ImageKit credentials.")
    else:
        print("\n🎉 All upload methods are working!") 