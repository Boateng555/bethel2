#!/usr/bin/env python
"""
Simple debug script for ImageKit
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Set environment variables for testing
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

import django
django.setup()

from django.conf import settings
from imagekitio import ImageKit
from io import BytesIO

def test_imagekit_direct():
    """Test ImageKit directly without Django storage"""
    print("🔍 Testing ImageKit directly...")
    
    try:
        # Initialize ImageKit
        imagekit = ImageKit(
            public_key=settings.IMAGEKIT_CONFIG['PUBLIC_KEY'],
            private_key=settings.IMAGEKIT_CONFIG['PRIVATE_KEY'],
            url_endpoint=settings.IMAGEKIT_CONFIG['URL_ENDPOINT']
        )
        print("✅ ImageKit initialized successfully")
        
        # Test list files
        print("🔄 Testing list files...")
        files = imagekit.list_files()  # Work around ImageKit bug
        print(f"✅ List files successful: {len(files.list) if files.list else 0} files found")
        
        # Test upload
        print("🔄 Testing upload...")
        test_content = b"This is a test file for ImageKit upload"
        file_obj = BytesIO(test_content)
        file_obj.name = "test.txt"
        
        upload = imagekit.upload_file(
            file=file_obj,
            file_name="test.txt"
        )
        
        print(f"✅ Upload successful! Status: {upload.response_metadata.http_status_code}")
        print(f"✅ File ID: {upload.file_id}")
        print(f"✅ URL: {upload.url}")
        
        # Clean up
        print("🔄 Cleaning up test file...")
        delete_result = imagekit.delete_file(upload.file_id)
        print(f"✅ Delete successful: {delete_result.response_metadata.http_status_code}")
        
        print("\n🎉 ImageKit is working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ ImageKit test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imagekit_direct()
    sys.exit(0 if success else 1) 