#!/usr/bin/env python
"""
Diagnostic script to analyze ImageKit issues and provide solutions
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Set ImageKit environment variables
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

from django.conf import settings
from core.models import Church, HeroMedia, Ministry, News, Sermon
import requests

def check_imagekit_config():
    """Check ImageKit configuration"""
    print("🔧 Checking ImageKit Configuration...")
    print("=" * 50)
    
    config = settings.IMAGEKIT_CONFIG
    print(f"Public Key: {'✅ Set' if config.get('PUBLIC_KEY') else '❌ Missing'}")
    print(f"Private Key: {'✅ Set' if config.get('PRIVATE_KEY') else '❌ Missing'}")
    print(f"URL Endpoint: {'✅ Set' if config.get('URL_ENDPOINT') else '❌ Missing'}")
    print(f"Storage Backend: {settings.DEFAULT_FILE_STORAGE}")
    
    if all(config.values()):
        print("✅ ImageKit configuration is complete")
        return True
    else:
        print("❌ ImageKit configuration is incomplete")
        return False

def analyze_image_status():
    """Analyze the status of all images in the database"""
    print("\n📊 Analyzing Image Status...")
    print("=" * 50)
    
    models_to_check = [
        (HeroMedia, 'image', 'HeroMedia'),
        (Church, 'logo', 'Church'),
        (Ministry, 'image', 'Ministry'),
        (News, 'image', 'News'),
        (Sermon, 'thumbnail', 'Sermon'),
    ]
    
    total_images = 0
    imagekit_urls = 0
    broken_urls = 0
    working_urls = 0
    
    for model_class, field_name, model_name in models_to_check:
        print(f"\n{model_name} Images:")
        print("-" * 30)
        
        model_count = 0
        model_imagekit = 0
        model_broken = 0
        model_working = 0
        
        for obj in model_class.objects.all():
            field = getattr(obj, field_name)
            if field:
                model_count += 1
                total_images += 1
                
                url = str(field)
                if 'ik.imagekit.io' in url:
                    model_imagekit += 1
                    imagekit_urls += 1
                    
                    # Test URL accessibility
                    try:
                        response = requests.head(url, timeout=5)
                        if response.status_code == 200:
                            print(f"  ✅ {obj}: Working")
                            model_working += 1
                            working_urls += 1
                        else:
                            print(f"  ❌ {obj}: {response.status_code} error")
                            model_broken += 1
                            broken_urls += 1
                    except Exception as e:
                        print(f"  ⚠️ {obj}: Error - {e}")
                        model_broken += 1
                        broken_urls += 1
                else:
                    print(f"  🔄 {obj}: Not ImageKit URL")
        
        print(f"  Total: {model_count}, ImageKit: {model_imagekit}, Working: {model_working}, Broken: {model_broken}")
    
    print(f"\n📈 SUMMARY:")
    print(f"Total images: {total_images}")
    print(f"ImageKit URLs: {imagekit_urls}")
    print(f"Working URLs: {working_urls}")
    print(f"Broken URLs: {broken_urls}")
    
    return {
        'total': total_images,
        'imagekit': imagekit_urls,
        'working': working_urls,
        'broken': broken_urls
    }

def provide_solutions(stats):
    """Provide solutions based on the analysis"""
    print("\n💡 SOLUTIONS")
    print("=" * 50)
    
    if stats['broken'] > 0:
        print(f"🔧 You have {stats['broken']} broken ImageKit URLs that need to be fixed.")
        print("\nRecommended actions:")
        print("1. Upload new images through Django admin to replace broken ones")
        print("2. Or run the fix script to create placeholder images")
        print("3. Check your ImageKit dashboard to see if files exist")
    else:
        print("✅ All ImageKit URLs are working properly!")
    
    print(f"\n📝 Current Status:")
    print(f"- {stats['working']} images are working correctly")
    print(f"- {stats['broken']} images need to be fixed")
    print(f"- {stats['total'] - stats['imagekit']} images are not using ImageKit")
    
    if stats['broken'] > 0:
        print(f"\n🚀 To fix broken images, you can:")
        print("1. Run: python fix_imagekit_images.py")
        print("2. Or manually upload new images through Django admin")
        print("3. Or clear broken image fields and re-upload")

def test_new_upload():
    """Test if new uploads work correctly"""
    print("\n🧪 Testing New Upload Capability...")
    print("=" * 50)
    
    try:
        from django.core.files.base import ContentFile
        from core.models import HeroMedia, Church
        
        # Get first church and hero
        church = Church.objects.first()
        if not church:
            print("❌ No churches found")
            return False
        
        hero = church.hero_set.first()
        if not hero:
            print("❌ No hero found")
            return False
        
        # Create test content
        test_content = b"Test image content for upload verification"
        test_file = ContentFile(test_content, name='test_upload.jpg')
        
        # Create hero media
        hero_media = HeroMedia.objects.create(
            hero=hero,
            image=test_file,
            order=999
        )
        
        print(f"✅ Test upload successful!")
        print(f"URL: {hero_media.image.url}")
        
        # Test URL accessibility
        try:
            response = requests.head(hero_media.image.url, timeout=5)
            if response.status_code == 200:
                print("✅ Uploaded image is accessible!")
                success = True
            else:
                print(f"⚠️ Uploaded image returned status: {response.status_code}")
                success = False
        except Exception as e:
            print(f"⚠️ Could not verify uploaded image: {e}")
            success = False
        
        # Clean up
        hero_media.delete()
        print("✅ Test cleaned up")
        
        return success
        
    except Exception as e:
        print(f"❌ Test upload failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 ImageKit Diagnostic Tool")
    print("=" * 60)
    
    # Check configuration
    config_ok = check_imagekit_config()
    
    if not config_ok:
        print("\n❌ ImageKit is not properly configured. Please check your environment variables.")
        sys.exit(1)
    
    # Analyze images
    stats = analyze_image_status()
    
    # Provide solutions
    provide_solutions(stats)
    
    # Test new uploads
    upload_works = test_new_upload()
    
    print("\n" + "=" * 60)
    print("📋 FINAL RECOMMENDATIONS")
    print("=" * 60)
    
    if upload_works:
        print("✅ New uploads are working correctly")
        if stats['broken'] > 0:
            print("🔧 You can fix broken images by uploading new ones through Django admin")
        else:
            print("🎉 Everything is working perfectly!")
    else:
        print("❌ New uploads are not working - check ImageKit configuration")
    
    print(f"\n📊 Summary:")
    print(f"- Configuration: {'✅ OK' if config_ok else '❌ Issues'}")
    print(f"- New uploads: {'✅ Working' if upload_works else '❌ Failed'}")
    print(f"- Broken images: {stats['broken']}")
    print(f"- Working images: {stats['working']}") 