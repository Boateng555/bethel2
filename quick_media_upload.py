#!/usr/bin/env python
"""
Quick script to upload media files to Cloudinary
This will help you get your local images and videos onto the live site
"""
import os
import cloudinary
import cloudinary.uploader
from pathlib import Path

# Set up Cloudinary (you'll need to set these environment variables)
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

def upload_media_files():
    """
    Upload media files from local media directory to Cloudinary
    """
    print("🚀 Starting media upload to Cloudinary...")
    print("=" * 60)
    
    # Check if Cloudinary is configured
    if not all([os.environ.get('CLOUDINARY_CLOUD_NAME'), 
                os.environ.get('CLOUDINARY_API_KEY'), 
                os.environ.get('CLOUDINARY_API_SECRET')]):
        print("❌ Cloudinary credentials not found!")
        print("Please set these environment variables:")
        print("  CLOUDINARY_CLOUD_NAME")
        print("  CLOUDINARY_API_KEY") 
        print("  CLOUDINARY_API_SECRET")
        return
    
    # Media directory
    media_dir = Path("media")
    if not media_dir.exists():
        print("❌ Media directory not found!")
        return
    
    print(f"📁 Scanning media directory: {media_dir}")
    
    # Upload all media files
    uploaded_files = []
    
    for file_path in media_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', '.mov', '.webm']:
            print(f"📤 Uploading: {file_path}")
            
            try:
                # Upload to Cloudinary
                result = cloudinary.uploader.upload(
                    str(file_path),
                    folder="bethel_media",  # Organize in a folder
                    resource_type="auto"  # Auto-detect image/video
                )
                
                uploaded_files.append({
                    'local_path': str(file_path),
                    'cloudinary_url': result['secure_url'],
                    'public_id': result['public_id']
                })
                
                print(f"  ✅ Uploaded: {result['secure_url']}")
                
            except Exception as e:
                print(f"  ❌ Error uploading {file_path}: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎉 Upload completed! {len(uploaded_files)} files uploaded.")
    
    # Save the mapping for reference
    if uploaded_files:
        with open("uploaded_media_mapping.txt", "w") as f:
            f.write("Local Path -> Cloudinary URL\n")
            f.write("=" * 50 + "\n")
            for item in uploaded_files:
                f.write(f"{item['local_path']} -> {item['cloudinary_url']}\n")
        
        print("\n📝 Mapping saved to: uploaded_media_mapping.txt")
        print("\nNext steps:")
        print("1. Your media files are now on Cloudinary")
        print("2. You can use these URLs in your Django admin")
        print("3. Or update your database to use these Cloudinary URLs")

if __name__ == "__main__":
    upload_media_files() 