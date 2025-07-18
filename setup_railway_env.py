#!/usr/bin/env python
"""
Script to help set up Railway environment variables for Cloudinary
"""
import os
import subprocess
import sys

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🚀 Railway Cloudinary Environment Setup")
    print("=" * 50)
    
    # Check if railway CLI is installed
    success, stdout, stderr = run_command("railway --version")
    if not success:
        print("❌ Railway CLI not found. Please install it first:")
        print("   npm install -g @railway/cli")
        print("   Then run: railway login")
        return
    
    print("✅ Railway CLI found")
    
    # Check if logged in
    success, stdout, stderr = run_command("railway status")
    if not success:
        print("❌ Not logged into Railway. Please run:")
        print("   railway login")
        return
    
    print("✅ Logged into Railway")
    
    # Get Cloudinary credentials from user
    print("\n📝 Please enter your Cloudinary credentials:")
    print("   (You can find these in your Cloudinary Dashboard)")
    
    cloud_name = input("Cloud Name: ").strip()
    api_key = input("API Key: ").strip()
    api_secret = input("API Secret: ").strip()
    
    if not all([cloud_name, api_key, api_secret]):
        print("❌ All Cloudinary credentials are required!")
        return
    
    # Set environment variables in Railway
    print("\n🔧 Setting Railway environment variables...")
    
    env_vars = {
        'CLOUDINARY_CLOUD_NAME': cloud_name,
        'CLOUDINARY_API_KEY': api_key,
        'CLOUDINARY_API_SECRET': api_secret,
        'DJANGO_DEBUG': 'False',
        'DJANGO_SECRET_KEY': os.environ.get('DJANGO_SECRET_KEY', 'your-secret-key-here'),
    }
    
    for key, value in env_vars.items():
        print(f"Setting {key}...")
        success, stdout, stderr = run_command(f'railway variables set {key}="{value}"')
        if success:
            print(f"✅ {key} set successfully")
        else:
            print(f"❌ Failed to set {key}: {stderr}")
    
    print("\n🎉 Environment variables set!")
    print("\n📋 Next steps:")
    print("1. Deploy your app: railway up")
    print("2. Check your Railway dashboard to verify the variables")
    print("3. Your images should now work with Cloudinary")
    
    # Option to deploy now
    deploy_now = input("\n🚀 Deploy now? (y/n): ").strip().lower()
    if deploy_now == 'y':
        print("\n📤 Deploying to Railway...")
        success, stdout, stderr = run_command("railway up")
        if success:
            print("✅ Deployment successful!")
        else:
            print(f"❌ Deployment failed: {stderr}")

if __name__ == "__main__":
    main() 