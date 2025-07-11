#!/usr/bin/env python
"""
Test script to verify that all default content is created when a new church is set up.
Run this script to test the setup_default_functionality method.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church, Event, Ministry, News, Sermon, DonationMethod, Hero, LocalAboutPage, LocalLeadershipPage, EventSpeaker, EventScheduleItem, EventHighlight, EventRegistration
from django.contrib.auth.models import User

def test_church_setup():
    """Test that all default content is created for a new church"""
    
    # Create a test church
    test_church = Church.objects.create(
        name='Test Church',
        slug='test-church',
        address='123 Test Street',
        city='Test City',
        country='Test Country',
        pastor_name='Test Pastor',
        description='A test church for verification'
    )
    
    print(f"✅ Created test church: {test_church.name}")
    
    # Check that all default content was created
    checks = [
        ('Events', Event.objects.filter(church=test_church).count(), 2),
        ('Ministries', Ministry.objects.filter(church=test_church).count(), 7),
        ('Donation Methods', DonationMethod.objects.filter(church=test_church).count(), 3),
        ('News', News.objects.filter(church=test_church).count(), 1),
        ('Sermons', Sermon.objects.filter(church=test_church).count(), 1),
        ('Hero Sections', Hero.objects.filter(church=test_church).count(), 1),
        ('About Page', LocalAboutPage.objects.filter(church=test_church).count(), 1),
        ('Leadership Page', LocalLeadershipPage.objects.filter(church=test_church).count(), 1),
        ('Event Speakers', EventSpeaker.objects.filter(event__church=test_church).count(), 2),
        ('Event Schedule Items', EventScheduleItem.objects.filter(event__church=test_church).count(), 8),
        ('Event Highlights', EventHighlight.objects.filter(church=test_church).count(), 2),
        ('Event Registrations', EventRegistration.objects.filter(church=test_church).count(), 2),
    ]
    
    print("\n📊 Checking default content creation:")
    all_passed = True
    
    for name, actual, expected in checks:
        status = "✅" if actual == expected else "❌"
        print(f"{status} {name}: {actual}/{expected}")
        if actual != expected:
            all_passed = False
    
    # Check specific features
    print("\n🔍 Checking specific features:")
    
    # Check QR code is enabled by default
    events_with_qr = Event.objects.filter(church=test_church, show_qr_code=True).count()
    print(f"{'✅' if events_with_qr == 2 else '❌'} QR Code enabled by default: {events_with_qr}/2 events")
    
    # Check events are public
    public_events = Event.objects.filter(church=test_church, is_public=True).count()
    print(f"{'✅' if public_events == 2 else '❌'} Events are public by default: {public_events}/2 events")
    
    # Check ministries are active and public
    active_ministries = Ministry.objects.filter(church=test_church, is_active=True, is_public=True).count()
    print(f"{'✅' if active_ministries == 7 else '❌'} Ministries are active and public: {active_ministries}/7 ministries")
    
    # Check donation methods are active
    active_donations = DonationMethod.objects.filter(church=test_church, is_active=True).count()
    print(f"{'✅' if active_donations == 3 else '❌'} Donation methods are active: {active_donations}/3 methods")
    
    # Check hero is active
    active_heroes = Hero.objects.filter(church=test_church, is_active=True).count()
    print(f"{'✅' if active_heroes == 1 else '❌'} Hero section is active: {active_heroes}/1 hero")
    
    print(f"\n{'🎉 All tests passed!' if all_passed else '⚠️ Some tests failed!'}")
    
    # Clean up
    test_church.delete()
    print(f"\n🧹 Cleaned up test church: {test_church.name}")
    
    return all_passed

if __name__ == '__main__':
    print("🚀 Testing church default setup...")
    success = test_church_setup()
    sys.exit(0 if success else 1) 