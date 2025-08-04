#!/usr/bin/env python
"""
Script to refresh Django admin configuration and clear caching
"""

import os
import django
from django.core.cache import cache
from django.contrib.admin.sites import site

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def refresh_admin():
    """Refresh admin configuration and clear cache"""
    print("🔄 Refreshing Django Admin Configuration...")
    
    # Clear Django cache
    try:
        cache.clear()
        print("✅ Django cache cleared")
    except Exception as e:
        print(f"⚠️ Could not clear cache: {e}")
    
    # Force admin site to reload
    try:
        # Re-register the GlobalSettings admin
        from core.admin import GlobalSettingsAdmin
        from core.models import GlobalSettings
        
        # Unregister and re-register to force refresh
        if GlobalSettings in site._registry:
            site.unregister(GlobalSettings)
            print("✅ Unregistered GlobalSettings from admin")
        
        site.register(GlobalSettings, GlobalSettingsAdmin)
        print("✅ Re-registered GlobalSettings with updated admin")
        
    except Exception as e:
        print(f"⚠️ Could not refresh admin registration: {e}")
    
    # Check admin fieldsets
    try:
        admin_instance = GlobalSettingsAdmin(GlobalSettings, site)
        fieldsets = admin_instance.get_fieldsets(None)
        print(f"✅ Admin fieldsets loaded: {len(fieldsets)} sections")
        
        for name, options in fieldsets:
            print(f"  - {name}: {len(options['fields'])} fields")
            if name == 'Global Hero Settings':
                print(f"    Fields: {options['fields']}")
                
    except Exception as e:
        print(f"❌ Error checking admin fieldsets: {e}")
    
    print("\n🎯 Admin refresh completed!")
    print("📝 Please:")
    print("1. Clear your browser cache (Ctrl+F5)")
    print("2. Refresh the Global Settings page")
    print("3. Look for the 'Global Hero Settings' section")

if __name__ == "__main__":
    refresh_admin() 