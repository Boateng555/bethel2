"""
Storage initialization that runs after Django is fully loaded
"""

import os
from django.core.files.storage import default_storage

def initialize_imagekit_storage():
    """
    Initialize ImageKit storage after Django is fully loaded
    """
    try:
        # Check if ImageKit credentials are available
        public_key = os.environ.get('IMAGEKIT_PUBLIC_KEY')
        private_key = os.environ.get('IMAGEKIT_PRIVATE_KEY')
        url_endpoint = os.environ.get('IMAGEKIT_URL_ENDPOINT')
        
        if not all([public_key, private_key, url_endpoint]):
            print("⚠️ ImageKit credentials not found, using default storage")
            return False
        
        # Import ImageKit storage
        from core.storage import ImageKitStorage
        
        # Create ImageKit storage instance
        imagekit_storage = ImageKitStorage()
        
        # Override the default storage
        from django.core.files.storage import default_storage
        default_storage._wrapped = imagekit_storage
        
        print("✅ ImageKit storage initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize ImageKit storage: {e}")
        return False

# Auto-execute when imported (after Django setup)
initialize_imagekit_storage() 