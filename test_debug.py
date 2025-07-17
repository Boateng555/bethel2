#!/usr/bin/env python
"""
Test DEBUG and Cloudinary settings
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings

def test_settings():
    """Test current settings"""
    print("🔍 Testing Settings...")
    print("=" * 50)
    
    print(f"DEBUG: {settings.DEBUG}")
    print(f"DEBUG type: {type(settings.DEBUG)}")
    print(f"DJANGO_DEBUG env: {os.environ.get('DJANGO_DEBUG', 'NOT SET')}")
    
    print(f"\nStorage: {settings.DEFAULT_FILE_STORAGE}")
    
    # Check Cloudinary variables
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    
    print(f"\nCloudinary variables:")
    print(f"CLOUDINARY_CLOUD_NAME: {cloud_name or 'NOT SET'}")
    print(f"CLOUDINARY_API_KEY: {api_key or 'NOT SET'}")
    print(f"CLOUDINARY_API_SECRET: {'*' * len(api_secret) if api_secret else 'NOT SET'}")
    
    # Check if all are set
    all_set = all([cloud_name, api_key, api_secret])
    print(f"All Cloudinary variables set: {all_set}")
    
    # Check the logic
    if settings.DEBUG:
        print("\n🔧 Should be using local storage (DEBUG=True)")
    elif all_set:
        print("\n☁️ Should be using Cloudinary (DEBUG=False, all vars set)")
    else:
        print("\n⚠️ Should be using local storage (DEBUG=False, missing vars)")

if __name__ == "__main__":
    test_settings() 