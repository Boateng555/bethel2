# 🚀 Manual Server Setup Guide

Since SSH authentication is having issues, please follow these steps manually:

## **Step 1: SSH into your server**
```bash
ssh root@91.99.232.214
```

## **Step 2: Set up the project directory**
```bash
# Create project directory
mkdir -p /home/cyberpanel/public_html/bethel
cd /home/cyberpanel/public_html/bethel

# Clone the repository
git clone https://github.com/Boateng555/bethel2.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p staticfiles media logs

# Set permissions
chown -R cyberpanel:cyberpanel /home/cyberpanel/public_html/bethel
chmod -R 755 /home/cyberpanel/public_html/bethel
```

## **Step 3: Set up PostgreSQL Database**
```bash
# Install PostgreSQL if not already installed
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE bethel_db;
CREATE USER bethel_user WITH PASSWORD 'bethel_secure_password_2024';
GRANT ALL PRIVILEGES ON DATABASE bethel_db TO bethel_user;
\q
```

## **Step 4: Create production environment file**
```bash
cd /home/cyberpanel/public_html/bethel
nano production.env
```

Add this content:
```
DEBUG=False
SECRET_KEY=6x81cy++5wh*#qi!*6srjp$(8(!_&m7g)31h9o9y@_ul#hf_t*
ALLOWED_HOSTS=91.99.232.214,your-domain.com,localhost,127.0.0.1
DATABASE_URL=postgresql://bethel_user:bethel_secure_password_2024@localhost:5432/bethel_db
IMAGEKIT_PUBLIC_KEY=public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=
IMAGEKIT_PRIVATE_KEY=private_Dnsrj2VW7uJakaeMaNYaav+P784=
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/9buar9mbp
WEB_CONCURRENCY=4
PYTHONUNBUFFERED=1
CONN_MAX_AGE=600
PYTHONHASHSEED=random
PYTHONDONTWRITEBYTECODE=1
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://91.99.232.214
STATIC_ROOT=/home/cyberpanel/public_html/bethel/staticfiles
MEDIA_ROOT=/home/cyberpanel/public_html/bethel/media
LOG_LEVEL=INFO
```

## **Step 5: Run Django setup**
```bash
# Load environment variables
export $(cat production.env | xargs)

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser (optional)
python manage.py createsuperuser
```

## **Step 6: Set up Gunicorn service**
```bash
sudo nano /etc/systemd/system/bethel-gunicorn.service
```

Add this content:
```ini
[Unit]
Description=Bethel Prayer Ministry Gunicorn
After=network.target

[Service]
User=cyberpanel
Group=cyberpanel
WorkingDirectory=/home/cyberpanel/public_html/bethel
Environment="PATH=/home/cyberpanel/public_html/bethel/venv/bin"
ExecStart=/home/cyberpanel/public_html/bethel/venv/bin/gunicorn --workers 4 --bind unix:/home/cyberpanel/public_html/bethel/bethel.sock backend.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

## **Step 7: Start services**
```bash
# Enable and start Gunicorn
sudo systemctl enable bethel-gunicorn
sudo systemctl start bethel-gunicorn

# Check status
sudo systemctl status bethel-gunicorn
```

## **Step 8: Configure Nginx (if using CyberPanel)**
Since you're using CyberPanel, you can create a website through the CyberPanel interface and point it to:
- Document Root: `/home/cyberpanel/public_html/bethel`
- Python App: Yes
- Python Version: 3.x
- Application Entry Point: `backend.wsgi:application`

## **Step 9: Test the deployment**
Visit: `http://91.99.232.214` or your domain

---

## **🎉 Your Bethel Prayer Ministry platform should now be live!**

If you encounter any issues, check the logs:
```bash
sudo journalctl -u bethel-gunicorn -f
``` 