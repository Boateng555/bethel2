#!/usr/bin/env python3
"""
Copy Images Script
This script copies images from railway_media to media folder.
"""

import os
import shutil
from pathlib import Path

def copy_images():
    """Copy all images from railway_media to media folder"""
    print("📁 Copying Images from railway_media to media")
    print("=" * 50)
    
    # Get paths
    base_dir = Path(__file__).parent
    railway_media = base_dir / 'railway_media'
    media_folder = base_dir / 'media'
    
    print(f"Source: {railway_media}")
    print(f"Destination: {media_folder}")
    
    if not railway_media.exists():
        print("❌ Railway media folder does not exist")
        return
    
    # Create media folder if it doesn't exist
    media_folder.mkdir(exist_ok=True)
    
    copied_count = 0
    failed_count = 0
    
    try:
        # Copy all files from railway_media to media
        for root, dirs, files in os.walk(railway_media):
            # Calculate relative path
            rel_path = os.path.relpath(root, railway_media)
            target_dir = media_folder / rel_path
            
            # Create target directory if it doesn't exist
            target_dir.mkdir(parents=True, exist_ok=True)
            
            for file in files:
                source_file = Path(root) / file
                target_file = target_dir / file
                
                try:
                    shutil.copy2(source_file, target_file)
                    print(f"  ✅ Copied: {os.path.join(rel_path, file)}")
                    copied_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to copy {file}: {e}")
                    failed_count += 1
        
        print(f"\n📊 Copy Summary:")
        print(f"  Files copied: {copied_count}")
        print(f"  Files failed: {failed_count}")
        
        if copied_count > 0:
            print("✅ Images copied successfully!")
            print("   Your images should now be visible on the website")
            print("   Refresh your browser to see the images")
        
    except Exception as e:
        print(f"❌ Error copying images: {e}")

if __name__ == "__main__":
    copy_images() 