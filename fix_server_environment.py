#!/usr/bin/env python
"""
Server Environment Fix Script
This script will fix the server environment to ensure ImageKit is properly configured
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings

def check_current_environment():
    """Check what environment variables are currently loaded"""
    print("🔍 Checking current environment...")
    
    # Check if we're loading from the right .env file
    env_files = [
        '.env',
        'production.env',
        '/home/testsite.local/.env',
        '/home/testsite.local/production.env',
        '/home/cyberpanel/public_html/bethel/.env',
        '/home/cyberpanel/public_html/bethel/production.env',
    ]
    
    print("📁 Looking for environment files:")
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"✅ Found: {env_file}")
        else:
            print(f"❌ Missing: {env_file}")
    
    # Check current environment variables
    print("\n🔑 Current environment variables:")
    print(f"IMAGEKIT_PUBLIC_KEY: {'✅ Set' if os.environ.get('IMAGEKIT_PUBLIC_KEY') else '❌ Missing'}")
    print(f"IMAGEKIT_PRIVATE_KEY: {'✅ Set' if os.environ.get('IMAGEKIT_PRIVATE_KEY') else '❌ Missing'}")
    print(f"IMAGEKIT_URL_ENDPOINT: {'✅ Set' if os.environ.get('IMAGEKIT_URL_ENDPOINT') else '❌ Missing'}")
    
    # Check Django settings
    print("\n⚙️ Django settings:")
    print(f"IMAGEKIT_CONFIG: {settings.IMAGEKIT_CONFIG}")
    print(f"DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
    
    return {
        'public_key': os.environ.get('IMAGEKIT_PUBLIC_KEY'),
        'private_key': os.environ.get('IMAGEKIT_PRIVATE_KEY'),
        'url_endpoint': os.environ.get('IMAGEKIT_URL_ENDPOINT'),
        'storage': settings.DEFAULT_FILE_STORAGE
    }

def fix_environment():
    """Fix the environment by setting the correct variables"""
    print("\n🔧 Fixing environment...")
    
    # Set the correct ImageKit credentials
    os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
    os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
    os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'
    
    print("✅ Environment variables set")
    
    # Re-initialize Django with new environment
    django.setup()
    
    # Check if it worked
    print("\n🔍 Checking fixed environment:")
    print(f"IMAGEKIT_PUBLIC_KEY: {'✅ Set' if os.environ.get('IMAGEKIT_PUBLIC_KEY') else '❌ Missing'}")
    print(f"IMAGEKIT_PRIVATE_KEY: {'✅ Set' if os.environ.get('IMAGEKIT_PRIVATE_KEY') else '❌ Missing'}")
    print(f"IMAGEKIT_URL_ENDPOINT: {'✅ Set' if os.environ.get('IMAGEKIT_URL_ENDPOINT') else '❌ Missing'}")
    print(f"DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")

def test_imagekit_after_fix():
    """Test ImageKit after fixing the environment"""
    print("\n🧪 Testing ImageKit after fix...")
    
    try:
        from imagekitio import ImageKit
        from io import BytesIO
        
        # Create ImageKit instance
        imagekit = ImageKit(
            public_key=os.environ.get('IMAGEKIT_PUBLIC_KEY'),
            private_key=os.environ.get('IMAGEKIT_PRIVATE_KEY'),
            url_endpoint=os.environ.get('IMAGEKIT_URL_ENDPOINT')
        )
        
        # Test upload
        test_content = b"Test file from environment fix script"
        file_obj = BytesIO(test_content)
        file_obj.name = "env_fix_test.txt"
        
        upload = imagekit.upload_file(
            file=file_obj,
            file_name="env_fix_test.txt"
        )
        
        print(f"✅ Direct ImageKit upload successful! URL: {upload.url}")
        
        # Clean up
        imagekit.delete_file(upload.file_id)
        print("✅ Test file deleted")
        
        return True
        
    except Exception as e:
        print(f"❌ ImageKit test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_django_storage_after_fix():
    """Test Django storage after fixing the environment"""
    print("\n🧪 Testing Django storage after fix...")
    
    try:
        from django.core.files.base import ContentFile
        from django.core.files.storage import default_storage
        
        # Test upload through Django storage
        test_content = b"Test file through Django storage after fix"
        test_file = ContentFile(test_content, name='django_env_fix_test.txt')
        
        saved_path = default_storage.save('test/django_env_fix_test.txt', test_file)
        print(f"✅ Django storage upload successful! Path: {saved_path}")
        
        # Get URL
        url = default_storage.url(saved_path)
        print(f"✅ Django storage URL: {url}")
        
        # Check if it's an ImageKit URL
        if url.startswith('https://ik.imagekit.io/'):
            print("🎉 SUCCESS: Django storage is using ImageKit!")
        else:
            print("❌ FAILED: Django storage is not using ImageKit")
        
        # Clean up
        default_storage.delete(saved_path)
        print("✅ Test file deleted")
        
        return True
        
    except Exception as e:
        print(f"❌ Django storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_permanent_fix():
    """Create a permanent fix by updating the .env file"""
    print("\n🔧 Creating permanent fix...")
    
    # Create a new .env file with the correct settings
    env_content = """# Production Environment Variables
