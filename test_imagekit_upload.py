#!/usr/bin/env python
"""
Simple test script to understand ImageKit API response format
"""
import os
import imagekitio
from pathlib import Path
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church

def test_imagekit_upload():
    """
    Test a simple upload to ImageKit
    """
    print("🧪 Testing ImageKit Upload...")
    print("=" * 50)
    
    # Configure ImageKit
    public_key = os.environ.get('IMAGEKIT_PUBLIC_KEY')
    private_key = os.environ.get('IMAGEKIT_PRIVATE_KEY')
    url_endpoint = os.environ.get('IMAGEKIT_URL_ENDPOINT')
    
    print(f"Public Key: {public_key[:20]}...")
    print(f"Private Key: {private_key[:20]}...")
    print(f"URL Endpoint: {url_endpoint}")
    
    # Initialize ImageKit
    imagekit = imagekitio.ImageKit(
        public_key=public_key,
        private_key=private_key,
        url_endpoint=url_endpoint
    )
    
    print("🖼️ ImageKit initialized")
    
    # Test with one church logo
    churches = Church.objects.all()
    if churches.exists():
        church = churches.first()
        print(f"\n📤 Testing with: {church.name}")
        
        if church.logo and hasattr(church.logo, 'path'):
            local_path = church.logo.path
            if os.path.exists(local_path):
                print(f"📸 Found logo: {local_path}")
                print(f"📏 File size: {os.path.getsize(local_path)} bytes")
                
                try:
                    # Upload to ImageKit
                    with open(local_path, 'rb') as file:
                        print("🔄 Uploading...")
                        result = imagekit.upload_file(
                            file=file,
                            file_name=f"test_church_{church.id}_logo{os.path.splitext(local_path)[1]}",
                            options={
                                "folder": "bethel/test",
                                "use_unique_file_name": False
                            }
                        )
                    
                    print(f"📋 Result type: {type(result)}")
                    print(f"📋 Result: {result}")
                    
                    # Try to access different attributes
                    if hasattr(result, 'response_metadata'):
                        print(f"✅ Has response_metadata")
                        print(f"📋 response_metadata: {result.response_metadata}")
                    else:
                        print(f"❌ No response_metadata")
                    
                    if hasattr(result, 'url'):
                        print(f"✅ Has url: {result.url}")
                    else:
                        print(f"❌ No url attribute")
                    
                    # Try to access as dictionary
                    if isinstance(result, dict):
                        print(f"✅ Result is a dictionary")
                        print(f"📋 Keys: {list(result.keys())}")
                        if 'url' in result:
                            print(f"✅ Found URL in dict: {result['url']}")
                    else:
                        print(f"❌ Result is not a dictionary")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"❌ File doesn't exist: {local_path}")
        else:
            print(f"❌ No logo for this church")
    else:
        print(f"❌ No churches found")

if __name__ == "__main__":
    test_imagekit_upload() 