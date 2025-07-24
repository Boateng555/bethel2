#!/usr/bin/env python3
"""
ImageKit Setup Script
This script helps you set up ImageKit environment variables for local development.
"""

import os
import sys

def setup_imagekit():
    print("🖼️ ImageKit Setup for Local Development")
    print("=" * 50)
    
    print("\nTo use ImageKit for media storage, you need to:")
    print("1. Sign up at https://imagekit.io")
    print("2. Get your API credentials from Developer Options → API Keys")
    print("3. Set the environment variables below")
    
    print("\n" + "=" * 50)
    print("📝 Environment Variables to Set:")
    print("=" * 50)
    
    # Check current values
    public_key = os.environ.get('IMAGEKIT_PUBLIC_KEY', 'Not set')
    private_key = os.environ.get('IMAGEKIT_PRIVATE_KEY', 'Not set')
    url_endpoint = os.environ.get('IMAGEKIT_URL_ENDPOINT', 'Not set')
    
    print(f"IMAGEKIT_PUBLIC_KEY={public_key}")
    print(f"IMAGEKIT_PRIVATE_KEY={private_key}")
    print(f"IMAGEKIT_URL_ENDPOINT={url_endpoint}")
    
    print("\n" + "=" * 50)
    print("🔧 How to Set Environment Variables:")
    print("=" * 50)
    
    print("\nOption 1: PowerShell (Current Session)")
    print("$env:IMAGEKIT_PUBLIC_KEY='your_public_key'")
    print("$env:IMAGEKIT_PRIVATE_KEY='your_private_key'")
    print("$env:IMAGEKIT_URL_ENDPOINT='your_url_endpoint'")
    
    print("\nOption 2: Create .env file")
    print("Create a .env file in your project root with:")
    print("IMAGEKIT_PUBLIC_KEY=your_public_key")
    print("IMAGEKIT_PRIVATE_KEY=your_private_key")
    print("IMAGEKIT_URL_ENDPOINT=your_url_endpoint")
    
    print("\nOption 3: Windows Environment Variables")
    print("1. Open System Properties → Environment Variables")
    print("2. Add the variables to User Variables")
    
    print("\n" + "=" * 50)
    print("✅ Current Storage Status:")
    print("=" * 50)
    
    if all([public_key != 'Not set', private_key != 'Not set', url_endpoint != 'Not set']):
        print("🖼️ ImageKit is configured! Your app will use ImageKit for storage.")
    else:
        print("⚙️ ImageKit not configured. Using local storage.")
        print("   (This is fine for development)")
    
    print("\n" + "=" * 50)
    print("🚀 Next Steps:")
    print("=" * 50)
    print("1. Get your ImageKit credentials from https://imagekit.io")
    print("2. Set the environment variables using one of the options above")
    print("3. Restart your Django server")
    print("4. Test by uploading an image through the admin interface")
    
    print("\n💡 For production (Railway), set these in Railway dashboard:")
    print("   - Go to your Railway project")
    print("   - Click Variables tab")
    print("   - Add the three IMAGEKIT_* variables")

if __name__ == "__main__":
    setup_imagekit() 