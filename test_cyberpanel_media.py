#!/usr/bin/env python
"""
Script to test media file serving on CyberPanel server
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Hero, HeroMedia, GlobalSettings
from django.conf import settings

def test_media_files():
    """Test if media files exist and are accessible"""
    print("=== CyberPanel Media File Test ===\n")
    
    # Check MEDIA_ROOT
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"DEBUG: {settings.DEBUG}")
    
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
            print(f"\nGlobal Hero: {hero.title}")
            
            # Check hero media
            hero_media = hero.hero_media.all()
            print(f"Hero Media Items: {hero_media.count()}")
            
            for i, media in enumerate(hero_media, 1):
                print(f"\n  {i}. Media Item:")
                print(f"     Order: {media.order}")
                
                # Check image
                if media.image:
                    image_path = media.image.path
                    image_url = media.image.url
                    print(f"     Image: {image_path}")
                    print(f"     Image URL: {image_url}")
                    
                    if os.path.exists(image_path):
                        print(f"     ✅ Image file exists")
                        # Test if file is readable
                        try:
                            with open(image_path, 'rb') as f:
                                f.read(1024)  # Read first 1KB
                            print(f"     ✅ Image file is readable")
                        except Exception as e:
                            print(f"     ❌ Image file not readable: {e}")
                    else:
                        print(f"     ❌ Image file missing")
                
                # Check video
                if media.video:
                    video_path = media.video.path
                    video_url = media.video.url
                    print(f"     Video: {video_path}")
                    print(f"     Video URL: {video_url}")
                    
                    if os.path.exists(video_path):
                        print(f"     ✅ Video file exists")
                        # Test if file is readable
                        try:
                            with open(video_path, 'rb') as f:
                                f.read(1024)  # Read first 1KB
                            print(f"     ✅ Video file is readable")
                        except Exception as e:
                            print(f"     ❌ Video file not readable: {e}")
                    else:
                        print(f"     ❌ Video file missing")
                
                # Check background video
                if media.background_video:
                    bg_video_path = media.background_video.path
                    bg_video_url = media.background_video.url
                    print(f"     Background Video: {bg_video_path}")
                    print(f"     Background Video URL: {bg_video_url}")
                    
                    if os.path.exists(bg_video_path):
                        print(f"     ✅ Background video file exists")
                    else:
                        print(f"     ❌ Background video file missing")
            
            # Check hero background video
            if hero.background_video:
                bg_path = hero.background_video.path
                bg_url = hero.background_video.url
                print(f"\nHero Background Video:")
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

def check_file_permissions():
    """Check file permissions"""
    print("\n=== File Permissions Check ===\n")
    
    media_root = settings.MEDIA_ROOT
    
    # Check ownership
    try:
        import pwd
        stat_info = os.stat(media_root)
        owner = pwd.getpwuid(stat_info.st_uid).pw_name
        print(f"Media directory owner: {owner}")
        
        # Check if owned by cyberpanel or www-data
        if owner in ['cyberpanel', 'www-data', 'root']:
            print(f"✅ Ownership looks correct")
        else:
            print(f"⚠️ Ownership might need adjustment")
            
    except Exception as e:
        print(f"Could not check ownership: {e}")
    
    # Check permissions
    try:
        stat_info = os.stat(media_root)
        mode = stat_info.st_mode & 0o777
        print(f"Media directory permissions: {oct(mode)}")
        
        if mode >= 0o755:
            print(f"✅ Permissions look correct")
        else:
            print(f"⚠️ Permissions might need adjustment")
            
    except Exception as e:
        print(f"Could not check permissions: {e}")

def main():
    """Main function"""
    print("Testing CyberPanel media file serving...\n")
    
    # Test media files
    media_ok = test_media_files()
    
    # Check permissions
    check_file_permissions()
    
    if media_ok:
        print("\n✅ Media files appear to be configured correctly")
        print("\n📝 Next steps:")
        print("1. The Django fallback should already be working")
        print("2. Test your website to see if media files load")
        print("3. If not working, check CyberPanel configuration")
    else:
        print("\n❌ Media files have issues")
        print("\n📝 Troubleshooting:")
        print("1. Check if media files exist in the correct directory")
        print("2. Verify file permissions")
        print("3. Check Django logs for errors")
    
    print("\n🌐 To test media files:")
    print("   - Visit your domain/media/ to see if files are accessible")
    print("   - Check browser developer tools for 404 errors")
    print("   - Verify file paths in Django admin")

if __name__ == "__main__":
    main() 