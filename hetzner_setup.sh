#!/bin/bash

# =============================================================================
# Hetzner VPS Setup Script for Bethel Prayer Ministry
# =============================================================================
# This script sets up a fresh Hetzner VPS with CyberPanel and Django deployment
# =============================================================================

set -e  # Exit on any error

echo "🚀 Starting Hetzner VPS Setup for Bethel Prayer Ministry"
echo "📅 $(date)"
echo ""

# =============================================================================
# System Update & Basic Setup
# =============================================================================

echo "🔄 Updating system packages..."
apt update && apt upgrade -y

echo "📦 Installing essential packages..."
apt install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    htop \
    nano \
    vim \
    ufw \
    fail2ban

# =============================================================================
# CyberPanel Installation
# =============================================================================

echo "🔧 Installing CyberPanel..."
cd /usr/local/src
wget -O - https://cyberpanel.net/install.sh | bash

echo "✅ CyberPanel installation completed!"
echo "🌐 CyberPanel URL: https://YOUR_SERVER_IP:8090"
echo "📧 Default admin email: admin@example.com"
echo "🔑 Default password: 1234567"

# =============================================================================
# PostgreSQL Installation
# =============================================================================

echo "🐘 Installing PostgreSQL..."
apt install -y postgresql postgresql-contrib

# Start and enable PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Create database and user for Django
echo "🗄️ Setting up PostgreSQL database..."
sudo -u postgres psql << EOF
CREATE DATABASE bethel_db;
CREATE USER bethel_user WITH PASSWORD 'bethel_secure_password_2024';
ALTER ROLE bethel_user SET client_encoding TO 'utf8';
ALTER ROLE bethel_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE bethel_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE bethel_db TO bethel_user;
\q
EOF

echo "✅ PostgreSQL setup completed!"

# =============================================================================
# Python & Dependencies
# =============================================================================

echo "🐍 Installing Python and dependencies..."
apt install -y python3 python3-pip python3-venv python3-dev
apt install -y build-essential libpq-dev

# Create application directory
mkdir -p /home/cyberpanel/public_html/bethel
cd /home/cyberpanel/public_html/bethel

# =============================================================================
# Clone Django Project
# =============================================================================

echo "📥 Cloning Django project..."
git clone https://github.com/Boateng555/bethel2.git .

# Create virtual environment
echo "🔧 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# =============================================================================
# Environment Configuration
# =============================================================================

echo "⚙️ Setting up environment variables..."
cat > .env << EOF
# Django Settings
DEBUG=False
SECRET_KEY=your_super_secret_key_here_change_this_in_production
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,YOUR_SERVER_IP

# Database Settings
DATABASE_URL=postgresql://bethel_user:bethel_secure_password_2024@localhost:5432/bethel_db

# ImageKit Settings
IMAGEKIT_PUBLIC_KEY=your_imagekit_public_key
IMAGEKIT_PRIVATE_KEY=your_imagekit_private_key
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_endpoint

# Email Settings (if needed)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security Settings
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
EOF

echo "✅ Environment configuration completed!"

# =============================================================================
# Django Setup
# =============================================================================

echo "🔧 Setting up Django..."
python manage.py collectstatic --noinput
python manage.py migrate

# Create superuser (optional)
echo "👤 Creating superuser..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@bethel.com', 'admin_password_2024')" | python manage.py shell

# =============================================================================
# Gunicorn Configuration
# =============================================================================

echo "🦄 Setting up Gunicorn..."
cat > gunicorn.conf.py << EOF
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

# Create logs directory
mkdir -p logs

# =============================================================================
# Systemd Service
# =============================================================================

echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/bethel.service << EOF
[Unit]
Description=Bethel Prayer Ministry Django Application
After=network.target

[Service]
Type=notify
User=cyberpanel
Group=cyberpanel
WorkingDirectory=/home/cyberpanel/public_html/bethel
Environment=PATH=/home/cyberpanel/public_html/bethel/venv/bin
ExecStart=/home/cyberpanel/public_html/bethel/venv/bin/gunicorn --config gunicorn.conf.py backend.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable bethel
systemctl start bethel

# =============================================================================
# Nginx Configuration (for CyberPanel)
# =============================================================================

