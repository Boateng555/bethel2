#!/usr/bin/env python
"""
Diagnostic script to troubleshoot image display issues on the global website
"""

import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import GlobalSettings, Hero, HeroMedia

def debug_global_hero_images():
    """Debug global hero image issues"""
    print("🔍 Debugging Global Hero Images")
    print("=" * 50)
    
    # Check global settings
    try:
        global_settings = GlobalSettings.get_settings()
        print(f"✅ Global Settings found: {global_settings.site_name}")
        
        # Check global hero
        if global_settings.global_hero:
            hero = global_settings.global_hero
            print(f"\n🌟 Global Hero: {hero.title}")
            print(f"   Status: {'✅ Active' if hero.is_active else '❌ Inactive'}")
            print(f"   Background Type: {hero.background_type}")
            
            # Check background image
            if hero.background_image:
                print(f"   Background Image: {hero.background_image}")
                print(f"   Image URL: {hero.get_background_image_url()}")
                
                # Check if file exists
                if hasattr(hero.background_image, 'path'):
                    file_path = hero.background_image.path
                    if os.path.exists(file_path):
                        print(f"   ✅ File exists: {file_path}")
                        file_size = os.path.getsize(file_path)
                        print(f"   File size: {file_size} bytes")
                    else:
                        print(f"   ❌ File missing: {file_path}")
                else:
                    print(f"   ⚠️  No local file path (might be external URL)")
            else:
                print(f"   ❌ No background image set")
            
            # Check hero media
            hero_media = hero.hero_media.all()
            print(f"\n📸 Hero Media: {hero_media.count()} items")
            
            for i, media in enumerate(hero_media, 1):
                print(f"   {i}. Order: {media.order}")
                if media.image:
                    print(f"      Image: {media.image}")
                    print(f"      Image URL: {media.get_image_url()}")
                    
                    # Check if file exists
                    if hasattr(media.image, 'path'):
                        file_path = media.image.path
                        if os.path.exists(file_path):
                            print(f"      ✅ File exists: {file_path}")
                            file_size = os.path.getsize(file_path)
                            print(f"      File size: {file_size} bytes")
                        else:
                            print(f"      ❌ File missing: {file_path}")
                    else:
                        print(f"      ⚠️  No local file path (might be external URL)")
                else:
                    print(f"      ❌ No image")
                
                if media.video:
                    print(f"      Video: {media.video}")
                    print(f"      Video URL: {media.get_video_url()}")
                else:
                    print(f"      ❌ No video")
        else:
            print("\n❌ No global hero selected")
            
    except Exception as e:
        print(f"❌ Error getting global settings: {e}")
    
    # Check media settings
    print(f"\n📁 Media Settings:")
    print(f"   MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'Not set')}")
    print(f"   MEDIA_ROOT: {getattr(settings, 'MEDIA_ROOT', 'Not set')}")
    
    # Check if media directory exists
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    if media_root and os.path.exists(media_root):
        print(f"   ✅ MEDIA_ROOT exists: {media_root}")
        
        # Check hero directory
        hero_dir = os.path.join(media_root, 'hero')
        if os.path.exists(hero_dir):
            print(f"   ✅ Hero directory exists: {hero_dir}")
            
            # List files in hero directory
            try:
                hero_files = os.listdir(hero_dir)
                print(f"   Files in hero directory: {len(hero_files)}")
                for file in hero_files[:5]:  # Show first 5 files
                    file_path = os.path.join(hero_dir, file)
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        print(f"      - {file} ({size} bytes)")
            except Exception as e:
                print(f"   ❌ Error listing hero directory: {e}")
        else:
            print(f"   ❌ Hero directory missing: {hero_dir}")
    else:
        print(f"   ❌ MEDIA_ROOT missing or invalid: {media_root}")

def check_image_urls():
    """Check if image URLs are accessible"""
    print(f"\n🌐 Checking Image URLs")
    print("=" * 50)
    
    try:
        global_settings = GlobalSettings.get_settings()
        if global_settings.global_hero:
            hero = global_settings.global_hero
            
            # Check background image URL
            if hero.background_image:
                bg_url = hero.get_background_image_url()
                print(f"Background Image URL: {bg_url}")
                
                # Try to access the URL
                import requests
                try:
                    response = requests.head(bg_url, timeout=5)
                    if response.status_code == 200:
                        print(f"✅ Background image accessible (Status: {response.status_code})")
                    else:
                        print(f"❌ Background image not accessible (Status: {response.status_code})")
                except Exception as e:
                    print(f"❌ Error accessing background image: {e}")
            
            # Check hero media URLs
            for media in hero.hero_media.all():
                if media.image:
                    img_url = media.get_image_url()
                    print(f"Hero Media URL: {img_url}")
                    
                    try:
                        response = requests.head(img_url, timeout=5)
                        if response.status_code == 200:
                            print(f"✅ Hero media accessible (Status: {response.status_code})")
                        else:
                            print(f"❌ Hero media not accessible (Status: {response.status_code})")
                    except Exception as e:
                        print(f"❌ Error accessing hero media: {e}")
                        
    except Exception as e:
        print(f"❌ Error checking image URLs: {e}")

def suggest_fixes():
    """Suggest common fixes for image issues"""
    print(f"\n🔧 Suggested Fixes")
    print("=" * 50)
    
    print("1. **Check File Permissions:**")
    print("   - Ensure media files have proper read permissions")
    print("   - Check that web server can access media directory")
    
    print("\n2. **Verify File Uploads:**")
    print("   - Make sure images were uploaded successfully")
    print("   - Check file sizes (should be > 0 bytes)")
    print("   - Verify file formats (JPG, PNG, etc.)")
    
    print("\n3. **Check Media Settings:**")
    print("   - Verify MEDIA_URL and MEDIA_ROOT in settings")
    print("   - Ensure media files are being served correctly")
    
    print("\n4. **Clear Browser Cache:**")
    print("   - Press Ctrl+F5 to hard refresh")
    print("   - Try incognito/private mode")
    
    print("\n5. **Check Server Configuration:**")
    print("   - Verify nginx/apache is serving media files")
    print("   - Check for any URL rewriting issues")
    
    print("\n6. **Database Issues:**")
    print("   - Verify hero is active and properly configured")
    print("   - Check that global hero is selected in Global Settings")

if __name__ == "__main__":
    debug_global_hero_images()
    check_image_urls()
    suggest_fixes()
    
    print(f"\n✅ Diagnostic completed!")
    print(f"📝 If images still don't work, check the suggestions above.") 