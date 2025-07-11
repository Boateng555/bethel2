#!/usr/bin/env python
"""
Script to check Hero Media status for all churches
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church, Hero, HeroMedia
from django.db import models

def check_hero_media_status():
    """Check Hero Media status for all churches"""
    print("🔍 Checking Hero Media status for all churches...")
    print("=" * 60)
    
    churches = Church.objects.filter(is_active=True, is_approved=True)
    
    if not churches.exists():
        print("❌ No active churches found!")
        return
    
    print(f"Found {churches.count()} active churches:")
    print()
    
    for church in churches:
        hero = Hero.objects.filter(church=church).first()
        
        if not hero:
            print(f"❌ {church.name} - NO HERO CONTENT")
            continue
        
        hero_media_count = hero.hero_media.count()
        hero_media_with_files = hero.hero_media.filter(
            models.Q(image__isnull=False) | models.Q(video__isnull=False)
        ).count()
        
        if hero_media_count == 0:
            print(f"⚠️  {church.name} - Has hero but NO HERO MEDIA")
        elif hero_media_with_files == 0:
            print(f"📝 {church.name} - Has {hero_media_count} Hero Media entries (no files uploaded)")
        else:
            print(f"✅ {church.name} - Has {hero_media_count} Hero Media entries ({hero_media_with_files} with files)")
    
    print()
    print("=" * 60)
    print("📊 SUMMARY:")
    
    total_churches = churches.count()
    churches_with_hero = churches.filter(hero__isnull=False).count()
    churches_without_hero = total_churches - churches_with_hero
    
    print(f"Total active churches: {total_churches}")
    print(f"Churches with hero content: {churches_with_hero}")
    print(f"Churches without hero content: {churches_without_hero}")
    
    if churches_with_hero > 0:
        churches_with_media = 0
        churches_with_files = 0
        
        for church in churches:
            hero = Hero.objects.filter(church=church).first()
            if hero:
                if hero.hero_media.exists():
                    churches_with_media += 1
                    if hero.hero_media.filter(
                        models.Q(image__isnull=False) | models.Q(video__isnull=False)
                    ).exists():
                        churches_with_files += 1
        
        print(f"Churches with Hero Media entries: {churches_with_media}")
        print(f"Churches with Hero Media files: {churches_with_files}")
    
    print()
    print("💡 NEXT STEPS:")
    if churches_without_hero > 0:
        print(f"  • Run: python manage.py add_hero_media_to_churches")
    if churches_with_hero > 0:
        print(f"  • Go to /admin/core/localhero/ to add images/videos")
        print(f"  • Edit each hero and add content in the 'Hero Media' section")

if __name__ == "__main__":
    check_hero_media_status() 