#!/usr/bin/env python3
"""
Create .env file with Cloudinary credentials template
"""

def create_env_file():
    """Create .env file with template"""
    
    env_content = """# Django Settings
DJANGO_SECRET_KEY=django-insecure-dt1#i48=k*oc^@cwtgj7v1ou(_(n%z=&omp$)fhfh3d)hvv^sg
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# Cloudinary Settings (for production media storage)
# Replace these with your actual Cloudinary credentials from your dashboard
CLOUDINARY_CLOUD_NAME=your-cloud-name-here
CLOUDINARY_API_KEY=your-api-key-here
CLOUDINARY_API_SECRET=your-api-secret-here

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
        print("✅ .env file created successfully!")
        print("\n📝 Next steps:")
        print("1. Open the .env file in your text editor")
        print("2. Replace the placeholder values with your actual Cloudinary credentials:")
        print("   - CLOUDINARY_CLOUD_NAME=your-cloud-name-here")
        print("   - CLOUDINARY_API_KEY=your-api-key-here") 
        print("   - CLOUDINARY_API_SECRET=your-api-secret-here")
        print("3. Save the file")
        print("4. Run: python test_cloudinary_credentials_final.py")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == "__main__":
    create_env_file() 