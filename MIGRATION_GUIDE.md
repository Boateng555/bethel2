# 🚀 Railway to Hetzner VPS Migration Guide

## 📋 Pre-Migration Checklist

### Before You Start:
- [ ] Hetzner VPS (CX11) purchased and running
- [ ] Domain name ready
- [ ] SSH access to VPS configured
- [ ] Railway environment variables exported
- [ ] ImageKit credentials available
- [ ] Database backup from Railway (if needed)

## 🔧 Step-by-Step Migration Process

### Phase 1: VPS Preparation

#### 1.1 SSH into your Hetzner VPS
```bash
ssh root@YOUR_HETZNER_IP
```

#### 1.2 Run the automated setup script
```bash
# Download and run the setup script
wget https://raw.githubusercontent.com/Boateng555/bethel2/main/hetzner_setup.sh
chmod +x hetzner_setup.sh
./hetzner_setup.sh
```

**What this script does:**
- Updates system packages
- Installs CyberPanel
- Sets up PostgreSQL database
- Installs Python and dependencies
- Clones your Django project
- Creates virtual environment
- Sets up Gunicorn service
- Configures security (firewall, fail2ban)
- Creates backup and monitoring scripts

### Phase 2: CyberPanel Configuration

#### 2.1 Access CyberPanel
```
https://YOUR_HETZNER_IP:8090
Login: admin@example.com
Password: 1234567
```

