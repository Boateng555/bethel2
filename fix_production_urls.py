#!/usr/bin/env python
"""
Script to fix Django URLs to serve media files in production
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings

def fix_production_urls():
    """Fix Django URLs to serve media files in production"""
    print("=== Fixing Production URLs ===\n")
    
    # Read the current urls.py file
    urls_file = "backend/urls.py"
    
    try:
        with open(urls_file, 'r') as f:
            content = f.read()
        
        print(f"📁 Current URLs file: {urls_file}")
        
        # Check if media files are already served in production
        if "if not settings.DEBUG:" in content:
            print("✅ Production media serving already configured")
            return True
        
        # Create the new content
        new_content = '''"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# Serve media files in both development and production
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    print("🔧 Serving local media files for development")
else:
    # In production, also serve media files through Django
    # This is a fallback if nginx is not configured properly
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    print("🔧 Serving media files in production (fallback)")
'''
        
        # Write the new content
        with open(urls_file, 'w') as f:
            f.write(new_content)
        
        print("✅ Updated URLs file to serve media files in production")
        print("📝 Note: This is a fallback. For better performance, configure nginx to serve media files.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating URLs file: {e}")
        return False

def create_nginx_media_config():
    """Create nginx configuration for media files"""
    print("\n=== Nginx Media Configuration ===\n")
    
    nginx_config = '''# Nginx configuration for serving Django media files
# Add this to your Nginx site configuration

# Serve media files
location /media/ {
    alias /home/cyberpanel/public_html/bethel/media/;
    expires 30d;
    add_header Cache-Control "public";
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    
    # Allow common image and video formats
    location ~* \\.(jpg|jpeg|png|gif|ico|svg|webp|mp4|avi|mov|wmv|flv|webm)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Allow PDF and document formats
    location ~* \\.(pdf|doc|docx|xls|xlsx|ppt|pptx)$ {
        expires 7d;
        add_header Cache-Control "public";
    }
}
'''
    
    # Write nginx config
    with open("nginx_media_config.conf", "w") as f:
        f.write(nginx_config)
    
    print("✅ Created nginx_media_config.conf")
    print("📝 Instructions:")
    print("   1. Copy the content from nginx_media_config.conf")
    print("   2. Add it to your nginx site configuration")
    print("   3. Test nginx configuration: sudo nginx -t")
    print("   4. Reload nginx: sudo systemctl reload nginx")
    
    return True

def main():
    """Main function"""
    print("🔧 Fixing production media file serving...\n")
    
    # Fix Django URLs
    urls_fixed = fix_production_urls()
    
    # Create nginx config
    nginx_created = create_nginx_media_config()
    
    if urls_fixed and nginx_created:
        print("\n✅ Production media serving configured!")
        print("\n📋 Next steps:")
        print("   1. Restart your Django application")
        print("   2. Configure nginx to serve media files (see nginx_media_config.conf)")
        print("   3. Test media file access on your production site")
        print("   4. Check browser developer tools for any remaining 404 errors")
    else:
        print("\n❌ Some configuration steps failed")

if __name__ == "__main__":
    main() 