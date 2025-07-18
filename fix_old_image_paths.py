#!/usr/bin/env python
"""
Fix old local image paths by uploading them to Cloudinary
"""
import os
import django
import cloudinary
import cloudinary.uploader
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church, News, Ministry, Sermon, HeroMedia

def fix_old_image_paths():
    """Fix old local image paths by uploading to Cloudinary"""
    
    print("🔧 Fixing Old Local Image Paths")
    print("=" * 40)
    
    # Configure Cloudinary
    cloudinary.config(
        cloud_name='dhzdusb5k',
        api_key='566563723513225',
        api_secret='E-HJnJ8weQEL67J1708uBCLS_eU'
    )
    
    # Fix Churches
    print("\n🏛️ Fixing Church Images...")
    churches = Church.objects.filter(is_approved=True)
    for church in churches:
        if church.logo and '/media/' in str(church.logo):
            print(f"Fixing {church.name}: {church.logo}")
            try:
                # Get the local file path
                local_path = str(church.logo).replace('/media/', 'media/')
                full_path = Path(local_path)
                
                if full_path.exists():
                    # Upload to Cloudinary
                    result = cloudinary.uploader.upload(
                        str(full_path),
                        public_id=f"bethel/churches/logos/{church.name.replace(' ', '_')}",
                        resource_type="image"
                    )
                    
                    # Update the database
                    church.logo = result['secure_url']
                    church.save()
                    print(f"✅ Fixed {church.name}: {church.logo}")
                else:
                    print(f"❌ File not found: {full_path}")
            except Exception as e:
                print(f"❌ Error fixing {church.name}: {e}")
    
    # Fix News
    print("\n📰 Fixing News Images...")
    news_items = News.objects.all()
    for news in news_items:
        if news.image and '/media/' in str(news.image):
            print(f"Fixing news: {news.title}")
            try:
                local_path = str(news.image).replace('/media/', 'media/')
                full_path = Path(local_path)
                
                if full_path.exists():
                    result = cloudinary.uploader.upload(
                        str(full_path),
                        public_id=f"bethel/news/{news.title.replace(' ', '_')[:50]}",
                        resource_type="image"
                    )
                    
                    news.image = result['secure_url']
                    news.save()
                    print(f"✅ Fixed news: {news.title}")
                else:
                    print(f"❌ File not found: {full_path}")
            except Exception as e:
                print(f"❌ Error fixing news: {e}")
    
    # Fix Ministries
    print("\n⛪ Fixing Ministry Images...")
    ministries = Ministry.objects.filter(is_approved=True)
    for ministry in ministries:
        if ministry.image and '/media/' in str(ministry.image):
            print(f"Fixing ministry: {ministry.name}")
            try:
                local_path = str(ministry.image).replace('/media/', 'media/')
                full_path = Path(local_path)
                
                if full_path.exists():
                    result = cloudinary.uploader.upload(
                        str(full_path),
                        public_id=f"bethel/ministries/{ministry.name.replace(' ', '_')}",
                        resource_type="image"
                    )
                    
                    ministry.image = result['secure_url']
                    ministry.save()
                    print(f"✅ Fixed ministry: {ministry.name}")
                else:
                    print(f"❌ File not found: {full_path}")
            except Exception as e:
                print(f"❌ Error fixing ministry: {e}")
    
    # Fix Sermons
    print("\n📖 Fixing Sermon Images...")
    sermons = Sermon.objects.filter(is_approved=True)
    for sermon in sermons:
        if sermon.image and '/media/' in str(sermon.image):
            print(f"Fixing sermon: {sermon.title}")
            try:
                local_path = str(sermon.image).replace('/media/', 'media/')
                full_path = Path(local_path)
                
                if full_path.exists():
                    result = cloudinary.uploader.upload(
                        str(full_path),
                        public_id=f"bethel/sermons/{sermon.title.replace(' ', '_')[:50]}",
                        resource_type="image"
                    )
                    
                    sermon.image = result['secure_url']
                    sermon.save()
                    print(f"✅ Fixed sermon: {sermon.title}")
                else:
                    print(f"❌ File not found: {full_path}")
            except Exception as e:
                print(f"❌ Error fixing sermon: {e}")
    
    print("\n🎉 All old image paths fixed!")
    print("Now go to: https://web-production-158c.up.railway.app/churches/")
    print("The images should be visible!")

if __name__ == "__main__":
    fix_old_image_paths() 