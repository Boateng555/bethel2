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
class ImageKitStorage(Storage):
    """
    Custom Django storage backend for ImageKit.io
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

        upload = self.imagekit.upload_file(
            file=content,
            file_name=os.path.basename(name),
            options={
                "folder": os.path.dirname(name) or "bethel",
                "use_unique_file_name": False
            }
        )

        if upload.response_metadata.http_status_code != 200:
            raise Exception(f"ImageKit upload failed: {upload.response_metadata.raw}")
        return name

    def _open(self, name, mode='rb'):
        url = self.url(name)
        response = requests.get(url)
        if response.status_code == 200:
            return ContentFile(response.content, name=name)
        raise FileNotFoundError(f"File {name} not found in ImageKit")

    def delete(self, name):
        name = self._clean_name(name)
        try:
            files = self.imagekit.list_files(options={"path": name})
            if files.list:
                file_id = files.list[0].file_id
                result = self.imagekit.delete_file(file_id)
                return result.response_metadata.http_status_code == 200
        except Exception:
            pass
        return False

    def exists(self, name):
        name = self._clean_name(name)
        try:
            files = self.imagekit.list_files(options={"path": name})
            return bool(files.list)
        except Exception:
            return False

    def url(self, name):
        return f"{self.base_url}/{self._clean_name(name)}" if name else ''

    def size(self, name):
        try:
            files = self.imagekit.list_files(options={"path": self._clean_name(name)})
            return files.list[0].size if files.list else 0
        except Exception:
            return 0

    def get_created_time(self, name):
        try:
            files = self.imagekit.list_files(options={"path": self._clean_name(name)})
            return files.list[0].created_at if files.list else None
        except Exception:
            return None

    def get_modified_time(self, name):
        try:
            files = self.imagekit.list_files(options={"path": self._clean_name(name)})
            return files.list[0].updated_at if files.list else None
        except Exception:
            return None

    def get_accessed_time(self, name):
        return self.get_modified_time(name)
