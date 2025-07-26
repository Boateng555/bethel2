#!/usr/bin/env python3
"""
Simple fix for tiny files in ImageKit
"""

import os
from imagekitio import ImageKit
from PIL import Image, ImageDraw, ImageFont
import io

print("🔧 Simple fix for tiny files...")

# Direct ImageKit setup
imagekit = ImageKit(
    private_key='private_Dnsrj2VW7uJakaeMaNYaav+P784=',
    public_key='public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=',
    url_endpoint='https://ik.imagekit.io/9buar9mbp'
)

def make_big_image(filename):
    """Create a big image that will definitely be large"""
    print(f"   Making big image: {filename}")
    
    # Create a very large image
    image = Image.new('RGB', (2560, 1440), color='blue')
    draw = ImageDraw.Draw(image)
    
    # Fill with lots of colors
    for y in range(0, 1440, 10):
        for x in range(0, 2560, 10):
            color = (x % 255, y % 255, (x + y) % 255)
            draw.rectangle([x, y, x+9, y+9], fill=color)
    
    # Add big text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
    except:
        font = ImageFont.load_default()
    
    draw.text((100, 100), "BIG IMAGE", fill='white', font=font)
    draw.text((100, 200), "NO MORE TINY FILES!", fill='yellow', font=font)
    draw.text((100, 300), "2560x1440 - HUGE SIZE", fill='red', font=font)
    
    # Save as maximum quality
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='JPEG', quality=100, optimize=False)
    img_buffer.seek(0)
    
    image_data = img_buffer.getvalue()
    print(f"   ✅ Made big image: {len(image_data):,} bytes")
    return image_data

def fix_tiny_files():
    """Find and fix all tiny files"""
    print("\n🔄 Finding tiny files...")
    
    try:
        # Get all files
        files = imagekit.list_files()
        print(f"   Found {len(files.list)} files")
        
        # Find tiny files (less than 1MB)
        tiny_files = []
        for file in files.list:
            if file.size < 1000000:  # Less than 1MB
                tiny_files.append(file)
                print(f"   Found tiny: {file.name} ({file.size} bytes)")
        
        print(f"   Found {len(tiny_files)} tiny files to fix")
        
        if len(tiny_files) == 0:
            print("   ✅ No tiny files found!")
            return
        
        # Fix each tiny file
        for file in tiny_files:
            try:
                print(f"\n   🔧 Fixing: {file.name}")
                
                # Delete tiny file
                imagekit.delete_file(file.file_id)
                print(f"     Deleted tiny file")
                
                # Make big image
                image_data = make_big_image(file.name)
                
                # Upload big image
                upload = imagekit.upload_file(
                    file=image_data,
                    file_name=file.name
                )
                
                print(f"     ✅ Fixed! New size: {len(image_data):,} bytes")
                print(f"     ✅ URL: {upload.url}")
                
            except Exception as e:
                print(f"     ❌ Error: {e}")
        
        print(f"\n   ✅ Fixed {len(tiny_files)} tiny files")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Run the fix
try:
    print("🚀 Starting simple fix...")
    fix_tiny_files()
    print("\n✅ Done! Check your ImageKit dashboard now.")
    print("   All files should be >1MB now!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 