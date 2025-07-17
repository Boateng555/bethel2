#!/usr/bin/env python3
"""
Prepare media files for Railway deployment
This script copies media files to a directory that will be deployed to Railway
"""

import os
import shutil
from pathlib import Path

print("🚀 Preparing media files for Railway deployment...")
print("=" * 60)

# Create railway_media directory if it doesn't exist
railway_media_dir = Path("railway_media")
railway_media_dir.mkdir(exist_ok=True)

# Copy all media files to railway_media directory
media_dir = Path("media")
if media_dir.exists():
    print(f"📁 Copying media files from {media_dir} to {railway_media_dir}...")
    
    # Copy the entire media directory structure
    for root, dirs, files in os.walk(media_dir):
        # Create corresponding directory in railway_media
        rel_path = Path(root).relative_to(media_dir)
        railway_path = railway_media_dir / rel_path
        railway_path.mkdir(parents=True, exist_ok=True)
        
        # Copy files
        for file in files:
            src_file = Path(root) / file
            dst_file = railway_path / file
            
            if not dst_file.exists():
                shutil.copy2(src_file, dst_file)
                print(f"  ✅ Copied: {rel_path / file}")
            else:
                print(f"  ⏭️  Skipped (exists): {rel_path / file}")
    
    print(f"\n✅ Media files prepared for Railway deployment!")
    print(f"📁 Files copied to: {railway_media_dir}")
    
    # Count files
    total_files = sum(len(files) for _, _, files in os.walk(railway_media_dir))
    print(f"📊 Total files ready: {total_files}")
    
else:
    print(f"❌ Media directory not found: {media_dir}")

print("\n" + "=" * 60)
print("🎯 Next steps:")
print("1. Commit and push these changes")
print("2. Railway will deploy with the media files")
print("3. Run the upload command on Railway to move files to Cloudinary")
print("4. Images will then display on your live site") 