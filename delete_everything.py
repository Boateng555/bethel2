#!/usr/bin/env python
"""
Script to delete ALL data from all core app models and all users except superusers.
This will reset the database to a clean state for testing new church creation.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Church, ChurchAdmin, Event, Ministry, News, Sermon, Hero, DonationMethod, Convention, ConventionRegistration, ChurchApplication, Testimony, AboutPage, LeadershipPage, LocalLeadershipPage, LocalAboutPage, EventHighlight, EventSpeaker, EventScheduleItem, EventRegistration

def delete_everything():
    print("Deleting ALL data from all core app models and all users except superusers...")
    
    # Delete all core app data
    for model in [
        EventRegistration, EventScheduleItem, EventSpeaker, EventHighlight, LocalLeadershipPage, LocalAboutPage, LeadershipPage, AboutPage, Testimony, ChurchApplication, ConventionRegistration, Convention, DonationMethod, Hero, Sermon, News, Ministry, Event, ChurchAdmin, Church
    ]:
        model.objects.all().delete()
    
    # Delete all users except superusers
    User.objects.filter(is_superuser=False).delete()
    
    print("All data deleted. Database is now clean.")

if __name__ == '__main__':
    delete_everything() 