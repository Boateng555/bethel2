#!/usr/bin/env python
"""
Script to run Django migrations in production
"""
import os
import django
from pathlib import Path

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import call_command

def run_migrations():
    """Run Django migrations"""
    print("🔄 Running Django migrations...")
    print("=" * 50)
    
    try:
        # Run migrations
        call_command('migrate', verbosity=2)
        print("\n✅ Migrations completed successfully!")
        
        # Show migration status
        print("\n📊 Migration Status:")
        call_command('showmigrations', verbosity=1)
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    run_migrations() 