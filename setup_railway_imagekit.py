#!/usr/bin/env python
"""
Script to help set up ImageKit environment variables in Railway
"""
import os
import subprocess
import sys

def setup_railway_imagekit():
    """Set up ImageKit environment variables in Railway"""
    print("🚀 Setting up ImageKit in Railway")
    print("=" * 50)
    
    # ImageKit credentials
    imagekit_credentials = {
        'IMAGEKIT_PUBLIC_KEY': 'public_IEJhHLyqZ2J9lqJFcIZF2AOFJKQ=',
        'IMAGEKIT_PRIVATE_KEY': 'private_ODyStF26VuvPNYuHJyYYoeQePkU=',
        'IMAGEKIT_URL_ENDPOINT': 'https://ik.imagekit.io/144671b7r'
    }
    
    print("📋 Your ImageKit credentials:")
    for key, value in imagekit_credentials.items():
        print(f"  {key} = {value}")
    
    print("\n🔧 Setting up Railway environment variables...")
    
    try:
        # Check if Railway CLI is installed
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Railway CLI not found!")
            print("Please install Railway CLI first:")
            print("  npm install -g @railway/cli")
            print("  railway login")
            print("  railway link")
            return False
        
        # Set environment variables
        for key, value in imagekit_credentials.items():
            print(f"Setting {key}...")
            result = subprocess.run(['railway', 'variables', 'set', f'{key}={value}'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ {key} set successfully")
            else:
                print(f"  ❌ Failed to set {key}: {result.stderr}")
        
        print("\n🎉 ImageKit setup completed!")
        print("\nNext steps:")
        print("1. Railway will automatically redeploy")
        print("2. Check Railway logs for: '🖼️ Using ImageKit for production'")
        print("3. Test image uploads through admin interface")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Railway: {e}")
        print("\n📝 Manual Setup Instructions:")
        print("1. Go to your Railway project dashboard")
        print("2. Click on your service")
        print("3. Go to the 'Variables' tab")
        print("4. Add these environment variables:")
        for key, value in imagekit_credentials.items():
            print(f"   {key} = {value}")
        return False

if __name__ == "__main__":
    setup_railway_imagekit() 