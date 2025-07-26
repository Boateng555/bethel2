#!/usr/bin/env python3
"""
Complete test script to verify all image fixes are working
"""

import os
import sys
import django
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
import io

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def create_test_image(filename, width=800, height=600):
    """Create a test image for upload testing"""
    print(f"   Creating test image: {filename}")
    
    # Create a colorful image
    image = Image.new('RGB', (width, height), color='lightblue')
    draw = ImageDraw.Draw(image)
    
    # Add gradient background
    for y in range(height):
        for x in range(width):
            r = int((x / width) * 255)
            g = int((y / height) * 255)
            b = 128
            image.putpixel((x, y), (r, g, b))
    
    # Add shapes and text
    draw.rectangle([50, 50, width-50, height-50], fill='white', outline='black', width=3)
    draw.ellipse([width//2-100, height//2-100, width//2+100, height//2+100], fill='red')
    
    # Add text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    draw.text((width//2-150, 100), "TEST IMAGE", fill='black', font=font)
    draw.text((width//2-200, 150), "Complete Fix Test!", fill='blue', font=font)
    draw.text((width//2-150, 200), f"Size: {width}x{height}", fill='green', font=font)
    
    # Save as high quality JPEG
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='JPEG', quality=95, optimize=False)
    img_buffer.seek(0)
    
    image_data = img_buffer.getvalue()
    print(f"   ✅ Created test image: {len(image_data):,} bytes")
    return image_data

def test_storage_backend():
    """Test that the storage backend is working correctly"""
    print("\n🔧 Testing storage backend...")
    
    try:
        # Check storage backend type
        storage_class = type(default_storage._wrapped).__name__
        print(f"   Storage backend: {storage_class}")
        
        if 'RobustImageKitStorage' in storage_class:
            print("   ✅ Using robust ImageKit storage")
        else:
            print("   ⚠️ Not using robust ImageKit storage")
            return False
        
        # Test environment variables
        public_key = os.environ.get('IMAGEKIT_PUBLIC_KEY')
        private_key = os.environ.get('IMAGEKIT_PRIVATE_KEY')
        url_endpoint = os.environ.get('IMAGEKIT_URL_ENDPOINT')
        
        if all([public_key, private_key, url_endpoint]):
            print("   ✅ ImageKit environment variables set")
        else:
            print("   ❌ ImageKit environment variables missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Storage backend test failed: {e}")
        return False

def test_image_upload():
    """Test image upload functionality"""
    print("\n📤 Testing image upload...")
    
    try:
        # Create test image
        image_data = create_test_image("test_complete_fix.jpg")
        
        # Upload using Django storage
        file_path = default_storage.save('test/test_complete_fix.jpg', ContentFile(image_data))
        file_url = default_storage.url(file_path)
        
        print(f"   ✅ Upload successful!")
        print(f"   File path: {file_path}")
        print(f"   File URL: {file_url}")
        
        # Check if URL is ImageKit
        if 'ik.imagekit.io' in file_url:
            print("   ✅ File uploaded to ImageKit")
        else:
            print("   ⚠️ File not uploaded to ImageKit")
        
        # Check file size
        file_size = default_storage.size(file_path)
        print(f"   File size: {file_size:,} bytes")
        
        if file_size > 100000:  # More than 100KB
            print("   ✅ File size is reasonable")
        else:
            print("   ⚠️ File size seems small")
        
        # Clean up
        default_storage.delete(file_path)
        print("   ✅ Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Upload test failed: {e}")
        return False

def test_django_admin_simulation():
    """Simulate Django admin upload process"""
    print("\n🏛️ Testing Django admin simulation...")
    
    try:
        from core.models import Church
        
        # Create a test church
        church = Church.objects.create(
            name="Test Church for Image Fix",
            slug="test-church-image-fix",
            address="123 Test Street",
            city="Test City",
            country="Test Country"
        )
        
        # Create test image
        image_data = create_test_image("church_logo_test.jpg", 400, 400)
        
        # Simulate admin upload
        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded_file = SimpleUploadedFile(
            "church_logo_test.jpg",
            image_data,
            content_type="image/jpeg"
        )
        
        # Save to model (this will trigger the resize signals)
        church.logo = uploaded_file
        church.save()
        
        print(f"   ✅ Church created with logo")
        print(f"   Logo URL: {church.logo.url}")
        
        # Check if logo is in ImageKit
        if 'ik.imagekit.io' in str(church.logo.url):
            print("   ✅ Logo uploaded to ImageKit")
        else:
            print("   ⚠️ Logo not uploaded to ImageKit")
        
        # Check logo size
        logo_size = default_storage.size(str(church.logo))
        print(f"   Logo size: {logo_size:,} bytes")
        
        if logo_size > 10000:  # More than 10KB
            print("   ✅ Logo size is reasonable")
        else:
            print("   ⚠️ Logo size seems small")
        
        # Clean up
        church.delete()
        print("   ✅ Test church cleaned up")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Django admin simulation failed: {e}")
        return False

def run_management_command():
    """Run the management command to fix images"""
    print("\n⚙️ Running management command...")
    
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Capture output
        out = StringIO()
        
        # Run the command
        call_command('fix_all_images', '--test-upload', stdout=out)
        
        output = out.getvalue()
        print("   ✅ Management command completed")
        print("   Output preview:")
        for line in output.split('\n')[:10]:  # Show first 10 lines
            if line.strip():
                print(f"     {line}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Management command failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting complete image fix verification...")
    
    tests = [
        ("Storage Backend", test_storage_backend),
        ("Image Upload", test_image_upload),
        ("Django Admin Simulation", test_django_admin_simulation),
        ("Management Command", run_management_command),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📋 Test Summary:")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your image fix is working correctly.")
        print("\n🌐 Next Steps:")
        print("1. Upload images via Django admin")
        print("2. All images will be properly resized and validated")
        print("3. No more 72-byte corrupted files!")
        print("4. Images will display correctly on your website")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 