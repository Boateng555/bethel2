#!/usr/bin/env python3
"""
Check if database URLs have been updated to Cloudinary
"""

import os
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church, News, Ministry, Sermon, HeroMedia

print("🔍 Checking database URLs...")
print("=" * 50)

# Check Church logos
print("\n📋 CHURCH LOGOS:")
churches = Church.objects.all()
for church in churches:
    if church.logo:
        print(f"  {church.name}:")
        print(f"    URL: {church.logo}")
        if 'res.cloudinary.com' in str(church.logo):
            print(f"    ✅ Cloudinary URL")
        else:
            print(f"    ❌ Still local path")

# Check Hero Media
print("\n📋 HERO MEDIA:")
hero_media = HeroMedia.objects.all()
for hero in hero_media:
    if hero.image:
        print(f"  Hero {hero.id}:")
        print(f"    URL: {hero.image}")
        if 'res.cloudinary.com' in str(hero.image):
            print(f"    ✅ Cloudinary URL")
        else:
            print(f"    ❌ Still local path")

print("\n" + "=" * 50)
print("💡 If you see ❌, the upload command didn't run successfully")
print("💡 If you see ✅, the URLs are correct but images might not be loading") 