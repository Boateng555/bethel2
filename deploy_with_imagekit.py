#!/usr/bin/env python3
"""
Deploy with ImageKit Script
This script helps you deploy your Django app with ImageKit configuration.
"""

import os
import subprocess
import sys
from datetime import datetime

def check_git_status():
    """Check git status and ensure we're ready to deploy"""
    print("🔍 Checking Git Status")
    print("=" * 50)
    
    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Not in a git repository")
            return False
        
        # Check for uncommitted changes
        result = subprocess.run(['git', 'diff', '--name-only'], capture_output=True, text=True)
        if result.stdout.strip():
            print("⚠️  You have uncommitted changes:")
            for file in result.stdout.strip().split('\n'):
                if file:
                    print(f"   - {file}")
            return False
        
        print("✅ Git repository is clean and ready for deployment")
        return True
        
    except Exception as e:
        print(f"❌ Error checking git status: {e}")
        return False

def check_imagekit_setup():
    """Check if ImageKit is properly configured"""
    print(f"\n🖼️ Checking ImageKit Setup")
    print("=" * 50)
    
    # Check if we have the required files
    required_files = [
        'core/storage.py',
        'backend/settings.py',
        'requirements.txt'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Missing!")
            return False
    
    # Check if imagekitio is in requirements
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
            if 'imagekitio' in requirements:
                print("✅ imagekitio in requirements.txt")
            else:
                print("❌ imagekitio not in requirements.txt")
                return False
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False
    
    print("✅ ImageKit setup files are ready")
    return True

def create_deployment_commit():
    """Create a deployment commit"""
    print(f"\n📝 Creating Deployment Commit")
    print("=" * 50)
    
    try:
        # Add all files
        result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error adding files: {result.stderr}")
            return False
        
        # Create commit
        commit_message = f"Deploy with ImageKit setup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        result = subprocess.run(['git', 'commit', '-m', commit_message], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error creating commit: {result.stderr}")
            return False
        
        print(f"✅ Created commit: {commit_message}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating commit: {e}")
        return False

def push_to_railway():
    """Push to Railway"""
    print(f"\n🚀 Pushing to Railway")
    print("=" * 50)
    
    try:
        # Push to main branch
        result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error pushing to Railway: {result.stderr}")
            return False
        
        print("✅ Successfully pushed to Railway")
        print("   Railway will automatically deploy your changes")
        return True
        
    except Exception as e:
        print(f"❌ Error pushing to Railway: {e}")
        return False

def show_next_steps():
    """Show next steps after deployment"""
    print(f"\n🎯 Next Steps After Deployment")
    print("=" * 50)
    
    print("""
1. 📊 Monitor Railway Deployment:
   - Go to your Railway project dashboard
   - Check the deployment logs
   - Look for: "🖼️ Using ImageKit for storage"

2. 🔧 Set ImageKit Environment Variables:
   - Go to Railway dashboard → Variables tab
   - Add these variables:
     * IMAGEKIT_PUBLIC_KEY=your_public_key
     * IMAGEKIT_PRIVATE_KEY=your_private_key
     * IMAGEKIT_URL_ENDPOINT=your_url_endpoint

3. 🧪 Test Your Live Site:
   - Visit: https://web-production-158c.up.railway.app/
   - Test image uploads through admin
   - Verify images load correctly

4. 📈 Monitor Performance:
   - Check ImageKit dashboard for usage
   - Monitor image loading speed
   - Verify CDN delivery

5. 🔄 Upload Existing Media (Optional):
   - Run: railway run python manage.py upload_media_to_imagekit
   - This will migrate existing images to ImageKit
""")

def main():
    print("🚀 Deploy with ImageKit")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check prerequisites
    if not check_git_status():
        print("\n❌ Please commit your changes before deploying")
        return
    
    if not check_imagekit_setup():
        print("\n❌ ImageKit setup is not complete")
        return
    
    # Ask for confirmation
    print(f"\n🤔 Ready to deploy?")
    response = input("Type 'yes' to continue: ").strip().lower()
    
    if response != 'yes':
        print("❌ Deployment cancelled")
        return
    
    # Create deployment commit
    if not create_deployment_commit():
        print("\n❌ Failed to create deployment commit")
        return
    
    # Push to Railway
    if not push_to_railway():
        print("\n❌ Failed to push to Railway")
        return
    
    # Show next steps
    show_next_steps()
    
    print(f"\n🎉 Deployment process completed!")
    print("=" * 60)

if __name__ == "__main__":
    main() 