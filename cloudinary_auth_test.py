#!/usr/bin/env python3
"""
Comprehensive Cloudinary authentication test
"""

import cloudinary
import cloudinary.uploader
import requests
import json

def test_different_auth_methods():
    """Test different authentication methods"""
    
    print("🔍 Comprehensive Cloudinary Authentication Test")
    print("="*60)
    
    cloud_name = "dhzdusb5k"
    api_key = "566563723513225"
    api_secret = "E-HJnJ8weQEL67JI708uBCLS_eU"
    
    print(f"Cloud Name: {cloud_name}")
    print(f"API Key: {api_key}")
    print(f"API Secret: {api_secret}")
    print()
    
    # Test 1: Basic upload without folder
    print("🧪 Test 1: Basic upload without folder")
    try:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        
        with open('basic_test.txt', 'w') as f:
            f.write("Basic test")
        
        result = cloudinary.uploader.upload(
            'basic_test.txt',
            public_id="basic_test",
            overwrite=True
        )
        
        print("✅ Basic upload successful!")
        print(f"   URL: {result['secure_url']}")
        
        # Clean up
        import os
        os.remove('basic_test.txt')
        cloudinary.uploader.destroy("basic_test")
        return True
        
    except Exception as e:
        print(f"❌ Basic upload failed: {e}")
    
    # Test 2: Try with different API secret format
    print("\n🧪 Test 2: Different API secret format")
    try:
        # Try without the "E-" prefix
        alt_secret = api_secret.replace("E-", "")
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=alt_secret
        )
        
        with open('alt_test.txt', 'w') as f:
            f.write("Alternative test")
        
        result = cloudinary.uploader.upload(
            'alt_test.txt',
            public_id="alt_test",
            overwrite=True
        )
        
        print("✅ Alternative secret format successful!")
        print(f"   URL: {result['secure_url']}")
        
        # Clean up
        import os
        os.remove('alt_test.txt')
        cloudinary.uploader.destroy("alt_test")
        return True
        
    except Exception as e:
        print(f"❌ Alternative secret format failed: {e}")
    
    # Test 3: Check account status via API
    print("\n🧪 Test 3: Check account status")
    try:
        url = f"https://{api_key}:{api_secret}@api.cloudinary.com/v1_1/{cloud_name}/usage"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Account status check successful!")
            print(f"   Plan: {data.get('plan', 'Unknown')}")
            print(f"   Credits: {data.get('credits', 'Unknown')}")
            return True
        else:
            print(f"❌ Account status check failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Account status check failed: {e}")
    
    print("\n❌ All authentication methods failed.")
    print("\n🔍 Possible issues:")
    print("1. API Secret might be incorrect")
    print("2. Account might have restrictions")
    print("3. API Key might be for a different environment")
    print("4. Account might need activation")
    
    return False

if __name__ == "__main__":
    success = test_different_auth_methods()
    if success:
        print("\n🎉 Authentication test passed!")
    else:
        print("\n❌ Authentication test failed.")
        print("\n💡 Next steps:")
        print("1. Double-check the API Secret in Cloudinary console")
        print("2. Make sure the account is active")
        print("3. Try generating a new API key")
        print("4. Check if there are any account restrictions") 