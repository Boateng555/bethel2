#!/usr/bin/env python
"""
Script to check ImageKit status on production site
"""
import requests
import json

def check_production_status():
    print("🔍 Checking Production ImageKit Status")
    print("=" * 50)
    
    # Check if production site is accessible
    try:
        response = requests.get('https://web-production-158c.up.railway.app', timeout=10)
        print(f"✅ Production site accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot access production site: {e}")
        return
    
    # Check for any image URLs on the site
    try:
        # Get the main page content
        response = requests.get('https://web-production-158c.up.railway.app', timeout=10)
        content = response.text
        
        # Look for image URLs
        if 'res.cloudinary.com' in content:
            print("☁️ Found Cloudinary URLs in production")
        if 'ik.imagekit.io' in content:
            print("🖼️ Found ImageKit URLs in production")
        if '/media/' in content:
            print("📁 Found local media URLs in production")
            
        print(f"\n📊 Content analysis:")
        print(f"  Total content length: {len(content)} characters")
        print(f"  Contains Cloudinary: {'✅' if 'res.cloudinary.com' in content else '❌'}")
        print(f"  Contains ImageKit: {'✅' if 'ik.imagekit.io' in content else '❌'}")
        print(f"  Contains local media: {'✅' if '/media/' in content else '❌'}")
        
    except Exception as e:
        print(f"❌ Error analyzing content: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Production check completed!")

if __name__ == "__main__":
    check_production_status() 