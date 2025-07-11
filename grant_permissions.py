#!/usr/bin/env python
"""
Grant all event-related permissions to all local admins.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User, Permission
from core.models import ChurchAdmin

# List of required permissions (codename format: <action>_<model>)
model_codenames = [
    'ministry', 'event', 'news', 'sermon', 'hero', 'donationmethod', 'localhero', 'eventheromedia'
]
actions = ['add', 'change', 'delete', 'view']
app_label = 'core'

def grant_permissions():
    for ca in ChurchAdmin.objects.filter(role='local_admin'):
        user = ca.user
        for codename in model_codenames:
            for action in actions:
                perm_codename = f"{action}_{codename}"
                try:
                    permission = Permission.objects.get(codename=perm_codename, content_type__app_label=app_label)
                    user.user_permissions.add(permission)
                except Permission.DoesNotExist:
                    print(f'Permission not found: {perm_codename}')
        user.save()
    print('✅ Permissions granted to all local admins.')

if __name__ == '__main__':
    grant_permissions()

"""
Script to force re-grant all hero and hero media permissions to all local admins
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import Permission
from core.models import ChurchAdmin, User

HERO_MODELS = [
    'hero', 'heromedia',
]
ACTIONS = ['add', 'change', 'delete', 'view']

def grant_permissions():
    local_admins = ChurchAdmin.objects.filter(role='local_admin', is_active=True)
    print(f"Found {local_admins.count()} local admins.")
    for ca in local_admins:
        user = ca.user
        for model in HERO_MODELS:
            for action in ACTIONS:
                codename = f"{action}_{model}"
                try:
                    perm = Permission.objects.get(codename=codename)
                    user.user_permissions.add(perm)
                except Permission.DoesNotExist:
                    print(f"Permission {codename} does not exist!")
        user.save()
        print(f"Granted hero/hero media permissions to {user.username}")
    print("All local admins have been updated.")

if __name__ == "__main__":
    grant_permissions() 