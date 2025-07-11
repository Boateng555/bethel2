#!/usr/bin/env python
"""
Check local admin status for kwameb320@gmail.com
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church, ChurchAdmin, Event
from django.contrib.auth.models import User

def check_local_admin():
    """Check the local admin status for kwameb320@gmail.com"""
    
    # Find the user
    try:
        user = User.objects.get(email='kwameb320@gmail.com')
        print(f"✓ Found user: {user.username} ({user.email})")
        print(f"  - Is superuser: {user.is_superuser}")
        print(f"  - Is staff: {user.is_staff}")
    except User.DoesNotExist:
        print("✗ User with email kwameb320@gmail.com not found")
        return
    
    # Check ChurchAdmin record
    try:
        church_admin = ChurchAdmin.objects.get(user=user, is_active=True)
        print(f"✓ Found ChurchAdmin record:")
        print(f"  - Role: {church_admin.role}")
        print(f"  - Church: {church_admin.church}")
        print(f"  - Is active: {church_admin.is_active}")
        
        # Check if church exists
        if church_admin.church:
            print(f"  - Church exists: {church_admin.church.name}")
            
            # Check events for this church
            events = Event.objects.filter(church=church_admin.church)
            print(f"  - Events in this church: {events.count()}")
            for event in events:
                print(f"    * {event.title} (ID: {event.id})")
        else:
            print("  - No church assigned!")
            
    except ChurchAdmin.DoesNotExist:
        print("✗ No active ChurchAdmin record found for this user")
        return
    
    # Check all ChurchAdmin records for this user
    all_records = ChurchAdmin.objects.filter(user=user)
    print(f"\nAll ChurchAdmin records for {user.username}:")
    for record in all_records:
        print(f"  - Role: {record.role}, Church: {record.church}, Active: {record.is_active}")

if __name__ == "__main__":
    check_local_admin() 