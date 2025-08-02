#!/usr/bin/env python
"""
Script to set up the main global church in GlobalSettings
Run this script to configure which church should be used as the fallback
when no local church is found for a user.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import GlobalSettings, Church

def setup_main_global_church():
    """Set up the main global church in GlobalSettings"""
    
    # Get or create GlobalSettings
    try:
        global_settings = GlobalSettings.objects.first()
        if not global_settings:
            print("Creating new GlobalSettings...")
            global_settings = GlobalSettings.objects.create()
    except Exception as e:
        print(f"Error getting GlobalSettings: {e}")
        return
    
    # Get all active and approved churches
    churches = Church.objects.filter(is_active=True, is_approved=True)
    
    if not churches.exists():
        print("❌ No active and approved churches found!")
        print("Please create and approve at least one church first.")
        return
    
    print(f"✅ Found {churches.count()} active and approved churches:")
    print()
    
    # Display churches with numbers
    for i, church in enumerate(churches, 1):
        print(f"{i}. {church.name}")
        print(f"   Location: {church.city}, {church.country}")
        print(f"   Pastor: {church.pastor_name}")
        print()
    
    # Ask user to select the main global church
    while True:
        try:
            choice = input(f"Enter the number (1-{churches.count()}) of the church to set as main global church: ")
            choice_num = int(choice)
            
            if 1 <= choice_num <= churches.count():
                selected_church = churches[choice_num - 1]
                break
            else:
                print(f"Please enter a number between 1 and {churches.count()}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nSetup cancelled.")
            return
    
    # Set the main global church
    global_settings.main_global_church = selected_church
    global_settings.save()
    
    print()
    print("✅ Successfully set up main global church!")
    print(f"   Main Global Church: {selected_church.name}")
    print(f"   Location: {selected_church.city}, {selected_church.country}")
    print()
    print("Now when users visit the website and no local church is found for their location,")
    print("they will be automatically redirected to this main global church.")
    print()
    print("You can change this setting anytime in the Django admin under Global Settings.")

if __name__ == "__main__":
    print("🌍 Setting up Main Global Church")
    print("=" * 40)
    print()
    setup_main_global_church() 