#!/usr/bin/env python
"""
Script to fix church logos by uploading them to Cloudinary
"""
import os
import cloudinary
import cloudinary.uploader
from pathlib import Path
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.files import File
from core.models import Church

def fix_church_logos_cloudinary():
    """
    Upload church logos to Cloudinary and update database
    """
    print("🚀 Fixing Church Logos for Cloudinary...")
    print("=" * 70)
    
    # Configure Cloudinary with correct credentials
    cloudinary.config(
        cloud_name="dhzdusb5k",
        api_key="462763744132765",
        api_secret="s-FWNQuY_M40XwHKrskwIh0C-XI"
    )
    
    print("☁️ Cloudinary configured with Root API credentials")
    
    # Process Church Logos
    print("\n🏛️ Processing Church Logos...")
    churches = Church.objects.all()
    
    for church in churches:
        print(f"  📤 {church.name}")
        
        if church.logo and hasattr(church.logo, 'path'):
            local_path = church.logo.path
            if os.path.exists(local_path):
                print(f"    📸 Uploading logo...")
                try:
                    # Upload to Cloudinary
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="bethel/churches/logos",
                        public_id=f"church_{church.id}_logo"
                    )
                    
                    # Create a new file object with the Cloudinary URL
                    from django.core.files.base import ContentFile
                    import requests
                    
                    # Download the file from Cloudinary
                    response = requests.get(result['secure_url'])
                    if response.status_code == 200:
                        # Create a new file with the Cloudinary content
                        cloudinary_file = ContentFile(response.content, name=os.path.basename(local_path))
                        
                        # Update the church object
                        church.logo.save(os.path.basename(local_path), cloudinary_file, save=True)
                        print(f"      ✅ Uploaded and updated: {result['secure_url']}")
                    else:
                        print(f"      ❌ Failed to download from Cloudinary")
                        
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"    ⚠️ Logo file missing: {local_path}")
        else:
            print(f"    ❌ No logo uploaded for this church")
    
    print("\n" + "=" * 70)
    print("🎉 Church Logos Cloudinary fix completed!")
    print("\nNext steps:")
    print("1. Check your live site: https://web-production-158c.up.railway.app/")
    print("2. Church logos should now be visible in the church cards")
    print("3. If not, clear browser cache and refresh")

if __name__ == "__main__":
    fix_church_logos_cloudinary() 