# CyberPanel Media Files Fix Guide

## Problem
The global hero media (videos and pictures) is working on local development but not on production server running CyberPanel.

## Root Cause
CyberPanel uses OpenLiteSpeed Web Server instead of nginx. Media files need to be configured properly in OpenLiteSpeed.

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
    # This is a fallback if web server is not configured properly
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    print("Serving media files in production (fallback)")
```

### 2. CyberPanel/OpenLiteSpeed Configuration

#### Option A: Use Django Fallback (Quick Fix)
The Django configuration above should already work. Try this first:

```bash
# 1. Navigate to your project directory
cd /home/cyberpanel/public_html/bethel

# 2. Pull latest changes
git pull origin main

# 3. Apply migrations (if any)
python manage.py migrate

# 4. Restart your Django application
sudo systemctl restart bethel
```

#### Option B: Configure OpenLiteSpeed (Recommended for Performance)

1. **Access CyberPanel:**
   - Go to your CyberPanel admin: `https://your-server-ip:8090`
   - Login with your admin credentials

2. **Configure Virtual Host:**
   - Go to "Websites" → Your Domain
   - Click on "Manage" → "File Manager"
   - Navigate to `/home/cyberpanel/public_html/bethel/`

3. **Create .htaccess file:**
   Create a `.htaccess` file in your project root with:
   ```apache
   # Serve media files
   RewriteEngine On
   
   # Allow direct access to media files
   RewriteCond %{REQUEST_URI} ^/media/
   RewriteCond %{REQUEST_FILENAME} -f
   RewriteRule ^(.*)$ $1 [L]
   
   # Proxy everything else to Django
   RewriteCond %{REQUEST_FILENAME} !-f
   RewriteCond %{REQUEST_FILENAME} !-d
   RewriteRule ^(.*)$ http://127.0.0.1:8000/$1 [P,L]
   ```

4. **Alternative: Configure in CyberPanel:**
   - Go to "Websites" → Your Domain → "Manage"
   - Click on "Rewrite Rules"
   - Add the media serving rules

### 3. Server Commands for CyberPanel

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

# 6. Restart OpenLiteSpeed (if needed)
sudo systemctl restart lsws
```

### 4. File Permissions
Ensure media files are readable by the web server:

```bash
# Set proper permissions for media directory
sudo chown -R cyberpanel:cyberpanel /home/cyberpanel/public_html/bethel/media
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

2. **Check OpenLiteSpeed logs:**
   ```bash
   sudo tail -f /usr/local/lsws/logs/error.log
   sudo tail -f /usr/local/lsws/logs/access.log
   ```

3. **Verify file paths in Django admin:**
   - Go to Django admin: `http://your-domain.com/admin/`
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
   - Verify OpenLiteSpeed configuration
   - Check file permissions

2. **Permission denied:**
   - Set proper ownership: `sudo chown -R cyberpanel:cyberpanel /path/to/media`
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
- ✅ Fast loading of media files

## Performance Notes
- **Django serving media files:** Works but slower for production
- **OpenLiteSpeed serving media files:** Recommended for better performance
- **CDN:** Consider using a CDN for even better performance

## Next Steps
1. Deploy the changes to production
2. Test media file access
3. Monitor for any remaining issues
4. Consider implementing CDN for better performance 