#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import ChurchAdmin, Church
from django.contrib.auth.models import User

def check_local_admins():
    """Check what local admins exist in the system"""
    print("👥 CHECKING LOCAL ADMINS IN SYSTEM")
    print("=" * 50)
    
    # Get all local admins
    local_admins = ChurchAdmin.objects.filter(
        role='local_admin',
        is_active=True
    ).select_related('user', 'church')
    
    print(f"Found {local_admins.count()} active local admin(s):")
    
    for admin in local_admins:
        print(f"\n📋 Local Admin Details:")
        print(f"   Username: {admin.user.username}")
        print(f"   Email: {admin.user.email}")
        print(f"   First Name: {admin.user.first_name}")
        print(f"   Last Name: {admin.user.last_name}")
        print(f"   Church: {admin.church.name if admin.church else 'No church assigned'}")
        print(f"   Church ID: {admin.church.id if admin.church else 'N/A'}")
        print(f"   Role: {admin.role}")
        print(f"   Active: {admin.is_active}")
        print(f"   Created: {admin.created_at}")
    
    # Also check all users with email containing 'kwame'
    print(f"\n🔍 SEARCHING FOR KWAME USERS:")
    kwame_users = User.objects.filter(email__icontains='kwame')
    print(f"Found {kwame_users.count()} user(s) with 'kwame' in email:")
    
    for user in kwame_users:
        print(f"   - {user.username} ({user.email})")
        try:
            church_admin = ChurchAdmin.objects.get(user=user)
            print(f"     Role: {church_admin.role}, Church: {church_admin.church.name if church_admin.church else 'None'}")
        except ChurchAdmin.DoesNotExist:
            print(f"     No ChurchAdmin record found")
    
    # Check all users
    print(f"\n👤 ALL USERS IN SYSTEM:")
    all_users = User.objects.all()
    print(f"Total users: {all_users.count()}")
    
    for user in all_users:
        print(f"   - {user.username} ({user.email})")
        try:
            church_admin = ChurchAdmin.objects.get(user=user)
            print(f"     Role: {church_admin.role}, Church: {church_admin.church.name if church_admin.church else 'None'}")
        except ChurchAdmin.DoesNotExist:
            print(f"     No ChurchAdmin record found")

if __name__ == "__main__":
    check_local_admins() 