#!/usr/bin/env python
"""
Test script to verify global logo context is working
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.context_processors import global_settings
from django.test import RequestFactory

def test_global_logo_context():
    """Test if the global logo context is working"""
    print("🧪 Testing Global Logo Context")
    print("=" * 40)
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/')
    
    # Get the context
    context = global_settings(request)
    
    print(f"Context keys: {list(context.keys())}")
    
    if 'global_settings' in context:
        settings = context['global_settings']
        if settings:
            print(f"✅ Global settings found: {settings.site_name}")
            if settings.global_nav_logo:
                print(f"✅ Global nav logo: {settings.global_nav_logo}")
                print(f"✅ Logo URL: {settings.get_global_nav_logo_url()}")
            else:
                print("❌ No global nav logo set")
        else:
            print("❌ Global settings is None")
    else:
        print("❌ global_settings not in context")

if __name__ == "__main__":
    test_global_logo_context() 