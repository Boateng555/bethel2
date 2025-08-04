#!/usr/bin/env python
"""
Script to add more videos and pictures to the global hero
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import GlobalSettings, Hero, HeroMedia
from django.core.files import File
from django.conf import settings

def main():
    print("=== Adding More Media to Global Hero ===\n")
    
    # Get global settings and hero
    try:
        gs = GlobalSettings.objects.first()
        if not gs or not gs.global_hero:
            print("❌ No global hero found!")
            return
        
        hero = gs.global_hero
        print(f"✅ Found Global Hero: {hero.title}")
        print(f"   Hero ID: {hero.id}")
        
        # Check current media items
        current_media = hero.hero_media.all()
        print(f"\n📊 Current Media Items: {current_media.count()}")
        
        for media in current_media:
            print(f"   - ID {media.id}: Image={media.image}, Video={media.video}, Order={media.order}")
        
        # Check if we can add more media
        max_media = 10  # Based on admin configuration
        if current_media.count() >= max_media:
            print(f"\n⚠️  Maximum media items ({max_media}) already reached!")
            print("   You can add more through the Django admin interface.")
            return
        
        print(f"\n🎯 You can add {max_media - current_media.count()} more media items")
        
        # Instructions for adding more media
        print("\n📝 To add more videos and pictures to your global hero:")
        print("   1. Go to Django Admin: http://127.0.0.1:8000/admin/")
        print("   2. Navigate to 'Core' → 'Heros'")
        print("   3. Click on your global hero (title: 'kwame')")
        print("   4. Scroll down to the 'Hero Media' section")
        print("   5. Click 'Add another Hero media' to add more items")
        print("   6. Upload images or videos for each item")
        print("   7. Set the order (1, 2, 3, etc.) to control display sequence")
        print("   8. Save the hero")
        
        # Show current admin configuration
        print(f"\n⚙️  Admin Configuration:")
        print(f"   - Extra forms: 3 (you can add 3 items at once)")
        print(f"   - Maximum items: {max_media}")
        print(f"   - Current items: {current_media.count()}")
        
        # Suggest next steps
        print(f"\n🚀 Next Steps:")
        print(f"   1. Add {min(3, max_media - current_media.count())} more media items through admin")
        print(f"   2. Mix images and videos for variety")
        print(f"   3. Set proper order numbers (1, 2, 3, etc.)")
        print(f"   4. Test the carousel on your homepage")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 