#!/usr/bin/env python3
"""
Set up Cloudinary credentials and test them
"""

import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

def setup_and_test_cloudinary():
    """Set up Cloudinary credentials and test them"""
    
    print("🔧 Setting up Cloudinary credentials...")
    
    # Based on our previous conversation, we know the cloud name
    cloud_name = "dhzdusb5k"
    
    # Try to get API key and secret from environment or use common patterns
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    
    if not api_key or not api_secret:
        print("⚠️ API Key or Secret not found in environment variables")
        print("Please provide your Cloudinary API Key and Secret:")
        
        # For now, let's try to use the credentials that might be in Railway
        # You'll need to get these from your Cloudinary dashboard
        print("\n📋 To get your credentials:")
        print("1. Go to https://cloudinary.com/console")
        print("2. Sign in to your account")
        print("3. Copy your API Key and API Secret")
        print("4. Update your .env file with these values")
        
        return False
    
    print(f"Cloud Name: {cloud_name}")
    print(f"API Key: {api_key[:10]}..." if api_key else "API Key: Not set")
    print(f"API Secret: {api_secret[:10]}..." if api_secret else "API Secret: Not set")
    
    # Configure Cloudinary
    try:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        print("✅ Cloudinary configured successfully")
    except Exception as e:
        print(f"❌ Error configuring Cloudinary: {e}")
        return False
    
    # Test upload
    try:
        print("📤 Testing upload with a simple text file...")
        
        # Create a test file
        test_content = "This is a test file for Cloudinary credentials verification."
        test_filename = "test_credentials.txt"
        
        with open(test_filename, 'w') as f:
            f.write(test_content)
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            test_filename,
            folder="bethel/test",
            public_id="credentials_test",
            overwrite=True
        )
        
        print(f"✅ Upload successful!")
        print(f"   URL: {result['secure_url']}")
        print(f"   Public ID: {result['public_id']}")
        
        # Clean up test file
        os.remove(test_filename)
        
        # Delete the test file from Cloudinary
        cloudinary.uploader.destroy("bethel/test/credentials_test")
        print("🧹 Test file cleaned up from Cloudinary")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        print("\n🔍 This usually means:")
        print("1. API Key or Secret is incorrect")
        print("2. Cloud name is wrong")
        print("3. Account has restrictions")
        return False

if __name__ == "__main__":
    success = setup_and_test_cloudinary()
    if success:
        print("\n🎉 All tests passed! Your Cloudinary credentials are working correctly.")
        print("You can now run the media upload command.")
    else:
        print("\n❌ Tests failed. Please check your credentials and try again.") 