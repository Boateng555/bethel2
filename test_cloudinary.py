#!/usr/bin/env python
"""
Test Cloudinary configuration
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings

def test_cloudinary():
    """Test Cloudinary configuration"""
    print("🔍 Testing Cloudinary Configuration...")
    print("=" * 50)
    
    # Check if Cloudinary is configured
    if hasattr(settings, 'CLOUDINARY_STORAGE'):
        print("✅ Cloudinary is configured!")
        print(f"Cloud Name: {settings.CLOUDINARY_STORAGE['CLOUD_NAME']}")
        print(f"API Key: {settings.CLOUDINARY_STORAGE['API_KEY']}")
        print(f"API Secret: {'*' * len(settings.CLOUDINARY_STORAGE['API_SECRET'])}")
        print(f"Storage: {settings.DEFAULT_FILE_STORAGE}")
    else:
        print("❌ Cloudinary is NOT configured!")
        print(f"Storage: {settings.DEFAULT_FILE_STORAGE}")
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    
    print(f"CLOUDINARY_CLOUD_NAME: {cloud_name or 'NOT SET'}")
    print(f"CLOUDINARY_API_KEY: {api_key or 'NOT SET'}")
    print(f"CLOUDINARY_API_SECRET: {'*' * len(api_secret) if api_secret else 'NOT SET'}")
    
    if all([cloud_name, api_key, api_secret]):
        print("\n✅ All Cloudinary environment variables are set!")
    else:
        print("\n❌ Missing Cloudinary environment variables!")
        print("Please set them in Railway Variables tab.")

if __name__ == "__main__":
    test_cloudinary() 