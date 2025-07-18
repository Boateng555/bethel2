#!/usr/bin/env python
"""
Railway setup script to run migrations and fix image issues
"""
import os
import django
from pathlib import Path

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings

def railway_setup():
    """Run Railway setup tasks"""
    print("🚀 Railway Setup Script")
    print("=" * 50)
    
    # Check storage configuration
    print(f"📦 Storage Backend: {settings.DEFAULT_FILE_STORAGE}")
    
    # Check ImageKit configuration
    if hasattr(settings, 'IMAGEKIT_CONFIG'):
        config = settings.IMAGEKIT_CONFIG
        print("🖼️ ImageKit Configuration:")
        print(f"  Public Key: {'✅ Set' if config.get('PUBLIC_KEY') else '❌ Missing'}")
        print(f"  Private Key: {'✅ Set' if config.get('PRIVATE_KEY') else '❌ Missing'}")
        print(f"  URL Endpoint: {'✅ Set' if config.get('URL_ENDPOINT') else '❌ Missing'}")
    else:
        print("❌ ImageKit configuration not found")
    
    # Run migrations
    print("\n🔄 Running database migrations...")
    try:
        call_command('migrate', verbosity=2)
        print("✅ Migrations completed successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    # Create superuser if needed
    print("\n👤 Checking for superuser...")
    from django.contrib.auth.models import User
    if not User.objects.filter(is_superuser=True).exists():
        print("Creating superuser...")
        try:
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            print("✅ Superuser created: admin/admin123")
        except Exception as e:
            print(f"❌ Failed to create superuser: {e}")
    
    # Check database tables
    print("\n📊 Database Status:")
    try:
        from core.models import Church, Event, News, Ministry, Sermon, Hero
        print(f"  Churches: {Church.objects.count()}")
        print(f"  Events: {Event.objects.count()}")
        print(f"  News: {News.objects.count()}")
        print(f"  Ministries: {Ministry.objects.count()}")
        print(f"  Sermons: {Sermon.objects.count()}")
        print(f"  Heroes: {Hero.objects.count()}")
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    
    print("\n🎉 Railway setup completed!")
    return True

if __name__ == "__main__":
    railway_setup() 