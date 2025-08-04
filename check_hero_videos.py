#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Hero, HeroMedia

def check_hero_media():
    print("=== Checking Hero Media ===")
    
    heroes = Hero.objects.all()
    for hero in heroes:
        print(f"\nHero: {hero.title} (ID: {hero.id})")
        print(f"Background Type: {hero.background_type}")
        print(f"Background Image: {hero.background_image.name if hero.background_image else 'None'}")
        print(f"Background Video: {hero.background_video.name if hero.background_video else 'None'}")
        
        media_items = hero.hero_media.all()
        print(f"Hero Media Items: {media_items.count()}")
        
        for media in media_items:
            print(f"\n  Media ID: {media.id}")
            print(f"  Image: {media.image.name if media.image else 'None'}")
            print(f"  Video: {media.video.name if media.video else 'None'}")
            print(f"  Order: {media.order}")
            
            if media.video:
                print(f"  Video URL: {media.get_video_url()}")
                print(f"  Video exists: {os.path.exists(media.video.path) if hasattr(media.video, 'path') else 'N/A'}")
            else:
                print(f"  Video URL: No video")
        
        print("-" * 50)

if __name__ == "__main__":
    check_hero_media() 