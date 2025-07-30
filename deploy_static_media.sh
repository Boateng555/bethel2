#!/bin/bash

# Deployment script for Django static and media files on Ubuntu/Nginx
# Run this script as root or with sudo

echo "🚀 Deploying Django static and media files..."

# 1. Create directories
echo "📁 Creating directories..."
sudo mkdir -p /var/www/myproject/static
sudo mkdir -p /var/www/myproject/media

# 2. Set proper ownership and permissions
echo "🔐 Setting permissions..."
sudo chown -R www-data:www-data /var/www/myproject/
sudo chmod -R 755 /var/www/myproject/
sudo chmod -R 644 /var/www/myproject/static/
sudo chmod -R 644 /var/www/myproject/media/

# 3. Collect static files
echo "📦 Collecting static files..."
cd /path/to/your/django/project  # Replace with your actual project path
python manage.py collectstatic --noinput --clear

# 4. Set permissions again after collectstatic
echo "🔐 Setting permissions after collectstatic..."
sudo chown -R www-data:www-data /var/www/myproject/
sudo chmod -R 755 /var/www/myproject/
sudo chmod -R 644 /var/www/myproject/static/
sudo chmod -R 644 /var/www/myproject/media/

# 5. Test Nginx configuration
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
    
    # 6. Reload Nginx
    echo "🔄 Reloading Nginx..."
    sudo systemctl reload nginx
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx reloaded successfully"
    else
        echo "❌ Failed to reload Nginx"
        exit 1
    fi
else
    echo "❌ Nginx configuration test failed"
    exit 1
fi

echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Summary:"
echo "   - Static files: /var/www/myproject/static/ (30-day cache)"
echo "   - Media files: /var/www/myproject/media/ (7-day cache)"
echo "   - Permissions: www-data:www-data (755 for dirs, 644 for files)"
echo ""
echo "🔍 To verify:"
echo "   - Check static files: curl -I http://yourdomain.com/static/admin/css/base.css"
echo "   - Check media files: curl -I http://yourdomain.com/media/your-image.jpg" 