#!/usr/bin/env python
"""
Script to help you get Cloudinary credentials for local development
"""
import webbrowser
import os

def get_cloudinary_credentials():
    """Help user get Cloudinary credentials"""
    print("🔧 Getting Cloudinary Credentials for Local Development")
    print("=" * 60)
    
    print("Your database has Cloudinary URLs, but you need credentials to view them locally.")
    print()
    
    # Open Cloudinary console
    print("📱 Opening Cloudinary Console...")
    webbrowser.open("https://cloudinary.com/console")
    
    print("\n📋 Follow these steps:")
    print("1. Sign in to your Cloudinary account")
    print("2. Go to the 'Dashboard' tab")
    print("3. Look for 'Account Details' section")
    print("4. Copy these values:")
    print("   - Cloud Name: dhzdusb5k (you already have this)")
    print("   - API Key: (copy from dashboard)")
    print("   - API Secret: (copy from dashboard)")
    print()
    
    print("🔧 Then update your .env file:")
    print("Replace these lines in your .env file:")
    print("CLOUDINARY_API_KEY=your_cloudinary_api_key_here")
    print("CLOUDINARY_API_SECRET=your_cloudinary_api_secret_here")
    print()
    
    print("With your actual credentials:")
    print("CLOUDINARY_API_KEY=123456789012345")
    print("CLOUDINARY_API_SECRET=abcdefghijklmnopqrstuvwxyz")
    print()
    
    print("🔄 After updating .env, restart your Django server:")
    print("python manage.py runserver")
    print()
    
    print("✅ Your images should then work in local development!")

if __name__ == "__main__":
    get_cloudinary_credentials() 