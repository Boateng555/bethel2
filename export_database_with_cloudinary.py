#!/usr/bin/env python3
"""
Export database with Cloudinary URLs for Railway import
"""

import os
import django
import subprocess
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def export_database():
    """Export database with Cloudinary URLs"""
    
    print("🔄 First, let's update local database URLs to Cloudinary...")
    
    # Import the update function
    from core.management.commands.update_urls_to_cloudinary import Command
    cmd = Command()
    cmd.handle()
    
    print("\n📤 Now exporting database...")
    
    # Export the database
    try:
        subprocess.run([
            'python', 'manage.py', 'dumpdata',
            '--exclude', 'contenttypes',
            '--exclude', 'auth.Permission',
            '--exclude', 'sessions',
            '--indent', '2',
            '-o', 'railway_database.json'
        ], check=True)
        
        print("✅ Database exported successfully to 'railway_database.json'")
        print("\n📋 Next steps:")
        print("1. Upload 'railway_database.json' to Railway")
        print("2. Run: python manage.py loaddata railway_database.json")
        print("3. Your images should now work!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error exporting database: {e}")
    except FileNotFoundError:
        print("❌ Error: Could not find manage.py")

if __name__ == "__main__":
    export_database() 