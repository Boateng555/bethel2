#!/usr/bin/env python
"""
Script to run on Railway to fix production database images
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import call_command

def run_on_railway():
    """Run the production image fix command"""
    print("🚀 Running Production Image Fix on Railway")
    print("=" * 50)
    
    try:
        # Run the management command to fix production images
        call_command('fix_production_images', '--upload-placeholders')
        print("\n✅ Production image fix completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running command: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_on_railway() 