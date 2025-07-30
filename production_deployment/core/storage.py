"""
Local file storage implementation for Django
Replaces ImageKit storage with local file system storage
"""

from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


class LocalFileStorage(FileSystemStorage):
    """
    Local file storage backend for Django
    """
    
    def __init__(self, location=None, base_url=None):
        if location is None:
            location = settings.MEDIA_ROOT
        if base_url is None:
            base_url = settings.MEDIA_URL
        super().__init__(location, base_url)
    
    def url(self, name):
        """
        Return the URL where the contents of the file referenced by name can be
        accessed.
        """
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        return self.base_url + name
