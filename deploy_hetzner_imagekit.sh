#!/bin/bash

# =============================================================================
# Hetzner ImageKit Deployment Script
# =============================================================================
# This script updates the Hetzner server with ImageKit fixes
# =============================================================================

set -e  # Exit on any error

echo "🚀 Starting ImageKit deployment on Hetzner server..."
echo "📅 $(date)"
echo ""

# =============================================================================
# Variables
# =============================================================================

PROJECT_DIR="/home/cyberpanel/public_html/bethel"
SERVICE_NAME="bethel"

# =============================================================================
# Backup Current Setup
# =============================================================================

echo "💾 Creating backup..."
BACKUP_DIR="/home/cyberpanel/backups/bethel"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup current .env file
cp $PROJECT_DIR/.env $BACKUP_DIR/.env_backup_$DATE

# Backup database
pg_dump -h localhost -U bethel_user bethel_db > $BACKUP_DIR/db_backup_$DATE.sql

echo "✅ Backup completed: $BACKUP_DIR"

# =============================================================================
# Update Code
# =============================================================================

echo "📥 Pulling latest code..."
cd $PROJECT_DIR

# Stash any local changes
git stash

# Pull latest code
git pull origin main

echo "✅ Code updated"

# =============================================================================
# Update Environment
# =============================================================================

echo "⚙️ Updating environment configuration..."

# Create new .env file with ImageKit credentials
cat > .env << EOF
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

echo "✅ Environment updated"

# =============================================================================
# Update Python Dependencies
# =============================================================================

echo "🐍 Updating Python dependencies..."

# Activate virtual environment
source venv/bin/activate

# Upgrade ImageKit library
pip install --upgrade imagekitio

# Install any new requirements
pip install -r requirements.txt

echo "✅ Dependencies updated"

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
# Test ImageKit Configuration
# =============================================================================

echo "🧪 Testing ImageKit configuration..."

# Create test script
cat > test_imagekit_hetzner.py << 'EOF'
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
    print("🔍 Testing ImageKit on Hetzner Server...")
    
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
        test_content = b"Test file from Hetzner server deployment"
        file_obj = BytesIO(test_content)
        file_obj.name = "hetzner_deploy_test.txt"
        
        upload = imagekit.upload_file(
            file=file_obj,
            file_name="hetzner_deploy_test.txt"
        )
        
        print(f"✅ Upload successful! URL: {upload.url}")
        
        # Clean up
        imagekit.delete_file(upload.file_id)
        print("✅ Test file deleted")
        
        print("\n🎉 ImageKit is working on Hetzner server!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_imagekit()
    sys.exit(0 if success else 1)
EOF

# Run the test
if python test_imagekit_hetzner.py; then
    echo "✅ ImageKit test passed"
else
    echo "❌ ImageKit test failed"
    exit 1
fi

# =============================================================================
# Restart Services
# =============================================================================

echo "🔄 Restarting Django service..."

# Restart the Django service
systemctl restart $SERVICE_NAME

# Wait a moment for service to start
sleep 5

# Check service status
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Django service is running"
else
    echo "❌ Django service failed to start"
    journalctl -u $SERVICE_NAME --no-pager -n 20
    exit 1
fi

# =============================================================================
# Final Verification
# =============================================================================

echo "🔍 Final verification..."

# Check if service is responding
if curl -f -s http://127.0.0.1:8000/ > /dev/null; then
    echo "✅ Django application is responding"
else
    echo "❌ Django application is not responding"
    exit 1
fi

# =============================================================================
# Cleanup
# =============================================================================

echo "🧹 Cleaning up..."

# Remove test script
rm -f test_imagekit_hetzner.py

# Set proper permissions
chown -R cyberpanel:cyberpanel $PROJECT_DIR/
chmod -R 755 $PROJECT_DIR/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.env_backup_*" -mtime +7 -delete

# =============================================================================
# Success Message
# =============================================================================

echo ""
echo "🎉 ImageKit deployment completed successfully!"
echo ""
echo "📋 What was updated:"
echo "✅ Latest code with ImageKit fixes"
echo "✅ ImageKit environment variables"
echo "✅ Upgraded ImageKit library"
echo "✅ Django migrations and static files"
echo "✅ Service restarted and verified"
echo ""
echo "🔧 Useful commands:"
echo "- Check service status: systemctl status $SERVICE_NAME"
echo "- View logs: journalctl -u $SERVICE_NAME -f"
echo "- Test ImageKit: python test_imagekit_hetzner.py"
echo ""
echo "📁 Backup location: $BACKUP_DIR"
echo ""
echo "🌐 Your application should now upload images to ImageKit cloud!"
echo "   Test by uploading a new image through Django admin."
echo ""

echo "✅ Hetzner ImageKit deployment completed!" 