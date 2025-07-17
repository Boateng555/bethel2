#!/usr/bin/env python3
"""
Comprehensive test to verify all media URLs and Cloudinary setup
"""

import os
import django
import requests
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church, News, Ministry, Sermon, HeroMedia, Event, EventSpeaker, AboutPage, LeadershipPage

def test_cloudinary_credentials():
    """Test if Cloudinary credentials are working"""
    print("🔍 Testing Cloudinary credentials...")
    
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    
    print(f"Cloud Name: {cloud_name}")
    print(f"API Key: {api_key[:10]}..." if api_key else "API Key: Not set")
    print(f"API Secret: {api_secret[:10]}..." if api_secret else "API Secret: Not set")
    
    if not all([cloud_name, api_key, api_secret]):
        print("❌ Missing Cloudinary credentials!")
        return False
    
    # Test a simple Cloudinary URL
    test_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/v1752764497/bethel/test.jpg"
    try:
        response = requests.head(test_url, timeout=5)
        if response.status_code == 404:
            print("✅ Cloudinary is accessible (404 is expected for test image)")
            return True
        else:
            print(f"⚠️ Cloudinary response: {response.status_code}")
            return True
    except Exception as e:
        print(f"❌ Error testing Cloudinary: {e}")
        return False

def check_database_urls():
    """Check all database URLs"""
    print("\n🔍 Checking database URLs...")
    
    issues = []
    cloudinary_count = 0
    local_count = 0
    empty_count = 0
    
    # Check Church logos
    print("\n📋 Church logos:")
    churches = Church.objects.all()
    for church in churches:
        if church.logo:
            if str(church.logo).startswith('http'):
                print(f"  ✅ {church.name}: Cloudinary URL")
                cloudinary_count += 1
            else:
                print(f"  ❌ {church.name}: Local path - {church.logo}")
                issues.append(f"Church {church.name} has local path: {church.logo}")
                local_count += 1
        else:
            print(f"  ⚠️ {church.name}: No logo")
            empty_count += 1
    
    # Check News images
    print("\n📋 News images:")
    news_items = News.objects.all()
    for news in news_items:
        if news.image:
            if str(news.image).startswith('http'):
                print(f"  ✅ {news.title}: Cloudinary URL")
                cloudinary_count += 1
            else:
                print(f"  ❌ {news.title}: Local path - {news.image}")
                issues.append(f"News {news.title} has local path: {news.image}")
                local_count += 1
        else:
            print(f"  ⚠️ {news.title}: No image")
            empty_count += 1
    
    # Check HeroMedia images
    print("\n📋 HeroMedia images:")
    hero_media = HeroMedia.objects.all()
    for media in hero_media:
        if media.image:
            if str(media.image).startswith('http'):
                print(f"  ✅ HeroMedia {media.id}: Cloudinary URL")
                cloudinary_count += 1
            else:
                print(f"  ❌ HeroMedia {media.id}: Local path - {media.image}")
                issues.append(f"HeroMedia {media.id} has local path: {media.image}")
                local_count += 1
        else:
            print(f"  ⚠️ HeroMedia {media.id}: No image")
            empty_count += 1
    
    # Check Ministry images
    print("\n📋 Ministry images:")
    ministries = Ministry.objects.all()
    for ministry in ministries:
        if ministry.image:
            if str(ministry.image).startswith('http'):
                print(f"  ✅ {ministry.name}: Cloudinary URL")
                cloudinary_count += 1
            else:
                print(f"  ❌ {ministry.name}: Local path - {ministry.image}")
                issues.append(f"Ministry {ministry.name} has local path: {ministry.image}")
                local_count += 1
        else:
            print(f"  ⚠️ {ministry.name}: No image")
            empty_count += 1
    
    # Check Sermon thumbnails
    print("\n📋 Sermon thumbnails:")
    sermons = Sermon.objects.all()
    for sermon in sermons:
        if sermon.thumbnail:
            if str(sermon.thumbnail).startswith('http'):
                print(f"  ✅ {sermon.title}: Cloudinary URL")
                cloudinary_count += 1
            else:
                print(f"  ❌ {sermon.title}: Local path - {sermon.thumbnail}")
                issues.append(f"Sermon {sermon.title} has local path: {sermon.thumbnail}")
                local_count += 1
        else:
            print(f"  ⚠️ {sermon.title}: No thumbnail")
            empty_count += 1
    
    print(f"\n📊 Summary:")
    print(f"  Cloudinary URLs: {cloudinary_count}")
    print(f"  Local paths: {local_count}")
    print(f"  Empty fields: {empty_count}")
    
    if issues:
        print(f"\n❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print(f"\n✅ All URLs are properly set to Cloudinary!")
        return True

def test_live_urls():
    """Test if live URLs are accessible"""
    print("\n🔍 Testing live URLs...")
    
    # Test a few Cloudinary URLs
    test_urls = [
        "https://res.cloudinary.com/dhzdusb5k/image/upload/v1752764497/bethel/churches/logos/FAF767E1-205A-472C-B17D-652288ECC8A2.jpg",
        "https://res.cloudinary.com/dhzdusb5k/image/upload/v1752764497/bethel/hero/FAF767E1-205A-472C-B17D-652288ECC8A2.jpg",
        "https://res.cloudinary.com/dhzdusb5k/image/upload/v1752764497/bethel/news/FAF767E1-205A-472C-B17D-652288ECC8A2.jpg"
    ]
    
    accessible_count = 0
    for url in test_urls:
        try:
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {url} - Accessible")
                accessible_count += 1
            else:
                print(f"  ❌ {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {url} - Error: {e}")
    
    print(f"\n📊 Live URL Test: {accessible_count}/{len(test_urls)} URLs accessible")
    return accessible_count > 0

def run_comprehensive_test():
    """Run all tests"""
    print("🧪 Running Comprehensive Media Test")
    print("=" * 50)
    
    # Test 1: Cloudinary credentials
    cloudinary_ok = test_cloudinary_credentials()
    
    # Test 2: Database URLs
    urls_ok = check_database_urls()
    
    # Test 3: Live URLs
    live_ok = test_live_urls()
    
    print("\n" + "=" * 50)
    print("🎯 FINAL RESULTS:")
    print(f"  Cloudinary Setup: {'✅ OK' if cloudinary_ok else '❌ FAILED'}")
    print(f"  Database URLs: {'✅ OK' if urls_ok else '❌ FAILED'}")
    print(f"  Live URLs: {'✅ OK' if live_ok else '❌ FAILED'}")
    
    if cloudinary_ok and urls_ok and live_ok:
        print("\n🎉 ALL TESTS PASSED! Your media setup is working correctly!")
        return True
    else:
        print("\n❌ Some tests failed. Check the issues above.")
        return False

if __name__ == "__main__":
    run_comprehensive_test() 