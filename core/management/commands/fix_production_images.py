from django.core.management.base import BaseCommand
from django.conf import settings
import os
import requests
from django.core.files.base import ContentFile
from core.models import HeroMedia, Church, News, Ministry, Sermon

class Command(BaseCommand):
    help = 'Fix image URLs in production database to use ImageKit'

    def add_arguments(self, parser):
        parser.add_argument(
            '--upload-placeholders',
            action='store_true',
            help='Upload placeholder images for missing files',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔧 Fixing Production Database Image URLs'))
        self.stdout.write('=' * 60)
        
        # Check if we're connected to production database
        db_info = settings.DATABASES['default']
        if 'sqlite' in db_info['ENGINE']:
            self.stdout.write(
                self.style.ERROR('❌ Connected to local SQLite database!')
            )
            self.stdout.write('💡 This command needs to run on Railway with production database.')
            return
        
        self.stdout.write(self.style.SUCCESS('✅ Connected to production database'))
        self.stdout.write(f'📦 Storage Backend: {settings.DEFAULT_FILE_STORAGE}')
        
        # Check if ImageKit is configured
        if not all(settings.IMAGEKIT_CONFIG.values()):
            self.stdout.write(
                self.style.ERROR('❌ ImageKit not configured in production!')
            )
            return
        
        self.stdout.write(self.style.SUCCESS('✅ ImageKit configured'))
        
        # Models to fix
        models_to_fix = [
            (HeroMedia, 'image', 'hero'),
            (Church, 'logo', 'churches/logos'),
            (News, 'image', 'news'),
            (Ministry, 'image', 'ministries'),
            (Sermon, 'thumbnail', 'sermons/thumbnails'),
        ]
        
        total_fixed = 0
        total_errors = 0
        
        for model, field_name, folder in models_to_fix:
            self.stdout.write(f'\n📋 Fixing {model.__name__}.{field_name}...')
            
            instances = model.objects.all()
            self.stdout.write(f'  Found {instances.count()} instances')
            
            for instance in instances:
                field = getattr(instance, field_name)
                if not field:
                    continue
                    
                field_str = str(field)
                self.stdout.write(f'  📋 {instance} - Current: {field_str}')
                
                # Check if it's already a proper ImageKit path
                if not field_str.startswith('http') and '/' in field_str:
                    self.stdout.write(f'    ✅ Already ImageKit path')
                    continue
                
                # Check if it's already ImageKit URL
                if 'ik.imagekit.io' in field_str:
                    self.stdout.write(f'    ✅ Already ImageKit URL')
                    continue
                
                # Handle Cloudinary URLs
                if 'res.cloudinary.com' in field_str:
                    try:
                        self.stdout.write(f'    📤 Downloading from Cloudinary...')
                        
                        # Download from Cloudinary
                        response = requests.get(field_str, timeout=30)
                        if response.status_code != 200:
                            self.stdout.write(
                                self.style.ERROR(f'      ❌ Failed to download: {response.status_code}')
                            )
                            total_errors += 1
                            continue
                        
                        # Get filename
                        filename = os.path.basename(field_str.split('/')[-1])
                        if '?' in filename:
                            filename = filename.split('?')[0]
                        
                        # Create new file path for ImageKit
                        new_path = f"{folder}/{filename}"
                        
                        # Create ContentFile
                        content_file = ContentFile(response.content, name=filename)
                        
                        # Save to ImageKit
                        from django.core.files.storage import default_storage
                        saved_path = default_storage.save(new_path, content_file)
                        
                        # Update the field
                        setattr(instance, field_name, saved_path)
                        instance.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'      ✅ Migrated to: {saved_path}')
                        )
                        total_fixed += 1
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'      ❌ Error: {e}')
                        )
                        total_errors += 1
                
                # Handle local file paths
                elif field_str.startswith('/media/') or field_str.startswith('media/'):
                    try:
                        self.stdout.write(f'    📁 Converting local path...')
                        
                        # Clean the path
                        clean_path = field_str.replace('/media/', '').replace('media/', '')
                        
                        # Create new path in ImageKit folder structure
                        new_path = f"{folder}/{os.path.basename(clean_path)}"
                        
                        # Update the field
                        setattr(instance, field_name, new_path)
                        instance.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'      ✅ Converted to: {new_path}')
                        )
                        total_fixed += 1
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'      ❌ Error: {e}')
                        )
                        total_errors += 1
                
                # Upload placeholders for missing images
                elif options['upload_placeholders']:
                    try:
                        self.stdout.write(f'    📤 Uploading placeholder...')
                        
                        # Create a simple SVG placeholder
                        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1e3a8a;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="300" height="200" fill="url(#grad1)"/>
  <circle cx="150" cy="100" r="60" fill="#ffffff" opacity="0.9"/>
  <text x="150" y="95" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="#3b82f6" text-anchor="middle">BETHEL</text>
  <text x="150" y="115" font-family="Arial, sans-serif" font-size="14" fill="#1e3a8a" text-anchor="middle">{model.__name__}</text>
  <text x="150" y="135" font-family="Arial, sans-serif" font-size="12" fill="#1e3a8a" text-anchor="middle">{instance}</text>
  <text x="150" y="175" font-family="Arial, sans-serif" font-size="10" fill="#ffffff" text-anchor="middle">Production</text>
</svg>'''
                        
                        # Get filename from the path or create one
                        if '/' in field_str:
                            filename = os.path.basename(field_str)
                        else:
                            filename = f"{model.__name__.lower()}_{instance.id}.svg"
                        
                        if not filename.endswith('.svg'):
                            filename = filename.replace('.png', '.svg').replace('.jpg', '.svg').replace('.jpeg', '.svg')
                        
                        # Create new path
                        new_path = f"{folder}/{filename}"
                        
                        # Create ContentFile
                        content_file = ContentFile(svg_content.encode('utf-8'), name=filename)
                        
                        # Save to ImageKit
                        from django.core.files.storage import default_storage
                        saved_path = default_storage.save(new_path, content_file)
                        
                        # Update the field
                        setattr(instance, field_name, saved_path)
                        instance.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'      ✅ Uploaded placeholder: {saved_path}')
                        )
                        total_fixed += 1
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'      ❌ Error uploading placeholder: {e}')
                        )
                        total_errors += 1
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(f'🎉 Production database fix completed!')
        self.stdout.write(f'✅ Successfully fixed: {total_fixed}')
        self.stdout.write(f'❌ Errors: {total_errors}')
        
        if total_fixed > 0:
            self.stdout.write('\n🔄 Production database updated!')
            self.stdout.write('💡 Your production site should now show images correctly.') 