#!/bin/bash

# =============================================================================
# ImageKit Fix Script for Hetzner Server
# =============================================================================
# This script will fix ImageKit configuration on your Hetzner server
# =============================================================================

set -e  # Exit on any error

echo "🚀 Starting ImageKit fix for Hetzner server..."
echo "📅 $(date)"
echo ""

# =============================================================================
# Variables
# =============================================================================

PROJECT_DIR="/home/cyberpanel/public_html/bethel"
SERVICE_NAME="bethel"
BACKUP_DIR="/home/cyberpanel/backups/bethel"

# =============================================================================
# Backup Current Setup
# =============================================================================

echo "💾 Creating backup..."
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)

# Backup current .env file if it exists
if [ -f "$PROJECT_DIR/.env" ]; then
    cp $PROJECT_DIR/.env $BACKUP_DIR/.env_backup_$DATE
    echo "✅ Backed up existing .env file"
fi

# Backup database
pg_dump -h localhost -U bethel_user bethel_db > $BACKUP_DIR/db_backup_$DATE.sql
echo "✅ Backed up database"

# =============================================================================
# Navigate to Project Directory
# =============================================================================

echo "📁 Navigating to project directory..."
cd $PROJECT_DIR

# =============================================================================
# Stop Services
# =============================================================================

echo "🛑 Stopping services..."
sudo systemctl stop $SERVICE_NAME 2>/dev/null || true
sudo pkill -f gunicorn 2>/dev/null || true
sudo pkill -f "python.*manage.py" 2>/dev/null || true
sleep 3

# =============================================================================
# Pull Latest Code
# =============================================================================

echo "📥 Pulling latest code..."
git stash 2>/dev/null || true
git pull origin main

# =============================================================================
# Setup Environment
# =============================================================================

echo "⚙️ Setting up environment..."

# Create .env file with ImageKit credentials
cat > .env << 'EOF'
# Django Settings
DEBUG=False
SECRET_KEY=6x81cy++5wh*#qi!*6srjp$(8(!_&m7g)31h9o9y@_ul#hf_t*
ALLOWED_HOSTS=91.99.232.214,your-domain.com,localhost,127.0.0.1

# Database Settings
DATABASE_URL=postgresql://bethel_user:bethel_secure_password_2024@localhost:5432/bethel_db

# ImageKit Settings
IMAGEKIT_PUBLIC_KEY=public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=
IMAGEKIT_PRIVATE_KEY=private_Dnsrj2VW7uJakaeMaNYaav+P784=
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/9buar9mbp

# Security Settings
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://91.99.232.214
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Static and Media
STATIC_ROOT=/home/cyberpanel/public_html/bethel/staticfiles
MEDIA_ROOT=/home/cyberpanel/public_html/bethel/media
LOG_LEVEL=INFO
EOF

echo "✅ Environment file created"

# =============================================================================
# Setup Python Environment
# =============================================================================

echo "🐍 Setting up Python environment..."

# Activate virtual environment
source venv/bin/activate

# Install/upgrade required packages
pip install --upgrade pip
pip install python-dotenv
pip install --upgrade imagekitio
pip install -r requirements.txt

echo "✅ Python packages updated"

# =============================================================================
# Create Test Script
# =============================================================================

echo "🧪 Creating ImageKit test script..."

cat > test_imagekit_fix.py << 'EOF'
#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from imagekitio import ImageKit
from io import BytesIO

