#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import HeroMedia

def check_hero_media_item():
    print("=== Checking Hero Media Item ID 46 ===")
    
    try:
        hm = HeroMedia.objects.get(id=46)
        print(f"ID: {hm.id}")
        print(f"Hero: {hm.hero.title}")
        print(f"Image: {hm.image}")
        print(f"Video: {hm.video}")
        print(f"Video name: {hm.video.name if hm.video else 'None'}")
        print(f"Order: {hm.order}")
        
        # Check if video field is actually empty
        if hm.video:
            print(f"Video exists: True")
            print(f"Video URL: {hm.get_video_url()}")
        else:
            print(f"Video exists: False")
            
    except HeroMedia.DoesNotExist:
        print("Hero Media Item 46 does not exist!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_hero_media_item() 