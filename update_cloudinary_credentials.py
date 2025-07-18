#!/usr/bin/env python
"""
Script to help update Cloudinary credentials for Railway
"""
import os

def main():
    print("🔧 Cloudinary Credentials Update")
    print("=" * 40)
    
    # New credentials
    new_cloud_name = "dhzdusb5k"  # Keep the same cloud name
    new_api_key = "462763744132765"
    new_api_secret = "s-FWNQuY_M40XwHKrskwIh0C-XI"
    
    print(f"📋 New Cloudinary Credentials:")
    print(f"   Cloud Name: {new_cloud_name}")
    print(f"   API Key: {new_api_key}")
    print(f"   API Secret: {new_api_secret}")
    
    print("\n🔧 To update these in Railway:")
    print("1. Go to your Railway dashboard: https://railway.app/dashboard")
    print("2. Select your project: 'thorough-wisdom'")
    print("3. Go to the 'Variables' tab")
    print("4. Update these environment variables:")
    print()
    print(f"   CLOUDINARY_CLOUD_NAME = {new_cloud_name}")
    print(f"   CLOUDINARY_API_KEY = {new_api_key}")
    print(f"   CLOUDINARY_API_SECRET = {new_api_secret}")
    print()
    print("5. Save the changes")
    print("6. Deploy again with: railway up")
    
    # Create a .env file for local testing
    env_content = f"""# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME={new_cloud_name}
CLOUDINARY_API_KEY={new_api_key}
CLOUDINARY_API_SECRET={new_api_secret}

# Django Configuration
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=calt*nc09l)qowjzv)lb%c9vbm!r8tm(drncevpdyliuwxrqt-
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ Created .env file with new credentials for local testing")
    print(f"📁 File: {os.path.abspath('.env')}")
    
    print("\n🚀 After updating Railway variables, deploy with:")
    print("   railway up")

if __name__ == "__main__":
    main() 