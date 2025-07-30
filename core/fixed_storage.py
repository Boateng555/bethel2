import os
import uuid
import requests
from io import BytesIO
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible
from imagekitio import ImageKit


@deconstructible
class FixedImageKitStorage(Storage):
    """
    Fixed Django storage backend for ImageKit.io
    """

    def __init__(self, location=None, base_url=None):
        self.location = location or ''
        self.base_url = base_url or settings.IMAGEKIT_CONFIG.get('URL_ENDPOINT')
        self.imagekit = ImageKit(
            public_key=settings.IMAGEKIT_CONFIG['PUBLIC_KEY'],
            private_key=settings.IMAGEKIT_CONFIG['PRIVATE_KEY'],
            url_endpoint=self.base_url
        )

    def _clean_name(self, name):
        return name.lstrip('/').replace('\\', '/')

    def _get_extension(self, filename):
        return os.path.splitext(filename)[1] if filename else ''

    def _save(self, name, content):
        name = self._clean_name(name or f"{uuid.uuid4()}{self._get_extension(content.name)}")

        # Read the content into bytes
        if hasattr(content, 'read'):
            content.seek(0)
            file_bytes = content.read()
        else:
            file_bytes = content

        # Create BytesIO object for upload
        file_obj = BytesIO(file_bytes)
        file_obj.name = os.path.basename(name)
        file_obj.seek(0)

        # Upload to ImageKit
        try:
            upload = self.imagekit.upload_file(
                file=file_obj,
                file_name=os.path.basename(name)
            )

            if upload.response_metadata.http_status_code != 200:
                raise Exception(f"ImageKit upload failed: {upload.response_metadata.raw}")
            
            # Return the actual file path from ImageKit response
            return upload.file_path.lstrip('/')
            
        except Exception as e:
            print(f"❌ ImageKit upload error: {e}")
            # Fallback: save to local storage temporarily
            from django.core.files.storage import FileSystemStorage
            local_storage = FileSystemStorage()
            return local_storage.save(name, content)

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
        except Exception:
            pass
        return False

    def exists(self, name):
        name = self._clean_name(name)
        try:
            files = self.imagekit.list_files()
            for file in files.list:
                if file.file_path == name:
                    return True
            return False
        except Exception:
            return False

    def url(self, name):
        if not name:
            return ''
        
        # If name is already a full ImageKit URL, return it as is
        if name.startswith('https://ik.imagekit.io/'):
            return name
        
        clean_name = self._clean_name(name)
        # Return the full ImageKit URL
        return f"{self.base_url}/{clean_name}"

    def size(self, name):
        try:
            files = self.imagekit.list_files()
            for file in files.list:
                if file.file_path == self._clean_name(name):
                    return file.size
            return 0
        except Exception:
            return 0

    def get_created_time(self, name):
        try:
            files = self.imagekit.list_files()
            for file in files.list:
                if file.file_path == self._clean_name(name):
                    return file.created_at
            return None
        except Exception:
            return None

    def get_modified_time(self, name):
        try:
            files = self.imagekit.list_files()
            for file in files.list:
                if file.file_path == self._clean_name(name):
                    return file.updated_at
            return None
        except Exception:
            return None

    def get_accessed_time(self, name):
        return self.get_modified_time(name) 