#!/usr/bin/env python3
"""
Test Cloudinary credentials and upload a simple test file
"""

import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_cloudinary_credentials():
    """Test Cloudinary credentials and upload a test file"""
    
    print("🔍 Testing Cloudinary credentials...")
    
    # Get credentials from environment
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    
    print(f"Cloud Name: {cloud_name}")
    print(f"API Key: {api_key[:10]}..." if api_key else "API Key: Not set")
    print(f"API Secret: {api_secret[:10]}..." if api_secret else "API Secret: Not set")
    
    # Check if all credentials are present
    if not all([cloud_name, api_key, api_secret]):
        print("❌ Missing Cloudinary credentials!")
        print("Please check your .env file and make sure all credentials are set.")
        return False
    
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
        return False

if __name__ == "__main__":
    success = test_cloudinary_credentials()
    if success:
        print("\n🎉 All tests passed! Your Cloudinary credentials are working correctly.")
        print("You can now run the media upload command.")
    else:
        print("\n❌ Tests failed. Please check your credentials and try again.") 