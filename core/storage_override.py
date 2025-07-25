"""
Direct storage override to force ImageKit usage
"""

import os
from django.core.files.storage import default_storage
from django.conf import settings

def force_imagekit_storage():
    """
    Force Django to use ImageKit storage by directly overriding default_storage
    """
    try:
        # Ensure environment variables are set
        if hasattr(settings, 'IMAGEKIT_CONFIG'):
            os.environ.setdefault('IMAGEKIT_PUBLIC_KEY', settings.IMAGEKIT_CONFIG.get('PUBLIC_KEY', ''))
            os.environ.setdefault('IMAGEKIT_PRIVATE_KEY', settings.IMAGEKIT_CONFIG.get('PRIVATE_KEY', ''))
            os.environ.setdefault('IMAGEKIT_URL_ENDPOINT', settings.IMAGEKIT_CONFIG.get('URL_ENDPOINT', ''))
        
        # Import ImageKit storage
        from core.storage import ImageKitStorage
        
        # Create ImageKit storage instance
        imagekit_storage = ImageKitStorage()
        
        # Directly override the default storage
        default_storage._wrapped = imagekit_storage
        
        print("✅ Successfully forced ImageKit storage")
        return True
        
    except Exception as e:
        print(f"❌ Failed to force ImageKit storage: {e}")
        return False

# Auto-execute when imported
if hasattr(settings, 'IMAGEKIT_CONFIG') and all(settings.IMAGEKIT_CONFIG.values()):
    force_imagekit_storage() 