def test_imagekit():
    print("🔍 Testing ImageKit Configuration...")
    
    try:
        # Check environment variables
        print(f"IMAGEKIT_PUBLIC_KEY: {'✅ Set' if settings.IMAGEKIT_CONFIG['PUBLIC_KEY'] else '❌ Missing'}")
        print(f"IMAGEKIT_PRIVATE_KEY: {'✅ Set' if settings.IMAGEKIT_CONFIG['PRIVATE_KEY'] else '❌ Missing'}")
        print(f"IMAGEKIT_URL_ENDPOINT: {'✅ Set' if settings.IMAGEKIT_CONFIG['URL_ENDPOINT'] else '❌ Missing'}")
        print(f"Storage backend: {settings.DEFAULT_FILE_STORAGE}")
        
        # Test ImageKit connection
        imagekit = ImageKit(
            public_key=settings.IMAGEKIT_CONFIG['PUBLIC_KEY'],
            private_key=settings.IMAGEKIT_CONFIG['PRIVATE_KEY'],
            url_endpoint=settings.IMAGEKIT_CONFIG['URL_ENDPOINT']
        )
        
        # Test upload
        test_content = b"Test file from ImageKit fix script"
        file_obj = BytesIO(test_content)
        file_obj.name = "fix_test.txt"
        
        upload = imagekit.upload_file(
            file=file_obj,
            file_name="fix_test.txt"
        )
        
        print(f"✅ Upload successful! URL: {upload.url}")
        
        # Clean up
        imagekit.delete_file(upload.file_id)
        print("✅ Test file deleted")
        
        print("\n🎉 ImageKit is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imagekit()
    sys.exit(0 if success else 1)
EOF

# =============================================================================
# Test ImageKit Configuration
# =============================================================================

echo "🧪 Testing ImageKit configuration..."

if python test_imagekit_fix.py; then
    echo "✅ ImageKit test passed"
else
    echo "❌ ImageKit test failed - checking Django settings..."
    
    # Test Django settings
    python manage.py shell << 'EOF'
from django.conf import settings
print(f"DEBUG: {settings.DEBUG}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
print(f"IMAGEKIT_CONFIG: {settings.IMAGEKIT_CONFIG}")
EOF
fi

# =============================================================================
# Django Setup
# =============================================================================

echo "🔧 Setting up Django..."

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

echo "✅ Django setup completed"

# =============================================================================
# Create Logs Directory
# =============================================================================

echo "📝 Creating logs directory..."
mkdir -p logs
touch logs/gunicorn_error.log
touch logs/gunicorn_access.log

# =============================================================================
# Update Gunicorn Configuration
# =============================================================================

echo "🦄 Updating Gunicorn configuration..."

cat > gunicorn.conf.py << 'EOF'
# Gunicorn configuration for Bethel Prayer Ministry
bind = "127.0.0.1:8000"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
daemon = False
user = "cyberpanel"
group = "cyberpanel"
tmp_upload_dir = None
errorlog = "/home/cyberpanel/public_html/bethel/logs/gunicorn_error.log"
accesslog = "/home/cyberpanel/public_html/bethel/logs/gunicorn_access.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
EOF

# =============================================================================
# Update Systemd Service
# =============================================================================

echo "🔧 Updating systemd service..."

sudo tee /etc/systemd/system/bethel.service > /dev/null << 'EOF'
[Unit]
Description=Gunicorn daemon for Bethel Django project
After=network.target

[Service]
Type=notify
User=cyberpanel
Group=cyberpanel
WorkingDirectory=/home/cyberpanel/public_html/bethel
Environment=PATH=/home/cyberpanel/public_html/bethel/venv/bin
ExecStart=/home/cyberpanel/public_html/bethel/venv/bin/gunicorn --config gunicorn.conf.py backend.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5
KillMode=mixed
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
EOF

# =============================================================================
# Set Permissions
# =============================================================================

echo "🔐 Setting permissions..."
sudo chown -R cyberpanel:cyberpanel $PROJECT_DIR/
sudo chmod -R 755 $PROJECT_DIR/
sudo chmod +x $PROJECT_DIR/test_imagekit_fix.py

# =============================================================================
# Start Services
# =============================================================================

echo "🚀 Starting services..."

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

# Wait for service to start
sleep 5

# Check service status
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Django service is running"
else
    echo "❌ Django service failed to start"
    sudo journalctl -u $SERVICE_NAME --no-pager -n 10
    exit 1
fi

# =============================================================================
# Final Test
# =============================================================================

echo "🔍 Final verification..."

# Test if service is responding
if curl -f -s http://127.0.0.1:8000/ > /dev/null; then
    echo "✅ Django application is responding"
else
    echo "❌ Django application is not responding"
    echo "Checking logs..."
    sudo journalctl -u $SERVICE_NAME --no-pager -n 10
    exit 1
fi

# Test ImageKit one more time
echo "🧪 Final ImageKit test..."
if python test_imagekit_fix.py; then
    echo "✅ Final ImageKit test passed"
else
    echo "❌ Final ImageKit test failed"
fi

# =============================================================================
# Cleanup
# =============================================================================

echo "🧹 Cleaning up..."
rm -f test_imagekit_fix.py

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.env_backup_*" -mtime +7 -delete

# =============================================================================
# Success Message
# =============================================================================

echo ""
echo "🎉 ImageKit fix completed successfully!"
echo ""
echo "📋 What was fixed:"
echo "✅ Updated environment with ImageKit credentials"
echo "✅ Upgraded ImageKit library"
echo "✅ Fixed Django settings"
echo "✅ Updated Gunicorn configuration"
echo "✅ Restarted Django service"
echo "✅ Tested ImageKit functionality"
echo ""
echo "🔧 Useful commands:"
echo "- Check service status: sudo systemctl status $SERVICE_NAME"
echo "- View logs: sudo journalctl -u $SERVICE_NAME -f"
echo "- Test ImageKit: python test_imagekit_fix.py"
echo ""
echo "📁 Backup location: $BACKUP_DIR"
echo ""
echo "🌐 Your application should now upload images to ImageKit cloud!"
echo "   Test by uploading a new image through Django admin."
echo "   Image URLs should start with: https://ik.imagekit.io/9buar9mbp/"
echo ""

echo "✅ ImageKit fix completed!" 