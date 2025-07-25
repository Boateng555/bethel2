# ImageKit Setup for Hetzner Server (CyberPanel)

## Current Status
✅ **ImageKit credentials are already configured** in your `production.env` file:
- `IMAGEKIT_PUBLIC_KEY=public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=`
- `IMAGEKIT_PRIVATE_KEY=private_Dnsrj2VW7uJakaeMaNYaav+P784=`
- `IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/9buar9mbp`

## Setup Steps for Hetzner Server

### 1. Update Your Hetzner Server Environment

SSH into your Hetzner server and update the environment file:

```bash
# SSH to your server
ssh root@91.99.232.214

# Navigate to your Django project
cd /home/cyberpanel/public_html/bethel

# Update the .env file with ImageKit credentials
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
```

### 2. Pull Latest Code with ImageKit Fixes

```bash
# Pull the latest code with ImageKit fixes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/upgrade ImageKit library
pip install --upgrade imagekitio

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput
```

### 3. Test ImageKit Configuration

Create a test script on your server:

```bash
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
        test_content = b"Test file from Hetzner server"
        file_obj = BytesIO(test_content)
        file_obj.name = "hetzner_test.txt"
        
        upload = imagekit.upload_file(
            file=file_obj,
            file_name="hetzner_test.txt"
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
python test_imagekit_hetzner.py
```

### 4. Restart Django Application

```bash
# Restart the Django service
systemctl restart bethel

# Check status
systemctl status bethel

# View logs if needed
journalctl -u bethel -f
```

### 5. Verify ImageKit is Working

After restarting, test by:

1. **Upload a new image** through your Django admin
2. **Check the image URL** - it should start with `https://ik.imagekit.io/9buar9mbp/`
3. **Verify the image loads** from ImageKit CDN

### 6. Monitor and Troubleshoot

#### Check Django Logs
```bash
# View Django application logs
tail -f /home/cyberpanel/public_html/bethel/logs/gunicorn_error.log
tail -f /home/cyberpanel/public_html/bethel/logs/gunicorn_access.log
```

#### Check System Service Logs
```bash
# View systemd service logs
journalctl -u bethel -f
```

#### Test ImageKit Directly
```bash
# Run the test script again
python test_imagekit_hetzner.py
```

## Expected Results

After completing the setup:

✅ **Images upload to ImageKit cloud** instead of local storage  
✅ **Image URLs are from ImageKit CDN** (`https://ik.imagekit.io/9buar9mbp/`)  
✅ **Better performance** with CDN delivery  
✅ **No local storage issues** on your Hetzner server  

## Troubleshooting

### If images still don't upload to ImageKit:

1. **Check environment variables**:
   ```bash
   cat /home/cyberpanel/public_html/bethel/.env | grep IMAGEKIT
   ```

2. **Verify Django settings**:
   ```bash
   python manage.py shell
   >>> from django.conf import settings
   >>> print(settings.DEFAULT_FILE_STORAGE)
   >>> print(settings.IMAGEKIT_CONFIG)
   ```

3. **Check ImageKit account**:
   - Ensure your ImageKit account is active
   - Verify you have sufficient credits
   - Check if the credentials are correct

4. **Test network connectivity**:
   ```bash
   curl -I https://ik.imagekit.io/9buar9mbp/
   ```

### Common Issues:

1. **Permission issues**: Ensure the `cyberpanel` user has write access
2. **Environment not loaded**: Make sure `.env` file is being loaded
3. **ImageKit library version**: Ensure you have the latest version

## Security Notes

- ✅ ImageKit credentials are properly configured
- ✅ Images are served from secure CDN
- ✅ No sensitive data stored locally
- ✅ Environment variables are protected

## Backup Strategy

Since images are now in ImageKit cloud, your backup strategy should focus on:

1. **Database backups** (church data, user data, etc.)
2. **Code backups** (Django application)
3. **Configuration backups** (environment files)

ImageKit handles image storage and CDN delivery automatically. 