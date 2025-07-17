#!/usr/bin/env python
"""
Script to check live site media configuration and test Cloudinary
"""
import requests
import json
import os

def check_live_site_media():
    """
    Check the live site's media configuration
    """
    print("🔍 Checking Live Site Media Configuration")
    print("=" * 60)
    
    # Test the live site
    live_url = "https://web-production-158c.up.railway.app/"
    
    try:
        print(f"📡 Testing live site: {live_url}")
        response = requests.get(live_url, timeout=10)
        print(f"✅ Site is accessible (Status: {response.status_code})")
        
        # Check if it redirects to a church page
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"🔄 Redirects to: {redirect_url}")
            
            # Test the church page
            church_url = f"https://web-production-158c.up.railway.app{redirect_url}"
            print(f"📡 Testing church page: {church_url}")
            
            church_response = requests.get(church_url, timeout=10)
            print(f"✅ Church page accessible (Status: {church_response.status_code})")
            
            # Look for image URLs in the HTML
            html_content = church_response.text
            print(f"📄 HTML content length: {len(html_content)} characters")
            
            # Check for Cloudinary URLs
            cloudinary_urls = []
            if 'res.cloudinary.com' in html_content:
                print("☁️ Found Cloudinary URLs in HTML")
                # Extract Cloudinary URLs
                import re
                cloudinary_pattern = r'https://res\.cloudinary\.com/[^"\s]+'
                cloudinary_urls = re.findall(cloudinary_pattern, html_content)
                print(f"📸 Found {len(cloudinary_urls)} Cloudinary URLs")
                
                for i, url in enumerate(cloudinary_urls[:5]):  # Show first 5
                    print(f"  {i+1}. {url}")
            else:
                print("❌ No Cloudinary URLs found in HTML")
            
            # Check for local media URLs
            if '/media/' in html_content:
                print("📁 Found local media URLs in HTML")
                local_pattern = r'/media/[^"\s]+'
                local_urls = re.findall(local_pattern, html_content)
                print(f"📁 Found {len(local_urls)} local media URLs")
                
                for i, url in enumerate(local_urls[:5]):  # Show first 5
                    print(f"  {i+1}. {url}")
            else:
                print("❌ No local media URLs found in HTML")
            
            # Check for placeholder images
            if 'placeholder' in html_content.lower() or 'icon' in html_content.lower():
                print("⚠️ Found placeholder/icon references in HTML")
            
        else:
            print(f"📄 Direct response (no redirect)")
            
    except Exception as e:
        print(f"❌ Error testing live site: {e}")
    
    print("\n" + "=" * 60)
    print("🔧 Troubleshooting Steps:")
    print("1. Check if Railway redeploy is complete")
    print("2. Verify Cloudinary environment variables are set correctly")
    print("3. Check if media files are actually uploaded to the database")
    print("4. Test uploading a new image via admin interface")
    print("5. Clear browser cache and try again")

def test_cloudinary_connectivity():
    """
    Test Cloudinary connectivity
    """
    print("\n☁️ Testing Cloudinary Connectivity")
    print("=" * 60)
    
    # Check if we can access Cloudinary
    try:
        cloudinary_test_url = "https://res.cloudinary.com/dhzdusb5k/image/upload/v1/sample"
        print(f"📡 Testing Cloudinary: {cloudinary_test_url}")
        
        response = requests.get(cloudinary_test_url, timeout=10)
        print(f"✅ Cloudinary is accessible (Status: {response.status_code})")
        
        if response.status_code == 200:
            print("☁️ Cloudinary is working correctly")
        else:
            print(f"⚠️ Cloudinary returned status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing Cloudinary: {e}")

if __name__ == "__main__":
    check_live_site_media()
    test_cloudinary_connectivity() 