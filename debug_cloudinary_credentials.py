#!/usr/bin/env python3
"""
Debug Cloudinary credentials step by step
"""

import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_credentials():
    """Debug Cloudinary credentials step by step"""
    
    print("🔍 Debugging Cloudinary credentials...")
    print("="*50)
    
    # Get credentials
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    
    print(f"1. Cloud Name: {cloud_name}")
    print(f"2. API Key: {api_key}")
    print(f"3. API Secret: {api_secret}")
    print()
    
    # Check if all are present
    if not all([cloud_name, api_key, api_secret]):
        print("❌ Missing credentials!")
        return False
    
    # Try different API secret variations (case sensitivity)
    api_secret_variations = [
        api_secret,
        api_secret.upper(),
        api_secret.lower(),
        api_secret.replace('I', 'l').replace('l', 'I'),  # Common confusion
    ]
    
    for i, secret in enumerate(api_secret_variations):
        print(f"Testing API Secret variation {i+1}: {secret[:10]}...")
        
        try:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=secret
            )
            
            # Try a simple upload
            result = cloudinary.uploader.upload(
                "test_credentials.txt",
                folder="bethel/test",
                public_id=f"debug_test_{i}",
                overwrite=True
            )
            
            print(f"✅ SUCCESS with variation {i+1}!")
            print(f"   URL: {result['secure_url']}")
            
            # Clean up
            cloudinary.uploader.destroy(f"bethel/test/debug_test_{i}")
            
            # Update .env with working secret
            update_env_with_working_secret(secret)
            return True
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)[:100]}...")
            continue
    
    print("\n❌ All variations failed.")
    print("\n🔍 Possible issues:")
    print("1. API Secret might be wrong")
    print("2. API Key might be wrong")
    print("3. Cloud name might be wrong")
    print("4. Account might have restrictions")
    
    return False

def update_env_with_working_secret(working_secret):
    """Update .env file with the working secret"""
    
    print(f"\n🔄 Updating .env file with working secret...")
    
    # Read current .env
    with open('.env', 'r') as f:
        content = f.read()
    
    # Replace the API secret
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('CLOUDINARY_API_SECRET='):
            lines[i] = f'CLOUDINARY_API_SECRET={working_secret}'
            break
    
    # Write back
    with open('.env', 'w') as f:
        f.write('\n'.join(lines))
    
    print("✅ .env file updated with working secret!")

if __name__ == "__main__":
    debug_credentials() 