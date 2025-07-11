#!/usr/bin/env python
"""
Debug script to check HeroMedia saving issues
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church, Hero, HeroMedia, LocalHero
from django.contrib.auth.models import User
from django.db import models

def debug_hero_media_save():
    """Debug HeroMedia saving issues"""
    print("🔍 Debugging HeroMedia saving issues...")
    print("=" * 60)
    
    # Check all users
    print("👥 All users:")
    for user in User.objects.all():
        print(f"  - {user.username} ({user.email})")
    
    print("\n🏛️ All churches:")
    for church in Church.objects.all():
        print(f"  - {church.name} (ID: {church.id})")
        
        # Check if church has hero content
        hero = Hero.objects.filter(church=church).first()
        if hero:
            hero_media_count = hero.hero_media.count()
            print(f"    ✅ Has hero: {hero.title} with {hero_media_count} media items")
            
            if hero_media_count > 0:
                for media in hero.hero_media.all():
                    print(f"      - Media ID: {media.id}, Image: {media.image}, Video: {media.video}")
        else:
            print(f"    ❌ No hero content")
    
    # Check all HeroMedia entries
    print("\n📸 All HeroMedia entries:")
    all_media = HeroMedia.objects.all()
    print(f"Total HeroMedia entries: {all_media.count()}")
    
    for media in all_media:
        print(f"  - ID: {media.id}")
        print(f"    Hero: {media.hero.title if media.hero else 'No hero'}")
        print(f"    Image: {media.image}")
        print(f"    Video: {media.video}")
        print(f"    Order: {media.order}")
        
        # Check if files actually exist
        if media.image:
            try:
                image_path = media.image.path
                print(f"    Image path: {image_path}")
                print(f"    Image exists: {os.path.exists(image_path)}")
            except Exception as e:
                print(f"    Image error: {e}")
        
        if media.video:
            try:
                video_path = media.video.path
                print(f"    Video path: {video_path}")
                print(f"    Video exists: {os.path.exists(video_path)}")
            except Exception as e:
                print(f"    Video error: {e}")
        print()
    
    # Check media directory
    print("\n📁 Media directory check:")
    media_root = os.path.join(os.getcwd(), 'media')
    hero_dir = os.path.join(media_root, 'hero')
    
    print(f"Media root: {media_root}")
    print(f"Media root exists: {os.path.exists(media_root)}")
    print(f"Hero directory: {hero_dir}")
    print(f"Hero directory exists: {os.path.exists(hero_dir)}")
    
    if os.path.exists(hero_dir):
        print("\nFiles in hero directory:")
        for root, dirs, files in os.walk(hero_dir):
            level = root.replace(hero_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
    
    # Check database directly
    print("\n🗄️ Database check:")
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, hero_id, image, video, "order" 
            FROM core_heromedia
        """)
        
        rows = cursor.fetchall()
        print(f"Raw database entries: {len(rows)}")
        for row in rows:
            print(f"  ID: {row[0]}, Hero ID: {row[1]}, Image: {row[2]}, Video: {row[3]}, Order: {row[4]}")
    
    print("\n" + "=" * 60)
    print("💡 Recommendations:")
    print("1. Check if files are being uploaded to the correct directory")
    print("2. Verify file permissions on the media directory")
    print("3. Check if the admin form is properly handling file uploads")
    print("4. Ensure the inline formset is saving correctly")

if __name__ == '__main__':
    debug_hero_media_save() 