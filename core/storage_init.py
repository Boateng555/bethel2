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
        # Set environment variables
        os.environ.setdefault('IMAGEKIT_PUBLIC_KEY', 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=')
        os.environ.setdefault('IMAGEKIT_PRIVATE_KEY', 'private_Dnsrj2VW7uJakaeMaNYaav+P784=')
        os.environ.setdefault('IMAGEKIT_URL_ENDPOINT', 'https://ik.imagekit.io/9buar9mbp')
        
        # Import ImageKit storage
        from core.storage import ImageKitStorage
        
        # Create ImageKit storage instance
        imagekit_storage = ImageKitStorage()
        
        # Override the default storage
        default_storage._wrapped = imagekit_storage
        
        print("✅ ImageKit storage initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize ImageKit storage: {e}")
        return False

# Auto-execute when imported (after Django setup)
initialize_imagekit_storage() 