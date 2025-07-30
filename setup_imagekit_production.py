#!/usr/bin/env python3
"""
ImageKit Production Setup Script
This script helps you set up ImageKit for production deployment.
"""

import os
import sys
import requests
import json
from datetime import datetime

def check_imagekit_credentials():
    """Check if ImageKit credentials are properly configured"""
    print("🔍 Checking ImageKit Configuration")
    print("=" * 50)
    
    required_vars = [
        'IMAGEKIT_PUBLIC_KEY',
        'IMAGEKIT_PRIVATE_KEY', 
        'IMAGEKIT_URL_ENDPOINT'
    ]
    
    config = {}
    missing_vars = []
    
    for var in required_vars:
        value = os.environ.get(var)
        config[var] = value
        if not value:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {'*' * (len(value) - 8) + value[-8:] if len(value) > 8 else '***'}")
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        return False, config
    
    print(f"\n✅ All ImageKit credentials are configured!")
    return True, config

def test_imagekit_connection(config):
    """Test connection to ImageKit API"""
    print(f"\n🌐 Testing ImageKit Connection")
    print("=" * 50)
    
    try:
        import imagekitio
        
        # Initialize ImageKit
        imagekit = imagekitio.ImageKit(
            public_key=config['IMAGEKIT_PUBLIC_KEY'],
            private_key=config['IMAGEKIT_PRIVATE_KEY'],
            url_endpoint=config['IMAGEKIT_URL_ENDPOINT']
        )
        
        # Test API connection by listing files
        files = imagekit.list_files(options={"limit": 1})
        
        if files.response_metadata.http_status_code == 200:
            print("✅ ImageKit API connection successful!")
            print(f"   Files in account: {len(files.list)}")
            return True
        else:
            print(f"❌ ImageKit API connection failed: {files.response_metadata.http_status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ImageKit connection test failed: {e}")
        return False

def test_imagekit_upload(config):
    """Test uploading a file to ImageKit"""
    print(f"\n📤 Testing ImageKit Upload")
    print("=" * 50)
    
    try:
        import imagekitio
        from django.core.files.base import ContentFile
        
        # Create test image
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="300" height="200" fill="#3b82f6"/>
  <text x="150" y="100" font-family="Arial" font-size="24" fill="white" text-anchor="middle">BETHEL</text>
  <text x="150" y="130" font-family="Arial" font-size="16" fill="white" text-anchor="middle">ImageKit Test</text>
</svg>'''
        
        test_image = ContentFile(svg_content.encode('utf-8'), name="bethel_test.svg")
        
        # Initialize ImageKit
        imagekit = imagekitio.ImageKit(
            public_key=config['IMAGEKIT_PUBLIC_KEY'],
            private_key=config['IMAGEKIT_PRIVATE_KEY'],
            url_endpoint=config['IMAGEKIT_URL_ENDPOINT']
        )
        
        # Upload test file
        upload = imagekit.upload_file(
            file=test_image,
            file_name="bethel_test.svg",
            options={
                "folder": "bethel/test",
                "use_unique_file_name": False
            }
        )
        
        if upload.response_metadata.http_status_code == 200:
            print("✅ ImageKit upload test successful!")
            print(f"   File ID: {upload.file_id}")
            print(f"   File URL: {upload.url}")
            print(f"   File Path: {upload.file_path}")
            
            # Clean up test file
            try:
                result = imagekit.delete_file(upload.file_id)
                if result.response_metadata.http_status_code == 200:
                    print("   🧹 Test file cleaned up")
                else:
                    print("   ⚠️ Could not clean up test file")
            except Exception as e:
                print(f"   ⚠️ Cleanup failed: {e}")
            
            return True
        else:
            print(f"❌ ImageKit upload failed: {upload.response_metadata.http_status_code}")
            print(f"   Error: {upload.response_metadata.raw}")
            return False
            
    except Exception as e:
        print(f"❌ ImageKit upload test failed: {e}")
        return False

def create_env_template():
    """Create a template .env file for local testing"""
    print(f"\n📄 Creating .env Template")
    print("=" * 50)
    
    env_content = """# ImageKit Configuration
# Get these from https://imagekit.io → Developer Options → API Keys

IMAGEKIT_PUBLIC_KEY=your_public_key_here
IMAGEKIT_PRIVATE_KEY=your_private_key_here
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_endpoint

# Django Settings
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your_secret_key_here

# Database (for local testing)
DATABASE_URL=sqlite:///db.sqlite3
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env.template file")
    print("   Copy this to .env and fill in your ImageKit credentials")

def main():
    print("🖼️ ImageKit Production Setup")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check current configuration
    has_credentials, config = check_imagekit_credentials()
    
    if has_credentials:
        print(f"\n🎯 Testing ImageKit Setup...")
        
        # Test connection
        if test_imagekit_connection(config):
            # Test upload
            if test_imagekit_upload(config):
                print(f"\n🎉 ImageKit is fully configured and working!")
                print(f"   Your Django app will use ImageKit for storage")
                print(f"   Images will be served via CDN for better performance")
            else:
                print(f"\n⚠️ ImageKit credentials are set but upload test failed")
                print(f"   Check your API permissions and try again")
        else:
            print(f"\n❌ ImageKit connection failed")
            print(f"   Check your credentials and try again")
    else:
        print(f"\n📋 Setup Required")
        print(f"   ImageKit credentials are not configured")
        print(f"   Follow the instructions below to set them up")
    
    # Create template
    create_env_template()
    
    print(f"\n" + "=" * 60)
    print(f"🎯 Next Steps:")
    print(f"1. Get ImageKit credentials from https://imagekit.io")
    print(f"2. Set environment variables in your environment")
    print(f"3. Deploy your application")
    print(f"4. Test image uploads on your live site")
    print(f"=" * 60)

if __name__ == "__main__":
    main() 