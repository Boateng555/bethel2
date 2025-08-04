# Production Media Files Fix Guide

## Problem
The global hero media (videos and pictures) is working on local development but not on production server.

## Root Cause
In production, Django doesn't serve media files through the development server. Media files need to be served by nginx or configured properly in Django.

## Solution Steps

### 1. Django Configuration (Already Fixed)
✅ **Updated `backend/urls.py`** to serve media files in both development and production:
```python
# Serve media files in both development and production
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    print("Serving local media files for development")
else:
    # In production, also serve media files through Django
    # This is a fallback if nginx is not configured properly
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    print("Serving media files in production (fallback)")
```

### 2. Nginx Configuration (Recommended)
For better performance, configure nginx to serve media files directly.

**Add this to your nginx site configuration:**
```nginx
# Serve media files
location /media/ {
    alias /home/cyberpanel/public_html/bethel/media/;
    expires 30d;
    add_header Cache-Control "public";
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    
    # Allow common image and video formats
    location ~* \.(jpg|jpeg|png|gif|ico|svg|webp|mp4|avi|mov|wmv|flv|webm)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Allow PDF and document formats
    location ~* \.(pdf|doc|docx|xls|xlsx|ppt|pptx)$ {
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

### 3. Server Commands
Run these commands on your production server:

```bash
# 1. Navigate to your project directory
cd /home/cyberpanel/public_html/bethel

# 2. Pull latest changes
git pull origin main

# 3. Apply migrations (if any)
python manage.py migrate

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Restart Django application
sudo systemctl restart bethel

# 6. Test nginx configuration
sudo nginx -t

# 7. Reload nginx
sudo systemctl reload nginx
```

### 4. File Permissions
Ensure media files are readable by the web server:

```bash
# Set proper permissions for media directory
sudo chown -R www-data:www-data /home/cyberpanel/public_html/bethel/media
sudo chmod -R 755 /home/cyberpanel/public_html/bethel/media
```

### 5. Verify Media Files
Check if media files exist on the server:

```bash
# List media files
ls -la /home/cyberpanel/public_html/bethel/media/

# Check specific hero media
find /home/cyberpanel/public_html/bethel/media/ -name "*.jpg" -o -name "*.png" -o -name "*.mp4"
```

### 6. Test Media Access
Test if media files are accessible:

```bash
# Test from server
curl -I http://your-domain.com/media/your-image.jpg

# Or visit in browser
http://your-domain.com/media/
```

## Troubleshooting

### If media files still don't work:

1. **Check Django logs:**
   ```bash
   sudo journalctl -u bethel -f
   ```

2. **Check nginx logs:**
   ```bash
   sudo tail -f /var/log/nginx/error.log
   sudo tail -f /var/log/nginx/access.log
   ```

3. **Verify file paths in Django admin:**
   - Go to Django admin
   - Check Hero Media items
   - Verify file paths are correct

4. **Check browser developer tools:**
   - Open browser developer tools (F12)
   - Go to Network tab
   - Reload page
   - Look for 404 errors on media files

### Common Issues:

1. **File not found (404):**
   - Check if files exist in MEDIA_ROOT
   - Verify nginx configuration
   - Check file permissions

2. **Permission denied:**
   - Set proper ownership: `sudo chown -R www-data:www-data /path/to/media`
   - Set proper permissions: `sudo chmod -R 755 /path/to/media`

3. **Wrong MEDIA_ROOT:**
   - Verify MEDIA_ROOT in settings.py points to correct directory
   - Check production environment variables

## Quick Fix Script
Run this script on your production server to diagnose issues:

```bash
# Create and run diagnosis script
python fix_production_media.py
```

## Expected Result
After implementing these fixes:
- ✅ Media files should be accessible via `/media/` URLs
- ✅ Global hero images and videos should display correctly
- ✅ No 404 errors in browser developer tools
- ✅ Fast loading of media files (if using nginx)

## Performance Notes
- **Django serving media files:** Works but slower for production
- **Nginx serving media files:** Recommended for better performance
- **CDN:** Consider using a CDN for even better performance

## Next Steps
1. Deploy the changes to production
2. Test media file access
3. Monitor for any remaining issues
4. Consider implementing CDN for better performance 