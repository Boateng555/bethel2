#!/usr/bin/env python
"""
Test script to check shop URLs and navigation logic
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church

print("🔍 Testing Shop Navigation Logic")
print("=" * 50)

# Get all churches
churches = Church.objects.all()

for church in churches:
    print(f"\n🏛️  Church: {church.name}")
    print(f"   ID: {church.id}")
    print(f"   Shop URL: {church.shop_url}")
    print(f"   Is Active: {church.is_active}")
    print(f"   Is Approved: {church.is_approved}")
    
    # Test navigation logic
    if church.shop_url:
        print(f"   ✅ Shop will show: {church.shop_url} (opens in new tab)")
    else:
        print(f"   ⚠️  Shop will show: /shop (global shop page)")
    
    # Test if church would show in navigation
    if church.is_active and church.is_approved:
        print(f"   ✅ Church will appear in navigation")
    else:
        print(f"   ❌ Church will NOT appear in navigation (inactive or not approved)")

print(f"\n📊 Summary:")
print(f"   Total churches: {churches.count()}")
print(f"   Churches with shop URLs: {churches.filter(shop_url__isnull=False).count()}")
print(f"   Active and approved churches: {churches.filter(is_active=True, is_approved=True).count()}") 