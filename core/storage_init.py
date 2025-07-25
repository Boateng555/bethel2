"""
Custom storage initialization to force ImageKit storage
"""

import os
from django.core.files.storage import get_storage_class
from django.conf import settings

def get_imagekit_storage():
    """
    Force ImageKit storage initialization
    """
    # Ensure environment variables are set
    if hasattr(settings, 'IMAGEKIT_CONFIG'):
        os.environ.setdefault('IMAGEKIT_PUBLIC_KEY', settings.IMAGEKIT_CONFIG.get('PUBLIC_KEY', ''))
        os.environ.setdefault('IMAGEKIT_PRIVATE_KEY', settings.IMAGEKIT_CONFIG.get('PRIVATE_KEY', ''))
        os.environ.setdefault('IMAGEKIT_URL_ENDPOINT', settings.IMAGEKIT_CONFIG.get('URL_ENDPOINT', ''))
    
    # Get the ImageKit storage class
    storage_class = get_storage_class('core.storage.ImageKitStorage')
    
    # Create and return the storage instance
    return storage_class()

# Override the default storage
from django.core.files.storage import default_storage

# Force ImageKit storage if configured
if hasattr(settings, 'IMAGEKIT_CONFIG') and all(settings.IMAGEKIT_CONFIG.values()):
    try:
        # Create a new ImageKit storage instance
        imagekit_storage = get_imagekit_storage()
        
        # Replace the default storage
        default_storage._wrapped = imagekit_storage
        print("✅ Forced ImageKit storage initialization")
    except Exception as e:
        print(f"⚠️ Could not force ImageKit storage: {e}")
        print("🔄 Using fallback storage") 