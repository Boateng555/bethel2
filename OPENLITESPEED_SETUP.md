# OpenLiteSpeed Server Setup Guide

## Current Setup Analysis
Your Hetzner server is using **OpenLiteSpeed** as the web server:
- ✅ OpenLiteSpeed is running on port 80
- ✅ Django is running on port 8000
- ✅ CyberPanel is managing the setup

## Quick Fix (Django Fallback)
Since Django is now configured to serve media files in production, your media files should work immediately after restarting the Django application.

## Step 1: Restart Django Application
```bash
# Navigate to your project directory
cd /home/testsite.local

# Restart your Django application
sudo systemctl restart bethel

# Check if the service is running
sudo systemctl status bethel
```

## Step 2: Test Media Files
After restarting, test if media files are accessible:
```bash
# Test from server
curl -I http://your-domain.com/media/

# Or visit in browser
http://your-domain.com/media/
```

## Step 3: OpenLiteSpeed Configuration (Recommended)
For better performance, configure OpenLiteSpeed to serve media files directly:

### Option A: Through CyberPanel (Easiest)
1. **Login to CyberPanel** (usually at `http://your-server-ip:8090`)
2. **Go to Websites** → **List Websites**
3. **Click on your domain**
4. **Go to File Manager**
5. **Navigate to `/home/testsite.local/media/`**
6. **Set permissions** to 755 for directories and 644 for files

### Option B: Direct OpenLiteSpeed Configuration
```bash
# Access OpenLiteSpeed admin panel
# Usually at: http://your-server-ip:7080

# Or edit configuration directly
sudo nano /usr/local/lsws/conf/vhosts/your-domain.com/vhost.conf
```

Add this configuration to your virtual host:
```apache
# Media files configuration
context /media/ {
    type                    static
    location                /home/testsite.local/media/
    allowBrowse            1
    index                   index.html, index.php
    expires                30d
    addDefaultCharset      off
    addMimeType            .mp4 video/mp4
    addMimeType            .avi video/x-msvideo
    addMimeType            .mov video/quicktime
    addMimeType            .wmv video/x-ms-wmv
    addMimeType            .flv video/x-flv
    addMimeType            .webm video/webm
    addMimeType            .jpg image/jpeg
    addMimeType            .jpeg image/jpeg
    addMimeType            .png image/png
    addMimeType            .gif image/gif
    addMimeType            .svg image/svg+xml
    addMimeType            .webp image/webp
    addMimeType            .pdf application/pdf
    addMimeType            .doc application/msword
    addMimeType            .docx application/vnd.openxmlformats-officedocument.wordprocessingml.document
}

# Static files configuration
context /static/ {
    type                    static
    location                /home/testsite.local/staticfiles/
    allowBrowse            1
    index                   index.html, index.php
    expires                30d
    addDefaultCharset      off
}
```

### Option C: Proxy Configuration
If you want OpenLiteSpeed to proxy to Django:

```apache
# Django application proxy
context / {
    type                    proxy
    handler                 http://127.0.0.1:8000
    addDefaultCharset      off
}

# Media files (served directly by OpenLiteSpeed)
context /media/ {
    type                    static
    location                /home/testsite.local/media/
    allowBrowse            1
    expires                30d
}

# Static files (served directly by OpenLiteSpeed)
context /static/ {
    type                    static
    location                /home/testsite.local/staticfiles/
    allowBrowse            1
    expires                30d
}
```

## Step 4: Restart OpenLiteSpeed
```bash
# Restart OpenLiteSpeed after configuration changes
sudo systemctl restart lsws

# Check OpenLiteSpeed status
sudo systemctl status lsws
```

## Step 5: Set File Permissions
```bash
# Set proper permissions for media directory
sudo chown -R nobody:nobody /home/testsite.local/media
sudo chmod -R 755 /home/testsite.local/media

# Set proper permissions for static directory
sudo chown -R nobody:nobody /home/testsite.local/staticfiles
sudo chmod -R 755 /home/testsite.local/staticfiles

# Make sure OpenLiteSpeed can read the files
sudo chmod -R 644 /home/testsite.local/media/*
sudo chmod -R 644 /home/testsite.local/staticfiles/*
```

## Step 6: Collect Static Files
```bash
# Navigate to your project
cd /home/testsite.local

# Collect static files
python manage.py collectstatic --noinput
```

## Step 7: Test Configuration
```bash
# Test media files
curl -I http://your-domain.com/media/

# Test static files
curl -I http://your-domain.com/static/

# Check if files exist
ls -la /home/testsite.local/media/
ls -la /home/testsite.local/staticfiles/
```

## Troubleshooting

### Check OpenLiteSpeed Logs
```bash
# Check OpenLiteSpeed error logs
sudo tail -f /usr/local/lsws/logs/error.log

# Check access logs
sudo tail -f /usr/local/lsws/logs/access.log

# Check specific domain logs
sudo tail -f /usr/local/lsws/logs/your-domain.com.log
```

### Check Django Logs
```bash
# Check Django application logs
sudo journalctl -u bethel -f
```

### Common Issues and Solutions

1. **Permission Denied:**
   ```bash
   # Fix ownership
   sudo chown -R nobody:nobody /home/testsite.local/media
   sudo chmod -R 755 /home/testsite.local/media
   ```

2. **Files Not Found:**
   ```bash
   # Check if files exist
   ls -la /home/testsite.local/media/
   
   # Check OpenLiteSpeed configuration
   sudo cat /usr/local/lsws/conf/vhosts/your-domain.com/vhost.conf
   ```

3. **Configuration Not Applied:**
   ```bash
   # Restart OpenLiteSpeed
   sudo systemctl restart lsws
   
   # Check configuration syntax
   sudo /usr/local/lsws/bin/lswsctrl status
   ```

## CyberPanel Integration

If you're using CyberPanel:

1. **Login to CyberPanel** (`http://your-server-ip:8090`)
2. **Go to Websites** → **List Websites**
3. **Click on your domain**
4. **Go to File Manager**
5. **Navigate to `/home/testsite.local/media/`**
6. **Right-click on files** → **Change Permissions**
7. **Set to 644 for files, 755 for directories**

## Expected Result
After following these steps:
- ✅ Media files should be accessible via `/media/` URLs
- ✅ Global hero images and videos should display correctly
- ✅ No 404 errors for media files
- ✅ Better performance with OpenLiteSpeed serving media files directly

## Quick Test Commands
```bash
# 1. Check Django status
sudo systemctl status bethel

# 2. Check OpenLiteSpeed status
sudo systemctl status lsws

# 3. Test media access
curl -I http://localhost/media/

# 4. Check file permissions
ls -la /home/testsite.local/media/

# 5. Check OpenLiteSpeed configuration
sudo cat /usr/local/lsws/conf/vhosts/your-domain.com/vhost.conf
```

## Alternative: Django Fallback Only
If you prefer to keep it simple and let Django serve media files:

```bash
# Just restart Django (this should work immediately)
cd /home/testsite.local
sudo systemctl restart bethel

# Test
curl -I http://your-domain.com/media/
```

This approach works but is slower than having OpenLiteSpeed serve media files directly. 