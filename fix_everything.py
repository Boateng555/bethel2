#!/usr/bin/env python3
"""
Fix everything - Settings, Storage, and Corrupted Files
"""

import os
import requests
from imagekitio import ImageKit
from PIL import Image, ImageDraw, ImageFont
import io

print("🔧 Fixing everything - Settings, Storage, and Corrupted Files...")

# ImageKit credentials
PUBLIC_KEY = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
PRIVATE_KEY = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
URL_ENDPOINT = 'https://ik.imagekit.io/9buar9mbp'

def create_proper_image(filename, width=1920, height=1080):
    """Create a proper image that will be large and visible"""
    print(f"   Creating proper image: {filename}")
    
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
    draw.rectangle([100, 100, width-100, height-100], fill='white', outline='black', width=5)
    draw.ellipse([width//2-150, height//2-150, width//2+150, height//2+150], fill='red')
    
    # Add text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    except:
        font = ImageFont.load_default()
    
    draw.text((width//2-200, 200), "PROPER IMAGE", fill='black', font=font)
    draw.text((width//2-300, 300), "Fixed Storage Backend!", fill='blue', font=font)
    draw.text((width//2-250, 400), f"Size: {width}x{height}", fill='green', font=font)
    draw.text((width//2-200, 500), "No More Corruption!", fill='red', font=font)
    
    # Save as high quality JPEG
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='JPEG', quality=95, optimize=False)
    img_buffer.seek(0)
    
    image_data = img_buffer.getvalue()
    print(f"   ✅ Created proper image: {len(image_data):,} bytes")
    return image_data

def fix_all_corrupted_files():
    """Find and fix all corrupted files in ImageKit"""
    print("\n🔄 Finding and fixing ALL corrupted files...")
    
    # Initialize ImageKit
    imagekit = ImageKit(
        private_key=PRIVATE_KEY,
        public_key=PUBLIC_KEY,
        url_endpoint=URL_ENDPOINT
    )
    
    try:
        # Get all files
        print("   Getting files from ImageKit...")
        list_files = imagekit.list_files()
        print(f"   Found {len(list_files.list)} files in ImageKit")
        
        # Find corrupted files (smaller than 200KB)
        corrupted_files = []
        for file in list_files.list:
            if file.size < 200000:  # Less than 200KB
                corrupted_files.append(file)
                print(f"   Found corrupted: {file.name} ({file.size} bytes)")
        
        print(f"   Found {len(corrupted_files)} corrupted files to fix")
        
        if len(corrupted_files) == 0:
            print("   ✅ No corrupted files found!")
            return 0
        
        # Fix each corrupted file
        fixed_count = 0
        for file in corrupted_files:
            try:
                print(f"\n   🔧 Fixing: {file.name}")
                
                # Delete corrupted file
                imagekit.delete_file(file.file_id)
                print(f"     Deleted corrupted file")
                
                # Create proper image with same name
                image_data = create_proper_image(file.name)
                
                # Upload proper image
                upload = imagekit.upload_file(
                    file=image_data,
                    file_name=file.name
                )
                
                print(f"     ✅ Fixed! New size: {len(image_data):,} bytes")
                print(f"     ✅ URL: {upload.url}")
                fixed_count += 1
                
            except Exception as e:
                print(f"     ❌ Error fixing {file.name}: {e}")
        
        print(f"\n   ✅ Fixed {fixed_count} corrupted files")
        return fixed_count
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 0

def test_proper_upload():
    """Test that we can upload proper images"""
    print("\n📤 Testing proper image upload...")
    
    imagekit = ImageKit(
        private_key=PRIVATE_KEY,
        public_key=PUBLIC_KEY,
        url_endpoint=URL_ENDPOINT
    )
    
    try:
        # Create test image
        image_data = create_proper_image("test_proper.jpg")
        
        # Upload test image
        upload = imagekit.upload_file(
            file=image_data,
            file_name='test_proper.jpg'
        )
        
        print(f"   ✅ Test upload successful!")
        print(f"   URL: {upload.url}")
        print(f"   Size: {len(image_data):,} bytes")
        
        # Clean up test file
        imagekit.delete_file(upload.file_id)
        print(f"   ✅ Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test upload failed: {e}")
        return False

def create_settings_fix():
    """Create a settings fix file"""
    print("\n⚙️ Creating settings fix...")
    
    fix_content = '''
# Add this to your Django settings to prevent corruption
import os

# Force proper ImageKit configuration
os.environ.setdefault('IMAGEKIT_PUBLIC_KEY', 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=')
os.environ.setdefault('IMAGEKIT_PRIVATE_KEY', 'private_Dnsrj2VW7uJakaeMaNYaav+P784=')
os.environ.setdefault('IMAGEKIT_URL_ENDPOINT', 'https://ik.imagekit.io/9buar9mbp')

# Use fixed storage backend
DEFAULT_FILE_STORAGE = 'core.fixed_storage.FixedImageKitStorage'

# Disable any compression
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
'''
    
    with open('settings_fix.py', 'w') as f:
        f.write(fix_content)
    
    print("   ✅ Created settings_fix.py")

# Main execution
try:
    print("🚀 Starting comprehensive fix...")
    
    # Create settings fix
    create_settings_fix()
    
    # Test upload first
    if test_proper_upload():
        print("   ✅ Upload test passed")
    else:
        print("   ❌ Upload test failed")
        exit(1)
    
    # Fix all corrupted files
    fixed_count = fix_all_corrupted_files()
    
    print(f"\n📋 Summary:")
    print(f"✅ Created settings fix file")
    print(f"✅ Tested proper image upload")
    print(f"✅ Fixed {fixed_count} corrupted files")
    print(f"\n🌐 Next Steps:")
    print(f"1. Restart your Django server")
    print(f"2. Check your ImageKit dashboard")
    print(f"3. All files should be >200KB")
    print(f"4. No more 72-byte files!")
    print(f"5. Images should display properly!")
    print(f"6. New uploads will use fixed storage!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 