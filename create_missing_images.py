#!/usr/bin/env python3
"""
Create missing placeholder images with the correct filenames
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

from core.models import HeroMedia, Church, Ministry, News, Sermon
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import uuid

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
    
    return img

def create_missing_images():
    """Create missing placeholder images"""
    print("🔧 Creating Missing Images")
    print("=" * 50)
    
    created_count = 0
    
    # Create HeroMedia images
    print("\n📸 Creating HeroMedia Images")
    hero_media_list = HeroMedia.objects.all()
    for media in hero_media_list:
        if media.image:
            filename = str(media.image)
            if filename and not os.path.exists(os.path.join('media', filename)):
                # Create placeholder
                img = create_placeholder_image(1200, 800, f"HeroMedia {media.id}")
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(os.path.join('media', filename)), exist_ok=True)
                
                # Save image
                img.save(os.path.join('media', filename))
                print(f"  ✅ Created: {filename}")
                created_count += 1
    
    # Create Church images
    print("\n🏛️ Creating Church Images")
    church_list = Church.objects.all()
    for church in church_list:
        if church.logo:
            filename = str(church.logo)
            if filename and not os.path.exists(os.path.join('media', filename)):
                img = create_placeholder_image(400, 400, f"Logo: {church.name}")
                os.makedirs(os.path.dirname(os.path.join('media', filename)), exist_ok=True)
                img.save(os.path.join('media', filename))
                print(f"  ✅ Created: {filename}")
                created_count += 1
        
        if church.banner_image:
            filename = str(church.banner_image)
            if filename and not os.path.exists(os.path.join('media', filename)):
                img = create_placeholder_image(1200, 600, f"Banner: {church.name}")
                os.makedirs(os.path.dirname(os.path.join('media', filename)), exist_ok=True)
                img.save(os.path.join('media', filename))
                print(f"  ✅ Created: {filename}")
                created_count += 1
    
    # Create Ministry images
    print("\n⛪ Creating Ministry Images")
    ministry_list = Ministry.objects.all()
    for ministry in ministry_list:
        if ministry.image:
            filename = str(ministry.image)
            if filename and not os.path.exists(os.path.join('media', filename)):
                img = create_placeholder_image(800, 600, f"Ministry: {ministry.name}")
                os.makedirs(os.path.dirname(os.path.join('media', filename)), exist_ok=True)
                img.save(os.path.join('media', filename))
                print(f"  ✅ Created: {filename}")
                created_count += 1
    
    # Create News images
    print("\n📰 Creating News Images")
    news_list = News.objects.all()
    for news in news_list:
        if news.image:
            filename = str(news.image)
            if filename and not os.path.exists(os.path.join('media', filename)):
                img = create_placeholder_image(800, 600, f"News: {news.title}")
                os.makedirs(os.path.dirname(os.path.join('media', filename)), exist_ok=True)
                img.save(os.path.join('media', filename))
                print(f"  ✅ Created: {filename}")
                created_count += 1
    
    # Create Sermon images
    print("\n📖 Creating Sermon Images")
    sermon_list = Sermon.objects.all()
    for sermon in sermon_list:
        if sermon.thumbnail:
            filename = str(sermon.thumbnail)
            if filename and not os.path.exists(os.path.join('media', filename)):
                img = create_placeholder_image(400, 300, f"Sermon: {sermon.title}")
                os.makedirs(os.path.dirname(os.path.join('media', filename)), exist_ok=True)
                img.save(os.path.join('media', filename))
                print(f"  ✅ Created: {filename}")
                created_count += 1
    
    print(f"\n🎉 Created {created_count} missing images!")
    print("All images should now be available for the frontend.")

if __name__ == "__main__":
    create_missing_images() 