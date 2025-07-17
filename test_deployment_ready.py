#!/usr/bin/env python3
"""
Test if deployment is ready and trigger URL fix
"""
import requests
import time
import sys

def test_deployment():
    """Test if the deployment is ready"""
    try:
        # Test the main site
        response = requests.get("https://web-production-158c.up.railway.app/", timeout=10)
        if response.status_code == 200:
            print("✅ Main site is accessible")
            return True
        else:
            print(f"❌ Main site returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing main site: {e}")
        return False

def trigger_url_fix():
    """Trigger the URL fix on production"""
    try:
        print("🔄 Triggering URL fix on production...")
        response = requests.get("https://web-production-158c.up.railway.app/fix-all/", timeout=30)
        
        if response.status_code == 200:
            print("✅ URL fix triggered successfully!")
            print("Response:", response.text[:500] + "..." if len(response.text) > 500 else response.text)
            return True
        else:
            print(f"❌ URL fix failed with status {response.status_code}")
            print("Response:", response.text)
            return False
    except Exception as e:
        print(f"❌ Error triggering URL fix: {e}")
        return False

def main():
    print("🚀 Testing deployment and triggering URL fix...")
    print("=" * 50)
    
    # Wait for deployment to be ready
    max_attempts = 10
    for attempt in range(max_attempts):
        print(f"\n📡 Attempt {attempt + 1}/{max_attempts}: Testing deployment...")
        
        if test_deployment():
            print("\n🎉 Deployment is ready! Triggering URL fix...")
            if trigger_url_fix():
                print("\n✅ All done! Your media URLs should now be fixed on production.")
                return
            else:
                print("\n❌ URL fix failed. You may need to wait a bit longer for the deployment to fully complete.")
                return
        else:
            if attempt < max_attempts - 1:
                print("⏳ Waiting 30 seconds before next attempt...")
                time.sleep(30)
            else:
                print("❌ Deployment not ready after maximum attempts.")
                print("Please wait a few more minutes and try again manually.")

if __name__ == "__main__":
    main() 