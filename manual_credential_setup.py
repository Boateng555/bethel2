#!/usr/bin/env python3
"""
Manual Cloudinary credential setup
"""

import os
from dotenv import load_dotenv

def manual_setup():
    """Manual credential setup"""
    
    print("🔧 Manual Cloudinary Credential Setup")
    print("="*50)
    
    print("\n📋 Please enter your Cloudinary credentials:")
    print("(You can find these at https://cloudinary.com/console)")
    
    # Get credentials from user
    cloud_name = input("\n1. Cloud Name (e.g., dhzdusb5k): ").strip()
    api_key = input("2. API Key: ").strip()
    api_secret = input("3. API Secret: ").strip()
    
    if not all([cloud_name, api_key, api_secret]):
        print("❌ All fields are required!")
        return False
    
    # Create .env content
    env_content = f"""# Django Settings
DJANGO_SECRET_KEY=django-insecure-dt1#i48=k*oc^@cwtgj7v1ou(_(n%z=&omp$)fhfh3d)hvv^sg
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# Cloudinary Settings (for production media storage)
CLOUDINARY_CLOUD_NAME={cloud_name}
CLOUDINARY_API_KEY={api_key}
CLOUDINARY_API_SECRET={api_secret}

# Email Settings (optional)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
# DEFAULT_FROM_EMAIL=your-email@gmail.com

# Other Settings
# CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
"""
    
    # Write to .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ .env file updated!")
        print(f"   Cloud Name: {cloud_name}")
        print(f"   API Key: {api_key[:10]}...")
        print(f"   API Secret: {api_secret[:10]}...")
        
        print("\n🧪 Testing credentials...")
        
        # Test the credentials
        import cloudinary
        import cloudinary.uploader
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        
        # Create test file
        with open('test_manual.txt', 'w') as f:
            f.write("Manual credential test")
        
        # Test upload
        result = cloudinary.uploader.upload(
            'test_manual.txt',
            folder="bethel/test",
            public_id="manual_test",
            overwrite=True
        )
        
        print("✅ Upload successful!")
        print(f"   URL: {result['secure_url']}")
        
        # Clean up
        os.remove('test_manual.txt')
        cloudinary.uploader.destroy("bethel/test/manual_test")
        
        print("\n🎉 Credentials are working! You can now upload your media.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔍 Please check your credentials and try again.")
        return False

if __name__ == "__main__":
    manual_setup() 