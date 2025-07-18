#!/usr/bin/env python
"""
Check local development environment configuration
"""

import os
import django
from django.conf import settings

def check_local_environment():
    """Check if local development environment is configured correctly"""
    print("🔍 Local Development Environment Check")
    print("=" * 50)
    
    # Check environment variables
    print("Environment Variables:")
    print(f"  DJANGO_DEBUG: {os.environ.get('DJANGO_DEBUG', 'Not Set')}")
    print(f"  DATABASE_URL: {'Set' if os.environ.get('DATABASE_URL') else 'Not Set'}")
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    
    # Check Django settings
    print("\nDjango Settings:")
    print(f"  DEBUG: {settings.DEBUG}")
    print(f"  Database Engine: {settings.DATABASES['default']['ENGINE']}")
    print(f"  Storage Backend: {settings.DEFAULT_FILE_STORAGE}")
    
    # Check if we can connect to the database
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("  ✅ Database connection successful")
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
    
    # Summary
    print("\nSummary:")
    if settings.DEBUG and 'sqlite' in settings.DATABASES['default']['ENGINE']:
        print("  ✅ Local development environment is configured correctly!")
        print("  📦 Using SQLite database")
        print("  🖼️ Using local file storage")
    else:
        print("  ❌ Local development environment is NOT configured correctly!")
        print("  💡 Run: $env:DJANGO_DEBUG = 'True'")
        print("  💡 Or use: python start_local_server.py")

if __name__ == '__main__':
    check_local_environment() 