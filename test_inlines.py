#!/usr/bin/env python
"""
Test script to verify Event admin inlines are working
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib import admin
from core.models import Event, Church

def test_event_admin():
    """Test that Event admin has the correct inlines"""
    
    # Check if Event is registered
    if Event not in admin.site._registry:
        print("❌ Event is not registered in admin")
        return
    
    admin_class = admin.site._registry[Event]
    print(f"✅ Event is registered with: {admin_class.__class__.__name__}")
    
    # Check inlines
    if hasattr(admin_class, 'inlines'):
        print(f"✅ Inlines found: {len(admin_class.inlines)}")
        for inline in admin_class.inlines:
            print(f"   - {inline.__name__}: {inline.model.__name__}")
    else:
        print("❌ No inlines found")
    
    # Check if it's using LocalAdminMixin
    if 'LocalAdminMixin' in str(admin_class.__class__.__bases__):
        print("✅ Using LocalAdminMixin")
    else:
        print("❌ Not using LocalAdminMixin")
    
    # Test with a real event
    try:
        church = Church.objects.first()
        if church:
            event = Event.objects.filter(church=church).first()
            if event:
                print(f"✅ Found test event: {event.title} (ID: {event.id})")
                print(f"   - Church: {event.church.name}")
                print(f"   - Saved: {event.pk is not None}")
            else:
                print("❌ No events found for testing")
        else:
            print("❌ No churches found for testing")
    except Exception as e:
        print(f"❌ Error testing with real event: {e}")

if __name__ == "__main__":
    test_event_admin() 