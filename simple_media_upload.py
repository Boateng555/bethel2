#!/usr/bin/env python
"""
Simple script to help you upload media via the admin interface
This will guide you through the manual upload process
"""
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church, Hero, HeroMedia, News, Ministry, Sermon

def show_upload_guide():
    """
    Show a guide for uploading media via admin interface
    """
    print("🚀 Media Upload Guide for Live Site")
    print("=" * 60)
    print()
    print("Since Cloudinary API has signature issues, let's upload manually:")
    print()
    
    # Show what needs to be uploaded
    print("📋 What needs to be uploaded:")
    print()
    
    # Churches
    churches = Church.objects.all()
    print(f"🏛️ Churches ({churches.count()}):")
    for church in churches:
        if church.logo:
            print(f"  - {church.name}: Has logo")
        else:
            print(f"  - {church.name}: No logo")
    print()
    
    # Heroes
    heroes = Hero.objects.all()
    print(f"🌟 Heroes ({heroes.count()}):")
    for hero in heroes:
        hero_media = HeroMedia.objects.filter(hero=hero)
        print(f"  - {hero.title}: {hero_media.count()} media files")
        for media in hero_media:
            if media.image:
                print(f"    📸 Image: {media.image.name}")
            if media.video:
                print(f"    🎥 Video: {media.video.name}")
    print()
    
    # News
    news_items = News.objects.all()
    print(f"📰 News ({news_items.count()}):")
    for news in news_items:
        if news.image:
            print(f"  - {news.title}: Has image")
        else:
            print(f"  - {news.title}: No image")
    print()
    
    # Ministries
    ministries = Ministry.objects.all()
    print(f"⛪ Ministries ({ministries.count()}):")
    for ministry in ministries:
        if ministry.image:
            print(f"  - {ministry.name}: Has image")
        else:
            print(f"  - {ministry.name}: No image")
    print()
    
    # Sermons
    sermons = Sermon.objects.all()
    print(f"📖 Sermons ({sermons.count()}):")
    for sermon in sermons:
        if sermon.thumbnail:
            print(f"  - {sermon.title}: Has thumbnail")
        else:
            print(f"  - {sermon.title}: No thumbnail")
    print()
    
    print("=" * 60)
    print("📝 MANUAL UPLOAD STEPS:")
    print()
    print("1. Go to: https://web-production-158c.up.railway.app/admin/")
    print("2. Login with your admin credentials")
    print("3. For each item above, edit it and upload the media files")
    print("4. Save - files will automatically go to Cloudinary")
    print()
    print("🎯 Priority order:")
    print("1. Hero media (most important - shows on homepage)")
    print("2. Church logos")
    print("3. News images")
    print("4. Ministry images")
    print("5. Sermon thumbnails")
    print()
    print("💡 Tip: Open your local media folder and drag files to upload")

def create_upload_list():
    """
    Create a list of files that need to be uploaded
    """
    print("\n📁 Files to upload from your local media folder:")
    print("=" * 60)
    
    media_dir = Path("media")
    if media_dir.exists():
        for file_path in media_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', '.mov', '.webm']:
                print(f"  📄 {file_path}")
    else:
        print("  ❌ Media directory not found")

if __name__ == "__main__":
    from pathlib import Path
    
    show_upload_guide()
    create_upload_list() 