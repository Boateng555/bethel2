#!/usr/bin/env python
"""
Copy all media files to a temporary location for Railway upload
"""
import os
import shutil
from pathlib import Path

def main():
    print("📁 Copying media files for Railway upload...")
    
    # Source and destination directories
    source_dir = Path("media")
    dest_dir = Path("railway_media")
    
    if not source_dir.exists():
        print("❌ Media directory not found")
        return
    
    # Create destination directory
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir()
    
    # Copy all media files
    total_files = 0
    for root, dirs, files in os.walk(source_dir):
        # Create corresponding directory in destination
        rel_path = Path(root).relative_to(source_dir)
        dest_path = dest_dir / rel_path
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Copy files
        for file in files:
            src_file = Path(root) / file
            dst_file = dest_path / file
            shutil.copy2(src_file, dst_file)
            total_files += 1
            print(f"📋 Copied: {src_file} -> {dst_file}")
    
    print(f"\n✅ Copied {total_files} files to {dest_dir}")
    print("🚀 Ready for Railway upload!")

if __name__ == '__main__':
    main() 