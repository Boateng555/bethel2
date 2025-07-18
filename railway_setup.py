#!/usr/bin/env python
"""
Railway deployment setup script
Runs migrations and fixes common issues
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.conf import settings

def setup_railway():
    """Setup Railway deployment"""
    print("🚂 Railway Setup Starting...")
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    
    try:
        # Run migrations
        print("📦 Running migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed")
        
        # Check database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM core_church")
            church_count = cursor.fetchone()[0]
            print(f"📊 Database connected. Found {church_count} churches")
        
        # Fix image URLs if needed
        print("🖼️ Checking image URLs...")
        from core.models import Church, HeroMedia
        
        # Check if we have any local file paths that need fixing
        local_paths = 0
        for church in Church.objects.all():
            if church.logo and not str(church.logo).startswith('http'):
                local_paths += 1
            if church.banner_image and not str(church.banner_image).startswith('http'):
                local_paths += 1
        
        for hero_media in HeroMedia.objects.all():
            if hero_media.image and not str(hero_media.image).startswith('http'):
                local_paths += 1
        
        if local_paths > 0:
            print(f"🔧 Found {local_paths} local file paths, fixing...")
            # Import and run the fix
            from fix_production_images import fix_image_urls
            fix_image_urls()
        else:
            print("✅ All image URLs are already cloud URLs")
        
        # Create superuser if none exists
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            print("👤 Creating superuser...")
            User.objects.create_superuser(
                username='admin',
                email='admin@bethel.com',
                password='admin123'
            )
            print("✅ Superuser created: admin/admin123")
        
        print("🎉 Railway setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    setup_railway() 