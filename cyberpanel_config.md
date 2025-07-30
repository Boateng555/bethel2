# CyberPanel Configuration Guide for Bethel Prayer Ministry

## 🚀 Step-by-Step CyberPanel Setup

### 1. Initial CyberPanel Access
```bash
# SSH into your Hetzner VPS
ssh root@YOUR_SERVER_IP

# Access CyberPanel
https://YOUR_SERVER_IP:8090
# Default login: admin@example.com / 1234567
```

### 2. Create Website in CyberPanel

1. **Login to CyberPanel**
2. **Go to Websites → List Websites**
3. **Click "Create Website"**
4. **Fill in the details:**
   - Domain: `your-domain.com`
   - Email: `admin@your-domain.com`
   - Package: `Default`
   - PHP Version: `None` (we're using Python)
   - SSL: `Let's Encrypt`
   - DKIM: `Yes`

### 3. Configure Nginx for Django

After creating the website, edit the Nginx configuration:

1. **Go to Websites → List Websites**
2. **Click on your domain**
3. **Go to "Nginx Config"**
4. **Replace the content with:**

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration (CyberPanel handles this)
    ssl_certificate /home/cyberpanel/public_html/your-domain.com/ssl/your-domain.com.crt;
    ssl_certificate_key /home/cyberpanel/public_html/your-domain.com/ssl/your-domain.com.key;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Static Files
    location /static/ {
        alias /home/cyberpanel/public_html/bethel/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # Media Files
    location /media/ {
        alias /home/cyberpanel/public_html/bethel/media/;
        expires 1y;
        add_header Cache-Control "public";
        access_log off;
    }
    
    # Health Check
    location /health/ {
        proxy_pass http://127.0.0.1:8000/health/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        access_log off;
    }
    
    # Django Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        proxy_buffering off;
    }
}
```

### 4. SSL Certificate Setup

1. **Go to SSL → SSL Certificates**
2. **Select your domain**
3. **Click "Issue SSL"**
4. **Choose "Let's Encrypt"**
5. **Enable "Force HTTPS"**

### 5. Database Management

**Access PostgreSQL:**
```bash
sudo -u postgres psql
```

**Create database and user:**
```sql
CREATE DATABASE bethel_db;
CREATE USER bethel_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE bethel_db TO bethel_user;
\q
```

### 6. Environment Variables

Edit `/home/cyberpanel/public_html/bethel/.env`:

```env
# Django Settings
DEBUG=False
SECRET_KEY=your_super_secret_key_here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,YOUR_SERVER_IP

# Database
DATABASE_URL=postgresql://bethel_user:your_secure_password@localhost:5432/bethel_db

# ImageKit
IMAGEKIT_PUBLIC_KEY=your_imagekit_public_key
IMAGEKIT_PRIVATE_KEY=your_imagekit_private_key
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_endpoint

# Security
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 7. Django Setup Commands

```bash
cd /home/cyberpanel/public_html/bethel

# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Test the application
python manage.py runserver 127.0.0.1:8000
```

### 8. Service Management

**Start Django service:**
```bash
systemctl start bethel
systemctl enable bethel
```

**Check status:**
```bash
systemctl status bethel
```

**View logs:**
```bash
journalctl -u bethel -f
```

### 9. Backup Configuration

**Set up automatic backups in CyberPanel:**

1. **Go to Backup → Backup Home**
2. **Click "Create Backup"**
3. **Select your domain**
4. **Choose backup location**
5. **Set schedule (daily recommended)**

**Manual backup script:**
```bash
/home/cyberpanel/public_html/bethel/backup.sh
```

### 10. Monitoring Setup

**In CyberPanel:**
1. **Go to Monitor → System Status**
2. **Enable monitoring for your domain**
3. **Set up email notifications**

**Custom monitoring:**
```bash
# Check every 5 minutes
*/5 * * * * /home/cyberpanel/public_html/bethel/monitor.sh
```

### 11. Security Hardening

**In CyberPanel:**
1. **Go to Security → ModSecurity**
2. **Enable ModSecurity for your domain**
3. **Go to Security → CSF Firewall**
4. **Configure firewall rules**

**Additional security:**
```bash
# Update system regularly
apt update && apt upgrade -y

# Check for security updates
unattended-upgrades --dry-run --debug
```

### 12. Performance Optimization

**Enable caching in CyberPanel:**
1. **Go to LiteSpeed Cache**
2. **Enable for your domain**
3. **Configure cache settings**

**Database optimization:**
```sql
-- Run in PostgreSQL
VACUUM ANALYZE;
REINDEX DATABASE bethel_db;
```

### 13. Troubleshooting

**Common issues and solutions:**

1. **502 Bad Gateway:**
   ```bash
   systemctl restart bethel
   journalctl -u bethel -f
   ```

2. **Static files not loading:**
   ```bash
   python manage.py collectstatic --noinput
   chown -R cyberpanel:cyberpanel staticfiles/
   ```

3. **Database connection issues:**
   ```bash
   sudo -u postgres psql -d bethel_db -c "SELECT 1;"
   ```

4. **Permission issues:**
   ```bash
   chown -R cyberpanel:cyberpanel /home/cyberpanel/public_html/bethel/
   chmod -R 755 /home/cyberpanel/public_html/bethel/
   ```

### 14. Maintenance Commands

```bash
# Restart everything
systemctl restart bethel
systemctl restart nginx
systemctl restart postgresql

# Check disk space
df -h

# Check memory usage
free -h

# Check running services
systemctl list-units --type=service --state=running

# View recent logs
tail -f /home/cyberpanel/public_html/bethel/logs/gunicorn_error.log
```

### 15. Migration Checklist

- [ ] VPS setup completed
- [ ] CyberPanel installed
- [ ] Domain configured
- [ ] SSL certificate issued
- [ ] Database created
- [ ] Django app deployed
- [ ] Static files collected
- [ ] Service running
- [ ] Backup configured
- [ ] Monitoring enabled
- [ ] Security hardened
- [ ] Performance optimized
- [ ] DNS updated
- [ ] Old deployment disabled

### 16. Post-Migration Tasks

1. **Update DNS records** to point to your Hetzner VPS
2. **Test all functionality** thoroughly
3. **Monitor logs** for any issues
4. **Set up regular backups**
5. **Configure monitoring alerts**
6. **Document any custom configurations**
7. **Plan for future updates and maintenance** 