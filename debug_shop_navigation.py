#!/usr/bin/env python
"""
Debug script to check shop navigation for each church
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church
from django.test import Client, override_settings

print("🔍 Debugging Shop Navigation")
print("=" * 50)

@override_settings(ALLOWED_HOSTS=['testserver', '127.0.0.1', 'localhost'])
def debug_shop_navigation():
    client = Client()
    churches = Church.objects.filter(is_active=True, is_approved=True)
    
    for church in churches:
        print(f"\n🏛️  Church: {church.name}")
        print(f"   ID: {church.id}")
        print(f"   Shop URL: {church.shop_url}")
        
        # Test church home page
        try:
            response = client.get(f'/church/{church.id}/', HTTP_HOST='testserver')
            print(f"   Home page status: {response.status_code}")
            
            if response.status_code == 200:
                # Check if shop link exists in the response
                content = str(response.content)
                
                if church.shop_url:
                    if church.shop_url in content:
                        print(f"   ✅ Shop link found: {church.shop_url}")
                    else:
                        print(f"   ❌ Shop link NOT found for: {church.shop_url}")
                else:
                    if '/shop' in content:
                        print("   ✅ Global shop link found")
                    else:
                        print("   ❌ Global shop link NOT found")
                
                # Check if this is a church site
                if 'is_church_site' in content or f'church/{church.id}' in content:
                    print("   ✅ Church site detected")
                else:
                    print("   ❌ Church site NOT detected")
                    
            else:
                print("   ❌ Home page failed to load")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test church about page
        try:
            response = client.get(f'/church/{church.id}/about/', HTTP_HOST='testserver')
            print(f"   About page status: {response.status_code}")
            
            if response.status_code == 200:
                content = str(response.content)
                
                if church.shop_url:
                    if church.shop_url in content:
                        print(f"   ✅ Shop link found: {church.shop_url}")
                    else:
                        print(f"   ❌ Shop link NOT found for: {church.shop_url}")
                else:
                    if '/shop' in content:
                        print("   ✅ Global shop link found")
                    else:
                        print("   ❌ Global shop link NOT found")
                        
            else:
                print("   ❌ About page failed to load")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

# Run the debug
debug_shop_navigation()

print(f"\n📋 Instructions:")
print(f"   1. Visit: http://127.0.0.1:8000/church/[CHURCH_ID]/about/")
print(f"   2. Replace [CHURCH_ID] with the church ID from above")
print(f"   3. Check if you see the 'Shop' link in the navigation")
print(f"   4. If no shop link appears, there's a template issue")
print(f"   5. If shop link appears but doesn't work, there's a URL issue") 