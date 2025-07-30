#!/usr/bin/env python3
"""
Start Django server with ImageKit properly configured
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_imagekit_environment():
    """Set up ImageKit environment variables"""
    print("🔧 Setting up ImageKit environment variables...")
    
    # Set ImageKit environment variables
    os.environ['IMAGEKIT_PUBLIC_KEY'] = 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU='
    os.environ['IMAGEKIT_PRIVATE_KEY'] = 'private_Dnsrj2VW7uJakaeMaNYaav+P784='
    os.environ['IMAGEKIT_URL_ENDPOINT'] = 'https://ik.imagekit.io/9buar9mbp'
    
    print("✅ ImageKit environment variables set")
    print(f"   PUBLIC_KEY: {os.environ['IMAGEKIT_PUBLIC_KEY'][:20]}...")
    print(f"   PRIVATE_KEY: {os.environ['IMAGEKIT_PRIVATE_KEY'][:20]}...")
    print(f"   URL_ENDPOINT: {os.environ['IMAGEKIT_URL_ENDPOINT']}")

def start_django_server():
    """Start Django development server"""
    print("\n🚀 Starting Django server with ImageKit...")
    
    # Get the project root directory
    project_root = Path(__file__).resolve().parent
    
    # Start Django server
    try:
        subprocess.run([
            sys.executable, 
            str(project_root / 'manage.py'), 
            'runserver'
        ], env=os.environ, cwd=project_root)
    except KeyboardInterrupt:
        print("\n👋 Django server stopped")

if __name__ == "__main__":
    setup_imagekit_environment()
    start_django_server() 