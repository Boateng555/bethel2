#!/usr/bin/env python
"""
Script to delete all churches and their local admins from the database.
This will remove all church data, including events, ministries, sermons, etc.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Church, ChurchAdmin, Event, Ministry, News, Sermon, Hero, DonationMethod, Convention, ConventionRegistration, ChurchApplication, Testimony, AboutPage, LeadershipPage, LocalLeadershipPage, LocalAboutPage, EventHighlight, EventSpeaker, EventScheduleItem, EventRegistration

def delete_all_churches():
    """Delete all churches and their associated data"""
    
    print("Starting deletion of all churches and local admins...")
    
    # Count items before deletion
    church_count = Church.objects.count()
    local_admin_count = ChurchAdmin.objects.count()
    
    print(f"Found {church_count} churches and {local_admin_count} local admins to delete.")
    
    if church_count == 0:
        print("No churches found to delete.")
        return
    
    # Confirm deletion
    confirm = input(f"\nThis will delete ALL {church_count} churches and {local_admin_count} local admins, including all their events, ministries, sermons, etc.\n\nType 'YES' to confirm: ")
    
    if confirm != 'YES':
        print("Deletion cancelled.")
        return
    
    print("\nDeleting churches and associated data...")
    
    # Delete all churches (this will cascade to related objects)
    deleted_churches = Church.objects.all()
    church_names = [church.name for church in deleted_churches]
    
    # Delete churches
    deleted_count = deleted_churches.delete()
    
    print(f"\nDeletion completed!")
    print(f"Deleted {deleted_count[0]} total objects")
    print(f"Deleted churches: {', '.join(church_names)}")
    
    # Verify deletion
    remaining_churches = Church.objects.count()
    remaining_admins = ChurchAdmin.objects.count()
    
    print(f"\nVerification:")
    print(f"Remaining churches: {remaining_churches}")
    print(f"Remaining local admins: {remaining_admins}")
    
    if remaining_churches == 0 and remaining_admins == 0:
        print("✅ All churches and local admins successfully deleted!")
    else:
        print("⚠️  Some items may still remain. Check manually.")

if __name__ == '__main__':
    delete_all_churches() 