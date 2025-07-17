#!/usr/bin/env python
"""
Check hero data
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Hero, HeroMedia

def check_heroes():
    """Check hero data"""
    print("🔍 Checking Hero Data...")
    print("=" * 50)
    
    heroes = Hero.objects.filter(is_active=True)
    print(f"Active heroes: {heroes.count()}")
    
    for hero in heroes:
        church_name = hero.church.name if hero.church else "Global"
        media_count = hero.hero_media.count()
        print(f"- {hero.title} (Church: {church_name}) - Media: {media_count}")
        
        if media_count > 0:
            for media in hero.hero_media.all():
                if media.image:
                    print(f"  Image: {media.image}")
                if media.video:
                    print(f"  Video: {media.video}")

if __name__ == "__main__":
    check_heroes() 