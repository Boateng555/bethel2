# 🚀 Production Deployment Guide for Hetzner

## 📋 Prerequisites

1. **Hetzner VPS** - Your server is ready
2. **ImageKit Account** - For media file storage
3. **Domain Name** - Pointed to your Hetzner IP
4. **Git Repository** - Your code is in git

## 🔧 Step 1: Get Your ImageKit Credentials

1. Go to [ImageKit Dashboard](https://imagekit.io/dashboard)
2. Copy your:
   - **Public Key**
   - **Private Key** 
   - **URL Endpoint**

## 🔧 Step 2: Update Configuration

Edit `deploy_production.sh` and update these values:

```bash
SERVER_IP="YOUR_HETZNER_IP"
DOMAIN="your-domain.com"
DB_PASSWORD="your_secure_db_password"
IMAGEKIT_PUBLIC_KEY="your_imagekit_public_key"
IMAGEKIT_PRIVATE_KEY="your_imagekit_private_key"
IMAGEKIT_URL_ENDPOINT="your_imagekit_endpoint"
```

## 🔧 Step 3: Initial Server Setup (First Time Only)

If this is your first deployment, run the server setup:

```bash
# Copy setup script to server
scp hetzner_setup.sh root@YOUR_HETZNER_IP:/root/

# SSH to server and run setup
ssh root@YOUR_HETZNER_IP
chmod +x /root/hetzner_setup.sh
/root/hetzner_setup.sh
```

## 🔧 Step 4: Deploy to Production

```bash
# Make script executable
chmod +x deploy_production.sh

# Run deployment
./deploy_production.sh
```

## 🔧 Step 5: Verify Deployment

1. **Check Website**: Visit your domain
2. **Check Logs**: `ssh root@YOUR_IP 'journalctl -u bethel-gunicorn -f'`
3. **Test Image Upload**: Try uploading an image in admin

## 🔧 Step 6: Future Deployments

For future updates, just run:

```bash
./deploy_production.sh
```

This will:
- Pull latest code from git
- Install dependencies
- Run migrations
- Collect static files
- Restart services

## 🗄️ Database Setup

The script will automatically:
- Create PostgreSQL database
- Create database user
- Run Django migrations

## 📁 File Structure on Server

```
/home/cyberpanel/public_html/bethel/
├── venv/                    # Python virtual environment
├── staticfiles/            # Collected static files
├── media/                  # Local media files (if any)
├── production.env          # Environment variables
├── manage.py              # Django management
└── ...                    # Your Django project files
```

## 🔒 Security Notes

1. **Change default passwords** in CyberPanel
2. **Set up SSL certificate** in CyberPanel
3. **Configure firewall** (UFW is installed)
4. **Regular backups** of database and files

## 🐛 Troubleshooting

### Common Issues:

1. **Permission Denied**: Check file permissions
2. **Database Connection**: Verify PostgreSQL is running
3. **Static Files**: Check STATIC_ROOT path
4. **ImageKit**: Verify credentials are correct

### Useful Commands:

```bash
# Check service status
systemctl status bethel-gunicorn
systemctl status nginx
systemctl status postgresql

# View logs
journalctl -u bethel-gunicorn -f
tail -f /var/log/nginx/error.log

# Check database
sudo -u postgres psql -d bethel_db
```

## 📞 Support

If you encounter issues:
1. Check the logs first
2. Verify all environment variables
3. Ensure ImageKit credentials are correct
4. Check database connectivity

---

**🎉 Your Bethel Prayer Ministry platform is now live in production!** 