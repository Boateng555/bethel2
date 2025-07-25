#!/usr/bin/env python
"""
Upload a proper test image to ImageKit to verify the upload process
"""

import os
import django

# Set environment variables
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import io

print("🖼️ Creating and uploading a proper test image...")

try:
    # Create a simple test image using PIL
    print("📝 Creating test image...")
    
    # Create a 300x200 pixel image with a gradient
    width, height = 300, 200
    image = Image.new('RGB', (width, height), color='white')
    
    # Draw a simple gradient
    for y in range(height):
        for x in range(width):
            r = int((x / width) * 255)
            g = int((y / height) * 255)
            b = 128
            image.putpixel((x, y), (r, g, b))
    
    # Add some text
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(image)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 80), "Test Image", fill='black', font=font)
    draw.text((50, 110), "ImageKit Upload", fill='blue', font=font)
    
    # Save to bytes
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # Get the image data
    image_data = img_buffer.getvalue()
    print(f"✅ Created test image: {len(image_data)} bytes")
    
    # Upload to ImageKit
    print("📤 Uploading to ImageKit...")
    test_file = ContentFile(image_data, name='test_image.png')
    
    saved_path = default_storage.save('test/test_image.png', test_file)
    url = default_storage.url(saved_path)
    
    print(f"📁 Upload path: {saved_path}")
    print(f"🌐 Upload URL: {url}")
    
    if url.startswith('https://ik.imagekit.io/'):
        print("✅ SUCCESS: Image uploaded to ImageKit!")
        print("✅ This should display as a proper image, not an icon")
        
        # Test if the image is accessible
        import requests
        try:
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'unknown')
                print(f"✅ Image is accessible: {content_type}")
                
                if 'image' in content_type:
                    print("✅ Valid image file uploaded!")
                else:
                    print(f"⚠️ Unexpected content type: {content_type}")
            else:
                print(f"❌ Image not accessible: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Could not verify image accessibility: {e}")
            
    else:
        print("❌ FAILED: Image not uploaded to ImageKit")
        print(f"❌ URL is: {url}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n📋 Next steps:")
print("1. Check the uploaded image URL in your browser")
print("2. The image should display properly, not as an icon")
print("3. If this works, the issue was with the original image files")
print("4. You may need to re-upload your actual images") 