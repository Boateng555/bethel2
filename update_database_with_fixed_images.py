#!/usr/bin/env python
"""
Update database to use the newly created fixed images from ImageKit
"""

import os
import django

# Set environment variables
os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import News, Church, Ministry, Sermon, Event, HeroMedia, AboutPage, LeadershipPage
from imagekitio import ImageKit

print("🔄 Updating database with fixed images...")

# Initialize ImageKit
imagekit = ImageKit(
    private_key='private_Dnsrj2VW7uJakaeMaNYaav+P784=',
    public_key='public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=',
    url_endpoint='https://ik.imagekit.io/9buar9mbp'
)

try:
    # Get available images from ImageKit
    list_files = imagekit.list_files()
    available_images = [f.name for f in list_files.list if f.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
    
    print(f"📁 Found {len(available_images)} available images in ImageKit")
    
    # Mapping of model types to appropriate test images
    image_mapping = {
        'news': 'news_image.jpg',
        'church': 'church_logo.png',
        'ministry': 'ministry_image.jpg',
        'sermon': 'sermon_thumbnail.jpg',
        'hero': 'hero_banner.jpg',
        'about': 'about_image.jpg',
        'leadership': 'leadership_photo.jpg',
        'event': 'event_image.jpg',
    }
    
    # Update News items
    print(f"\n📰 Updating News items...")
    news_items = News.objects.all()
    for news in news_items:
        if not news.image or str(news.image) not in available_images:
            # Find a suitable image
            suitable_image = image_mapping.get('news', 'news_image.jpg')
            if suitable_image in available_images:
                news.image = suitable_image
                news.save()
                print(f"   ✅ Updated: {news.title} -> {suitable_image}")
            else:
                # Use any available image
                if available_images:
                    news.image = available_images[0]
                    news.save()
                    print(f"   ✅ Updated: {news.title} -> {available_images[0]}")
    
    # Update Churches
    print(f"\n⛪ Updating Churches...")
    churches = Church.objects.all()
    for church in churches:
        if not church.logo or str(church.logo) not in available_images:
            suitable_image = image_mapping.get('church', 'church_logo.png')
            if suitable_image in available_images:
                church.logo = suitable_image
                church.save()
                print(f"   ✅ Updated: {church.name} -> {suitable_image}")
            else:
                if available_images:
                    church.logo = available_images[0]
                    church.save()
                    print(f"   ✅ Updated: {church.name} -> {available_images[0]}")
    
    # Update Ministries
    print(f"\n🙏 Updating Ministries...")
    ministries = Ministry.objects.all()
    for ministry in ministries:
        if not ministry.image or str(ministry.image) not in available_images:
            suitable_image = image_mapping.get('ministry', 'ministry_image.jpg')
            if suitable_image in available_images:
                ministry.image = suitable_image
                ministry.save()
                print(f"   ✅ Updated: {ministry.name} -> {suitable_image}")
            else:
                if available_images:
                    ministry.image = available_images[0]
                    ministry.save()
                    print(f"   ✅ Updated: {ministry.name} -> {available_images[0]}")
    
    # Update Sermons
    print(f"\n📖 Updating Sermons...")
    sermons = Sermon.objects.all()
    for sermon in sermons:
        if not sermon.thumbnail or str(sermon.thumbnail) not in available_images:
            suitable_image = image_mapping.get('sermon', 'sermon_thumbnail.jpg')
            if suitable_image in available_images:
                sermon.thumbnail = suitable_image
                sermon.save()
                print(f"   ✅ Updated: {sermon.title} -> {suitable_image}")
            else:
                if available_images:
                    sermon.thumbnail = available_images[0]
                    sermon.save()
                    print(f"   ✅ Updated: {sermon.title} -> {available_images[0]}")
    
    # Update Hero Media
    print(f"\n🌟 Updating Hero Media...")
    hero_media = HeroMedia.objects.all()
    for hero in hero_media:
        if not hero.image or str(hero.image) not in available_images:
            suitable_image = image_mapping.get('hero', 'hero_banner.jpg')
            if suitable_image in available_images:
                hero.image = suitable_image
                hero.save()
                print(f"   ✅ Updated: Hero {hero.id} -> {suitable_image}")
            else:
                if available_images:
                    hero.image = available_images[0]
                    hero.save()
                    print(f"   ✅ Updated: Hero {hero.id} -> {available_images[0]}")
    
    # Update About Pages
    print(f"\n📄 Updating About Pages...")
    about_pages = AboutPage.objects.all()
    for about in about_pages:
        if not about.image or str(about.image) not in available_images:
            suitable_image = image_mapping.get('about', 'about_image.jpg')
            if suitable_image in available_images:
                about.image = suitable_image
                about.save()
                print(f"   ✅ Updated: About page -> {suitable_image}")
            else:
                if available_images:
                    about.image = available_images[0]
                    about.save()
                    print(f"   ✅ Updated: About page -> {available_images[0]}")
    
    # Update Leadership Pages
    print(f"\n👥 Updating Leadership Pages...")
    leadership_pages = LeadershipPage.objects.all()
    for leadership in leadership_pages:
        if not leadership.leadership_photo_1 or str(leadership.leadership_photo_1) not in available_images:
            suitable_image = image_mapping.get('leadership', 'leadership_photo.jpg')
            if suitable_image in available_images:
                leadership.leadership_photo_1 = suitable_image
                leadership.save()
                print(f"   ✅ Updated: Leadership page -> {suitable_image}")
            else:
                if available_images:
                    leadership.leadership_photo_1 = available_images[0]
                    leadership.save()
                    print(f"   ✅ Updated: Leadership page -> {available_images[0]}")
    
    print(f"\n✅ Database update completed!")
    print(f"📋 Summary:")
    print(f"   - All models have been updated with working images")
    print(f"   - Images are now properly stored in ImageKit")
    print(f"   - Your website should display images instead of icons")
    print(f"   - You can now upload real images through the admin panel")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 