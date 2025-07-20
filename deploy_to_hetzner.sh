#!/bin/bash

# =============================================================================
# Bethel Prayer Ministry - Railway to Hetzner Migration Script
# =============================================================================
# This script helps migrate your Django app from Railway to Hetzner VPS
# =============================================================================

set -e

echo "🚀 Starting Railway to Hetzner Migration"
echo "📅 $(date)"
echo ""

# =============================================================================
# Configuration
# =============================================================================

# Update these variables with your actual values
DOMAIN="your-domain.com"
SERVER_IP="YOUR_HETZNER_IP"
DB_PASSWORD="your_secure_db_password"
SECRET_KEY="your_super_secret_django_key"

# =============================================================================
# Step 1: Backup Railway Data
# =============================================================================

echo "📦 Step 1: Creating Railway backup..."

# Create backup directory
mkdir -p railway_backup
cd railway_backup

# Export environment variables from Railway
echo "🔧 Exporting Railway environment variables..."
# You'll need to manually copy these from Railway dashboard
cat > railway_env.txt << EOF
# Copy your Railway environment variables here
# DATABASE_URL=postgresql://...
# IMAGEKIT_PUBLIC_KEY=...
# IMAGEKIT_PRIVATE_KEY=...
# IMAGEKIT_URL_ENDPOINT=...
EOF

echo "⚠️  Please manually copy your Railway environment variables to railway_env.txt"
echo "   Then press Enter to continue..."
read

# =============================================================================
# Step 2: SSH to Hetzner VPS
# =============================================================================

echo "🔑 Step 2: Connecting to Hetzner VPS..."

# Test SSH connection
if ! ssh -o ConnectTimeout=10 root@$SERVER_IP "echo 'SSH connection successful'"; then
    echo "❌ Failed to connect to Hetzner VPS"
    echo "   Please check your IP address and SSH key setup"
    exit 1
fi

echo "✅ SSH connection established"

# =============================================================================
# Step 3: Run VPS Setup Script
# =============================================================================

echo "🔧 Step 3: Running VPS setup script..."

# Copy setup script to VPS
scp ../hetzner_setup.sh root@$SERVER_IP:/root/

# Run setup script on VPS
ssh root@$SERVER_IP "chmod +x /root/hetzner_setup.sh && /root/hetzner_setup.sh"

echo "✅ VPS setup completed"

# =============================================================================
# Step 4: Configure Environment Variables
# =============================================================================

echo "⚙️ Step 4: Configuring environment variables..."

# Read Railway environment variables
source railway_env.txt

# Create .env file for Hetzner
cat > hetzner.env << EOF
# Django Settings
DEBUG=False
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,$SERVER_IP

# Database Settings
DATABASE_URL=postgresql://bethel_user:$DB_PASSWORD@localhost:5432/bethel_db

# ImageKit Settings (from Railway)
IMAGEKIT_PUBLIC_KEY=$IMAGEKIT_PUBLIC_KEY
IMAGEKIT_PRIVATE_KEY=$IMAGEKIT_PRIVATE_KEY
IMAGEKIT_URL_ENDPOINT=$IMAGEKIT_URL_ENDPOINT

# Security Settings
CSRF_TRUSTED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email Settings (if you have them)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EOF

# Copy .env to VPS
scp hetzner.env root@$SERVER_IP:/home/cyberpanel/public_html/bethel/.env

echo "✅ Environment variables configured"

# =============================================================================
# Step 5: Deploy Django Application
# =============================================================================

echo "🚀 Step 5: Deploying Django application..."

# SSH into VPS and deploy
ssh root@$SERVER_IP << 'EOF'
cd /home/cyberpanel/public_html/bethel

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Set proper permissions
chown -R cyberpanel:cyberpanel /home/cyberpanel/public_html/bethel/
chmod -R 755 /home/cyberpanel/public_html/bethel/

# Start Django service
systemctl start bethel
systemctl enable bethel

# Check service status
systemctl status bethel
EOF

echo "✅ Django application deployed"

# =============================================================================
# Step 6: Configure CyberPanel Website
# =============================================================================

echo "🌐 Step 6: Configuring CyberPanel website..."

