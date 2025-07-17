#!/usr/bin/env python
"""
Standalone script to upload media files to ImageKit
Run this locally with your ImageKit credentials
"""
import os
import base64
import hashlib
import hmac
import time
import requests
import json
from pathlib import Path

def upload_to_imagekit(file_path, folder_name="bethel"):
    """Upload a file to ImageKit using direct HTTP requests"""
    try:
        # Read the file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Get file name
        file_name = os.path.basename(file_path)
        
        # Prepare the upload data
        upload_data = {
            'file': (file_name, file_data),
            'fileName': file_name,
            'folder': folder_name,
        }
        
        # Get ImageKit credentials from environment or input
        public_key = os.environ.get('IMAGEKIT_PUBLIC_KEY')
        private_key = os.environ.get('IMAGEKIT_PRIVATE_KEY')
        url_endpoint = os.environ.get('IMAGEKIT_URL_ENDPOINT')
        
        if not all([public_key, private_key, url_endpoint]):
            print("❌ ImageKit credentials not found in environment variables")
            print("Please enter your ImageKit credentials:")
            public_key = input("Public Key: ").strip()
            private_key = input("Private Key: ").strip()
            url_endpoint = input("URL Endpoint: ").strip()
            
            if not all([public_key, private_key, url_endpoint]):
                print("❌ Missing credentials")
                return None
        
        # Create signature
        timestamp = str(int(time.time()))
        signature = create_signature(private_key, timestamp)
        
        # Prepare headers
        headers = {
            'Authorization': f'Basic {base64.b64encode(f"{public_key}:{signature}".encode()).decode()}',
            'x-ik-timestamp': timestamp,
        }
        
        # Upload to ImageKit
        response = requests.post(
            'https://upload.imagekit.io/api/v1/files/upload',
            files=upload_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('url')
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error uploading: {e}")
        return None

def create_signature(private_key, timestamp):
    """Create signature for ImageKit API"""
    message = private_key + timestamp
    signature = hmac.new(
        private_key.encode(),
        message.encode(),
        hashlib.sha1
    ).hexdigest()
    return signature

def main():
    print("🚀 Starting ImageKit media upload...")
    print("=" * 50)
    
    # Check if we have the railway_media directory
    media_dir = Path("railway_media")
    if not media_dir.exists():
        print("❌ railway_media directory not found")
        print("Please run 'python copy_media_for_railway.py' first")
        return
    
    # Get all media files
    media_files = []
    for root, dirs, files in os.walk(media_dir):
        for file in files:
            file_path = Path(root) / file
            media_files.append(file_path)
    
    print(f"📁 Found {len(media_files)} files to upload")
    
    # Upload files
    uploaded_files = []
    failed_files = []
    
    for i, file_path in enumerate(media_files, 1):
        print(f"\n📤 Uploading {i}/{len(media_files)}: {file_path.name}")
        
        # Determine folder based on file path
        relative_path = file_path.relative_to(media_dir)
        folder_parts = relative_path.parts[:-1]  # Remove filename
        folder_name = "/".join(folder_parts) if folder_parts else "bethel"
        
        # Upload file
        imagekit_url = upload_to_imagekit(str(file_path), folder_name)
        
        if imagekit_url:
            uploaded_files.append({
                'local_path': str(file_path),
                'imagekit_url': imagekit_url,
                'folder': folder_name
            })
            print(f"✅ Uploaded: {imagekit_url}")
        else:
            failed_files.append(str(file_path))
            print(f"❌ Failed to upload: {file_path}")
    
    # Save results
    results = {
        'uploaded_files': uploaded_files,
        'failed_files': failed_files,
        'total_uploaded': len(uploaded_files),
        'total_failed': len(failed_files)
    }
    
    with open('upload_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 50)
    print(f"🎉 Upload completed!")
    print(f"✅ Successfully uploaded: {len(uploaded_files)}")
    print(f"❌ Failed uploads: {len(failed_files)}")
    print(f"📄 Results saved to: upload_results.json")
    
    if uploaded_files:
        print("\n📋 Next steps:")
        print("1. Copy the URLs from upload_results.json")
        print("2. Update your database with these ImageKit URLs")
        print("3. Or run the database update script if available")

if __name__ == '__main__':
    main() 