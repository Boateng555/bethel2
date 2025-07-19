#!/usr/bin/env python
"""
Railway setup script for Bethel Django application
Updated with optimized worker configuration
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import execute_from_command_line

def main():
    """Main setup function"""
    print("🚀 Railway Setup Starting...")
    
    # Run migrations
    print("📦 Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Collect static files
    print("📁 Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    print("✅ Railway setup completed!")

if __name__ == "__main__":
    main() 