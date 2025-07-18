#!/usr/bin/env python
"""
Check production database status and image URLs
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import (
    Church, Ministry, News, Sermon, Hero, HeroMedia, 
    EventHighlight, EventSpeaker, AboutPage, LeadershipPage,
    LocalLeadershipPage, LocalAboutPage, EventHeroMedia
)

def check_production_status():
    """Check the current status of the production database"""
    print("🔍 Production Status Check")
    print("=" * 50)
    
    # Check storage configuration
    print(f"📦 Storage Backend: {settings.DEFAULT_FILE_STORAGE}")
    
    # Check cloud storage config
    if hasattr(settings, 'IMAGEKIT_CONFIG') and all(settings.IMAGEKIT_CONFIG.values()):
        print("🖼️ ImageKit: ✅ Configured")
        print(f"   URL Endpoint: {settings.IMAGEKIT_CONFIG['URL_ENDPOINT']}")
    elif hasattr(settings, 'CLOUDINARY_STORAGE') and all(settings.CLOUDINARY_STORAGE.values()):
        print("☁️ Cloudinary: ✅ Configured")
        print(f"   Cloud Name: {settings.CLOUDINARY_STORAGE['CLOUD_NAME']}")
    else:
        print("❌ No cloud storage configured!")
    
    # Check database counts
    print("\n📊 Database Records:")
    print(f"  Churches: {Church.objects.count()}")
    print(f"  Ministries: {Ministry.objects.count()}")
    print(f"  News: {News.objects.count()}")
    print(f"  Sermons: {Sermon.objects.count()}")
    print(f"  Heroes: {Hero.objects.count()}")
    print(f"  Hero Media: {HeroMedia.objects.count()}")
    print(f"  Event Highlights: {EventHighlight.objects.count()}")
    print(f"  Event Speakers: {EventSpeaker.objects.count()}")
    
    # Check image URL status
    print("\n🖼️ Image URL Status:")
    
    models_to_check = [
        (Church, ['logo', 'banner_image']),
        (Ministry, ['image']),
        (News, ['image']),
        (Sermon, ['thumbnail']),
        (Hero, ['background_image']),
        (HeroMedia, ['image']),
        (EventHighlight, ['image']),
        (EventSpeaker, ['photo']),
    ]
    
    total_images = 0
    cloud_urls = 0
    local_paths = 0
    empty_fields = 0
    
    for model_class, image_fields in models_to_check:
        for obj in model_class.objects.all():
            for field_name in image_fields:
                field = getattr(obj, field_name)
                if field and str(field):
                    field_str = str(field)
                    total_images += 1
                    
                    if field_str.startswith('http'):
                        cloud_urls += 1
                    elif '/' in field_str:
                        local_paths += 1
                        print(f"  ❌ Local path found: {model_class.__name__}.{field_name} = {field_str}")
                else:
                    empty_fields += 1
    
    print(f"  Total image fields: {total_images}")
    print(f"  Cloud URLs: {cloud_urls}")
    print(f"  Local paths: {local_paths}")
    print(f"  Empty fields: {empty_fields}")
    
    if local_paths > 0:
        print(f"\n⚠️ Found {local_paths} local file paths that need fixing!")
        print("Run fix_production_images.py to fix them.")
    else:
        print("\n✅ All image URLs are properly configured!")
    
    # Check a few sample URLs
    print("\n🔗 Sample Image URLs:")
    sample_count = 0
    for church in Church.objects.all()[:3]:
        if church.logo:
            print(f"  Church {church.name} logo: {church.logo}")
            sample_count += 1
        if sample_count >= 3:
            break
    
    if sample_count == 0:
        print("  No sample images found")

if __name__ == '__main__':
    check_production_status() 