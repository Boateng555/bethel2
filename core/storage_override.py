"""
Direct storage override to force ImageKit usage
"""

import os
from django.core.files.storage import default_storage

def force_imagekit_storage():
    """
    Force Django to use ImageKit storage by directly overriding default_storage
    """
    try:
        # Set environment variables directly
        os.environ.setdefault('IMAGEKIT_PUBLIC_KEY', 'public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=')
        os.environ.setdefault('IMAGEKIT_PRIVATE_KEY', 'private_Dnsrj2VW7uJakaeMaNYaav+P784=')
        os.environ.setdefault('IMAGEKIT_URL_ENDPOINT', 'https://ik.imagekit.io/9buar9mbp')
        
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

# Don't auto-execute - let Django load first
# force_imagekit_storage() 