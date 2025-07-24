#!/usr/bin/env python
"""
Script to help set up the global navigation logo
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import GlobalSettings

def setup_global_logo():
    """Set up the global navigation logo"""
    print("🎯 Global Navigation Logo Setup")
    print("=" * 40)
    
    # Get or create global settings
    settings = GlobalSettings.get_settings()
    print(f"✅ Global settings found: {settings.site_name}")
    
    if settings.global_nav_logo:
        print(f"✅ Global navigation logo already set: {settings.global_nav_logo}")
        print(f"   URL: {settings.get_global_nav_logo_url()}")
    else:
        print("❌ No global navigation logo set")
        print("\n📝 To set up the global navigation logo:")
        print("1. Go to Django Admin: http://127.0.0.1:8000/admin/")
        print("2. Navigate to: Core > Global Settings")
        print("3. Upload a logo in the 'Global Navigation Logo' field")
        print("4. Save the changes")
        print("\n🎨 Logo Requirements:")
        print("- Format: PNG, JPG, or JPEG")
        print("- Size: 200x200 pixels or larger")
        print("- Shape: Square or circular (will be displayed as circle)")
        print("- File size: Under 2MB")
    
    print("\n🌐 The global logo will appear on:")
    print("- Global site navigation (home, events, ministries, etc.)")
    print("- All church pages (unless overridden by individual church logos)")
    print("- All templates that use the navigation bar")

if __name__ == "__main__":
    setup_global_logo() 