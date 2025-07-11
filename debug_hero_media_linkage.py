#!/usr/bin/env python
"""
Debug script to print all Hero, LocalHero, and HeroMedia for a given church, and force-create a test HeroMedia entry.
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church, Hero, LocalHero, HeroMedia
from django.core.files.base import ContentFile

CHURCH_NAME = 'bethel hamburg'  # Change to your church name if needed

def debug_hero_media():
    print(f"\n=== Debugging Hero/LocalHero/HeroMedia for church: {CHURCH_NAME} ===\n")
    try:
        church = Church.objects.get(name__iexact=CHURCH_NAME)
    except Church.DoesNotExist:
        print(f"Church '{CHURCH_NAME}' not found!")
        return
    print(f"Church: {church.name} (ID: {church.id})")

    # Print all Hero objects for this church
    heroes = Hero.objects.filter(church=church)
    print(f"\nHeroes for this church: {heroes.count()}")
    for hero in heroes:
        print(f"  Hero: {hero.id} | Title: {hero.title}")
        # Print all HeroMedia for this hero
        media = hero.hero_media.all()
        print(f"    HeroMedia count: {media.count()}")
        for m in media:
            print(f"      - ID: {m.id}, Image: {m.image}, Video: {m.video}, Order: {m.order}")

    # Print all LocalHero objects for this church
    local_heroes = LocalHero.objects.filter(church=church)
    print(f"\nLocalHero objects for this church: {local_heroes.count()}")
    for lhero in local_heroes:
        print(f"  LocalHero: {lhero.id} | Title: {lhero.title}")
        media = lhero.hero_media.all()
        print(f"    HeroMedia count: {media.count()}")
        for m in media:
            print(f"      - ID: {m.id}, Image: {m.image}, Video: {m.video}, Order: {m.order}")

    # Force-create a test HeroMedia entry for the first hero with a dummy image
    if heroes.exists():
        hero = heroes.first()
        print("\nForce-creating a test HeroMedia entry with a dummy image...")
        dummy_image_content = ContentFile(b"dummy image data", name="test_image_force.jpg")
        test_media = HeroMedia.objects.create(hero=hero, image=dummy_image_content, order=101)
        print(f"  Created test HeroMedia: ID={test_media.id}, Image={test_media.image}, Order={test_media.order}")

    # Print all HeroMedia in the database and their hero/church linkage
    print("\nAll HeroMedia in the database:")
    for m in HeroMedia.objects.all():
        print(f"  ID: {m.id}, Hero: {m.hero.id}, Hero Title: {m.hero.title}, Church: {m.hero.church.name if m.hero.church else 'None'}, Image: {m.image}, Video: {m.video}, Order: {m.order}")

    print("\n=== End of Debug ===\n")

if __name__ == '__main__':
    debug_hero_media() 