#!/usr/bin/env python
"""
Create larger, more realistic test images for the website
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

from imagekitio import ImageKit
from PIL import Image, ImageDraw, ImageFont
import io
import random

print("🖼️ Creating large, realistic test images...")

# Initialize ImageKit
imagekit = ImageKit(
    private_key='private_Dnsrj2VW7uJakaeMaNYaav+P784=',
    public_key='public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=',
    url_endpoint='https://ik.imagekit.io/9buar9mbp'
)

def create_large_test_image(filename, text="Test Image", width=1920, height=1080):
    """Create a large, realistic test image"""
    # Create a high-resolution image
    image = Image.new('RGB', (width, height), color='white')
    
    # Create a more complex gradient background
    for y in range(height):
        for x in range(width):
            # Create a more realistic gradient
            r = int((x / width) * 255)
            g = int((y / height) * 255)
            b = int(((x + y) / (width + height)) * 255)
            image.putpixel((x, y), (r, g, b))
    
    # Add some geometric shapes to make it more interesting
    draw = ImageDraw.Draw(image)
    
    # Draw some circles
    for i in range(5):
        x = random.randint(100, width-100)
        y = random.randint(100, height-100)
        radius = random.randint(50, 200)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
    
    # Draw some rectangles
    for i in range(3):
        x1 = random.randint(50, width-200)
        y1 = random.randint(50, height-200)
        x2 = x1 + random.randint(100, 300)
        y2 = y1 + random.randint(100, 300)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.rectangle([x1, y1, x2, y2], fill=color)
    
    # Add text with better positioning
    try:
        # Try to use a larger font
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    except:
        font = ImageFont.load_default()
    
    # Add main text
    draw.text((width//2 - 200, height//2 - 50), text, fill='black', font=font)
    draw.text((width//2 - 200, height//2 + 10), filename, fill='blue', font=font)
    
    # Add some additional text
    draw.text((width//2 - 200, height//2 + 70), f"{width}x{height} Test Image", fill='green', font=font)
    
    # Save to bytes with high quality
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='JPEG', quality=95, optimize=True)
    img_buffer.seek(0)
    return img_buffer.getvalue()

def create_large_video_placeholder(filename):
    """Create a larger video placeholder file"""
    # Create a more substantial video placeholder
    video_content = f"""# Video Placeholder for {filename}
# This is a placeholder for a video file
# In production, this would be replaced with actual video content
# File size: ~100KB to simulate a real video file

{'=' * 50}
VIDEO PLACEHOLDER CONTENT
{'=' * 50}

This file represents a video that would normally be:
- Several megabytes in size
- In MP4, AVI, or MOV format
- Playable in web browsers
- Optimized for streaming

For testing purposes, this placeholder contains:
- Metadata about the video
- File information
- Placeholder content to simulate file size

{'=' * 50}
END OF PLACEHOLDER
{'=' * 50}
""".encode('utf-8')
    
    # Pad the content to make it larger (simulate real video file size)
    while len(video_content) < 100000:  # Make it ~100KB
        video_content += b"# Additional content to increase file size\n"
    
    return video_content

try:
    # Get current files
    print("📁 Getting current files from ImageKit...")
    list_files = imagekit.list_files()
    print(f"Found {len(list_files.list)} files")
    
    # Delete existing test images to replace with larger ones
    print("\n🗑️ Deleting existing test images...")
    deleted_count = 0
    
    for file in list_files.list:
        if any(name in file.name.lower() for name in ['hero_banner', 'church_logo', 'event_image', 'sermon_thumbnail', 'ministry_image', 'news_image', 'leadership_photo', 'about_image', 'default-image']):
            try:
                print(f"   Deleting: {file.name}")
                imagekit.delete_file(file.file_id)
                deleted_count += 1
            except Exception as e:
                print(f"   Error deleting {file.name}: {e}")
    
    print(f"✅ Deleted {deleted_count} existing test images")
    
    # Create large, realistic test images
    print("\n📝 Creating large, realistic test images...")
    
    test_images = [
        ("hero_banner.jpg", "Hero Banner", 1920, 1080),  # Full HD
        ("church_logo.png", "Church Logo", 800, 600),    # Medium size
        ("event_image.jpg", "Event Image", 1600, 900),   # HD
        ("sermon_thumbnail.jpg", "Sermon Thumbnail", 1280, 720),  # HD
        ("ministry_image.jpg", "Ministry Image", 1400, 800),      # Large
        ("news_image.jpg", "News Image", 1200, 800),              # Medium-large
        ("leadership_photo.jpg", "Leadership Photo", 1000, 1000), # Square
        ("about_image.jpg", "About Page Image", 1500, 900),       # Large
        ("default-image.jpg", "Default Image", 1200, 800),        # Default
        ("large_banner.jpg", "Large Banner", 2560, 1440),         # 2K
        ("wide_image.jpg", "Wide Image", 1920, 800),              # Wide
    ]
    
    created_count = 0
    for filename, description, width, height in test_images:
        try:
            print(f"   Creating: {filename} ({width}x{height})")
            new_image_data = create_large_test_image(filename, description, width, height)
            
            upload = imagekit.upload_file(
                file=new_image_data,
                file_name=filename
            )
            
            # Get file size
            file_size = len(new_image_data)
            print(f"   ✅ Created: {filename} ({file_size:,} bytes)")
            created_count += 1
            
        except Exception as e:
            print(f"   ❌ Error creating {filename}: {e}")
    
    # Create a large video placeholder
    print("\n🎥 Creating large video placeholder...")
    try:
        video_data = create_large_video_placeholder("test_video.mp4")
        upload = imagekit.upload_file(
            file=video_data,
            file_name="test_video.mp4"
        )
        print(f"   ✅ Created: test_video.mp4 ({len(video_data):,} bytes)")
        created_count += 1
    except Exception as e:
        print(f"   ❌ Error creating video: {e}")
    
    print(f"\n✅ Successfully created {created_count} large test images/videos")
    print("📋 Your ImageKit should now show large, realistic test images")
    print("🌐 Your website should display high-quality images")
    print("📏 File sizes are now much larger and more realistic")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 