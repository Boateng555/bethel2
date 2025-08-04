#!/usr/bin/env python
import os
import sys
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Hero

def test_video_url():
    print("=== Testing Video URL ===")
    
    # Get the hero
    hero = Hero.objects.get(id='6cd420d4-bbf5-482b-9b82-3c20911bc417')
    
    if not hero.background_video:
        print("❌ No background video found")
        return
    
    # Get the video URL
    video_url = hero.get_background_video_url()
    print(f"Video URL: {video_url}")
    
    # Test if the URL is accessible
    try:
        # Make a request to the video URL
        full_url = f"http://127.0.0.1:8000{video_url}"
        print(f"Testing URL: {full_url}")
        
        response = requests.head(full_url, timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Video URL is accessible")
            content_type = response.headers.get('content-type', 'unknown')
            print(f"Content-Type: {content_type}")
            content_length = response.headers.get('content-length', 'unknown')
            print(f"Content-Length: {content_length} bytes")
        else:
            print(f"❌ Video URL returned status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing video URL: {e}")
        print("Make sure the Django server is running on port 8000")

if __name__ == "__main__":
    test_video_url() 