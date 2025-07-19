#!/usr/bin/env python
"""
Railway setup script for Bethel Django application
Updated with comprehensive memory optimizations for Railway deployment
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import execute_from_command_line

def main():
    """Main setup function with memory optimizations"""
    print("🚀 Railway Setup Starting with Memory Optimizations...")
    
    # Run migrations
    print("📦 Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Collect static files
    print("📁 Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    print("✅ Railway setup completed with memory optimizations!")

if __name__ == "__main__":
    main() 