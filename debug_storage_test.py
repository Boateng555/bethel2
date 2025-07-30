#!/usr/bin/env python3
"""
Debug Storage Test
Detailed debugging of the storage save method
"""

import os
import sys
import django
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Set ImageKit environment variables directly
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def debug_storage_save():
    """Debug the storage save method step by step"""
    print("🔍 Debugging Storage Save Method...")
    
    try:
        # Create a test image
        img = Image.new('RGB', (300, 200), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), "Debug Test", fill='black', font=font)
        draw.text((50, 100), "Storage Debug", fill='darkblue', font=font)
        
        # Save to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG', quality=95)
        img_bytes.seek(0)
        
        print(f"  🖼️ Test image created: {len(img_bytes.getvalue())} bytes")
        
        # Create test file
        test_file = ContentFile(img_bytes.getvalue(), name="debug_test.jpg")
        print(f"  📁 Test file name: {test_file.name}")
        
        # Check storage type
        print(f"  💾 Storage type: {type(default_storage)}")
        print(f"  🔗 Storage class: {default_storage.__class__.__name__}")
        
        # Save using Django storage
        print("  📤 Calling default_storage.save()...")
        saved_path = default_storage.save("test/debug_test.jpg", test_file)
        
        print(f"  📁 Returned path: {saved_path}")
        print(f"  📁 Path type: {type(saved_path)}")
        print(f"  🔍 Contains 'ik.imagekit.io': {'ik.imagekit.io' in str(saved_path)}")
        print(f"  🔍 Contains 'https://': {'https://' in str(saved_path)}")
        
        # Test URL generation
        print("  🔗 Testing URL generation...")
        url = default_storage.url(saved_path)
        print(f"  🔗 Generated URL: {url}")
        print(f"  🔗 URL type: {type(url)}")
        
        # Check if it's an ImageKit URL
        if 'ik.imagekit.io' in str(saved_path) or 'ik.imagekit.io' in str(url):
            print("  ✅ File saved to ImageKit")
            return True, saved_path
        else:
            print("  ❌ File not saved to ImageKit")
            print(f"  📋 Full saved path: {repr(saved_path)}")
            print(f"  📋 Full URL: {repr(url)}")
            return False, saved_path
            
    except Exception as e:
        print(f"  ❌ Storage save error: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def main():
    """Run debug test"""
    print("🚀 Debug Storage Test")
    print("=" * 40)
    
    success, saved_path = debug_storage_save()
    
    if success:
        print("\n✅ Storage is working with ImageKit!")
    else:
        print("\n❌ Storage is not working with ImageKit!")
        print("\n🔧 This suggests there might be an issue with:")
        print("   1. The storage backend configuration")
        print("   2. The ImageKit credentials")
        print("   3. The upload process")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 