echo "📋 Manual steps required in CyberPanel:"
echo "1. Access CyberPanel: https://$SERVER_IP:8090"
echo "2. Login with: admin@example.com / 1234567"
echo "3. Go to Websites → Create Website"
echo "4. Domain: $DOMAIN"
echo "5. SSL: Let's Encrypt"
echo "6. Update Nginx config (see cyberpanel_config.md)"
echo ""

echo "⚠️  Please complete the CyberPanel configuration manually"
echo "   Then press Enter to continue..."
read

# =============================================================================
# Step 7: Test Deployment
# =============================================================================

echo "🧪 Step 7: Testing deployment..."

# Test Django service
if ssh root@$SERVER_IP "systemctl is-active --quiet bethel"; then
    echo "✅ Django service is running"
else
    echo "❌ Django service is not running"
    ssh root@$SERVER_IP "systemctl status bethel"
fi

# Test database connection
if ssh root@$SERVER_IP "sudo -u postgres psql -d bethel_db -c 'SELECT 1;'"; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
fi

# Test static files
if ssh root@$SERVER_IP "ls -la /home/cyberpanel/public_html/bethel/staticfiles/"; then
    echo "✅ Static files collected"
else
    echo "❌ Static files not found"
fi

# =============================================================================
# Step 8: Setup Monitoring and Backups
# =============================================================================

echo "📊 Step 8: Setting up monitoring and backups..."

ssh root@$SERVER_IP << 'EOF'
# Create monitoring cron job
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/cyberpanel/public_html/bethel/monitor.sh") | crontab -

# Create daily backup cron job
(crontab -l 2>/dev/null; echo "0 2 * * * /home/cyberpanel/public_html/bethel/backup.sh") | crontab -

# Test backup script
/home/cyberpanel/public_html/bethel/backup.sh
EOF

echo "✅ Monitoring and backups configured"

# =============================================================================
# Step 9: Security Hardening
# =============================================================================

echo "🔒 Step 9: Security hardening..."

ssh root@$SERVER_IP << 'EOF'
# Update system
apt update && apt upgrade -y

# Configure firewall
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8090/tcp
ufw --force enable

# Enable fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# Set up automatic security updates
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
EOF

echo "✅ Security hardening completed"

# =============================================================================
# Step 10: Final Verification
# =============================================================================

echo "✅ Step 10: Final verification..."

echo "🔍 Testing application endpoints..."

# Test health endpoint
if curl -s "http://$SERVER_IP:8000/health/" > /dev/null; then
    echo "✅ Health endpoint accessible"
else
    echo "❌ Health endpoint not accessible"
fi

# Test static files
if curl -s "http://$SERVER_IP/static/admin/css/base.css" > /dev/null; then
    echo "✅ Static files accessible"
else
    echo "❌ Static files not accessible"
fi

# =============================================================================
# Migration Complete
# =============================================================================

echo ""
echo "🎉 Migration completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Update DNS records to point to $SERVER_IP"
echo "2. Test your website at https://$DOMAIN"
echo "3. Configure SSL certificate in CyberPanel"
echo "4. Set up email notifications"
echo "5. Monitor logs for any issues"
echo "6. Disable Railway deployment after testing"
echo ""
echo "🔧 Useful Commands:"
echo "- SSH to VPS: ssh root@$SERVER_IP"
echo "- Check Django: systemctl status bethel"
echo "- View logs: journalctl -u bethel -f"
echo "- Backup: /home/cyberpanel/public_html/bethel/backup.sh"
echo "- Monitor: /home/cyberpanel/public_html/bethel/monitor.sh"
echo ""
echo "📁 Important Paths:"
echo "- Django app: /home/cyberpanel/public_html/bethel/"
echo "- Logs: /home/cyberpanel/public_html/bethel/logs/"
echo "- Backups: /home/cyberpanel/backups/bethel/"
echo "- CyberPanel: https://$SERVER_IP:8090"
echo ""
echo "🔒 Security Notes:"
echo "- Change default passwords immediately"
echo "- Update .env file with secure values"
echo "- Configure firewall rules"
echo "- Set up regular backups"
echo ""
echo "✅ Railway to Hetzner migration completed!" 