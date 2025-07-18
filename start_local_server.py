#!/usr/bin/env python
"""
Start local development server with correct environment variables
"""

import os
import subprocess
import sys

def start_local_server():
    """Start Django development server with local settings"""
    print("🚀 Starting Local Development Server")
    print("=" * 50)
    
    # Set environment variables for local development
    os.environ['DJANGO_DEBUG'] = 'True'
    
    # Remove any Railway-specific environment variables
    if 'DATABASE_URL' in os.environ:
        print("⚠️ DATABASE_URL found - this will be ignored for local development")
    
    print("✅ Environment configured for local development")
    print("📦 Using SQLite database")
    print("🖼️ Using local file storage")
    print("\n🌐 Server will be available at: http://127.0.0.1:8000")
    print("⏹️ Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the Django development server
    try:
        subprocess.run([sys.executable, 'manage.py', 'runserver'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")

if __name__ == '__main__':
    start_local_server() 