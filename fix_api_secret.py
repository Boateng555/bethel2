#!/usr/bin/env python3
"""
Fix API Secret with correct characters
"""

def fix_api_secret():
    """Fix the API secret with correct characters"""
    
    env_content = """# Django Settings
DJANGO_SECRET_KEY=django-insecure-dt1#i48=k*oc^@cwtgj7v1ou(_(n%z=&omp$)fhfh3d)hvv^sg
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# Cloudinary Settings (for production media storage)
CLOUDINARY_CLOUD_NAME=dhzdusb5k
CLOUDINARY_API_KEY=566563723513225
CLOUDINARY_API_SECRET=E-HJnJ8weQEL67Jl708uBCLS_eU

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
        print("✅ .env file updated with corrected API Secret!")
        print("\n📋 Corrected credentials:")
        print("   Cloud Name: dhzdusb5k")
        print("   API Key: 566563723513225")
        print("   API Secret: E-HJnJ8weQEL67Jl708uBCLS_eU")
        print("\n🔍 Fixed: Changed 'I' to 'l' in API Secret")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")

if __name__ == "__main__":
    fix_api_secret() 