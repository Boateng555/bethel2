#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import GlobalSettings, Hero, HeroMedia

def add_video_to_hero_media():
    print("=== Adding Background Video to Hero Media ===")
    
    gs = GlobalSettings.objects.first()
    if not gs or not gs.global_hero:
        print("No global hero found!")
        return
    
    hero = gs.global_hero
    print(f"Global Hero: {hero.title} (ID: {hero.id})")
    
    # Check if hero has background video
    if not hero.background_video:
        print("No background video found!")
        return
    
    print(f"Background Video: {hero.background_video.name}")
    
    # Check if video already exists in THIS hero's media (explicitly check for non-null)
    existing_video = hero.hero_media.exclude(video__isnull=True).exclude(video='').first()
    if existing_video:
        print(f"Video already exists in this hero's media (ID: {existing_video.id})")
        print(f"Video: {existing_video.video.name}")
        return
    
    # Check if there's an existing hero media item without video
    existing_media = hero.hero_media.first()
    if existing_media and not existing_media.video:
        print(f"Found existing media item (ID: {existing_media.id}) without video")
        print(f"Adding video to existing item...")
        
        try:
            existing_media.video = hero.background_video
            existing_media.save()
            print(f"✅ Successfully added video to existing media item (ID: {existing_media.id})")
            print(f"Video URL: {existing_media.get_video_url()}")
        except Exception as e:
            print(f"❌ Error adding video: {e}")
    else:
        # Create new hero media item with the video
        try:
            new_media = HeroMedia.objects.create(
                hero=hero,
                video=hero.background_video,
                order=1  # Set as first item
            )
            print(f"✅ Successfully created new media item with video (ID: {new_media.id})")
            print(f"Video URL: {new_media.get_video_url()}")
            
        except Exception as e:
            print(f"❌ Error creating new media item: {e}")

if __name__ == "__main__":
    add_video_to_hero_media() 