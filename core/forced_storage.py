"""
Forced ImageKit Storage Backend
This ensures ImageKit storage is always used when configured
"""

import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings

class ForcedImageKitStorage(FileSystemStorage):
    """
    A storage backend that forces ImageKit usage
    """
    
    def __init__(self, *args, **kwargs):
        # Ensure environment variables are set
        if hasattr(settings, 'IMAGEKIT_CONFIG'):
            os.environ.setdefault('IMAGEKIT_PUBLIC_KEY', settings.IMAGEKIT_CONFIG.get('PUBLIC_KEY', ''))
            os.environ.setdefault('IMAGEKIT_PRIVATE_KEY', settings.IMAGEKIT_CONFIG.get('PRIVATE_KEY', ''))
            os.environ.setdefault('IMAGEKIT_URL_ENDPOINT', settings.IMAGEKIT_CONFIG.get('URL_ENDPOINT', ''))
        
        # Import and use ImageKit storage
        try:
            from core.storage import ImageKitStorage
            self.imagekit_storage = ImageKitStorage()
            print("✅ Forced ImageKit storage initialized")
        except Exception as e:
            print(f"⚠️ Could not initialize ImageKit storage: {e}")
            super().__init__(*args, **kwargs)
            return
    
    def _save(self, name, content):
        """Save file using ImageKit storage"""
        try:
            return self.imagekit_storage._save(name, content)
        except Exception as e:
            print(f"⚠️ ImageKit save failed, falling back to local: {e}")
            return super()._save(name, content)
    
    def url(self, name):
        """Get URL using ImageKit storage"""
        try:
            return self.imagekit_storage.url(name)
        except Exception as e:
            print(f"⚠️ ImageKit URL failed, falling back to local: {e}")
            return super().url(name)
    
    def delete(self, name):
        """Delete file using ImageKit storage"""
        try:
            return self.imagekit_storage.delete(name)
        except Exception as e:
            print(f"⚠️ ImageKit delete failed, falling back to local: {e}")
            return super().delete(name)
    
    def exists(self, name):
        """Check if file exists using ImageKit storage"""
        try:
            return self.imagekit_storage.exists(name)
        except Exception as e:
            print(f"⚠️ ImageKit exists failed, falling back to local: {e}")
            return super().exists(name)
    
    def size(self, name):
        """Get file size using ImageKit storage"""
        try:
            return self.imagekit_storage.size(name)
        except Exception as e:
            print(f"⚠️ ImageKit size failed, falling back to local: {e}")
            return super().size(name) 