#!/usr/bin/env python
"""
Create a test church, a local admin user, and a big event for testing.
"""

import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Church, ChurchAdmin, Event
from django.utils import timezone

# Create test church
def create_test_church():
    church, created = Church.objects.get_or_create(
        name='Test Church',
        defaults={
            'slug': 'test-church',
            'city': 'Test City',
            'country': 'Testland',
            'address': '123 Test St',
            'is_active': True,
            'is_approved': True,
            'is_featured': False,
        }
    )
    print(f"Church: {church.name} (created: {created})")
    
    # Create local admin user
    user, user_created = User.objects.get_or_create(
        username='testlocaladmin',
        defaults={
            'email': 'testlocaladmin@example.com',
            'is_staff': True,
            'is_active': True,
        }
    )
    if user_created:
        user.set_password('testpassword123')
        user.save()
    print(f"User: {user.username} (created: {user_created})")
    
    # Assign as local admin
    ca, ca_created = ChurchAdmin.objects.get_or_create(
        user=user,
        church=church,
        defaults={'role': 'local_admin', 'is_active': True}
    )
    print(f"ChurchAdmin: {ca.role} for {ca.church.name} (created: {ca_created})")
    
    # Create a big event
    start = timezone.now() + timedelta(days=7)
    end = start + timedelta(hours=3)
    event, event_created = Event.objects.get_or_create(
        church=church,
        title='Big Test Event',
        defaults={
            'description': 'This is a big test event.',
            'start_date': start,
            'end_date': end,
            'event_type': 'other',
            'is_big_event': True,
            'is_public': True,
            'is_featured': True,
        }
    )
    print(f"Event: {event.title} (created: {event_created})")
    
    print("Done! Test church, local admin, and big event created.")
    print("Login as testlocaladmin / testpassword123")

if __name__ == '__main__':
    create_test_church() 