#!/usr/bin/env python3
"""
Comprehensive test script to check all images across all models
"""

import os
import django
import requests
from PIL import Image
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import (
    HeroMedia, Hero, Church, Ministry, News, Sermon, 
    EventHighlight, LocalLeadershipPage, LocalAboutPage, 
    EventHeroMedia, Event
)

def test_all_images():
    """Test all images across all models"""
    print("🔍 Testing ALL Images Across All Models")
    print("=" * 60)
    
    total_images = 0
    working_images = 0
    broken_images = 0
    
    # Test HeroMedia images
    print("\n📸 Testing HeroMedia Images")
    print("-" * 30)
    hero_media_list = HeroMedia.objects.all()
    for media in hero_media_list:
        if media.image:
            total_images += 1
            result = test_single_image(f"HeroMedia ID {media.id}", media.get_image_url())
            if result:
                working_images += 1
            else:
                broken_images += 1
    
    # Test Church images
    print("\n🏛️ Testing Church Images")
    print("-" * 30)
    church_list = Church.objects.all()
    for church in church_list:
        if church.logo:
            total_images += 1
            result = test_single_image(f"Church {church.name} - Logo", church.get_logo_url())
            if result:
                working_images += 1
            else:
                broken_images += 1
        if church.banner_image:
            total_images += 1
            result = test_single_image(f"Church {church.name} - Banner", church.get_banner_url())
            if result:
                working_images += 1
            else:
                broken_images += 1
        if church.nav_logo:
            total_images += 1
            result = test_single_image(f"Church {church.name} - Nav Logo", church.get_nav_logo_url())
            if result:
                working_images += 1
            else:
                broken_images += 1
    
    # Test Ministry images
    print("\n⛪ Testing Ministry Images")
    print("-" * 30)
    ministry_list = Ministry.objects.all()
    for ministry in ministry_list:
        if ministry.image:
            total_images += 1
            result = test_single_image(f"Ministry {ministry.name}", ministry.get_image_url())
            if result:
                working_images += 1
            else:
                broken_images += 1
    
    # Test News images
    print("\n📰 Testing News Images")
    print("-" * 30)
    news_list = News.objects.all()
    for news in news_list:
        if news.image:
            total_images += 1
            result = test_single_image(f"News {news.title}", news.get_image_url())
            if result:
                working_images += 1
            else:
                broken_images += 1
    
    # Test Sermon images
    print("\n📖 Testing Sermon Images")
    print("-" * 30)
    sermon_list = Sermon.objects.all()
    for sermon in sermon_list:
        if sermon.thumbnail:
            total_images += 1
            result = test_single_image(f"Sermon {sermon.title}", sermon.get_thumbnail_url())
            if result:
                working_images += 1
            else:
                broken_images += 1
    
    # Test EventHighlight images
    print("\n🎉 Testing EventHighlight Images")
    print("-" * 30)
    event_highlight_list = EventHighlight.objects.all()
    for highlight in event_highlight_list:
        if highlight.image:
            total_images += 1
            result = test_single_image(f"EventHighlight {highlight.title}", highlight.get_image_url())
            if result:
                working_images += 1
            else:
                broken_images += 1
    
    # Test LocalLeadershipPage images
    print("\n👥 Testing LocalLeadershipPage Images")
    print("-" * 30)
    leadership_list = LocalLeadershipPage.objects.all()
    for leadership in leadership_list:
        for field_name in ['pastor_image', 'assistant_pastor_image', 'board_image', 'team_image', 
                          'leadership_photo_1', 'leadership_photo_2', 'leadership_photo_3']:
            image_field = getattr(leadership, field_name, None)
            if image_field:
                total_images += 1
                try:
                    url_method = getattr(leadership, f'get_{field_name}_url')
                    result = test_single_image(f"Leadership {leadership.church.name} - {field_name}", url_method())
                    if result:
                        working_images += 1
                    else:
                        broken_images += 1
                except AttributeError:
                    print(f"   ⚠️  Leadership {leadership.church.name} - {field_name}: No URL method")
                    broken_images += 1
    
    # Test LocalAboutPage images
    print("\nℹ️ Testing LocalAboutPage Images")
    print("-" * 30)
    about_list = LocalAboutPage.objects.all()
    for about in about_list:
        for field_name in ['logo', 'founder_image', 'extra_image', 'about_photo_1', 'about_photo_2', 'about_photo_3']:
            image_field = getattr(about, field_name, None)
            if image_field:
                total_images += 1
                try:
                    url_method = getattr(about, f'get_{field_name}_url')
                    result = test_single_image(f"About {about.church.name} - {field_name}", url_method())
                    if result:
                        working_images += 1
                    else:
                        broken_images += 1
                except AttributeError:
                    print(f"   ⚠️  About {about.church.name} - {field_name}: No URL method")
                    broken_images += 1
    
    # Test EventHeroMedia images
    print("\n🎬 Testing EventHeroMedia Images")
    print("-" * 30)
    event_hero_list = EventHeroMedia.objects.all()
    for event_hero in event_hero_list:
        if event_hero.image:
            total_images += 1
            result = test_single_image(f"EventHero {event_hero.event.title}", event_hero.get_image_url())
            if result:
                working_images += 1
            else:
                broken_images += 1
    
    # Test Hero images
    print("\n🦸 Testing Hero Images")
    print("-" * 30)
    hero_list = Hero.objects.all()
    for hero in hero_list:
        if hero.background_image:
            total_images += 1
            result = test_single_image(f"Hero {hero.title} - Background", hero.get_background_image_url())
            if result:
                working_images += 1
            else:
                broken_images += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total images tested: {total_images}")
    print(f"✅ Working images: {working_images}")
    print(f"❌ Broken images: {broken_images}")
    
    if broken_images == 0:
        print("\n🎉 ALL IMAGES ARE WORKING PERFECTLY!")
    else:
        print(f"\n⚠️  {broken_images} images need attention")
        print("Run the fix script to repair broken images")

def test_single_image(description, image_url):
    """Test a single image and return True if working, False if broken"""
    try:
        response = requests.head(image_url, timeout=10)
        if response.status_code == 200:
            print(f"   ✅ {description}: Working")
            return True
        else:
            print(f"   ❌ {description}: Broken (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ {description}: Error - {e}")
        return False

if __name__ == "__main__":
    test_all_images() 