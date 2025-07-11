#!/usr/bin/env python
"""
Script to check and fix the website field issue in Church model.
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church

def check_and_fix_website_field():
    print("=== Checking Church website fields ===")
    
    churches = Church.objects.all()
    print(f"Total churches: {churches.count()}")
    
    for church in churches:
        print(f"Church: {church.name}")
        print(f"  Website: '{church.website}' (type: {type(church.website)})")
        
        # Check if website is empty string and fix it
        if church.website == "":
            print(f"  FIXING: Empty string detected, setting to None")
            church.website = None
            try:
                church.save()
                print(f"  SUCCESS: Fixed website field")
            except Exception as e:
                print(f"  ERROR: Could not save: {e}")
        elif church.website is None:
            print(f"  OK: Website is None")
        else:
            print(f"  OK: Website has value")
        print()

if __name__ == '__main__':
    check_and_fix_website_field() 