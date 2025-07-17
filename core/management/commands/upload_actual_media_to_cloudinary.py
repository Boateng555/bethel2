import os
import cloudinary
import cloudinary.uploader
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage
from core.models import Church, News, Ministry, Sermon, HeroMedia, EventSpeaker, AboutPage, LeadershipPage
import glob

class Command(BaseCommand):
    help = 'Upload actual media files to Cloudinary and update database URLs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without actually uploading',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
        )
        
        self.stdout.write("🔧 Using local storage for development")
        self.stdout.write("🔧 Serving local media files for development")
        self.stdout.write("🚀 Starting media upload to Cloudinary...")
        self.stdout.write("=" * 60)
        self.stdout.write(f"☁️ Cloudinary configured: {settings.CLOUDINARY_STORAGE['CLOUD_NAME']}")
        
        uploaded_count = 0
        failed_count = 0
        
        # Process each media type
        media_types = [
            ('churches/logos', Church, 'logo'),
            ('news', News, 'image'),
            ('ministries', Ministry, 'image'),
            ('sermons/thumbnails', Sermon, 'thumbnail'),
            ('hero', HeroMedia, 'image'),
            ('events/speakers', EventSpeaker, 'image'),
            ('about', AboutPage, 'image'),
            ('leadership', LeadershipPage, 'image'),
        ]
        
        for media_path, model, field_name in media_types:
            self.stdout.write(f"\n📋 Processing {model.__name__} {field_name}s...")
            
            # Get all files in the media directory
            full_path = os.path.join(settings.MEDIA_ROOT, media_path)
            if not os.path.exists(full_path):
                self.stdout.write(f"  ⚠️ Directory not found: {full_path}")
                continue
                
            # Get all files in the directory
            files = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']:
                files.extend(glob.glob(os.path.join(full_path, ext)))
                files.extend(glob.glob(os.path.join(full_path, ext.upper())))
            
            if not files:
                self.stdout.write(f"  ⚠️ No media files found in {media_path}")
                continue
            
            # Upload each file
            for file_path in files:
                filename = os.path.basename(file_path)
                relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
                
                try:
                    if dry_run:
                        self.stdout.write(f"  📁 Would upload: {relative_path}")
                        uploaded_count += 1
                    else:
                        # Upload to Cloudinary
                        result = cloudinary.uploader.upload(
                            file_path,
                            folder=f"bethel/{media_path}",
                            public_id=os.path.splitext(filename)[0],
                            overwrite=True
                        )
                        
                        cloudinary_url = result['secure_url']
                        self.stdout.write(f"  ✅ Uploaded: {relative_path} -> {cloudinary_url}")
                        
                        # Update database records that reference this file
                        self.update_database_records(model, field_name, relative_path, cloudinary_url)
                        
                        uploaded_count += 1
                        
                except Exception as e:
                    self.stdout.write(f"  ❌ Error uploading {relative_path}: {str(e)}")
                    failed_count += 1
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("🎉 Upload completed!")
        if dry_run:
            self.stdout.write(f"📋 Would upload: {uploaded_count} files")
        else:
            self.stdout.write(f"✅ Successfully uploaded: {uploaded_count}")
        self.stdout.write(f"❌ Failed uploads: {failed_count}")
    
    def update_database_records(self, model, field_name, old_path, new_url):
        """Update database records that reference the old file path"""
        try:
            # Get the field object
            field = getattr(model, field_name)
            
            # Find records that reference this file path
            if hasattr(field, 'field'):  # FileField
                field_name_str = field.field.name
            else:
                field_name_str = field_name
            
            # Create filter condition
            filter_kwargs = {f"{field_name_str}__icontains": old_path}
            
            # Update records
            updated_count = model.objects.filter(**filter_kwargs).update(**{field_name_str: new_url})
            
            if updated_count > 0:
                self.stdout.write(f"    🔄 Updated {updated_count} database records")
                
        except Exception as e:
            self.stdout.write(f"    ⚠️ Error updating database: {str(e)}") 