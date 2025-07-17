#!/usr/bin/env python3
"""
Simple Cloudinary test with direct credentials
"""

import cloudinary
import cloudinary.uploader

def test_direct_credentials():
    """Test Cloudinary with credentials directly"""
    
    print("🧪 Testing Cloudinary with direct credentials...")
    
    # Use the credentials directly from the screenshot
    cloud_name = "dhzdusb5k"
    api_key = "566563723513225"
    api_secret = "E-HJnJ8weQEL67JI708uBCLS_eU"
    
    print(f"Cloud Name: {cloud_name}")
    print(f"API Key: {api_key}")
    print(f"API Secret: {api_secret}")
    
    try:
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        print("✅ Cloudinary configured successfully")
        
        # Create a simple test file
        test_content = "Simple test for Cloudinary"
        with open('simple_test.txt', 'w') as f:
            f.write(test_content)
        
        print("📤 Uploading test file...")
        
        # Try upload
        result = cloudinary.uploader.upload(
            'simple_test.txt',
            folder="bethel/simple_test",
            public_id="direct_test",
            overwrite=True
        )
        
        print("✅ Upload successful!")
        print(f"   URL: {result['secure_url']}")
        print(f"   Public ID: {result['public_id']}")
        
        # Clean up
        import os
        os.remove('simple_test.txt')
        cloudinary.uploader.destroy("bethel/simple_test/direct_test")
        print("🧹 Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_direct_credentials()
    if success:
        print("\n🎉 Direct credentials test passed!")
        print("The credentials are working correctly.")
    else:
        print("\n❌ Direct credentials test failed.")
        print("There might be an issue with the credentials or account settings.") 