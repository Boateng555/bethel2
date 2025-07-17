from django.core.management.base import BaseCommand
from django.conf import settings
import os
import base64
import hashlib
import hmac
import time
import requests
from core.models import Church, Event, Ministry, News, Sermon, HeroMedia

class Command(BaseCommand):
    help = 'Upload all media files to ImageKit and update database URLs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without actually uploading',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting ImageKit media upload...'))
        
        # Check environment variables
        required_vars = ['IMAGEKIT_PUBLIC_KEY', 'IMAGEKIT_PRIVATE_KEY', 'IMAGEKIT_URL_ENDPOINT']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            self.stdout.write(
                self.style.ERROR(f'❌ Missing environment variables: {", ".join(missing_vars)}')
            )
            return
        
        self.stdout.write('✅ ImageKit credentials found')
        
        # Define models and their media fields
        models_to_update = [
            (Church, 'logo', 'churches/logos'),
            (Event, 'image', 'events'),
            (Ministry, 'image', 'ministries'),
            (News, 'image', 'news'),
            (Sermon, 'thumbnail', 'sermons/thumbnails'),
            (HeroMedia, 'image', 'hero'),
        ]
        
        total_uploaded = 0
        total_failed = 0
        
        for model, field_name, folder_name in models_to_update:
            self.stdout.write(f'\n📝 Processing {model.__name__} {field_name}...')
            
            for instance in model.objects.all():
                field = getattr(instance, field_name)
                if not field or not hasattr(field, 'name') or not field.name:
                    continue
                
                # Check if already an ImageKit URL
                if 'imagekit.io' in str(field):
                    self.stdout.write(f'  ⏭️  {model.__name__} {instance.id}: Already ImageKit URL')
                    continue
                
                # Get local file path
                local_path = field.path if hasattr(field, 'path') else None
                if not local_path or not os.path.exists(local_path):
                    self.stdout.write(f'  ⚠️  {model.__name__} {instance.id}: File not found - {field}')
                    continue
                
                if options['dry_run']:
                    self.stdout.write(f'  📋 Would upload: {local_path}')
                    continue
                
                # Upload to ImageKit
                imagekit_url = self.upload_to_imagekit(local_path, folder_name)
                if imagekit_url:
                    # Update the field
                    setattr(instance, field_name, imagekit_url)
                    instance.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ {model.__name__} {instance.id}: {imagekit_url}')
                    )
                    total_uploaded += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ {model.__name__} {instance.id}: Upload failed')
                    )
                    total_failed += 1
        
        self.stdout.write('\n' + '='*50)
        if options['dry_run']:
            self.stdout.write('📋 Dry run completed - no files were uploaded')
        else:
            self.stdout.write(f'🎉 Upload completed!')
            self.stdout.write(f'✅ Successfully uploaded: {total_uploaded}')
            self.stdout.write(f'❌ Failed uploads: {total_failed}')

    def upload_to_imagekit(self, file_path, folder_name="bethel"):
        """Upload a file to ImageKit using direct HTTP requests"""
        try:
            # Read the file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Get file name
            file_name = os.path.basename(file_path)
            
            # Prepare the upload data
            upload_data = {
                'file': (file_name, file_data),
                'fileName': file_name,
                'folder': folder_name,
            }
            
            # Get ImageKit credentials
            public_key = os.environ.get('IMAGEKIT_PUBLIC_KEY')
            private_key = os.environ.get('IMAGEKIT_PRIVATE_KEY')
            url_endpoint = os.environ.get('IMAGEKIT_URL_ENDPOINT')
            
            # Create signature
            timestamp = str(int(time.time()))
            signature = self.create_signature(private_key, timestamp)
            
            # Prepare headers
            headers = {
                'Authorization': f'Basic {base64.b64encode(f"{public_key}:{signature}".encode()).decode()}',
                'x-ik-timestamp': timestamp,
            }
            
            # Upload to ImageKit
            response = requests.post(
                'https://upload.imagekit.io/api/v1/files/upload',
                files=upload_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('url')
            else:
                self.stdout.write(f'    Upload failed: {response.status_code} - {response.text}')
                return None
                
        except Exception as e:
            self.stdout.write(f'    Error uploading: {e}')
            return None

    def create_signature(self, private_key, timestamp):
        """Create signature for ImageKit API"""
        message = private_key + timestamp
        signature = hmac.new(
            private_key.encode(),
            message.encode(),
            hashlib.sha1
        ).hexdigest()
        return signature 