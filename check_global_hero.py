#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import GlobalSettings, Hero, HeroMedia

def check_global_hero():
    print("=== Checking Global Hero Settings ===")
    
    gs = GlobalSettings.objects.first()
    if not gs:
        print("No GlobalSettings found!")
        return
    
    print(f"Global Settings ID: {gs.id}")
    print(f"Global Hero: {gs.global_hero.title if gs.global_hero else 'None'}")
    print(f"Global Hero ID: {gs.global_hero.id if gs.global_hero else 'None'}")
    
    if gs.global_hero:
        hero = gs.global_hero
        print(f"\n=== Global Hero Details ===")
        print(f"Title: {hero.title}")
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
            else:
                print(f"  Video URL: No video")
    else:
        print("\nNo global hero is set!")
        print("Available heroes:")
        for hero in Hero.objects.all():
            print(f"- {hero.title} (ID: {hero.id})")

if __name__ == "__main__":
    check_global_hero() 