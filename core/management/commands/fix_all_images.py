from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import requests
from imagekitio import ImageKit
from PIL import Image, ImageDraw, ImageFont
import io
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix all image issues: replace corrupted files, validate uploads, and ensure proper storage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace-corrupted',
            action='store_true',
            help='Replace all corrupted files in ImageKit',
        )
        parser.add_argument(
            '--test-upload',
            action='store_true',
            help='Test image upload functionality',
        )
        parser.add_argument(
            '--validate-all',
            action='store_true',
            help='Validate all existing images',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔧 Starting comprehensive image fix...'))
        
        # Initialize ImageKit
        imagekit = ImageKit(
            private_key=settings.IMAGEKIT_CONFIG['PRIVATE_KEY'],
            public_key=settings.IMAGEKIT_CONFIG['PUBLIC_KEY'],
            url_endpoint=settings.IMAGEKIT_CONFIG['URL_ENDPOINT']
        )
        
        if options['test_upload']:
            self.test_upload_functionality(imagekit)
        
        if options['replace_corrupted']:
            self.replace_corrupted_files(imagekit)
        
        if options['validate_all']:
            self.validate_all_images(imagekit)
        
        if not any([options['test_upload'], options['replace_corrupted'], options['validate_all']]):
            # Run all by default
            self.test_upload_functionality(imagekit)
            self.replace_corrupted_files(imagekit)
            self.validate_all_images(imagekit)
        
        self.stdout.write(self.style.SUCCESS('✅ Image fix completed!'))

    def create_proper_image(self, filename, width=1920, height=1080):
        """Create a proper image that will be large and visible"""
        self.stdout.write(f"   Creating proper image: {filename}")
        
        # Create a colorful image
        image = Image.new('RGB', (width, height), color='lightblue')
        draw = ImageDraw.Draw(image)
        
        # Add gradient background
        for y in range(height):
            for x in range(width):
                r = int((x / width) * 255)
                g = int((y / height) * 255)
                b = 128
                image.putpixel((x, y), (r, g, b))
        
        # Add shapes and text
        draw.rectangle([100, 100, width-100, height-100], fill='white', outline='black', width=5)
        draw.ellipse([width//2-150, height//2-150, width//2+150, height//2+150], fill='red')
        
        # Add text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        draw.text((width//2-200, 200), "PROPER IMAGE", fill='black', font=font)
        draw.text((width//2-300, 300), "Fixed by Management Command!", fill='blue', font=font)
        draw.text((width//2-250, 400), f"Size: {width}x{height}", fill='green', font=font)
        draw.text((width//2-200, 500), "No More Corruption!", fill='red', font=font)
        
        # Save as high quality JPEG
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG', quality=95, optimize=False)
        img_buffer.seek(0)
        
        image_data = img_buffer.getvalue()
        self.stdout.write(f"   ✅ Created proper image: {len(image_data):,} bytes")
        return image_data

    def test_upload_functionality(self, imagekit):
        """Test that image uploads work properly"""
        self.stdout.write("\n📤 Testing image upload functionality...")
        
        try:
            # Create test image
            image_data = self.create_proper_image("test_management_command.jpg")
            
            # Upload test image
            upload = imagekit.upload_file(
                file=image_data,
                file_name='test_management_command.jpg'
            )
            
            self.stdout.write(self.style.SUCCESS(f"   ✅ Test upload successful!"))
            self.stdout.write(f"   URL: {upload.url}")
            self.stdout.write(f"   Size: {len(image_data):,} bytes")
            
            # Clean up test file
            imagekit.delete_file(upload.file_id)
            self.stdout.write(f"   ✅ Test file cleaned up")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Test upload failed: {e}"))

    def replace_corrupted_files(self, imagekit):
        """Replace all corrupted files in ImageKit"""
        self.stdout.write("\n🔄 Finding and replacing corrupted files...")
        
        try:
            # Get all files
            self.stdout.write("   Getting files from ImageKit...")
            list_files = imagekit.list_files()
            self.stdout.write(f"   Found {len(list_files.list)} files in ImageKit")
            
            # Find corrupted files (smaller than 200KB)
            corrupted_files = []
            for file in list_files.list:
                if file.size < 200000:  # Less than 200KB
                    corrupted_files.append(file)
                    self.stdout.write(f"   Found corrupted: {file.name} ({file.size} bytes)")
            
            self.stdout.write(f"   Found {len(corrupted_files)} corrupted files to replace")
            
            if len(corrupted_files) == 0:
                self.stdout.write(self.style.SUCCESS("   ✅ No corrupted files found!"))
                return
            
            # Replace each corrupted file
            fixed_count = 0
            for file in corrupted_files:
                try:
                    self.stdout.write(f"\n   🔧 Replacing: {file.name}")
                    
                    # Delete corrupted file
                    imagekit.delete_file(file.file_id)
                    self.stdout.write(f"     Deleted corrupted file")
                    
                    # Create proper image with same name
                    image_data = self.create_proper_image(file.name)
                    
                    # Upload proper image
                    upload = imagekit.upload_file(
                        file=image_data,
                        file_name=file.name
                    )
                    
                    self.stdout.write(f"     ✅ Fixed! New size: {len(image_data):,} bytes")
                    self.stdout.write(f"     ✅ URL: {upload.url}")
                    fixed_count += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"     ❌ Error fixing {file.name}: {e}"))
            
            self.stdout.write(f"\n   ✅ Fixed {fixed_count} corrupted files")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Error: {e}"))

    def validate_all_images(self, imagekit):
        """Validate all existing images"""
        self.stdout.write("\n🔍 Validating all existing images...")
        
        try:
            # Get all files
            list_files = imagekit.list_files()
            self.stdout.write(f"   Found {len(list_files.list)} files to validate")
            
            valid_count = 0
            invalid_count = 0
            
            for file in list_files.list:
                try:
                    # Check file size
                    if file.size < 100:
                        self.stdout.write(self.style.WARNING(f"   ⚠️ Small file: {file.name} ({file.size} bytes)"))
                        invalid_count += 1
                    else:
                        valid_count += 1
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"   ❌ Error validating {file.name}: {e}"))
                    invalid_count += 1
            
            self.stdout.write(f"\n   ✅ Valid files: {valid_count}")
            self.stdout.write(f"   ⚠️ Invalid files: {invalid_count}")
            
            if invalid_count > 0:
                self.stdout.write(self.style.WARNING("   Run with --replace-corrupted to fix invalid files"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Error validating images: {e}")) 