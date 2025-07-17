#!/usr/bin/env python3
"""
Test Cloudinary credentials and configuration
"""

import os
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Testing Cloudinary Configuration...")
print("=" * 50)

# Check environment variables
cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
api_key = os.environ.get('CLOUDINARY_API_KEY')
api_secret = os.environ.get('CLOUDINARY_API_SECRET')

print(f"CLOUDINARY_CLOUD_NAME: {'✅ Set' if cloud_name else '❌ Not set'}")
print(f"CLOUDINARY_API_KEY: {'✅ Set' if api_key else '❌ Not set'}")
print(f"CLOUDINARY_API_SECRET: {'✅ Set' if api_secret else '❌ Not set'}")

if cloud_name:
    print(f"Cloud Name: {cloud_name}")
if api_key:
    print(f"API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
if api_secret:
    print(f"API Secret: {api_secret[:8]}...{api_secret[-4:] if len(api_secret) > 12 else '***'}")

print("\n" + "=" * 50)

if all([cloud_name, api_key, api_secret]):
    print("✅ All Cloudinary credentials are set!")
    print("🔧 Testing upload capability...")
    
    try:
        import cloudinary
        import cloudinary.uploader
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test file for Cloudinary credentials verification.")
            temp_file_path = f.name
        
        try:
            # Test upload with the temporary file
            result = cloudinary.uploader.upload(
                temp_file_path,
                public_id="test_credentials",
                overwrite=True
            )
            
            print("✅ Cloudinary upload test successful!")
            print(f"Test file URL: {result.get('secure_url', 'N/A')}")
            
            # Clean up test file from Cloudinary
            cloudinary.uploader.destroy("test_credentials")
            print("🧹 Test file cleaned up from Cloudinary")
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
        
    except Exception as e:
        print(f"❌ Cloudinary test failed: {e}")
        print("\nPossible issues:")
        print("1. Invalid API credentials")
        print("2. Network connectivity issues")
        print("3. Cloudinary account restrictions")
        print("4. API key/secret mismatch")
        
else:
    print("❌ Missing Cloudinary credentials!")
    print("\nTo fix this:")
    print("1. Go to your Cloudinary Dashboard")
    print("2. Copy your Cloud Name, API Key, and API Secret")
    print("3. Set them as environment variables:")
    print("   - CLOUDINARY_CLOUD_NAME")
    print("   - CLOUDINARY_API_KEY") 
    print("   - CLOUDINARY_API_SECRET")

print("\n" + "=" * 50)
print("🔧 Current Django settings:")
print(f"DEBUG: {os.environ.get('DJANGO_DEBUG', 'Not set')}")
print(f"Storage: {'Local' if os.environ.get('DJANGO_DEBUG') == 'True' else 'Cloudinary'}") 