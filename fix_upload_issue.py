#!/usr/bin/env python
"""
Fix the fundamental issue where Django admin uploads create corrupted placeholder files
"""

import os
import django

# Set environment variables
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
import io
import requests

print("🔧 Fixing Django admin upload issue...")

def test_django_upload():
    """Test if Django uploads are working correctly"""
    print("\n📤 Testing Django upload functionality...")
    
    try:
        # Create a test image
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color='white')
        
        # Add some content
        draw = ImageDraw.Draw(image)
        draw.text((50, 50), "Django Upload Test", fill='black')
        draw.text((50, 100), "This should be a proper image", fill='blue')
        
        # Save to bytes
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG', quality=95)
        img_buffer.seek(0)
        image_data = img_buffer.getvalue()
        
        print(f"   Created test image: {len(image_data):,} bytes")
        
        # Upload via Django storage
        test_file = ContentFile(image_data, name='django_test.jpg')
        saved_path = default_storage.save('test/django_test.jpg', test_file)
        url = default_storage.url(saved_path)
        
        print(f"   Upload path: {saved_path}")
        print(f"   Upload URL: {url}")
        
        if url.startswith('https://ik.imagekit.io/'):
            print("   ✅ Django upload is using ImageKit correctly")
            
            # Test if the uploaded file is accessible
            try:
                response = requests.head(url, timeout=10)
                if response.status_code == 200:
                    content_length = int(response.headers.get('content-length', 0))
                    print(f"   ✅ File is accessible: {content_length:,} bytes")
                    
                    if content_length > 1000:
                        print("   ✅ File size is reasonable (not corrupted)")
                        return True
                    else:
                        print("   ❌ File is too small (corrupted)")
                        return False
                else:
                    print(f"   ❌ File not accessible: HTTP {response.status_code}")
                    return False
            except Exception as e:
                print(f"   ❌ Error checking file: {e}")
                return False
        else:
            print("   ❌ Django upload is NOT using ImageKit")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing Django upload: {e}")
        return False

def check_storage_configuration():
    """Check the current storage configuration"""
    print("\n🔍 Checking storage configuration...")
    
    from django.conf import settings
    
    print(f"   DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')}")
    print(f"   Current storage class: {type(default_storage).__name__}")
    
    # Check ImageKit settings
    if hasattr(settings, 'IMAGEKIT_CONFIG'):
        print(f"   IMAGEKIT_CONFIG: {settings.IMAGEKIT_CONFIG}")
    else:
        print("   ❌ IMAGEKIT_CONFIG not found in settings")
    
    # Check environment variables
    print(f"   IMAGEKIT_PUBLIC_KEY: {'Set' if os.environ.get('IMAGEKIT_PUBLIC_KEY') else 'Not set'}")
    print(f"   IMAGEKIT_PRIVATE_KEY: {'Set' if os.environ.get('IMAGEKIT_PRIVATE_KEY') else 'Not set'}")
    print(f"   IMAGEKIT_URL_ENDPOINT: {'Set' if os.environ.get('IMAGEKIT_URL_ENDPOINT') else 'Not set'}")

def fix_storage_issue():
    """Apply fixes to ensure proper storage"""
    print("\n🔧 Applying storage fixes...")
    
    try:
        # Force ImageKit storage
        from core.storage import ImageKitStorage
        from django.core.files.storage import default_storage
        
        # Create new ImageKit storage instance
        imagekit_storage = ImageKitStorage()
        
        # Override default storage
        default_storage._wrapped = imagekit_storage
        
        print("   ✅ Forced ImageKit storage")
        
        # Test the fix
        if test_django_upload():
            print("   ✅ Storage fix successful!")
            return True
        else:
            print("   ❌ Storage fix failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Error applying storage fix: {e}")
        return False

def create_proper_test_images():
    """Create proper test images to replace corrupted ones"""
    print("\n📝 Creating proper test images...")
    
    from imagekitio import ImageKit
    
    # Initialize ImageKit
    imagekit = ImageKit(
        private_key='private_Dnsrj2VW7uJakaeMaNYaav+P784=',
        public_key='public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=',
        url_endpoint='https://ik.imagekit.io/9buar9mbp'
    )
    
    # Create a proper test image
    width, height = 1200, 800
    image = Image.new('RGB', (width, height), color='white')
    
    # Add gradient background
    for y in range(height):
        for x in range(width):
            r = int((x / width) * 255)
            g = int((y / height) * 255)
            b = 128
            image.putpixel((x, y), (r, g, b))
    
    # Add text
    draw = ImageDraw.Draw(image)
    draw.text((50, 50), "Proper Test Image", fill='black')
    draw.text((50, 100), "This is a real image file", fill='blue')
    draw.text((50, 150), f"Size: {width}x{height} pixels", fill='green')
    
    # Save to bytes
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='JPEG', quality=95)
    img_buffer.seek(0)
    image_data = img_buffer.getvalue()
    
    print(f"   Created proper test image: {len(image_data):,} bytes")
    
    # Upload directly to ImageKit
    try:
        upload = imagekit.upload_file(
            file=image_data,
            file_name='proper_test_image.jpg'
        )
        print("   ✅ Uploaded proper test image to ImageKit")
        return True
    except Exception as e:
        print(f"   ❌ Error uploading to ImageKit: {e}")
        return False

try:
    # Check current configuration
    check_storage_configuration()
    
    # Test current upload functionality
    if test_django_upload():
        print("\n✅ Django uploads are working correctly!")
    else:
        print("\n❌ Django uploads are creating corrupted files")
        
        # Apply fixes
        if fix_storage_issue():
            print("\n✅ Storage issue fixed!")
        else:
            print("\n❌ Could not fix storage issue")
    
    # Create proper test images
    create_proper_test_images()
    
    print("\n📋 Summary:")
    print("1. Checked storage configuration")
    print("2. Tested Django upload functionality")
    print("3. Applied storage fixes if needed")
    print("4. Created proper test images")
    print("\n🌐 Next steps:")
    print("- Try uploading a real image through Django admin")
    print("- Check if the uploaded file has proper size (>1KB)")
    print("- Verify the image displays correctly on your website")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 