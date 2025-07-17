#!/usr/bin/env python3
"""
Update .env file with real Cloudinary credentials
"""

def update_env_file():
    """Update .env file with real credentials"""
    
    env_content = """# Django Settings
DJANGO_SECRET_KEY=django-insecure-dt1#i48=k*oc^@cwtgj7v1ou(_(n%z=&omp$)fhfh3d)hvv^sg
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# Cloudinary Settings (for production media storage)
CLOUDINARY_CLOUD_NAME=dhzdusb5k
CLOUDINARY_API_KEY=462763744132765
CLOUDINARY_API_SECRET=s-FWNQUY_M40XwHKrskwIh0C-XI

# Email Settings (optional)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
# DEFAULT_FROM_EMAIL=your-email@gmail.com

# Other Settings
# CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file updated with real Cloudinary credentials!")
        print("\n📋 Credentials set:")
        print("   Cloud Name: dhzdusb5k")
        print("   API Key: 462763744132765")
        print("   API Secret: s-FWNQUY_M40XwHKrskwIh0C-XI")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")

if __name__ == "__main__":
    update_env_file() 