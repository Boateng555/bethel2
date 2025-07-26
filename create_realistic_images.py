#!/usr/bin/env python
"""
Create realistic test images that match the size of real photos uploaded from Django admin
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
import math

print("🖼️ Creating realistic test images (like real photos)...")

# Initialize ImageKit
imagekit = ImageKit(
    private_key='private_Dnsrj2VW7uJakaeMaNYaav+P784=',
    public_key='public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=',
    url_endpoint='https://ik.imagekit.io/9buar9mbp'
)

def create_realistic_image(filename, text="Realistic Image", width=4000, height=3000):
    """Create a very large, realistic test image like a real photo"""
    # Create a high-resolution image (like from a modern camera)
    image = Image.new('RGB', (width, height), color='white')
    
    # Create a complex, realistic background
    for y in range(height):
        for x in range(width):
            # Create a more complex gradient with multiple color channels
            r = int((x / width) * 255)
            g = int((y / height) * 255)
            b = int(((x + y) / (width + height)) * 255)
            
            # Add some noise to make it more realistic
            noise = random.randint(-20, 20)
            r = max(0, min(255, r + noise))
            g = max(0, min(255, g + noise))
            b = max(0, min(255, b + noise))
            
            image.putpixel((x, y), (r, g, b))
    
    # Add realistic elements
    draw = ImageDraw.Draw(image)
    
    # Draw multiple circles (like objects in a photo)
    for i in range(15):
        x = random.randint(100, width-100)
        y = random.randint(100, height-100)
        radius = random.randint(50, 300)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
    
    # Draw rectangles (like buildings or objects)
    for i in range(8):
        x1 = random.randint(50, width-400)
        y1 = random.randint(50, height-400)
        x2 = x1 + random.randint(200, 500)
        y2 = y1 + random.randint(200, 500)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.rectangle([x1, y1, x2, y2], fill=color)
    
    # Add some lines (like roads or structures)
    for i in range(10):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.line([x1, y1, x2, y2], fill=color, width=random.randint(5, 20))
    
    # Add text with better positioning
    try:
        # Use a larger font for high-resolution images
        font_size = max(48, width // 50)  # Scale font with image size
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Add main text
    text_x = width // 2 - 300
    text_y = height // 2 - 100
    draw.text((text_x, text_y), text, fill='black', font=font)
    draw.text((text_x, text_y + 60), filename, fill='blue', font=font)
    draw.text((text_x, text_y + 120), f"{width}x{height} - Realistic Size", fill='green', font=font)
    
    # Save to bytes with high quality (like real photos)
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='JPEG', quality=95, optimize=True)
    img_buffer.seek(0)
    return img_buffer.getvalue()

def create_large_video_placeholder(filename):
    """Create a large video placeholder that simulates real video file size"""
    # Create a substantial video placeholder (like a real video file)
    video_content = f"""# Large Video Placeholder for {filename}
# This simulates a real video file that would be several MB in size
# Real videos are typically 10-100MB or more

{'=' * 60}
LARGE VIDEO PLACEHOLDER CONTENT
{'=' * 60}

This file represents a video that would normally be:
- Several megabytes in size (10-100MB+)
- In MP4, AVI, or MOV format
- Playable in web browsers
- Optimized for streaming
- High resolution (1080p, 4K, etc.)

For testing purposes, this placeholder contains:
- Metadata about the video
- File information
- Placeholder content to simulate large file size
- Multiple lines of content to increase size

{'=' * 60}
END OF PLACEHOLDER
{'=' * 60}
""".encode('utf-8')
    
    # Pad the content to make it much larger (simulate real video file size)
    target_size = 5000000  # 5MB to simulate a real video
    while len(video_content) < target_size:
        video_content += b"# Additional content to simulate large video file size\n"
        video_content += b"# This is placeholder data that would normally be video frames\n"
        video_content += b"# Real videos contain compressed video and audio data\n"
    
    return video_content

try:
    # Get current files
    print("📁 Getting current files from ImageKit...")
    list_files = imagekit.list_files()
    print(f"Found {len(list_files.list)} files")
    
    # Delete existing test images to replace with realistic ones
    print("\n🗑️ Deleting existing test images...")
    deleted_count = 0
    
    for file in list_files.list:
        if any(name in file.name.lower() for name in ['hero_banner', 'church_logo', 'event_image', 'sermon_thumbnail', 'ministry_image', 'news_image', 'leadership_photo', 'about_image', 'default-image', 'proper_test']):
            try:
                print(f"   Deleting: {file.name}")
                imagekit.delete_file(file.file_id)
                deleted_count += 1
            except Exception as e:
                print(f"   Error deleting {file.name}: {e}")
    
    print(f"✅ Deleted {deleted_count} existing test images")
    
    # Create realistic, large test images (like real photos)
    print("\n📝 Creating realistic test images (like real photos)...")
    
    # Different sizes that match real photo uploads
    test_images = [
        ("hero_banner.jpg", "Hero Banner", 4000, 3000),      # 4K resolution
        ("church_logo.png", "Church Logo", 2000, 1500),      # High-res logo
        ("event_image.jpg", "Event Image", 3500, 2500),      # Event photo
        ("sermon_thumbnail.jpg", "Sermon Thumbnail", 3000, 2000),  # Sermon image
        ("ministry_image.jpg", "Ministry Image", 3200, 2400),      # Ministry photo
        ("news_image.jpg", "News Image", 2800, 1800),              # News photo
        ("leadership_photo.jpg", "Leadership Photo", 2500, 2500),  # Square photo
        ("about_image.jpg", "About Page Image", 3600, 2400),       # About photo
        ("default-image.jpg", "Default Image", 3000, 2000),        # Default photo
        ("large_banner.jpg", "Large Banner", 5000, 3000),          # Ultra-wide
        ("wide_image.jpg", "Wide Image", 4500, 2000),              # Wide photo
        ("portrait_photo.jpg", "Portrait Photo", 2000, 3000),      # Portrait
        ("landscape_photo.jpg", "Landscape Photo", 4000, 2500),    # Landscape
    ]
    
    created_count = 0
    total_size = 0
    
    for filename, description, width, height in test_images:
        try:
            print(f"   Creating: {filename} ({width}x{height})")
            new_image_data = create_realistic_image(filename, description, width, height)
            
            upload = imagekit.upload_file(
                file=new_image_data,
                file_name=filename
            )
            
            # Get file size
            file_size = len(new_image_data)
            total_size += file_size
            print(f"   ✅ Created: {filename} ({file_size:,} bytes)")
            created_count += 1
            
        except Exception as e:
            print(f"   ❌ Error creating {filename}: {e}")
    
    # Create a large video placeholder
    print("\n🎥 Creating large video placeholder...")
    try:
        video_data = create_large_video_placeholder("realistic_video.mp4")
        upload = imagekit.upload_file(
            file=video_data,
            file_name="realistic_video.mp4"
        )
        video_size = len(video_data)
        total_size += video_size
        print(f"   ✅ Created: realistic_video.mp4 ({video_size:,} bytes)")
        created_count += 1
    except Exception as e:
        print(f"   ❌ Error creating video: {e}")
    
    print(f"\n✅ Successfully created {created_count} realistic test images/videos")
    print(f"📏 Total size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
    print("📋 Your ImageKit should now show large, realistic test images")
    print("🌐 Your website should display high-quality images like real photos")
    print("📸 File sizes now match real photos uploaded from Django admin")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 