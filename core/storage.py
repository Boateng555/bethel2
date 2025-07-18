import os
import imagekitio
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible
import requests
import uuid


@deconstructible
class ImageKitStorage(Storage):
    """
    Custom storage backend for ImageKit.io
    """
    
    def __init__(self, location=None, base_url=None):
        super().__init__()
        self.location = location or ''
        self.base_url = base_url
        
        # Initialize ImageKit client with error handling
        try:
            self.imagekit = imagekitio.ImageKit(
                public_key=settings.IMAGEKIT_CONFIG['PUBLIC_KEY'],
                private_key=settings.IMAGEKIT_CONFIG['PRIVATE_KEY'],
                url_endpoint=settings.IMAGEKIT_CONFIG['URL_ENDPOINT']
            )
        except Exception as e:
            print(f"❌ Failed to initialize ImageKit: {e}")
            raise Exception(f"ImageKit initialization failed: {e}")
    
    def _open(self, name, mode='rb'):
        """Open a file from ImageKit"""
        url = self.url(name)
        response = requests.get(url)
        if response.status_code == 200:
            return ContentFile(response.content, name=name)
        else:
            raise FileNotFoundError(f"File {name} not found in ImageKit")
    
    def _save(self, name, content):
        """Save a file to ImageKit"""
        # Generate a unique filename if needed
        if not name:
            ext = self._get_extension(content.name)
            name = f"{uuid.uuid4()}{ext}"
        
        # Ensure the name is clean
        name = self._clean_name(name)
        
        try:
            # Upload to ImageKit
            result = self.imagekit.upload_file(
                file=content,
                file_name=os.path.basename(name),
                options={
                    "folder": os.path.dirname(name) if os.path.dirname(name) else "bethel",
                    "use_unique_file_name": False
                }
            )
            
            if result.response_metadata.http_status_code == 200:
                return name
            else:
                raise Exception(f"Upload failed: {result.response_metadata.raw}")
                
        except Exception as e:
            raise Exception(f"ImageKit upload error: {str(e)}")
    
    def delete(self, name):
        """Delete a file from ImageKit"""
        try:
            # Get file ID first
            files = self.imagekit.list_files(options={"path": name})
            if files.response_metadata.http_status_code == 200 and files.list:
                file_id = files.list[0].file_id
                result = self.imagekit.delete_file(file_id)
                return result.response_metadata.http_status_code == 200
            return False
        except Exception:
            return False
    
    def exists(self, name):
        """Check if a file exists in ImageKit"""
        try:
            files = self.imagekit.list_files(options={"path": name})
            return files.response_metadata.http_status_code == 200 and bool(files.list)
        except Exception:
            return False
    
    def url(self, name):
        """Get the URL for a file in ImageKit"""
        if not name:
            return ''
        
        # Clean the name
        name = self._clean_name(name)
        
        # Return the ImageKit URL
        return f"{settings.IMAGEKIT_CONFIG['URL_ENDPOINT']}/{name}"
    
    def size(self, name):
        """Get the size of a file in ImageKit"""
        try:
            files = self.imagekit.list_files(options={"path": name})
            if files.response_metadata.http_status_code == 200 and files.list:
                return files.list[0].size
            return 0
        except Exception:
            return 0
    
    def _clean_name(self, name):
        """Clean the filename for ImageKit"""
        # Remove any leading slashes
        name = name.lstrip('/')
        
        # Replace any problematic characters
        name = name.replace('\\', '/')
        
        return name
    
    def _get_extension(self, filename):
        """Get file extension from filename"""
        if filename:
            return os.path.splitext(filename)[1]
        return ''
    
    def get_accessed_time(self, name):
        """Get the last accessed time of a file"""
        # ImageKit doesn't provide access time, so return modification time
        return self.get_modified_time(name)
    
    def get_created_time(self, name):
        """Get the creation time of a file"""
        try:
            files = self.imagekit.list_files(options={"path": name})
            if files.response_metadata.http_status_code == 200 and files.list:
                return files.list[0].created_at
            return None
        except Exception:
            return None
    
    def get_modified_time(self, name):
        """Get the modification time of a file"""
        try:
            files = self.imagekit.list_files(options={"path": name})
            if files.response_metadata.http_status_code == 200 and files.list:
                return files.list[0].updated_at
            return None
        except Exception:
            return None 