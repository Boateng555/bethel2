#!/bin/bash
# Production Deployment Script for Local Storage

set -e

echo "🚀 Deploying Bethel Prayer Ministry with Local Storage"
echo "📅 $(date)"
echo ""

# Configuration
REMOTE_PATH="/home/cyberpanel/public_html/bethel"
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"

echo "📦 Creating backup..."
if [ -d "$REMOTE_PATH" ]; then
    cp -r "$REMOTE_PATH" "$BACKUP_DIR"
    echo "✅ Backup created: $BACKUP_DIR"
else
    echo "ℹ️ No existing deployment to backup"
fi

echo "📁 Creating directories..."
mkdir -p "$REMOTE_PATH"
mkdir -p "$REMOTE_PATH/media/ministries"
mkdir -p "$REMOTE_PATH/media/churches"
mkdir -p "$REMOTE_PATH/media/hero"
mkdir -p "$REMOTE_PATH/media/news"
mkdir -p "$REMOTE_PATH/media/sermons"

echo "📤 Copying files..."
cp -r * "$REMOTE_PATH/"

echo "🐍 Setting up Python environment..."
cd "$REMOTE_PATH"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🔄 Running migrations..."
python manage.py migrate

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🔐 Setting permissions..."
chown -R cyberpanel:cyberpanel "$REMOTE_PATH/"
chmod -R 755 "$REMOTE_PATH/"
chmod -R 777 "$REMOTE_PATH/media/"

echo "🔄 Restarting Django service..."
systemctl restart bethel

echo "📊 Checking service status..."
systemctl status bethel --no-pager

echo ""
echo "🎉 Deployment completed successfully!"
echo "🌐 Your site should be available at: http://91.99.232.214"
echo "📁 Media files are stored at: $REMOTE_PATH/media/"
echo ""
echo "📋 Next steps:"
echo "1. Test your website functionality"
echo "2. Check that ministry images are displaying correctly"
echo "3. Upload new images through the admin interface"
