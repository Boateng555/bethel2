#!/usr/bin/env python
"""
Test script to verify ImageKit deployment status
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings

def main():
    print("🚀 ImageKit Deployment Test")
    print("=" * 50)
    print(f"Timestamp: {os.environ.get('RAILWAY_DEPLOYMENT_TIMESTAMP', 'Not set')}")
    print(f"Environment: {'Production' if not settings.DEBUG else 'Development'}")
    print(f"Storage Backend: {settings.DEFAULT_FILE_STORAGE}")
    
    # Check ImageKit credentials
    imagekit_public = os.environ.get('IMAGEKIT_PUBLIC_KEY')
    imagekit_private = os.environ.get('IMAGEKIT_PRIVATE_KEY')
    imagekit_endpoint = os.environ.get('IMAGEKIT_URL_ENDPOINT')
    
    print(f"\n🖼️ ImageKit Credentials:")
    print(f"  Public Key: {'✅ Set' if imagekit_public else '❌ Not set'}")
    print(f"  Private Key: {'✅ Set' if imagekit_private else '❌ Not set'}")
    print(f"  URL Endpoint: {'✅ Set' if imagekit_endpoint else '❌ Not set'}")
    
    if all([imagekit_public, imagekit_private, imagekit_endpoint]):
        print("🎉 All ImageKit credentials are configured!")
        print("✅ ImageKit should be working on production")
    else:
        print("⚠️ Some ImageKit credentials are missing")
        print("🔧 Please check Railway environment variables")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    main() 