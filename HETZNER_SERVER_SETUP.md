# Hetzner Server Setup Guide

## Current Issue
Your Hetzner server doesn't have nginx installed, but Django is already configured to serve media files in production.

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

## Step 3: Check What Web Server You're Using
Since nginx is not installed, let's check what web server you're using:

```bash
# Check what's listening on port 80/443
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Check for Apache
sudo systemctl status apache2

# Check for other web servers
ps aux | grep -E "(apache|httpd|nginx|lighttpd)"
```

## Step 4: Install and Configure Nginx (Recommended)
For better performance, install nginx:

```bash
# Update package list
sudo apt update

# Install nginx
sudo apt install nginx

# Start nginx
sudo systemctl start nginx

# Enable nginx to start on boot
sudo systemctl enable nginx

# Check nginx status
sudo systemctl status nginx
```

## Step 5: Configure Nginx for Your Django App
Create nginx configuration:

```bash
# Create nginx site configuration
sudo nano /etc/nginx/sites-available/bethel
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Django application
    location / {
        proxy_pass http://unix:/home/testsite.local/bethel.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Serve static files
    location /static/ {
        alias /home/testsite.local/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Serve media files
    location /media/ {
        alias /home/testsite.local/media/;
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
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
}
```

Enable the site:
```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/bethel /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

## Step 6: Set File Permissions
```bash
# Set proper permissions for media directory
sudo chown -R www-data:www-data /home/testsite.local/media
sudo chmod -R 755 /home/testsite.local/media

# Set proper permissions for static directory
sudo chown -R www-data:www-data /home/testsite.local/staticfiles
sudo chmod -R 755 /home/testsite.local/staticfiles
```

## Step 7: Collect Static Files
```bash
# Navigate to your project
cd /home/testsite.local

# Collect static files
python manage.py collectstatic --noinput
```

## Alternative: Use Apache (if already installed)
If you have Apache installed instead of nginx:

```bash
# Check Apache status
sudo systemctl status apache2

# If Apache is running, configure it for Django
sudo nano /etc/apache2/sites-available/bethel.conf
```

Add this Apache configuration:
```apache
<VirtualHost *:80>
    ServerName your-domain.com
    ServerAlias www.your-domain.com
    
    DocumentRoot /home/testsite.local
    
    Alias /static/ /home/testsite.local/staticfiles/
    Alias /media/ /home/testsite.local/media/
    
    <Directory /home/testsite.local/staticfiles>
        Require all granted
    </Directory>
    
    <Directory /home/testsite.local/media>
        Require all granted
    </Directory>
    
    ProxyPreserveHost On
    ProxyPass / http://unix:/home/testsite.local/bethel.sock
    ProxyPassReverse / http://unix:/home/testsite.local/bethel.sock
</VirtualHost>
```

Enable the site:
```bash
sudo a2ensite bethel.conf
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo systemctl reload apache2
```

## Troubleshooting

### Check Django Logs
```bash
# Check Django application logs
sudo journalctl -u bethel -f
```

### Check Web Server Logs
```bash
# For nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# For Apache
sudo tail -f /var/log/apache2/error.log
sudo tail -f /var/log/apache2/access.log
```

### Test Media Files
```bash
# Test from server
curl -I http://localhost/media/
curl -I http://your-domain.com/media/

# Check if files exist
ls -la /home/testsite.local/media/
```

## Expected Result
After following these steps:
- ✅ Media files should be accessible via `/media/` URLs
- ✅ Global hero images and videos should display correctly
- ✅ No 404 errors for media files
- ✅ Better performance with proper web server configuration

## Quick Test Commands
Run these commands to test your setup:

```bash
# 1. Check Django status
sudo systemctl status bethel

# 2. Check web server status
sudo systemctl status nginx  # or apache2

# 3. Test media access
curl -I http://localhost/media/

# 4. Check file permissions
ls -la /home/testsite.local/media/
``` 