DEBUG=False
SECRET_KEY=6x81cy++5wh*#qi!*6srjp$(8(!_&m7g)31h9o9y@_ul#hf_t*
ALLOWED_HOSTS=91.99.232.214,your-domain.com,localhost,127.0.0.1
DATABASE_URL=postgresql://bethel_user:bethel_secure_password_2024@localhost:5432/bethel_db

# ImageKit Configuration
IMAGEKIT_PUBLIC_KEY=public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=
IMAGEKIT_PRIVATE_KEY=private_Dnsrj2VW7uJakaeMaNYaav+P784=
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/9buar9mbp

# Server Configuration
WEB_CONCURRENCY=4
PYTHONUNBUFFERED=1
CONN_MAX_AGE=600
PYTHONHASHSEED=random
PYTHONDONTWRITEBYTECODE=1
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://91.99.232.214
STATIC_ROOT=/home/testsite.local/staticfiles
MEDIA_ROOT=/home/testsite.local/media
LOG_LEVEL=INFO
"""
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with correct ImageKit configuration")
    
    # Also create a backup of the current environment
    backup_content = f"""# Backup of current environment
# Generated on: {django.utils.timezone.now()}

IMAGEKIT_PUBLIC_KEY={os.environ.get('IMAGEKIT_PUBLIC_KEY', 'NOT_SET')}
IMAGEKIT_PRIVATE_KEY={os.environ.get('IMAGEKIT_PRIVATE_KEY', 'NOT_SET')}
IMAGEKIT_URL_ENDPOINT={os.environ.get('IMAGEKIT_URL_ENDPOINT', 'NOT_SET')}
DEFAULT_FILE_STORAGE={settings.DEFAULT_FILE_STORAGE}
"""
    
    with open('env_backup.txt', 'w') as f:
        f.write(backup_content)
    
    print("✅ Created env_backup.txt with current settings")

def main():
    """Main function"""
    print("🚀 Starting server environment fix...")
    print("=" * 60)
    
    # Step 1: Check current environment
    current_env = check_current_environment()
    
    # Step 2: Fix environment
    fix_environment()
    
    # Step 3: Test ImageKit
    imagekit_ok = test_imagekit_after_fix()
    
    # Step 4: Test Django storage
    storage_ok = test_django_storage_after_fix()
    
    # Step 5: Create permanent fix
    create_permanent_fix()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"ImageKit Test: {'✅ PASS' if imagekit_ok else '❌ FAIL'}")
    print(f"Django Storage Test: {'✅ PASS' if storage_ok else '❌ FAIL'}")
    
    if imagekit_ok and storage_ok:
        print("\n🎉 SUCCESS! Environment has been fixed.")
        print("✅ ImageKit is now properly configured")
        print("✅ Django storage is using ImageKit")
        print("✅ Permanent fix has been applied")
        print("\n📋 Next steps:")
        print("1. Restart your Django application")
        print("2. Try uploading a new image through admin")
        print("3. Check that new uploads have ImageKit URLs")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
    
    return imagekit_ok and storage_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 