#!/usr/bin/env python
"""
Final check to verify all images are working
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

from core.models import News, Church, Ministry, Sermon
from imagekitio import ImageKit

print("🔍 Final Image Check - Verifying all images are working...")

# Initialize ImageKit
imagekit = ImageKit(
    private_key='private_Dnsrj2VW7uJakaeMaNYaav+P784=',
    public_key='public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=',
    url_endpoint='https://ik.imagekit.io/9buar9mbp'
)

# Get all files in ImageKit
try:
    list_files = imagekit.list_files()
    imagekit_files = [f.name for f in list_files.list]
    print(f"✅ Found {len(imagekit_files)} files in ImageKit")
    
    working_count = 0
    total_count = 0
    
    # Check News items
    print("\n📰 NEWS ITEMS:")
    news_items = News.objects.all()
    for news in news_items:
        total_count += 1
        print(f"   📰 {news.title}")
        if news.image:
            if str(news.image) in imagekit_files:
                print(f"      ✅ Working: {news.image}")
                print(f"      🌐 URL: {news.image.url}")
                working_count += 1
            else:
                print(f"      ❌ Still broken: {news.image}")
        else:
            print(f"      📝 No image")
    
    # Check Church items
    print("\n⛪ CHURCH ITEMS:")
    church_items = Church.objects.all()
    for church in church_items:
        total_count += 1
        print(f"   ⛪ {church.name}")
        if church.logo:
            if str(church.logo) in imagekit_files:
                print(f"      ✅ Working: {church.logo}")
                print(f"      🌐 URL: {church.logo.url}")
                working_count += 1
            else:
                print(f"      ❌ Still broken: {church.logo}")
        else:
            print(f"      📝 No logo")
    
    # Check Ministry items
    print("\n🙏 MINISTRY ITEMS:")
    ministry_items = Ministry.objects.all()
    for ministry in ministry_items:
        total_count += 1
        print(f"   🙏 {ministry.name}")
        if ministry.image:
            if str(ministry.image) in imagekit_files:
                print(f"      ✅ Working: {ministry.image}")
                print(f"      🌐 URL: {ministry.image.url}")
                working_count += 1
            else:
                print(f"      ❌ Still broken: {ministry.image}")
        else:
            print(f"      📝 No image")
    
    # Check Sermon items
    print("\n📖 SERMON ITEMS:")
    sermon_items = Sermon.objects.all()
    for sermon in sermon_items:
        total_count += 1
        print(f"   📖 {sermon.title}")
        if sermon.thumbnail:
            if str(sermon.thumbnail) in imagekit_files:
                print(f"      ✅ Working: {sermon.thumbnail}")
                print(f"      🌐 URL: {sermon.thumbnail.url}")
                working_count += 1
            else:
                print(f"      ❌ Still broken: {sermon.thumbnail}")
        else:
            print(f"      📝 No thumbnail")
    
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   ✅ Working images: {working_count}")
    print(f"   📝 Items with images: {total_count}")
    print(f"   🎯 Success rate: {(working_count/total_count*100):.1f}%" if total_count > 0 else "   🎯 No items with images")
    
    if working_count == total_count:
        print(f"\n🎉 SUCCESS! All images are working correctly!")
        print(f"🌐 Your website should display all images properly now.")
    else:
        print(f"\n⚠️  Some images still need attention.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n📋 Next steps:")
print("1. Restart your Django application: sudo systemctl restart bethel")
print("2. Visit your website to see all the fixed images")
print("3. All images should now display correctly!") 