echo "🌐 Setting up Nginx configuration..."
cat > /home/cyberpanel/public_html/bethel/nginx.conf << EOF
# Nginx configuration for Bethel Prayer Ministry
# This will be used in CyberPanel

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL configuration (CyberPanel will handle this)
    ssl_certificate /home/cyberpanel/public_html/your-domain.com/ssl/your-domain.com.crt;
    ssl_certificate_key /home/cyberpanel/public_html/your-domain.com/ssl/your-domain.com.key;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Static files
    location /static/ {
        alias /home/cyberpanel/public_html/bethel/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /home/cyberpanel/public_html/bethel/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint
    location /health/ {
        proxy_pass http://127.0.0.1:8000/health/;
        access_log off;
    }
}
EOF

# =============================================================================
# Security Setup
# =============================================================================

echo "🔒 Setting up security..."

# Configure UFW firewall
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8090/tcp  # CyberPanel
ufw --force enable

# Configure fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# =============================================================================
# Backup Script
# =============================================================================

echo "💾 Creating backup script..."
cat > /home/cyberpanel/public_html/bethel/backup.sh << 'EOF'
#!/bin/bash

# Backup script for Bethel Prayer Ministry
BACKUP_DIR="/home/cyberpanel/backups/bethel"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump -h localhost -U bethel_user bethel_db > $BACKUP_DIR/db_backup_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz -C /home/cyberpanel/public_html/bethel media/

# Backup code (excluding venv and logs)
tar -czf $BACKUP_DIR/code_backup_$DATE.tar.gz \
    --exclude='venv' \
    --exclude='logs' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    -C /home/cyberpanel/public_html/bethel .

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /home/cyberpanel/public_html/bethel/backup.sh

# =============================================================================
# Monitoring Script
# =============================================================================

echo "📊 Creating monitoring script..."
cat > /home/cyberpanel/public_html/bethel/monitor.sh << 'EOF'
#!/bin/bash

# Monitoring script for Bethel Prayer Ministry
LOG_FILE="/home/cyberpanel/public_html/bethel/logs/monitor.log"

echo "$(date): Starting health check..." >> $LOG_FILE

# Check if Django app is running
if ! systemctl is-active --quiet bethel; then
    echo "$(date): Django app is down! Restarting..." >> $LOG_FILE
    systemctl restart bethel
fi

# Check database connectivity
if ! sudo -u postgres psql -d bethel_db -c "SELECT 1;" > /dev/null 2>&1; then
    echo "$(date): Database connection failed!" >> $LOG_FILE
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Disk usage is high: ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.2f", $3*100/$2}')
if (( $(echo "$MEM_USAGE > 80" | bc -l) )); then
    echo "$(date): Memory usage is high: ${MEM_USAGE}%" >> $LOG_FILE
fi

echo "$(date): Health check completed" >> $LOG_FILE
EOF

chmod +x /home/cyberpanel/public_html/bethel/monitor.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/cyberpanel/public_html/bethel/monitor.sh") | crontab -

# =============================================================================
# Final Setup
# =============================================================================

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Access CyberPanel: https://YOUR_SERVER_IP:8090"
echo "2. Login with: admin@example.com / 1234567"
echo "3. Create a new website in CyberPanel"
echo "4. Configure SSL certificate"
echo "5. Update .env file with your actual values"
echo "6. Test your Django application"
echo ""
echo "🔧 Useful Commands:"
echo "- Check Django status: systemctl status bethel"
echo "- View logs: journalctl -u bethel -f"
echo "- Restart Django: systemctl restart bethel"
echo "- Backup: /home/cyberpanel/public_html/bethel/backup.sh"
echo ""
echo "📁 Important Directories:"
echo "- Django app: /home/cyberpanel/public_html/bethel/"
echo "- Logs: /home/cyberpanel/public_html/bethel/logs/"
echo "- Backups: /home/cyberpanel/backups/bethel/"
echo ""
echo "🔒 Security Notes:"
echo "- Change default passwords immediately"
echo "- Update .env file with secure values"
echo "- Configure firewall rules"
echo "- Set up regular backups"
echo ""

# Set proper permissions
chown -R cyberpanel:cyberpanel /home/cyberpanel/public_html/bethel/
chmod -R 755 /home/cyberpanel/public_html/bethel/

echo "✅ Hetzner VPS setup completed!" 