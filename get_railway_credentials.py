#!/usr/bin/env python3
"""
Get Cloudinary credentials from Railway or guide user through setup
"""

import os
import subprocess
import sys

def get_railway_credentials():
    """Try to get credentials from Railway or guide user"""
    
    print("🔍 Checking for Cloudinary credentials...")
    
    # Check if we're on Railway
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        print("✅ Running on Railway")
        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
        api_key = os.environ.get('CLOUDINARY_API_KEY')
        api_secret = os.environ.get('CLOUDINARY_API_SECRET')
        
        if all([cloud_name, api_key, api_secret]):
            print("✅ Cloudinary credentials found on Railway!")
            print(f"Cloud Name: {cloud_name}")
            print(f"API Key: {api_key[:10]}...")
            print(f"API Secret: {api_secret[:10]}...")
            return True
        else:
            print("❌ Cloudinary credentials not found on Railway")
    else:
        print("ℹ️ Running locally")
    
    # Check local .env file
    if os.path.exists('.env'):
        print("📁 .env file found")
        with open('.env', 'r') as f:
            content = f.read()
            if 'your-cloud-name-here' in content or 'your-api-key-here' in content:
                print("⚠️ .env file still has placeholder values")
                print("\n📋 You need to update your .env file with real credentials:")
                print("1. Go to https://cloudinary.com/console")
                print("2. Sign in to your account")
                print("3. Copy your Cloud Name, API Key, and API Secret")
                print("4. Update the .env file")
                return False
            else:
                print("✅ .env file appears to have real credentials")
                return True
    else:
        print("❌ .env file not found")
    
    return False

def guide_user_through_setup():
    """Guide user through getting Cloudinary credentials"""
    
    print("\n" + "="*60)
    print("📋 CLOUDINARY SETUP GUIDE")
    print("="*60)
    
    print("\n1️⃣ Go to Cloudinary Dashboard:")
    print("   https://cloudinary.com/console")
    
    print("\n2️⃣ Sign in to your account")
    
    print("\n3️⃣ Find your credentials:")
    print("   - Cloud Name (usually shown at the top)")
    print("   - API Key (in the API Keys section)")
    print("   - API Secret (in the API Keys section)")
    
    print("\n4️⃣ Update your .env file:")
    print("   Open .env file and replace:")
    print("   CLOUDINARY_CLOUD_NAME=your-cloud-name-here")
    print("   CLOUDINARY_API_KEY=your-api-key-here")
    print("   CLOUDINARY_API_SECRET=your-api-secret-here")
    
    print("\n5️⃣ Test your credentials:")
    print("   python test_cloudinary_credentials_final.py")
    
    print("\n6️⃣ Upload your media:")
    print("   python manage.py upload_actual_media_to_cloudinary")
    
    print("\n" + "="*60)

def try_railway_cli():
    """Try to get credentials using Railway CLI"""
    
    print("\n🔧 Trying to get credentials from Railway...")
    
    try:
        # Try to get environment variables from Railway
        result = subprocess.run(['railway', 'variables'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI available")
            print(result.stdout)
            return True
        else:
            print("❌ Railway CLI not available or not logged in")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI not installed")
        return False

if __name__ == "__main__":
    print("🚀 Cloudinary Credentials Setup")
    print("="*40)
    
    if get_railway_credentials():
        print("\n✅ Credentials are available!")
        print("You can now run: python test_cloudinary_credentials_final.py")
    else:
        print("\n❌ Credentials not found")
        
        # Try Railway CLI
        if not try_railway_cli():
            guide_user_through_setup()
        
        print("\n💡 Alternative: If you know your credentials work on Railway,")
        print("   you can copy them from your Railway dashboard:")
        print("   1. Go to https://railway.app")
        print("   2. Select your project")
        print("   3. Go to Variables tab")
        print("   4. Copy CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET")
        print("   5. Add them to your local .env file") 