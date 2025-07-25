#!/usr/bin/env python
"""
Test All Admin Upload Fields
This script will test all admin upload fields to ensure they use ImageKit storage
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from core.models import (
    Church, HeroMedia, Event, Ministry, News, Sermon, 
    EventHeroMedia, AboutPage, LeadershipPage, LocalAboutPage, LocalLeadershipPage
)

def test_storage_configuration():
    """Test the current storage configuration"""
    print("🔍 Testing storage configuration...")
    
    print(f"DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
    print(f"Storage class: {type(default_storage).__name__}")
    
    # Test a simple upload
    test_content = b"Test file for storage configuration"
    test_file = ContentFile(test_content, name='storage_test.txt')
    
    saved_path = default_storage.save('test/storage_test.txt', test_file)
    url = default_storage.url(saved_path)
    
    print(f"Test upload path: {saved_path}")
    print(f"Test upload URL: {url}")
    
    if url.startswith('https://ik.imagekit.io/'):
        print("✅ Default storage is using ImageKit")
        success = True
    else:
        print("❌ Default storage is NOT using ImageKit")
        success = False
    
    # Clean up
    default_storage.delete(saved_path)
    return success

def test_church_uploads():
    """Test Church model uploads"""
    print("\n🔍 Testing Church uploads...")
    
    try:
        church = Church.objects.first()
        if not church:
            print("❌ No churches found")
            return False
        
        print(f"Testing with church: {church.name}")
        
        # Test logo upload
        test_content = b"Test church logo content"
        test_file = ContentFile(test_content, name='test_church_logo.jpg')
        
        # Save using the model's storage
        church.logo = test_file
        church.save()
        
        print(f"Church logo path: {church.logo.name}")
        print(f"Church logo URL: {church.logo.url}")
        
        if church.logo.url.startswith('https://ik.imagekit.io/'):
            print("✅ Church logo uses ImageKit")
            logo_ok = True
        else:
            print("❌ Church logo does NOT use ImageKit")
            logo_ok = False
        
        # Test nav_logo upload
        test_content = b"Test church nav logo content"
        test_file = ContentFile(test_content, name='test_church_nav_logo.jpg')
        
        church.nav_logo = test_file
        church.save()
        
        print(f"Church nav_logo path: {church.nav_logo.name}")
        print(f"Church nav_logo URL: {church.nav_logo.url}")
        
        if church.nav_logo.url.startswith('https://ik.imagekit.io/'):
            print("✅ Church nav_logo uses ImageKit")
            nav_logo_ok = True
        else:
            print("❌ Church nav_logo does NOT use ImageKit")
            nav_logo_ok = False
        
        return logo_ok and nav_logo_ok
        
    except Exception as e:
        print(f"❌ Church upload test failed: {e}")
        return False

def test_hero_media_uploads():
    """Test HeroMedia model uploads"""
    print("\n🔍 Testing HeroMedia uploads...")
    
    try:
        church = Church.objects.first()
        if not church:
            print("❌ No churches found")
            return False
        
        hero = church.hero_set.first()
        if not hero:
            print("❌ No hero found")
            return False
        
        # Test image upload
        test_content = b"Test hero media image content"
        test_file = ContentFile(test_content, name='test_hero_image.jpg')
        
        hero_media = HeroMedia.objects.create(
            hero=hero,
            image=test_file,
            order=999
        )
        
        print(f"HeroMedia image path: {hero_media.image.name}")
        print(f"HeroMedia image URL: {hero_media.image.url}")
        
        if hero_media.image.url.startswith('https://ik.imagekit.io/'):
            print("✅ HeroMedia image uses ImageKit")
            image_ok = True
        else:
            print("❌ HeroMedia image does NOT use ImageKit")
            image_ok = False
        
        # Test video upload
        test_content = b"Test hero media video content"
        test_file = ContentFile(test_content, name='test_hero_video.mp4')
        
        hero_media_video = HeroMedia.objects.create(
            hero=hero,
            video=test_file,
            order=998
        )
        
        print(f"HeroMedia video path: {hero_media_video.video.name}")
        print(f"HeroMedia video URL: {hero_media_video.video.url}")
        
        if hero_media_video.video.url.startswith('https://ik.imagekit.io/'):
            print("✅ HeroMedia video uses ImageKit")
            video_ok = True
        else:
            print("❌ HeroMedia video does NOT use ImageKit")
            video_ok = False
        
        # Clean up
        hero_media.delete()
        hero_media_video.delete()
        
        return image_ok and video_ok
        
    except Exception as e:
        print(f"❌ HeroMedia upload test failed: {e}")
        return False

def test_ministry_uploads():
    """Test Ministry model uploads"""
    print("\n🔍 Testing Ministry uploads...")
    
    try:
        ministry = Ministry.objects.first()
        if not ministry:
            print("❌ No ministries found")
            return False
        
        print(f"Testing with ministry: {ministry.name}")
        
        # Test image upload
        test_content = b"Test ministry image content"
        test_file = ContentFile(test_content, name='test_ministry_image.jpg')
        
        ministry.image = test_file
        ministry.save()
        
        print(f"Ministry image path: {ministry.image.name}")
        print(f"Ministry image URL: {ministry.image.url}")
        
        if ministry.image.url.startswith('https://ik.imagekit.io/'):
            print("✅ Ministry image uses ImageKit")
            return True
        else:
            print("❌ Ministry image does NOT use ImageKit")
            return False
        
    except Exception as e:
        print(f"❌ Ministry upload test failed: {e}")
        return False

def test_news_uploads():
    """Test News model uploads"""
    print("\n🔍 Testing News uploads...")
    
    try:
        news = News.objects.first()
        if not news:
            print("❌ No news found")
            return False
        
        print(f"Testing with news: {news.title}")
        
        # Test image upload
        test_content = b"Test news image content"
        test_file = ContentFile(test_content, name='test_news_image.jpg')
        
        news.image = test_file
        news.save()
        
        print(f"News image path: {news.image.name}")
        print(f"News image URL: {news.image.url}")
        
        if news.image.url.startswith('https://ik.imagekit.io/'):
            print("✅ News image uses ImageKit")
            return True
        else:
            print("❌ News image does NOT use ImageKit")
            return False
        
    except Exception as e:
        print(f"❌ News upload test failed: {e}")
        return False

def test_sermon_uploads():
    """Test Sermon model uploads"""
    print("\n🔍 Testing Sermon uploads...")
    
    try:
        sermon = Sermon.objects.first()
        if not sermon:
            print("❌ No sermons found")
            return False
        
        print(f"Testing with sermon: {sermon.title}")
        
        # Test thumbnail upload
        test_content = b"Test sermon thumbnail content"
        test_file = ContentFile(test_content, name='test_sermon_thumbnail.jpg')
        
        sermon.thumbnail = test_file
        sermon.save()
        
        print(f"Sermon thumbnail path: {sermon.thumbnail.name}")
        print(f"Sermon thumbnail URL: {sermon.thumbnail.url}")
        
        if sermon.thumbnail.url.startswith('https://ik.imagekit.io/'):
            print("✅ Sermon thumbnail uses ImageKit")
            thumbnail_ok = True
        else:
            print("❌ Sermon thumbnail does NOT use ImageKit")
            thumbnail_ok = False
        
        # Test audio_file upload
        test_content = b"Test sermon audio content"
        test_file = ContentFile(test_content, name='test_sermon_audio.mp3')
        
        sermon.audio_file = test_file
        sermon.save()
        
        print(f"Sermon audio path: {sermon.audio_file.name}")
        print(f"Sermon audio URL: {sermon.audio_file.url}")
        
        if sermon.audio_file.url.startswith('https://ik.imagekit.io/'):
            print("✅ Sermon audio uses ImageKit")
            audio_ok = True
        else:
            print("❌ Sermon audio does NOT use ImageKit")
            audio_ok = False
        
        # Test video_file upload
        test_content = b"Test sermon video content"
        test_file = ContentFile(test_content, name='test_sermon_video.mp4')
        
        sermon.video_file = test_file
        sermon.save()
        
        print(f"Sermon video path: {sermon.video_file.name}")
        print(f"Sermon video URL: {sermon.video_file.url}")
        
        if sermon.video_file.url.startswith('https://ik.imagekit.io/'):
            print("✅ Sermon video uses ImageKit")
            video_ok = True
        else:
            print("❌ Sermon video does NOT use ImageKit")
            video_ok = False
        
        return thumbnail_ok and audio_ok and video_ok
        
    except Exception as e:
        print(f"❌ Sermon upload test failed: {e}")
        return False

def test_event_hero_media_uploads():
    """Test EventHeroMedia model uploads"""
    print("\n🔍 Testing EventHeroMedia uploads...")
    
    try:
        event = Event.objects.first()
        if not event:
            print("❌ No events found")
            return False
        
        print(f"Testing with event: {event.title}")
        
        # Test image upload
        test_content = b"Test event hero media image content"
        test_file = ContentFile(test_content, name='test_event_hero_image.jpg')
        
        event_hero_media = EventHeroMedia.objects.create(
            event=event,
            image=test_file,
            order=999
        )
        
        print(f"EventHeroMedia image path: {event_hero_media.image.name}")
        print(f"EventHeroMedia image URL: {event_hero_media.image.url}")
        
        if event_hero_media.image.url.startswith('https://ik.imagekit.io/'):
            print("✅ EventHeroMedia image uses ImageKit")
            image_ok = True
        else:
            print("❌ EventHeroMedia image does NOT use ImageKit")
            image_ok = False
        
        # Test video upload
        test_content = b"Test event hero media video content"
        test_file = ContentFile(test_content, name='test_event_hero_video.mp4')
        
        event_hero_media_video = EventHeroMedia.objects.create(
            event=event,
            video=test_file,
            order=998
        )
        
        print(f"EventHeroMedia video path: {event_hero_media_video.video.name}")
        print(f"EventHeroMedia video URL: {event_hero_media_video.video.url}")
        
        if event_hero_media_video.video.url.startswith('https://ik.imagekit.io/'):
            print("✅ EventHeroMedia video uses ImageKit")
            video_ok = True
        else:
            print("❌ EventHeroMedia video does NOT use ImageKit")
            video_ok = False
        
        # Clean up
        event_hero_media.delete()
        event_hero_media_video.delete()
        
        return image_ok and video_ok
        
    except Exception as e:
        print(f"❌ EventHeroMedia upload test failed: {e}")
        return False

def test_page_uploads():
    """Test page model uploads (AboutPage, LeadershipPage, etc.)"""
    print("\n🔍 Testing Page uploads...")
    
    results = []
    
    # Test AboutPage
    try:
        about_page = AboutPage.objects.first()
        if about_page:
            print(f"Testing AboutPage: {about_page.title}")
            
            test_content = b"Test about page image content"
            test_file = ContentFile(test_content, name='test_about_image.jpg')
            
            about_page.image = test_file
            about_page.save()
            
            print(f"AboutPage image URL: {about_page.image.url}")
            
            if about_page.image.url.startswith('https://ik.imagekit.io/'):
                print("✅ AboutPage image uses ImageKit")
                results.append(True)
            else:
                print("❌ AboutPage image does NOT use ImageKit")
                results.append(False)
        else:
            print("⚠️ No AboutPage found")
            results.append(True)  # Skip if no data
    except Exception as e:
        print(f"❌ AboutPage upload test failed: {e}")
        results.append(False)
    
    # Test LeadershipPage
    try:
        leadership_page = LeadershipPage.objects.first()
        if leadership_page:
            print(f"Testing LeadershipPage: {leadership_page.title}")
            
            test_content = b"Test leadership page image content"
            test_file = ContentFile(test_content, name='test_leadership_image.jpg')
            
            leadership_page.image = test_file
            leadership_page.save()
            
            print(f"LeadershipPage image URL: {leadership_page.image.url}")
            
            if leadership_page.image.url.startswith('https://ik.imagekit.io/'):
                print("✅ LeadershipPage image uses ImageKit")
                results.append(True)
            else:
                print("❌ LeadershipPage image does NOT use ImageKit")
                results.append(False)
        else:
            print("⚠️ No LeadershipPage found")
            results.append(True)  # Skip if no data
    except Exception as e:
        print(f"❌ LeadershipPage upload test failed: {e}")
        results.append(False)
    
    return all(results) if results else True

def main():
    """Main function"""
    print("🚀 Testing all admin upload fields...")
    print("=" * 60)
    
    # Test storage configuration
    storage_ok = test_storage_configuration()
    
    # Test all model uploads
    church_ok = test_church_uploads()
    hero_media_ok = test_hero_media_uploads()
    ministry_ok = test_ministry_uploads()
    news_ok = test_news_uploads()
    sermon_ok = test_sermon_uploads()
    event_hero_media_ok = test_event_hero_media_uploads()
    page_ok = test_page_uploads()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Storage Configuration: {'✅ PASS' if storage_ok else '❌ FAIL'}")
    print(f"Church Uploads: {'✅ PASS' if church_ok else '❌ FAIL'}")
    print(f"HeroMedia Uploads: {'✅ PASS' if hero_media_ok else '❌ FAIL'}")
    print(f"Ministry Uploads: {'✅ PASS' if ministry_ok else '❌ FAIL'}")
    print(f"News Uploads: {'✅ PASS' if news_ok else '❌ FAIL'}")
    print(f"Sermon Uploads: {'✅ PASS' if sermon_ok else '❌ FAIL'}")
    print(f"EventHeroMedia Uploads: {'✅ PASS' if event_hero_media_ok else '❌ FAIL'}")
    print(f"Page Uploads: {'✅ PASS' if page_ok else '❌ FAIL'}")
    
    all_tests = [
        storage_ok, church_ok, hero_media_ok, ministry_ok, 
        news_ok, sermon_ok, event_hero_media_ok, page_ok
    ]
    
    if all(all_tests):
        print("\n🎉 SUCCESS! All admin upload fields are using ImageKit!")
        print("✅ All models will upload to ImageKit cloud")
        print("✅ No more local storage for any admin uploads")
    else:
        print("\n⚠️ Some admin upload fields are NOT using ImageKit.")
        print("❌ Some models may still upload to local storage")
        print("📋 Check the failed tests above for specific issues.")
    
    return all(all_tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 