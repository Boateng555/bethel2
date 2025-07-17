#!/usr/bin/env python3
"""
Test Cloudinary credentials with proper image upload
"""

import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_image_upload():
    """Test Cloudinary with image upload"""
    
    print("🧪 Testing Cloudinary credentials with image upload...")
    
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
    
    # Test upload with a simple image
    try:
        print("📤 Testing upload with a simple image...")
        
        # Create a simple PNG image using PIL
        try:
            from PIL import Image, ImageDraw
            
            # Create a simple test image
            img = Image.new('RGB', (100, 100), color='blue')
            draw = ImageDraw.Draw(img)
            draw.text((10, 40), "Test", fill='white')
            
            test_image_path = "test_image.png"
            img.save(test_image_path)
            
            print(f"✅ Created test image: {test_image_path}")
            
        except ImportError:
            # If PIL is not available, try to find an existing image
            print("⚠️ PIL not available, looking for existing images...")
            
            # Look for existing images in media folder
            media_paths = [
                "media/hero/Screenshot_4.png",
                "media/churches/logos/Screenshot_4.png",
                "media/news/Screenshot_6.png"
            ]
            
            test_image_path = None
            for path in media_paths:
                if os.path.exists(path):
                    test_image_path = path
                    print(f"✅ Found existing image: {path}")
                    break
            
            if not test_image_path:
                print("❌ No test images found. Please install PIL or add an image to test.")
                return False
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            test_image_path,
            folder="bethel/test",
            public_id="credentials_test_image",
            overwrite=True
        )
        
        print(f"✅ Upload successful!")
        print(f"   URL: {result['secure_url']}")
        print(f"   Public ID: {result['public_id']}")
        
        # Clean up test file if we created it
        if test_image_path == "test_image.png" and os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        # Delete the test file from Cloudinary
        cloudinary.uploader.destroy("bethel/test/credentials_test_image")
        print("🧹 Test file cleaned up from Cloudinary")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_image_upload()
    if success:
        print("\n🎉 Image upload test passed!")
        print("Your Cloudinary credentials are working correctly!")
        print("You can now run the media upload command.")
    else:
        print("\n❌ Image upload test failed.")
        print("Please check your credentials and try again.") 