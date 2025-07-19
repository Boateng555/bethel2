#!/usr/bin/env python3
"""
Script to set up local development environment
"""
import os
import shutil
from pathlib import Path

def setup_local_environment():
    """Set up local development environment"""
    print("🔧 Setting up local development environment...")
    
    # Check if .env exists
    if os.path.exists('.env'):
        # Backup the original .env
        if not os.path.exists('.env.production'):
            shutil.copy('.env', '.env.production')
            print("✅ Backed up production .env to .env.production")
        
        # Create local .env content
        local_env_content = """# Local Development Environment

# Database (using SQLite for local development)
# DATABASE_URL is not set, so Django will use SQLite

# Cloudinary Configuration (for existing images)
CLOUDINARY_CLOUD_NAME=dhzdusb5k
CLOUDINARY_API_KEY=your_cloudinary_api_key_here
CLOUDINARY_API_SECRET=your_cloudinary_api_secret_here

# ImageKit Configuration (for new uploads)
IMAGEKIT_PUBLIC_KEY=public_IEJhHLyqZ2J9lqJFcIZF2AOFJKQ=
IMAGEKIT_PRIVATE_KEY=private_ODyStF26VuvPNYuHJyYYoeQePkU=
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/144671b7r

# Django Settings
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=calt*nc09l)qowjzv)lb%c9vbm!r8tm(drncevpdyliuwxrqt-
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
"""
        
        # Write local .env
        with open('.env', 'w') as f:
            f.write(local_env_content)
        
        print("✅ Created local .env file with DEBUG=True and Cloudinary credentials")
        print("📝 Django will now use SQLite database for local development")
        print("🖼️ Images will work with Cloudinary URLs from your database")
        print("\n⚠️  IMPORTANT: You need to add your Cloudinary API credentials!")
        print("   Get them from: https://cloudinary.com/console")
        print("   Replace 'your_cloudinary_api_key_here' and 'your_cloudinary_api_secret_here'")
        
    else:
        print("❌ No .env file found")
        return False
    
    return True

def restore_production_env():
    """Restore production environment"""
    print("🔄 Restoring production environment...")
    
    if os.path.exists('.env.production'):
        shutil.copy('.env.production', '.env')
        print("✅ Restored production .env file")
        return True
    else:
        print("❌ No .env.production backup found")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_production_env()
    else:
        setup_local_environment() 