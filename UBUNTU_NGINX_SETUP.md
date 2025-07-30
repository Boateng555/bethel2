# Ubuntu/Nginx Django Static & Media Files Setup

## 1. Django Settings Updates ✅

Your `backend/settings.py` has been updated with:
```python
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/myproject/static'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/myproject/media'
```

## 2. Nginx Configuration

Add these location blocks to your existing `/etc/nginx/sites-available/myproject`:

```nginx
# Static files - served directly by Nginx with 30-day cache
location /static/ {
    alias /var/www/myproject/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    
    # Gzip compression for static files
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}

# Media files - served directly by Nginx with 7-day cache
location /media/ {
    alias /var/www/myproject/media/;
    expires 7d;
    add_header Cache-Control "public";
    add_header X-Content-Type-Options nosniff;
    
    # Gzip compression for media files
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}

# Optional: Add security for common file types
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
    add_header X-Content-Type-Options nosniff;
}
```

## 3. Manual Deployment Commands

Run these commands in order:

### Create directories and set permissions:
```bash
# Create directories
sudo mkdir -p /var/www/myproject/static
sudo mkdir -p /var/www/myproject/media

# Set ownership
sudo chown -R www-data:www-data /var/www/myproject/

# Set permissions
sudo chmod -R 755 /var/www/myproject/
sudo chmod -R 644 /var/www/myproject/static/
sudo chmod -R 644 /var/www/myproject/media/
```

### Collect static files:
```bash
# Navigate to your Django project directory
cd /path/to/your/django/project

# Collect static files
python manage.py collectstatic --noinput --clear
```

### Set permissions again after collectstatic:
```bash
sudo chown -R www-data:www-data /var/www/myproject/
sudo chmod -R 755 /var/www/myproject/
sudo chmod -R 644 /var/www/myproject/static/
sudo chmod -R 644 /var/www/myproject/media/
```

### Test and reload Nginx:
```bash
# Test Nginx configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx
```

## 4. Verification

Test that everything is working:

```bash
# Test static files
curl -I http://yourdomain.com/static/admin/css/base.css

# Test media files
curl -I http://yourdomain.com/media/your-image.jpg
```

You should see:
- HTTP 200 status
- Cache headers (expires, cache-control)
- Content-Type headers

## 5. Troubleshooting

### If Nginx test fails:
```bash
# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check Nginx configuration syntax
sudo nginx -t -c /etc/nginx/nginx.conf
```

### If files aren't accessible:
```bash
# Check file permissions
ls -la /var/www/myproject/static/
ls -la /var/www/myproject/media/

# Check Nginx user can read files
sudo -u www-data ls /var/www/myproject/static/
sudo -u www-data ls /var/www/myproject/media/
```

### If collectstatic fails:
```bash
# Check Django settings
python manage.py check

# Check static files configuration
python manage.py collectstatic --dry-run
```

## 6. Security Notes

- Static files have 30-day cache with `immutable` flag
- Media files have 7-day cache (shorter for user uploads)
- Security headers are added to prevent common attacks
- Gzip compression is enabled for better performance
- File permissions are set to 644 (read-only for web server)

## 7. Performance Benefits

- Static files served directly by Nginx (no Django overhead)
- Proper caching headers reduce server load
- Gzip compression reduces bandwidth usage
- Security headers protect against common vulnerabilities 