#!/usr/bin/env python
"""
Script to diagnose and fix media file issues in production
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Hero, HeroMedia, GlobalSettings
from django.conf import settings
import requests

def check_media_files():
    """Check if media files exist and are accessible"""
    print("=== Production Media File Diagnosis ===\n")
    
    # Check MEDIA_ROOT
    print(f"📁 MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"🌐 MEDIA_URL: {settings.MEDIA_URL}")
    print(f"🔧 DEBUG: {settings.DEBUG}")
    
    # Check if media directory exists
    if os.path.exists(settings.MEDIA_ROOT):
        print(f"✅ Media directory exists: {settings.MEDIA_ROOT}")
    else:
        print(f"❌ Media directory missing: {settings.MEDIA_ROOT}")
        return False
    
    # Check global hero
    try:
        global_settings = GlobalSettings.objects.first()
        if global_settings and global_settings.global_hero:
            hero = global_settings.global_hero
            print(f"\n🎯 Global Hero: {hero.title}")
            
            # Check hero media
            hero_media = hero.hero_media.all()
            print(f"📸 Hero Media Items: {hero_media.count()}")
            
            for i, media in enumerate(hero_media, 1):
                print(f"\n  {i}. Media Item:")
                print(f"     Order: {media.order}")
                print(f"     Title: {media.title}")
                
                # Check image
                if media.image:
                    image_path = media.image.path
                    image_url = media.image.url
                    print(f"     📷 Image: {image_path}")
                    print(f"     🌐 Image URL: {image_url}")
                    
                    if os.path.exists(image_path):
                        print(f"     ✅ Image file exists")
                        # Test URL accessibility
                        try:
                            full_url = f"http://127.0.0.1:8000{image_url}"
                            response = requests.head(full_url, timeout=5)
                            if response.status_code == 200:
                                print(f"     ✅ Image URL accessible")
                            else:
                                print(f"     ❌ Image URL not accessible (Status: {response.status_code})")
                        except Exception as e:
                            print(f"     ⚠️ Could not test image URL: {e}")
                    else:
                        print(f"     ❌ Image file missing")
                
                # Check video
                if media.video:
                    video_path = media.video.path
                    video_url = media.video.url
                    print(f"     🎥 Video: {video_path}")
                    print(f"     🌐 Video URL: {video_url}")
                    
                    if os.path.exists(video_path):
                        print(f"     ✅ Video file exists")
                        # Test URL accessibility
                        try:
                            full_url = f"http://127.0.0.1:8000{video_url}"
                            response = requests.head(full_url, timeout=5)
                            if response.status_code == 200:
                                print(f"     ✅ Video URL accessible")
                            else:
                                print(f"     ❌ Video URL not accessible (Status: {response.status_code})")
                        except Exception as e:
                            print(f"     ⚠️ Could not test video URL: {e}")
                    else:
                        print(f"     ❌ Video file missing")
                
                # Check background video
                if media.background_video:
                    bg_video_path = media.background_video.path
                    bg_video_url = media.background_video.url
                    print(f"     🎬 Background Video: {bg_video_path}")
                    print(f"     🌐 Background Video URL: {bg_video_url}")
                    
                    if os.path.exists(bg_video_path):
                        print(f"     ✅ Background video file exists")
                    else:
                        print(f"     ❌ Background video file missing")
            
            # Check hero background video
            if hero.background_video:
                bg_path = hero.background_video.path
                bg_url = hero.background_video.url
                print(f"\n🎬 Hero Background Video:")
                print(f"   Path: {bg_path}")
                print(f"   URL: {bg_url}")
                
                if os.path.exists(bg_path):
                    print(f"   ✅ Background video file exists")
                else:
                    print(f"   ❌ Background video file missing")
        else:
            print("❌ No global hero configured")
            return False
            
    except Exception as e:
        print(f"❌ Error checking hero media: {e}")
        return False
    
    return True

def fix_media_urls():
    """Fix media URLs in production"""
    print("\n=== Fixing Media URLs ===\n")
    
    # Check if we need to serve media files in production
    if not settings.DEBUG:
        print("🔧 Production environment detected")
        print("📝 To fix media files in production, you need to:")
        print("   1. Ensure nginx is configured to serve /media/ files")
        print("   2. Check that media files are uploaded to the correct directory")
        print("   3. Verify file permissions")
        
        # Check nginx configuration
        nginx_config_path = "/etc/nginx/sites-available/bethel"
        if os.path.exists(nginx_config_path):
            print(f"✅ Nginx config found: {nginx_config_path}")
        else:
            print(f"❌ Nginx config not found: {nginx_config_path}")
            print("   You may need to configure nginx to serve media files")
    
    return True

def main():
    """Main function"""
    print("🔍 Diagnosing production media file issues...\n")
    
    # Check media files
    media_ok = check_media_files()
    
    if media_ok:
        print("\n✅ Media files appear to be configured correctly")
    else:
        print("\n❌ Media files have issues")
    
    # Fix media URLs
    fix_media_urls()
    
    print("\n=== Recommendations ===")
    print("1. Check your nginx configuration includes media file serving")
    print("2. Ensure media files are uploaded to the production server")
    print("3. Verify file permissions (should be readable by web server)")
    print("4. Check that MEDIA_ROOT points to the correct directory")
    print("5. Restart nginx after configuration changes")
    
    print("\n🌐 To test media files:")
    print("   - Visit your domain/media/ to see if files are accessible")
    print("   - Check browser developer tools for 404 errors")
    print("   - Verify file paths in Django admin")

if __name__ == "__main__":
    main() 