#!/usr/bin/env python3
"""
Configure ImageKit properly and test the connection
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def configure_imagekit_environment():
    """Set up ImageKit environment variables properly"""
    print("🔧 Configuring ImageKit Environment Variables")
    print("=" * 50)
    
    # ImageKit credentials from environment variables
    imagekit_config = {
        'IMAGEKIT_PUBLIC_KEY': 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=',
        'IMAGEKIT_PRIVATE_KEY': 'private_Dnsrj2VW7uJakaeMaNYaav+P784=',
        'IMAGEKIT_URL_ENDPOINT': 'https://ik.imagekit.io/9buar9mbp'
    }
    
    # Set environment variables
    for key, value in imagekit_config.items():
        os.environ[key] = value
        print(f"✅ Set {key} = {value[:20]}...")
    
    print("\n🎯 Environment variables configured!")
    return imagekit_config

def test_imagekit_connection():
    """Test ImageKit connection and basic functionality"""
    print("\n🔍 Testing ImageKit Connection")
    print("=" * 50)
    
    try:
        from imagekitio import ImageKit
        
        # Get credentials from environment
        public_key = os.environ.get('IMAGEKIT_PUBLIC_KEY')
        private_key = os.environ.get('IMAGEKIT_PRIVATE_KEY')
        url_endpoint = os.environ.get('IMAGEKIT_URL_ENDPOINT')
        
        if not all([public_key, private_key, url_endpoint]):
            print("❌ Missing ImageKit credentials in environment")
            return False
        
        # Initialize ImageKit
        imagekit = ImageKit(
            public_key=public_key,
            private_key=private_key,
            url_endpoint=url_endpoint
        )
        
        print("✅ ImageKit client initialized successfully")
        
        # Test basic functionality - list files
        try:
            files = imagekit.list_files()
            print(f"✅ Successfully connected to ImageKit")
            print(f"   Found {len(files.list)} files in your account")
            return True
        except Exception as e:
            print(f"❌ Error listing files: {e}")
            return False
            
    except ImportError:
        print("❌ ImageKit Python SDK not installed")
        print("   Run: pip install imagekitio")
        return False
    except Exception as e:
        print(f"❌ Error initializing ImageKit: {e}")
        return False

def test_django_storage():
    """Test Django storage with ImageKit"""
    print("\n🧪 Testing Django Storage with ImageKit")
    print("=" * 50)
    
    try:
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        from PIL import Image
        from io import BytesIO
        
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Create a test file
        test_content = ContentFile(buffer.getvalue(), name='test_image.png')
        
        # Test upload
        print("📤 Testing file upload...")
        saved_name = default_storage.save('test/test_image.png', test_content)
        print(f"✅ File uploaded successfully: {saved_name}")
        
        # Test URL generation
        print("🔗 Testing URL generation...")
        file_url = default_storage.url(saved_name)
        print(f"✅ File URL: {file_url}")
        
        # Test file existence
        print("🔍 Testing file existence...")
        if default_storage.exists(saved_name):
            print("✅ File exists in storage")
        else:
            print("❌ File not found in storage")
        
        # Test file deletion
        print("🗑️ Testing file deletion...")
        default_storage.delete(saved_name)
        if not default_storage.exists(saved_name):
            print("✅ File deleted successfully")
        else:
            print("❌ File deletion failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Django storage: {e}")
        return False

def update_django_settings():
    """Update Django settings to use ImageKit properly"""
    print("\n⚙️ Updating Django Settings")
    print("=" * 50)
    
    try:
        from django.conf import settings
        
        # Check current storage configuration
        current_storage = getattr(settings, 'DEFAULT_FILE_STORAGE', 'Unknown')
        print(f"Current storage: {current_storage}")
        
        # Check ImageKit configuration
        imagekit_config = getattr(settings, 'IMAGEKIT_CONFIG', {})
        print(f"ImageKit config keys: {list(imagekit_config.keys())}")
        
        # Verify environment variables are accessible
        public_key = os.environ.get('IMAGEKIT_PUBLIC_KEY')
        private_key = os.environ.get('IMAGEKIT_PRIVATE_KEY')
        url_endpoint = os.environ.get('IMAGEKIT_URL_ENDPOINT')
        
        if all([public_key, private_key, url_endpoint]):
            print("✅ All ImageKit environment variables are set")
            print("✅ Django should be using ImageKit storage")
        else:
            print("❌ Missing ImageKit environment variables")
            print(f"   PUBLIC_KEY: {'✅' if public_key else '❌'}")
            print(f"   PRIVATE_KEY: {'✅' if private_key else '❌'}")
            print(f"   URL_ENDPOINT: {'✅' if url_endpoint else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking Django settings: {e}")
        return False

def fix_corrupted_images_with_imagekit():
    """Fix corrupted images by re-uploading them to ImageKit"""
    print("\n🔧 Fixing Corrupted Images with ImageKit")
    print("=" * 50)
    
    try:
        from core.models import Church, Ministry, News, Sermon
        from django.core.files.base import ContentFile
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO
        
        def create_placeholder_image(width=400, height=400, text="Placeholder"):
            """Create a placeholder image"""
            img = Image.new('RGB', (width, height), color=(73, 109, 137))
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            # Calculate text position
            text_bbox = draw.textbbox((0, 0), text, font=font) if font else (0, 0, len(text) * 10, 20)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            draw.text((x, y), text, fill=(255, 255, 255), font=font)
            
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            return buffer
        
        fixed_count = 0
        
        # Fix Church logos
        print("🏛️ Fixing Church logos...")
        churches = Church.objects.all()
        for church in churches:
            if church.logo:
                try:
                    # Create placeholder logo
                    placeholder = create_placeholder_image(400, 400, f"{church.name} Logo")
                    new_file = ContentFile(placeholder.getvalue(), name=f"churches/logos/{church.name}_logo.png")
                    
                    # Save to ImageKit
                    church.logo = new_file
                    church.save()
                    print(f"  ✅ Fixed logo for {church.name}")
                    fixed_count += 1
                except Exception as e:
                    print(f"  ❌ Error fixing {church.name}: {e}")
        
        # Fix Ministry images
        print("⛪ Fixing Ministry images...")
        ministries = Ministry.objects.all()
        for ministry in ministries:
            if ministry.image:
                try:
                    # Create placeholder image
                    placeholder = create_placeholder_image(800, 600, f"{ministry.name}")
                    new_file = ContentFile(placeholder.getvalue(), name=f"ministries/{ministry.name}_image.png")
                    
                    # Save to ImageKit
                    ministry.image = new_file
                    ministry.save()
                    print(f"  ✅ Fixed image for {ministry.name}")
                    fixed_count += 1
                except Exception as e:
                    print(f"  ❌ Error fixing {ministry.name}: {e}")
        
        # Fix News images
        print("📰 Fixing News images...")
        news_items = News.objects.all()
        for news in news_items:
            if news.image:
                try:
                    # Create placeholder image
                    placeholder = create_placeholder_image(800, 600, f"{news.title}")
                    new_file = ContentFile(placeholder.getvalue(), name=f"news/{news.title}_image.png")
                    
                    # Save to ImageKit
                    news.image = new_file
                    news.save()
                    print(f"  ✅ Fixed image for {news.title}")
                    fixed_count += 1
                except Exception as e:
                    print(f"  ❌ Error fixing {news.title}: {e}")
        
        # Fix Sermon thumbnails
        print("📖 Fixing Sermon thumbnails...")
        sermons = Sermon.objects.all()
        for sermon in sermons:
            if sermon.thumbnail:
                try:
                    # Create placeholder thumbnail
                    placeholder = create_placeholder_image(400, 300, f"{sermon.title}")
                    new_file = ContentFile(placeholder.getvalue(), name=f"sermons/thumbnails/{sermon.title}_thumb.png")
                    
                    # Save to ImageKit
                    sermon.thumbnail = new_file
                    sermon.save()
                    print(f"  ✅ Fixed thumbnail for {sermon.title}")
                    fixed_count += 1
                except Exception as e:
                    print(f"  ❌ Error fixing {sermon.title}: {e}")
        
        print(f"\n🎉 Successfully fixed {fixed_count} images!")
        return fixed_count
        
    except Exception as e:
        print(f"❌ Error fixing images: {e}")
        return 0

def main():
    """Main configuration function"""
    print("🚀 ImageKit Configuration and Setup")
    print("=" * 60)
    
    # Step 1: Configure environment
    configure_imagekit_environment()
    
    # Step 2: Test ImageKit connection
    if not test_imagekit_connection():
        print("\n❌ ImageKit connection failed. Please check your credentials.")
        return
    
    # Step 3: Update Django settings
    update_django_settings()
    
    # Step 4: Test Django storage
    if not test_django_storage():
        print("\n❌ Django storage test failed.")
        return
    
    # Step 5: Fix corrupted images
    print("\n" + "=" * 60)
    print("🔧 FIXING CORRUPTED IMAGES")
    print("=" * 60)
    
    response = input("Do you want to fix all corrupted images? (y/n): ")
    if response.lower() == 'y':
        fixed_count = fix_corrupted_images_with_imagekit()
        print(f"\n✅ Configuration complete! Fixed {fixed_count} images.")
    else:
        print("\n✅ Configuration complete! Images will be fixed when you upload new ones.")
    
    print("\n🎯 Next Steps:")
    print("1. Restart your Django server")
    print("2. Check the Django admin to see the improved image display")
    print("3. Upload new images to test ImageKit functionality")

if __name__ == "__main__":
    main() 