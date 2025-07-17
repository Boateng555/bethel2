#!/usr/bin/env python3
"""
Test Cloudinary using Django's configuration
"""

import os
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

import cloudinary
import cloudinary.uploader
import tempfile

print("🔍 Testing Cloudinary with Django configuration...")
print("=" * 50)

# Get credentials from Django settings
from django.conf import settings

cloud_name = settings.CLOUDINARY_STORAGE['CLOUD_NAME']
api_key = settings.CLOUDINARY_STORAGE['API_KEY']
api_secret = settings.CLOUDINARY_STORAGE['API_SECRET']

print(f"Cloud Name: {cloud_name}")
print(f"API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
print(f"API Secret: {api_secret[:8]}...{api_secret[-4:] if len(api_secret) > 12 else '***'}")

print("\n" + "=" * 50)

try:
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret
    )
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test file for Django Cloudinary configuration.")
        temp_file_path = f.name
    
    try:
        # Test upload with the temporary file
        result = cloudinary.uploader.upload(
            temp_file_path,
            public_id="test_django_credentials",
            overwrite=True
        )
        
        print("✅ Django Cloudinary upload test successful!")
        print(f"Test file URL: {result.get('secure_url', 'N/A')}")
        
        # Clean up test file from Cloudinary
        cloudinary.uploader.destroy("test_django_credentials")
        print("🧹 Test file cleaned up from Cloudinary")
        
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)
        
except Exception as e:
    print(f"❌ Django Cloudinary test failed: {e}")
    print("\nPossible issues:")
    print("1. Invalid API credentials")
    print("2. Network connectivity issues")
    print("3. Cloudinary account restrictions")
    print("4. API key/secret mismatch")

print("\n" + "=" * 50) 