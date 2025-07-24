#!/bin/bash

# =============================================================================
# Production Deployment Script for Bethel Prayer Ministry
# =============================================================================
# Deploy to Hetzner VPS with ImageKit and PostgreSQL
# =============================================================================

set -e

echo "🚀 Starting Production Deployment to Hetzner"
echo "📅 $(date)"
echo ""

# =============================================================================
# Configuration - UPDATE THESE VALUES
# =============================================================================

SERVER_IP="91.99.232.214"
DOMAIN="your-domain.com"
DB_PASSWORD="bethel_secure_password_2024"
SECRET_KEY="your_super_secret_django_key"

# ImageKit credentials (get from ImageKit dashboard)
IMAGEKIT_PUBLIC_KEY="public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU="
IMAGEKIT_PRIVATE_KEY="private_Dnsrj2VW7uJakaeMaNYaav+P784="
IMAGEKIT_URL_ENDPOINT="https://ik.imagekit.io/9buar9mbp"

# =============================================================================
# Step 1: Generate Secret Key
# =============================================================================

echo "🔑 Step 1: Generating Django secret key..."
if [ "$SECRET_KEY" = "your_super_secret_django_key" ]; then
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    echo "✅ Generated new secret key: $SECRET_KEY"
fi

# =============================================================================
# Step 2: Create Production Environment File
# =============================================================================

echo "⚙️ Step 2: Creating production environment file..."

cat > production.env << EOF
# Django Settings
DEBUG=False
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,$SERVER_IP

# Database Settings (PostgreSQL on Hetzner)
DATABASE_URL=postgresql://bethel_user:$DB_PASSWORD@localhost:5432/bethel_db

# ImageKit Settings (for media files)
IMAGEKIT_PUBLIC_KEY=$IMAGEKIT_PUBLIC_KEY
IMAGEKIT_PRIVATE_KEY=$IMAGEKIT_PRIVATE_KEY
IMAGEKIT_URL_ENDPOINT=$IMAGEKIT_URL_ENDPOINT

# Gunicorn Settings
WEB_CONCURRENCY=2
PYTHONUNBUFFERED=1

# Database optimization
CONN_MAX_AGE=300

# Memory optimization
PYTHONHASHSEED=random
PYTHONDONTWRITEBYTECODE=1

# Security
CSRF_TRUSTED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

# Static files
STATIC_ROOT=/home/cyberpanel/public_html/bethel/staticfiles
MEDIA_ROOT=/home/cyberpanel/public_html/bethel/media

# Logging
LOG_LEVEL=INFO
EOF

echo "✅ Production environment file created"

# =============================================================================
# Step 3: Deploy to Hetzner VPS
# =============================================================================

echo "🔑 Step 3: Deploying to Hetzner VPS..."

# Test SSH connection
if ! ssh -o ConnectTimeout=10 root@$SERVER_IP "echo 'SSH connection successful'"; then
    echo "❌ Failed to connect to Hetzner VPS"
    echo "   Please check your IP address and SSH key setup"
    exit 1
fi

echo "✅ SSH connection established"

# Copy environment file to server
scp production.env root@$SERVER_IP:/home/cyberpanel/public_html/bethel/

# Deploy on server
ssh root@$SERVER_IP << 'EOF'
cd /home/cyberpanel/public_html/bethel

echo "📥 Pulling latest code from git..."
git pull origin main

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing/updating dependencies..."
pip install -r requirements.txt

echo "⚙️ Loading production environment..."
export $(cat production.env | xargs)

echo "🗄️ Running database migrations..."
python manage.py migrate

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "🔄 Restarting Gunicorn service..."
systemctl restart bethel-gunicorn

echo "🔄 Restarting Nginx..."
systemctl restart nginx

echo "✅ Deployment completed!"
EOF

echo "🎉 Production deployment completed successfully!"
echo ""
echo "🌐 Your site should be available at: https://$DOMAIN"
echo "📧 Check logs if needed: ssh root@$SERVER_IP 'journalctl -u bethel-gunicorn -f'" 