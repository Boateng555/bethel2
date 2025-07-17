from django.core.management.base import BaseCommand
from django.conf import settings
import os
import cloudinary
import cloudinary.uploader
from core.models import (
    Church, Ministry, News, Sermon, HeroMedia, EventHighlight, 
    EventSpeaker, Hero, AboutPage, LeadershipPage
)

class Command(BaseCommand):
    help = 'Upload all media files to Cloudinary and update database URLs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without actually uploading',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting Cloudinary media upload...'))
        
        # Check environment variables
        required_vars = ['CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            self.stdout.write(
                self.style.ERROR(f'❌ Missing environment variables: {", ".join(missing_vars)}')
            )
            return
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
            api_key=os.environ.get('CLOUDINARY_API_KEY'),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET')
        )
        
        self.stdout.write('✅ Cloudinary credentials found')
        
        # Define models and their media fields
        models_to_update = [
            (Church, 'logo', 'churches/logos'),
            (Ministry, 'image', 'ministries'),
            (News, 'image', 'news'),
            (Sermon, 'thumbnail', 'sermons/thumbnails'),
            (HeroMedia, 'image', 'hero'),
            (EventHighlight, 'image', 'event_highlights'),
            (EventSpeaker, 'photo', 'events/speakers'),
            (Hero, 'background_image', 'hero'),
            (AboutPage, 'logo', 'about'),
            (AboutPage, 'founder_image', 'about'),
            (AboutPage, 'extra_image', 'about'),
            (LeadershipPage, 'chairman_image', 'leadership'),
            (LeadershipPage, 'vice_chairman_image', 'leadership'),
            (LeadershipPage, 'board_image', 'leadership'),
            (LeadershipPage, 'team_image', 'leadership'),
            (LeadershipPage, 'leadership_photo_1', 'leadership'),
            (LeadershipPage, 'leadership_photo_2', 'leadership'),
            (LeadershipPage, 'leadership_photo_3', 'leadership'),
        ]
        
        total_uploaded = 0
        total_failed = 0
        
        for model, field_name, folder_name in models_to_update:
            self.stdout.write(f'\n📝 Processing {model.__name__} {field_name}...')
            
            for instance in model.objects.all():
                field = getattr(instance, field_name)
                if not field or not hasattr(field, 'name') or not field.name:
                    continue
                
                # Check if already a Cloudinary URL
                if 'res.cloudinary.com' in str(field):
                    self.stdout.write(f'  ⏭️  {model.__name__} {instance.id}: Already Cloudinary URL')
                    continue
                
                # Get local file path
                local_path = field.path if hasattr(field, 'path') else None
                if not local_path or not os.path.exists(local_path):
                    self.stdout.write(f'  ⚠️  {model.__name__} {instance.id}: File not found - {field}')
                    continue
                
                if options['dry_run']:
                    self.stdout.write(f'  📋 Would upload: {local_path}')
                    continue
                
                # Upload to Cloudinary
                try:
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder=folder_name,
                        resource_type="auto"
                    )
                    cloudinary_url = result.get('secure_url')
                    
                    if cloudinary_url:
                        # Update the field
                        setattr(instance, field_name, cloudinary_url)
                        instance.save()
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✅ {model.__name__} {instance.id}: {cloudinary_url}')
                        )
                        total_uploaded += 1
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'  ❌ {model.__name__} {instance.id}: Upload failed')
                        )
                        total_failed += 1
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ {model.__name__} {instance.id}: Error - {e}')
                    )
                    total_failed += 1
        
        self.stdout.write('\n' + '='*50)
        if options['dry_run']:
            self.stdout.write('📋 Dry run completed - no files were uploaded')
        else:
            self.stdout.write(f'🎉 Upload completed!')
            self.stdout.write(f'✅ Successfully uploaded: {total_uploaded}')
            self.stdout.write(f'❌ Failed uploads: {total_failed}') 