#!/usr/bin/env python3
"""
Comprehensive System Status Checker for Bethel Django Application
Checks all critical components and configurations
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import connection
from django.contrib.auth.models import User
from core.models import Church, Event, Ministry, News, Sermon, ChurchAdmin

def check_system_status():
    """Comprehensive system status check"""
    print("🔍 BETHEL SYSTEM STATUS CHECK")
    print("=" * 50)
    
    status = {
        'overall': '✅ HEALTHY',
        'issues': [],
        'warnings': []
    }
    
    # 1. Django Settings Check
    print("\n📋 1. DJANGO SETTINGS")
    print("-" * 30)
    
    # Check media configuration
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    media_url = getattr(settings, 'MEDIA_URL', None)
    default_storage_backend = getattr(settings, 'DEFAULT_FILE_STORAGE', None)
    
    print(f"✅ MEDIA_ROOT: {media_root}")
    print(f"✅ MEDIA_URL: {media_url}")
    print(f"✅ DEFAULT_FILE_STORAGE: {default_storage_backend}")
    
    # Check if media directory exists
    if media_root and os.path.exists(media_root):
        print(f"✅ Media directory exists: {media_root}")
    else:
        print(f"❌ Media directory missing: {media_root}")
        status['issues'].append("Media directory does not exist")
    
    # 2. Database Connection Check
    print("\n🗄️  2. DATABASE CONNECTION")
    print("-" * 30)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        status['overall'] = '❌ UNHEALTHY'
        status['issues'].append(f"Database connection failed: {e}")
    
    # 3. Model Data Check
    print("\n📊 3. MODEL DATA")
    print("-" * 30)
    
    try:
        churches_count = Church.objects.count()
        events_count = Event.objects.count()
        ministries_count = Ministry.objects.count()
        news_count = News.objects.count()
        sermons_count = Sermon.objects.count()
        users_count = User.objects.count()
        church_admins_count = ChurchAdmin.objects.count()
        
        print(f"✅ Churches: {churches_count}")
        print(f"✅ Events: {events_count}")
        print(f"✅ Ministries: {ministries_count}")
        print(f"✅ News: {news_count}")
        print(f"✅ Sermons: {sermons_count}")
        print(f"✅ Users: {users_count}")
        print(f"✅ Church Admins: {church_admins_count}")
        
        if churches_count == 0:
            status['warnings'].append("No churches found in database")
        if users_count == 0:
            status['warnings'].append("No users found in database")
            
    except Exception as e:
        print(f"❌ Model data check failed: {e}")
        status['issues'].append(f"Model data check failed: {e}")
    
    # 4. File Storage Check
    print("\n💾 4. FILE STORAGE")
    print("-" * 30)
    
    try:
        # Test file storage
        test_file_path = 'test_storage_check.txt'
        test_content = 'Test content for storage verification'
        
        # Create a file-like object
        from io import StringIO
        test_file = StringIO(test_content)
        test_file.name = test_file_path
        
        # Save test file
        saved_path = default_storage.save(test_file_path, test_file)
        print(f"✅ File save test successful: {saved_path}")
        
        # Check if file exists
        if default_storage.exists(saved_path):
            print("✅ File exists check successful")
        else:
            print("❌ File exists check failed")
            status['issues'].append("File storage exists check failed")
        
        # Get file URL
        try:
            file_url = default_storage.url(saved_path)
            print(f"✅ File URL generation successful: {file_url}")
        except Exception as e:
            print(f"⚠️  File URL generation warning: {e}")
            status['warnings'].append(f"File URL generation warning: {e}")
        
        # Clean up test file
        default_storage.delete(saved_path)
        print("✅ Test file cleanup successful")
        
    except Exception as e:
        print(f"❌ File storage test failed: {e}")
        status['issues'].append(f"File storage test failed: {e}")
    
    # 5. Session Configuration Check
    print("\n🔐 5. SESSION CONFIGURATION")
    print("-" * 30)
    
    session_engine = getattr(settings, 'SESSION_ENGINE', None)
    session_cookie_age = getattr(settings, 'SESSION_COOKIE_AGE', None)
    session_save_every_request = getattr(settings, 'SESSION_SAVE_EVERY_REQUEST', None)
    session_expire_at_browser_close = getattr(settings, 'SESSION_EXPIRE_AT_BROWSER_CLOSE', None)
    
    print(f"✅ SESSION_ENGINE: {session_engine}")
    print(f"✅ SESSION_COOKIE_AGE: {session_cookie_age} seconds ({session_cookie_age/3600:.1f} hours)")
    print(f"✅ SESSION_SAVE_EVERY_REQUEST: {session_save_every_request}")
    print(f"✅ SESSION_EXPIRE_AT_BROWSER_CLOSE: {session_expire_at_browser_close}")
    
    # 6. CSRF Configuration Check
    print("\n🛡️  6. CSRF CONFIGURATION")
    print("-" * 30)
    
    csrf_trusted_origins = getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])
    print(f"✅ CSRF_TRUSTED_ORIGINS: {len(csrf_trusted_origins)} origins configured")
    for origin in csrf_trusted_origins:
        print(f"   - {origin}")
    
    # 7. Admin Configuration Check
    print("\n⚙️  7. ADMIN CONFIGURATION")
    print("-" * 30)
    
    # Check if admin site is properly configured
    try:
        from django.contrib import admin
        admin_site = admin.site
        registered_models = len(admin_site._registry)
        print(f"✅ Admin site configured with {registered_models} registered models")
        
        # Check specific admin models
        expected_models = ['Church', 'Event', 'Ministry', 'News', 'Sermon', 'ChurchAdmin']
        for model_name in expected_models:
            try:
                model = admin_site._registry.get(eval(model_name))
                if model:
                    print(f"✅ {model_name} admin configured")
                else:
                    print(f"⚠️  {model_name} admin not found")
                    status['warnings'].append(f"{model_name} admin not configured")
            except:
                print(f"⚠️  {model_name} admin check failed")
                status['warnings'].append(f"{model_name} admin check failed")
                
    except Exception as e:
        print(f"❌ Admin configuration check failed: {e}")
        status['issues'].append(f"Admin configuration check failed: {e}")
    
    # 8. Media Files Check
    print("\n🖼️  8. MEDIA FILES")
    print("-" * 30)
    
    if media_root and os.path.exists(media_root):
        try:
            # Count files in media directory
            media_files = []
            for root, dirs, files in os.walk(media_root):
                for file in files:
                    media_files.append(os.path.join(root, file))
            
            print(f"✅ Media directory contains {len(media_files)} files")
            
            # Check specific media subdirectories
            media_subdirs = ['churches', 'events', 'ministries', 'news', 'sermons', 'hero']
            for subdir in media_subdirs:
                subdir_path = os.path.join(media_root, subdir)
                if os.path.exists(subdir_path):
                    subdir_files = len([f for f in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, f))])
                    print(f"✅ {subdir}/: {subdir_files} files")
                else:
                    print(f"⚠️  {subdir}/: directory not found")
                    status['warnings'].append(f"Media subdirectory {subdir} not found")
                    
        except Exception as e:
            print(f"❌ Media files check failed: {e}")
            status['issues'].append(f"Media files check failed: {e}")
    
    # 9. Summary
    print("\n📈 9. SUMMARY")
    print("-" * 30)
    
    if status['issues']:
        print(f"❌ ISSUES FOUND ({len(status['issues'])}):")
        for issue in status['issues']:
            print(f"   - {issue}")
        status['overall'] = '❌ UNHEALTHY'
    
    if status['warnings']:
        print(f"⚠️  WARNINGS ({len(status['warnings'])}):")
        for warning in status['warnings']:
            print(f"   - {warning}")
    
    print(f"\n🎯 OVERALL STATUS: {status['overall']}")
    
    if status['overall'] == '✅ HEALTHY':
        print("\n🎉 Your Bethel Django application is working correctly!")
        print("✅ Admin interface should work properly")
        print("✅ File uploads should save correctly")
        print("✅ Sessions should persist without frequent logouts")
    else:
        print("\n🔧 Please address the issues above before using the application")
    
    return status

if __name__ == "__main__":
    check_system_status() 