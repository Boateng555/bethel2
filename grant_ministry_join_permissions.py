#!/usr/bin/env python
"""
Script to grant Ministry Join Request permissions to all existing local admins.
Run this script to ensure all current local admins have the necessary permissions.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import Permission
from core.models import ChurchAdmin

def grant_ministry_join_permissions():
    """Grant Ministry Join Request permissions to all existing local admins"""
    
    # Get all local admins
    local_admins = ChurchAdmin.objects.filter(role='local_admin', is_active=True)
    
    if not local_admins.exists():
        print("No active local admins found.")
        return
    
    # Get Ministry Join Request permissions
    ministry_join_permissions = []
    for action in ['add', 'change', 'delete', 'view']:
        try:
            perm = Permission.objects.get(codename=f"{action}_ministryjoinrequest")
            ministry_join_permissions.append(perm)
        except Permission.DoesNotExist:
            print(f"Warning: Permission '{action}_ministryjoinrequest' not found.")
    
    if not ministry_join_permissions:
        print("No Ministry Join Request permissions found. Make sure migrations are up to date.")
        return
    
    # Grant permissions to each local admin
    updated_count = 0
    for admin in local_admins:
        user = admin.user
        church_name = admin.church.name if admin.church else "No Church"
        
        # Check if user already has all the permissions
        existing_perms = set(user.user_permissions.filter(
            codename__in=[p.codename for p in ministry_join_permissions]
        ).values_list('codename', flat=True))
        
        needed_perms = [p for p in ministry_join_permissions if p.codename not in existing_perms]
        
        if needed_perms:
            user.user_permissions.add(*needed_perms)
            user.save()
            print(f"✓ Granted {len(needed_perms)} permissions to {user.username} ({church_name})")
            updated_count += 1
        else:
            print(f"✓ {user.username} ({church_name}) already has all Ministry Join Request permissions")
    
    print(f"\nSummary: Updated {updated_count} local admins with Ministry Join Request permissions.")
    print(f"Total local admins checked: {local_admins.count()}")

if __name__ == '__main__':
    print("Granting Ministry Join Request permissions to existing local admins...")
    print("=" * 60)
    grant_ministry_join_permissions()
    print("=" * 60)
    print("Done!") 