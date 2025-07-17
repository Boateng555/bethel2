#!/usr/bin/env python
"""
Simple script to upload media files to ImageKit
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.utils import update_media_urls_in_database

def main():
    print("🚀 Starting ImageKit upload process...")
    print("=" * 50)
    
    # Check if ImageKit credentials are available
    required_vars = ['IMAGEKIT_PUBLIC_KEY', 'IMAGEKIT_PRIVATE_KEY', 'IMAGEKIT_URL_ENDPOINT']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your Railway environment.")
        return
    
    print("✅ ImageKit credentials found")
    print(f"Public Key: {os.environ.get('IMAGEKIT_PUBLIC_KEY')[:10]}...")
    print(f"URL Endpoint: {os.environ.get('IMAGEKIT_URL_ENDPOINT')}")
    print()
    
    # Update all media URLs in the database
    update_media_urls_in_database()
    
    print("=" * 50)
    print("🎉 Upload process completed!")

if __name__ == '__main__':
    main() 