#### 2.2 Create Website
1. Go to **Websites → List Websites**
2. Click **"Create Website"**
3. Fill in details:
   - **Domain:** your-domain.com
   - **Email:** admin@your-domain.com
   - **Package:** Default
   - **PHP Version:** None (we're using Python)
   - **SSL:** Let's Encrypt
   - **DKIM:** Yes

#### 2.3 Configure Nginx for Django
1. Go to **Websites → List Websites**
2. Click on your domain
3. Go to **"Nginx Config"**
4. Replace content with the configuration from `cyberpanel_config.md`

### Phase 3: Environment Configuration

#### 3.1 Update Environment Variables
Edit `/home/cyberpanel/public_html/bethel/.env`:

```env
# Django Settings
DEBUG=False
SECRET_KEY=your_super_secret_key_here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,YOUR_SERVER_IP

# Database Settings
DATABASE_URL=postgresql://bethel_user:your_secure_password@localhost:5432/bethel_db

# ImageKit Settings (copy from Railway)
IMAGEKIT_PUBLIC_KEY=your_imagekit_public_key
IMAGEKIT_PRIVATE_KEY=your_imagekit_private_key
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_endpoint

# Security Settings
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email Settings (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Phase 4: Django Deployment

#### 4.1 Deploy Django Application
```bash
cd /home/cyberpanel/public_html/bethel

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Set proper permissions
chown -R cyberpanel:cyberpanel /home/cyberpanel/public_html/bethel/
chmod -R 755 /home/cyberpanel/public_html/bethel/
```

#### 4.2 Start Django Service
```bash
# Start and enable the service
systemctl start bethel
systemctl enable bethel

# Check status
systemctl status bethel
```

### Phase 5: SSL and Domain Setup

#### 5.1 Configure SSL Certificate
1. Go to **SSL → SSL Certificates**
2. Select your domain
3. Click **"Issue SSL"**
4. Choose **"Let's Encrypt"**
5. Enable **"Force HTTPS"**

#### 5.2 Update DNS Records
Update your domain's DNS records to point to your Hetzner VPS:
- **A Record:** `@` → `YOUR_HETZNER_IP`
- **A Record:** `www` → `YOUR_HETZNER_IP`

### Phase 6: Testing and Verification

#### 6.1 Test Application
```bash
# Test Django service
systemctl status bethel

# Test database connection
sudo -u postgres psql -d bethel_db -c "SELECT 1;"

# Test static files
ls -la /home/cyberpanel/public_html/bethel/staticfiles/

# Test health endpoint
curl http://localhost:8000/health/
```

#### 6.2 Test Website
- Visit `https://your-domain.com`
- Check all functionality
- Test admin panel
- Verify static files loading
- Test ImageKit uploads

### Phase 7: Monitoring and Maintenance

#### 7.1 Setup Monitoring
```bash
# Check monitoring script
/home/cyberpanel/public_html/bethel/monitor.sh

# Add to crontab (runs every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/cyberpanel/public_html/bethel/monitor.sh") | crontab -
```

#### 7.2 Setup Backups
```bash
# Test backup script
/home/cyberpanel/public_html/bethel/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/cyberpanel/public_html/bethel/backup.sh") | crontab -
```

#### 7.3 CyberPanel Backups
1. Go to **Backup → Backup Home**
2. Click **"Create Backup"**
3. Select your domain
4. Set schedule (daily recommended)

## 🔧 Useful Commands

### Service Management
```bash
# Check Django status
systemctl status bethel

# Restart Django
systemctl restart bethel

# View Django logs
journalctl -u bethel -f

# View Gunicorn logs
tail -f /home/cyberpanel/public_html/bethel/logs/gunicorn_error.log
```

### Database Management
```bash
# Access PostgreSQL
sudo -u postgres psql

# Connect to Django database
sudo -u postgres psql -d bethel_db

# Backup database
pg_dump -h localhost -U bethel_user bethel_db > backup.sql

# Restore database
psql -h localhost -U bethel_user bethel_db < backup.sql
```

### File Management
```bash
# Update code
cd /home/cyberpanel/public_html/bethel
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate
```

### Security
```bash
# Check firewall status
ufw status

# Update system
apt update && apt upgrade -y

# Check fail2ban status
systemctl status fail2ban

# View fail2ban logs
tail -f /var/log/fail2ban.log
```

## 🚨 Troubleshooting

### Common Issues

#### 1. 502 Bad Gateway
```bash
# Check Django service
systemctl status bethel

# Check logs
journalctl -u bethel -f

# Restart service
systemctl restart bethel
```

#### 2. Static Files Not Loading
```bash
# Recollect static files
python manage.py collectstatic --noinput

# Check permissions
chown -R cyberpanel:cyberpanel staticfiles/
chmod -R 755 staticfiles/
```

#### 3. Database Connection Issues
```bash
# Test database connection
sudo -u postgres psql -d bethel_db -c "SELECT 1;"

# Check PostgreSQL status
systemctl status postgresql

# Restart PostgreSQL
systemctl restart postgresql
```

#### 4. Permission Issues
```bash
# Fix ownership
chown -R cyberpanel:cyberpanel /home/cyberpanel/public_html/bethel/

# Fix permissions
chmod -R 755 /home/cyberpanel/public_html/bethel/
```

#### 5. SSL Certificate Issues
1. Go to **SSL → SSL Certificates**
2. Delete existing certificate
3. Re-issue Let's Encrypt certificate
4. Check domain DNS propagation

## 📊 Performance Optimization

### 1. Database Optimization
```sql
-- Run in PostgreSQL
VACUUM ANALYZE;
REINDEX DATABASE bethel_db;
```

### 2. Enable Caching
1. Go to **LiteSpeed Cache** in CyberPanel
2. Enable for your domain
3. Configure cache settings

### 3. Monitor Resources
```bash
# Check disk usage
df -h

# Check memory usage
free -h

# Check CPU usage
htop
```

## 🔒 Security Best Practices

### 1. Change Default Passwords
- CyberPanel admin password
- PostgreSQL user password
- Django superuser password

### 2. Regular Updates
```bash
# Set up automatic security updates
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

### 3. Firewall Configuration
```bash
# Check firewall rules
ufw status

# Allow only necessary ports
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8090/tcp
```

## 📞 Support and Maintenance

### 1. Regular Maintenance Tasks
- [ ] Weekly system updates
- [ ] Monthly database optimization
- [ ] Quarterly security audit
- [ ] Annual backup testing

### 2. Monitoring Alerts
- Set up email notifications in CyberPanel
- Monitor disk space usage
- Watch for failed login attempts
- Check application error logs

### 3. Backup Strategy
- Daily automated backups
- Weekly manual backups
- Monthly off-site backups
- Test restore procedures

## ✅ Post-Migration Checklist

- [ ] Website accessible via HTTPS
- [ ] All functionality working
- [ ] Static files loading correctly
- [ ] ImageKit uploads working
- [ ] Admin panel accessible
- [ ] SSL certificate valid
- [ ] Backups configured
- [ ] Monitoring active
- [ ] Security hardened
- [ ] DNS propagated
- [ ] Railway deployment disabled
- [ ] Documentation updated

## 🎉 Migration Complete!

Your Django application is now successfully running on Hetzner VPS with CyberPanel. You have full control over your server and can optimize it for your specific needs.

**Benefits of this setup:**
- ✅ Full server control
- ✅ Better performance
- ✅ Lower costs
- ✅ Professional control panel
- ✅ Automated backups
- ✅ SSL certificates
- ✅ Security features
- ✅ Monitoring tools 