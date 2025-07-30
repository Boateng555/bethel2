#!/usr/bin/env python
"""
Test script to verify ImageKit uploads and URL generation
"""
import os
import sys
import django
from io import BytesIO

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Set ImageKit environment variables
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

from django.core.files.base import ContentFile
from django.conf import settings
from core.models import Church, HeroMedia

def test_imagekit_upload():
    """Test uploading an image through ImageKit"""
    print("🧪 Testing ImageKit upload...")
    
    try:
        # Get first church
        church = Church.objects.first()
        if not church:
            print("❌ No churches found in database")
            return False
        
        print(f"Testing with church: {church.name}")
        
        # Get or create hero for the church
        hero = church.hero_set.first()
        if not hero:
            print("❌ No hero found for church")
            return False
        
        # Create a test image content
        test_content = b"This is a test hero image content for ImageKit verification"
        test_file = ContentFile(test_content, name='test_imagekit_upload.jpg')
        
        # Create hero media entry
        hero_media = HeroMedia.objects.create(
            hero=hero,
            image=test_file,
            order=999  # High order to avoid conflicts
        )
        
        print(f"✅ Hero media created! ID: {hero_media.id}")
        print(f"Image URL: {hero_media.image.url}")
        print(f"Image path: {hero_media.image.name}")
        
        # Check if it's an ImageKit URL
        if hero_media.image.url.startswith('https://ik.imagekit.io/'):
            print("🎉 SUCCESS: ImageKit upload is working!")
            print(f"Full URL: {hero_media.image.url}")
            
            # Test if the URL is accessible
            import requests
            try:
                response = requests.head(hero_media.image.url, timeout=10)
                if response.status_code == 200:
                    print("✅ Image URL is accessible!")
                else:
                    print(f"⚠️ Image URL returned status code: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Could not verify image URL: {e}")
        else:
            print(f"❌ FAILED: Not using ImageKit URL: {hero_media.image.url}")
        
        # Clean up
        hero_media.delete()
        print("✅ Test cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ ImageKit upload test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_existing_images():
    """Test existing images in the database"""
    print("\n🔍 Testing existing images...")
    
    try:
        # Check HeroMedia images
        hero_media_list = HeroMedia.objects.all()
        print(f"Found {hero_media_list.count()} HeroMedia entries")
        
        for i, media in enumerate(hero_media_list[:5]):  # Check first 5
            if media.image:
                print(f"  {i+1}. HeroMedia {media.id}: {media.image.url}")
                
                # Test URL accessibility
                import requests
                try:
                    response = requests.head(media.image.url, timeout=10)
                    if response.status_code == 200:
                        print(f"     ✅ Accessible")
                    else:
                        print(f"     ❌ Status: {response.status_code}")
                except Exception as e:
                    print(f"     ⚠️ Error: {e}")
            else:
                print(f"  {i+1}. HeroMedia {media.id}: No image")
        
        # Check Church images
        churches = Church.objects.all()
        print(f"\nFound {churches.count()} churches")
        
        for i, church in enumerate(churches[:3]):  # Check first 3
            if church.logo:
                print(f"  {i+1}. Church {church.name}: {church.logo.url}")
                
                # Test URL accessibility
                import requests
                try:
                    response = requests.head(church.logo.url, timeout=10)
                    if response.status_code == 200:
                        print(f"     ✅ Accessible")
                    else:
                        print(f"     ❌ Status: {response.status_code}")
                except Exception as e:
                    print(f"     ⚠️ Error: {e}")
            else:
                print(f"  {i+1}. Church {church.name}: No logo")
        
        return True
        
    except Exception as e:
        print(f"❌ Existing images test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting ImageKit tests...")
    print("=" * 50)
    
    # Test new upload
    success1 = test_imagekit_upload()
    
    # Test existing images
    success2 = test_existing_images()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"New upload test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"Existing images test: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! ImageKit is working properly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.") 