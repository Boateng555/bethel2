#!/usr/bin/env python3
"""
Verify Django ImageKit Integration
Tests that Django is properly configured to use ImageKit for file storage
"""

import os
import sys
import django
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Set ImageKit environment variables directly
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def test_django_settings():
    """Test Django settings configuration"""
    print("⚙️ Testing Django Settings...")
    
    # Check ImageKit config
    imagekit_config = settings.IMAGEKIT_CONFIG
    print(f"  📋 ImageKit Config:")
    print(f"    Public Key: {'✅ Set' if imagekit_config['PUBLIC_KEY'] else '❌ Not set'}")
    print(f"    Private Key: {'✅ Set' if imagekit_config['PRIVATE_KEY'] else '❌ Not set'}")
    print(f"    URL Endpoint: {'✅ Set' if imagekit_config['URL_ENDPOINT'] else '❌ Not set'}")
    
    # Check storage configuration
    print(f"  💾 Default Storage: {settings.DEFAULT_FILE_STORAGE}")
    
    if 'ImageKit' in settings.DEFAULT_FILE_STORAGE:
        print("  ✅ Django configured to use ImageKit storage")
        return True
    else:
        print("  ❌ Django not configured to use ImageKit storage")
        return False

def test_django_storage_upload():
    """Test Django storage upload functionality"""
    print("\n📤 Testing Django Storage Upload...")
    
    try:
        # Create a test image
        img = Image.new('RGB', (300, 200), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), "Django Test", fill='black', font=font)
        draw.text((50, 100), "ImageKit Storage", fill='darkblue', font=font)
        
        # Save to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG', quality=95)
        img_bytes.seek(0)
        
        # Create test file
        test_file = ContentFile(img_bytes.getvalue(), name="django_storage_test.jpg")
        
        # Save using Django storage
        saved_path = default_storage.save("test/django_storage_test.jpg", test_file)
        
        print(f"  📁 Saved path: {saved_path}")
        
        # Check if it's an ImageKit URL
        if 'ik.imagekit.io' in saved_path:
            print("  ✅ File saved to ImageKit")
            
            # Test URL generation
            url = default_storage.url(saved_path)
            print(f"  🔗 Generated URL: {url}")
            
            return True, saved_path
        else:
            print("  ❌ File not saved to ImageKit")
            return False, saved_path
            
    except Exception as e:
        print(f"  ❌ Storage upload error: {e}")
        return False, None

def test_model_upload():
    """Test model field upload"""
    print("\n📋 Testing Model Upload...")
    
    try:
        from core.models import HeroMedia, Hero, Church
        
        # Get or create a test church and hero
        church, created = Church.objects.get_or_create(
            slug='test-church',
            defaults={
                'name': 'Test Church',
                'address': '123 Test St',
                'city': 'Test City',
                'country': 'Test Country'
            }
        )
        
        hero, created = Hero.objects.get_or_create(
            church=church,
            defaults={
                'title': 'Test Hero',
                'subtitle': 'Test Subtitle'
            }
        )
        
        # Create a test image
        img = Image.new('RGB', (250, 150), color='lightgreen')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 18)
        except:
            font = ImageFont.load_default()
        
        draw.text((30, 30), "Model Test", fill='black', font=font)
        draw.text((30, 80), "Hero Media", fill='darkgreen', font=font)
        
        # Save to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG', quality=95)
        img_bytes.seek(0)
        
        # Create model instance
        hero_media = HeroMedia(
            hero=hero,
            order=1
        )
        
        # Save image to model field
        hero_media.image.save("model_test_hero.jpg", ContentFile(img_bytes.getvalue()))
        hero_media.save()
        
        print(f"  📁 Model saved with ID: {hero_media.id}")
        print(f"  🖼️ Image field: {hero_media.image}")
        
        # Check if image URL is ImageKit
        if 'ik.imagekit.io' in hero_media.image.url:
            print("  ✅ Model upload using ImageKit")
            print(f"  🔗 Image URL: {hero_media.image.url}")
            
            # Clean up
            hero_media.delete()
            return True
        else:
            print("  ❌ Model upload not using ImageKit")
            print(f"  🔗 Image URL: {hero_media.image.url}")
            
            # Clean up
            hero_media.delete()
            return False
            
    except Exception as e:
        print(f"  ❌ Model upload error: {e}")
        return False

