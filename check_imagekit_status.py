#!/usr/bin/env python
"""
Quick script to check ImageKit and media configuration status
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings

def main():
    print("🔍 ImageKit and Media Configuration Check")
    print("=" * 50)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    print(f"DJANGO_DEBUG: {os.environ.get('DJANGO_DEBUG', 'Not set')}")
    print(f"IMAGEKIT_PUBLIC_KEY: {'✅ Set' if os.environ.get('IMAGEKIT_PUBLIC_KEY') else '❌ Not set'}")
    print(f"IMAGEKIT_PRIVATE_KEY: {'✅ Set' if os.environ.get('IMAGEKIT_PRIVATE_KEY') else '❌ Not set'}")
    print(f"IMAGEKIT_URL_ENDPOINT: {'✅ Set' if os.environ.get('IMAGEKIT_URL_ENDPOINT') else '❌ Not set'}")
    print(f"CLOUDINARY_CLOUD_NAME: {'✅ Set' if os.environ.get('CLOUDINARY_CLOUD_NAME') else '❌ Not set'}")
    
    # Check Django settings
    print("\n⚙️ Django Settings:")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    
    # Check ImageKit configuration
    print("\n🖼️ ImageKit Configuration:")
    if hasattr(settings, 'IMAGEKIT_CONFIG'):
        config = settings.IMAGEKIT_CONFIG
        print(f"Public Key: {'✅ Set' if config.get('PUBLIC_KEY') else '❌ Not set'}")
        print(f"Private Key: {'✅ Set' if config.get('PRIVATE_KEY') else '❌ Not set'}")
        print(f"URL Endpoint: {'✅ Set' if config.get('URL_ENDPOINT') else '❌ Not set'}")
    else:
        print("❌ IMAGEKIT_CONFIG not found in settings")
    
    # Check Cloudinary configuration
    print("\n☁️ Cloudinary Configuration:")
    if hasattr(settings, 'CLOUDINARY_STORAGE'):
        config = settings.CLOUDINARY_STORAGE
        print(f"Cloud Name: {'✅ Set' if config.get('CLOUD_NAME') else '❌ Not set'}")
        print(f"API Key: {'✅ Set' if config.get('API_KEY') else '❌ Not set'}")
        print(f"API Secret: {'✅ Set' if config.get('API_SECRET') else '❌ Not set'}")
    else:
        print("❌ CLOUDINARY_STORAGE not found in settings")
    
    # Determine current storage backend
    print("\n🎯 Current Storage Backend:")
    if settings.DEBUG:
        print("🔧 Using local storage (DEBUG=True)")
    elif 'ImageKitStorage' in str(settings.DEFAULT_FILE_STORAGE):
        print("🖼️ Using ImageKit storage")
    elif 'CloudinaryStorage' in str(settings.DEFAULT_FILE_STORAGE):
        print("☁️ Using Cloudinary storage")
    else:
        print("📁 Using local file system storage")
    
    print("\n" + "=" * 50)
    print("✅ Check completed!")

if __name__ == "__main__":
    main() 