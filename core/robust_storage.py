import os
import uuid
import requests
from io import BytesIO
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible
from imagekitio import ImageKit
from PIL import Image
import logging

logger = logging.getLogger(__name__)

@deconstructible
class RobustImageKitStorage(Storage):
    """
    Robust Django storage backend for ImageKit.io that prevents corruption
    and ensures proper image handling
    """

    def __init__(self, location=None, base_url=None):
        self.location = location or ''
        self.base_url = base_url or settings.IMAGEKIT_CONFIG.get('URL_ENDPOINT')
        
        # Ensure environment variables are set
        os.environ.setdefault('IMAGEKIT_PUBLIC_KEY', settings.IMAGEKIT_CONFIG.get('PUBLIC_KEY', ''))
        os.environ.setdefault('IMAGEKIT_PRIVATE_KEY', settings.IMAGEKIT_CONFIG.get('PRIVATE_KEY', ''))
        os.environ.setdefault('IMAGEKIT_URL_ENDPOINT', settings.IMAGEKIT_CONFIG.get('URL_ENDPOINT', ''))
        
        self.imagekit = ImageKit(
            public_key=settings.IMAGEKIT_CONFIG['PUBLIC_KEY'],
            private_key=settings.IMAGEKIT_CONFIG['PRIVATE_KEY'],
            url_endpoint=self.base_url
        )

    def _clean_name(self, name):
        return name.lstrip('/').replace('\\', '/')

    def _get_extension(self, filename):
        return os.path.splitext(filename)[1] if filename else ''

    def _validate_image(self, file_bytes, filename):
        """Validate that the file is a real image and not corrupted"""
        try:
            # Check file size
            if len(file_bytes) < 100:
                raise ValueError(f"File too small ({len(file_bytes)} bytes) - likely corrupted")
            
            # Try to open as image to validate
            image = Image.open(BytesIO(file_bytes))
            image.verify()  # Verify the image
            
            # Get image info
            image = Image.open(BytesIO(file_bytes))
            width, height = image.size
            
            # Log image details
            logger.info(f"Validated image: {filename} - Size: {len(file_bytes)} bytes, Dimensions: {width}x{height}")
            
            return True
            
        except Exception as e:
            logger.error(f"Image validation failed for {filename}: {e}")
            raise ValueError(f"Invalid or corrupted image: {e}")

    def _save(self, name, content):
        """
        Robust save method that validates and uploads images properly
        """
        name = self._clean_name(name or f"{uuid.uuid4()}{self._get_extension(content.name)}")
        
        # Ensure content is properly read as bytes
        if hasattr(content, 'read'):
            content.seek(0)
            file_bytes = content.read()
        else:
            file_bytes = bytes(content)
        
        # Validate the image
        self._validate_image(file_bytes, name)
        
        # Create proper file object for upload
        file_obj = BytesIO(file_bytes)
        file_obj.seek(0)
        file_obj.name = os.path.basename(name)
        
        # Upload to ImageKit
        try:
            upload = self.imagekit.upload_file(
                file=file_obj,
                file_name=name  # Use the full path instead of just basename
            )
            
            if upload.response_metadata.http_status_code != 200:
                raise Exception(f"ImageKit upload failed: {upload.response_metadata.raw}")
            
            # Return the full ImageKit URL instead of just the path
            uploaded_path = upload.file_path.lstrip('/')
            full_url = f"{self.base_url}/{uploaded_path}"
            
            # Verify the uploaded file size
            uploaded_size = self.size(uploaded_path)
            if uploaded_size < 100:
                raise Exception(f"Uploaded file is too small ({uploaded_size} bytes) - upload may have failed")
            
            logger.info(f"Successfully uploaded: {full_url} - Size: {uploaded_size} bytes")
            return full_url
            
        except Exception as e:
            logger.error(f"Upload error for {name}: {e}")
            raise

    def _open(self, name, mode='rb'):
        url = self.url(name)
        response = requests.get(url)
        if response.status_code == 200:
            return ContentFile(response.content, name=name)
        raise FileNotFoundError(f"File {name} not found in ImageKit")

    def delete(self, name):
        name = self._clean_name(name)
        try:
            files = self.imagekit.list_files()
            for file in files.list:
                if file.file_path == name:
                    result = self.imagekit.delete_file(file.file_id)
                    return result.response_metadata.http_status_code == 200
        except Exception as e:
            logger.error(f"Delete error for {name}: {e}")
        return False

    def exists(self, name):
        name = self._clean_name(name)
        try:
            files = self.imagekit.list_files()
            for file in files.list:
                if file.file_path == name:
                    return True
            return False
        except Exception as e:
            logger.error(f"Exists check error for {name}: {e}")
            return False

    def url(self, name):
        if not name:
            return ''
        
        # If name is already a full ImageKit URL, return it as is
        if name.startswith('https://ik.imagekit.io/'):
            return name
        
        # Otherwise, construct the URL from the path
        clean_name = self._clean_name(name)
        return f"{self.base_url}/{clean_name}"

    def size(self, name):
        try:
            files = self.imagekit.list_files()
            for file in files.list:
                if file.file_path == self._clean_name(name):
                    return file.size
            return 0
        except Exception as e:
            logger.error(f"Size check error for {name}: {e}")
            return 0

    def get_created_time(self, name):
        try:
            files = self.imagekit.list_files()
            for file in files.list:
                if file.file_path == self._clean_name(name):
                    return file.created_at
            return None
        except Exception as e:
            logger.error(f"Created time check error for {name}: {e}")
            return None

    def get_modified_time(self, name):
        try:
            files = self.imagekit.list_files()
            for file in files.list:
                if file.file_path == self._clean_name(name):
                    return file.updated_at
            return None
        except Exception as e:
            logger.error(f"Modified time check error for {name}: {e}")
            return None

    def get_accessed_time(self, name):
        return self.get_modified_time(name) 