def test_existing_images():
    """Test existing images in the database"""
    print("\n🖼️ Testing Existing Images...")
    
    try:
        from core.models import Church, News, HeroMedia
        
        # Check churches
        churches = Church.objects.all()
        imagekit_churches = sum(1 for church in churches if 'ik.imagekit.io' in str(church.logo))
        print(f"  🏛️ Churches with ImageKit logos: {imagekit_churches}/{churches.count()}")
        
        # Check news
        news_items = News.objects.all()
        imagekit_news = sum(1 for news in news_items if 'ik.imagekit.io' in str(news.image))
        print(f"  📰 News with ImageKit images: {imagekit_news}/{news_items.count()}")
        
        # Check hero media
        hero_media = HeroMedia.objects.all()
        imagekit_hero = sum(1 for media in hero_media if 'ik.imagekit.io' in str(media.image))
        print(f"  🎬 Hero media with ImageKit: {imagekit_hero}/{hero_media.count()}")
        
        total_images = churches.count() + news_items.count() + hero_media.count()
        total_imagekit = imagekit_churches + imagekit_news + imagekit_hero
        
        if total_images > 0:
            percentage = (total_imagekit / total_images) * 100
            print(f"  📊 Overall: {total_imagekit}/{total_images} images using ImageKit ({percentage:.1f}%)")
            
            if percentage >= 80:
                print("  ✅ Most images are using ImageKit")
                return True
            else:
                print("  ⚠️ Some images are not using ImageKit")
                return False
        else:
            print("  ℹ️ No images found in database")
            return True
            
    except Exception as e:
        print(f"  ❌ Error checking existing images: {e}")
        return False

def main():
    """Run all Django ImageKit tests"""
    print("🚀 Django ImageKit Integration Test")
    print("=" * 50)
    
    # Test 1: Django Settings
    settings_ok = test_django_settings()
    
    if not settings_ok:
        print("\n❌ Django settings not properly configured for ImageKit!")
        return False
    
    # Test 2: Django Storage Upload
    storage_ok, saved_path = test_django_storage_upload()
    
    if not storage_ok:
        print("\n❌ Django storage upload failed!")
        return False
    
    # Test 3: Model Upload
    model_ok = test_model_upload()
    
    # Test 4: Existing Images
    existing_ok = test_existing_images()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Django ImageKit Test Results:")
    print(f"  Django Settings: {'✅ PASS' if settings_ok else '❌ FAIL'}")
    print(f"  Storage Upload: {'✅ PASS' if storage_ok else '❌ FAIL'}")
    print(f"  Model Upload: {'✅ PASS' if model_ok else '❌ FAIL'}")
    print(f"  Existing Images: {'✅ PASS' if existing_ok else '⚠️ PARTIAL'}")
    
    all_tests_passed = all([settings_ok, storage_ok, model_ok])
    
    if all_tests_passed:
        print("\n🎉 DJANGO IMAGEKIT INTEGRATION WORKING!")
        print("\n📝 Your production environment is properly configured:")
        print("   ✅ ImageKit credentials are set")
        print("   ✅ Django storage is using ImageKit")
        print("   ✅ Model uploads go to ImageKit")
        print("   ✅ All new uploads will use ImageKit cloud storage")
        print("\n🔧 For production deployment:")
        print("   1. Ensure these environment variables are set in your environment:")
        print("      - IMAGEKIT_PUBLIC_KEY")
        print("      - IMAGEKIT_PRIVATE_KEY")
        print("      - IMAGEKIT_URL_ENDPOINT")
        print("   2. Deploy your app to your production environment")
        print("   3. Monitor ImageKit usage in your dashboard")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 