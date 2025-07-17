#!/usr/bin/env python
"""
Test shop URLs and navigation functionality
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church
from django.test import Client, override_settings

print("🔍 Testing Shop URLs and Navigation")
print("=" * 50)

# Create a test client with proper settings
@override_settings(ALLOWED_HOSTS=['testserver', '127.0.0.1', 'localhost'])
def test_shop_functionality():
    client = Client()
    
    # Test global shop URL
    print("\n🌐 Testing Global Shop URL:")
    try:
        response = client.get('/shop/', HTTP_HOST='testserver')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Global shop page loads successfully")
        else:
            print("   ❌ Global shop page failed to load")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test church-specific pages
    churches = Church.objects.filter(is_active=True, is_approved=True)

    for church in churches:
        print(f"\n🏛️  Testing Church: {church.name}")
        print(f"   Shop URL: {church.shop_url}")
        
        # Test church about page (which should show shop in navigation)
        try:
            response = client.get(f'/church/{church.id}/about/', HTTP_HOST='testserver')
            print(f"   About page status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Church about page loads successfully")
                
                # Check if shop link is in the response
                if church.shop_url:
                    if church.shop_url in str(response.content):
                        print(f"   ✅ Shop link found: {church.shop_url}")
                    else:
                        print(f"   ❌ Shop link NOT found in page")
                else:
                    if '/shop' in str(response.content):
                        print("   ✅ Global shop link found")
                    else:
                        print("   ❌ Global shop link NOT found")
            else:
                print("   ❌ Church about page failed to load")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    print(f"\n📊 Summary:")
    print(f"   Total active churches: {churches.count()}")
    print(f"   Churches with shop URLs: {churches.filter(shop_url__isnull=False).count()}")
    print(f"   Churches without shop URLs: {churches.filter(shop_url__isnull=True).count()}")

# Run the test
test_shop_functionality() 