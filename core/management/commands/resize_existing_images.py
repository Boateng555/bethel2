from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import (
    Church, Event, Ministry, News, Sermon, Hero, HeroMedia, 
    EventHighlight, EventSpeaker, AboutPage, LeadershipPage,
    LocalLeadershipPage, LocalAboutPage, EventHeroMedia
)
from core.image_utils import resize_image_field, get_image_dimensions
import os

class Command(BaseCommand):
    help = 'Resize existing images in the database to reduce file sizes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be resized without actually resizing',
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Resize images for a specific model (e.g., Church, Event, News)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🖼️ Starting image resizing process...'))
        
        # Define models and their image fields with resize settings
        models_config = {
            'Church': {
                'model': Church,
                'fields': {
                    'logo': {'max_width': 400, 'max_height': 400, 'quality': 85},
                    'banner_image': {'max_width': 1200, 'max_height': 600, 'quality': 85}
                }
            },
            'Ministry': {
                'model': Ministry,
                'fields': {
                    'image': {'max_width': 600, 'max_height': 400, 'quality': 85}
                }
            },
            'News': {
                'model': News,
                'fields': {
                    'image': {'max_width': 800, 'max_height': 600, 'quality': 85}
                }
            },
            'Sermon': {
                'model': Sermon,
                'fields': {
                    'thumbnail': {'max_width': 400, 'max_height': 300, 'quality': 85}
                }
            },
            'Hero': {
                'model': Hero,
                'fields': {
                    'background_image': {'max_width': 1920, 'max_height': 1080, 'quality': 85}
                }
            },
            'HeroMedia': {
                'model': HeroMedia,
                'fields': {
                    'image': {'max_width': 1200, 'max_height': 800, 'quality': 85}
                }
            },
            'EventHighlight': {
                'model': EventHighlight,
                'fields': {
                    'image': {'max_width': 800, 'max_height': 600, 'quality': 85}
                }
            },
            'EventSpeaker': {
                'model': EventSpeaker,
                'fields': {
                    'photo': {'max_width': 300, 'max_height': 300, 'quality': 85}
                }
            },
            'AboutPage': {
                'model': AboutPage,
                'fields': {
                    'logo': {'max_width': 600, 'max_height': 600, 'quality': 85},
                    'founder_image': {'max_width': 600, 'max_height': 600, 'quality': 85},
                    'extra_image': {'max_width': 600, 'max_height': 600, 'quality': 85}
                }
            },
            'LeadershipPage': {
                'model': LeadershipPage,
                'fields': {
                    'chairman_image': {'max_width': 400, 'max_height': 400, 'quality': 85},
                    'vice_chairman_image': {'max_width': 400, 'max_height': 400, 'quality': 85},
                    'board_image': {'max_width': 400, 'max_height': 400, 'quality': 85},
                    'team_image': {'max_width': 400, 'max_height': 400, 'quality': 85},
                    'leadership_photo_1': {'max_width': 400, 'max_height': 400, 'quality': 85},
                    'leadership_photo_2': {'max_width': 400, 'max_height': 400, 'quality': 85},
                    'leadership_photo_3': {'max_width': 400, 'max_height': 400, 'quality': 85}
                }
            },
            'LocalLeadershipPage': {
                'model': LocalLeadershipPage,
                'fields': {
                    'pastor_image': {'max_width': 400, 'max_height': 400, 'quality': 85},
                    'assistant_pastor_image': {'max_width': 400, 'max_height': 400, 'quality': 85},
                    'board_image': {'max_width': 400, 'max_height': 400, 'quality': 85},
                    'team_image': {'max_width': 400, 'max_height': 400, 'quality': 85},
                    'leadership_photo_1': {'max_width': 400, 'max_height': 400, 'quality': 85},
                    'leadership_photo_2': {'max_width': 400, 'max_height': 400, 'quality': 85},
                    'leadership_photo_3': {'max_width': 400, 'max_height': 400, 'quality': 85}
                }
            },
            'LocalAboutPage': {
                'model': LocalAboutPage,
                'fields': {
                    'logo': {'max_width': 600, 'max_height': 600, 'quality': 85},
                    'founder_image': {'max_width': 600, 'max_height': 600, 'quality': 85},
                    'extra_image': {'max_width': 600, 'max_height': 600, 'quality': 85},
                    'about_photo_1': {'max_width': 600, 'max_height': 600, 'quality': 85},
                    'about_photo_2': {'max_width': 600, 'max_height': 600, 'quality': 85},
                    'about_photo_3': {'max_width': 600, 'max_height': 600, 'quality': 85}
                }
            },
            'EventHeroMedia': {
                'model': EventHeroMedia,
                'fields': {
                    'image': {'max_width': 1200, 'max_height': 800, 'quality': 85}
                }
            }
        }
        
        # Filter models if specific model requested
        if options['model']:
            if options['model'] not in models_config:
                self.stdout.write(
                    self.style.ERROR(f'❌ Model "{options["model"]}" not found. Available models: {", ".join(models_config.keys())}')
                )
                return
            models_config = {options['model']: models_config[options['model']]}
        
        total_resized = 0
        total_skipped = 0
        total_errors = 0
        
        for model_name, config in models_config.items():
            model = config['model']
            fields_config = config['fields']
            
            self.stdout.write(f'\n📋 Processing {model_name}...')
            
            instances = model.objects.all()
            model_resized = 0
            model_skipped = 0
            model_errors = 0
            
            for instance in instances:
                for field_name, resize_settings in fields_config.items():
                    field = getattr(instance, field_name)
                    
                    if not field or not hasattr(field, 'name') or not field.name:
                        continue
                    
                    # Skip if it's already a URL (ImageKit, etc.)
                    if str(field).startswith('http'):
                        continue
                    
                    # Check if file exists
                    if not hasattr(field, 'path') or not os.path.exists(field.path):
                        continue
                    
                    # Get original dimensions
                    original_dimensions = get_image_dimensions(field)
                    if not original_dimensions:
                        continue
                    
                    original_width, original_height = original_dimensions
                    max_width = resize_settings['max_width']
                    max_height = resize_settings['max_height']
                    
                    # Check if resizing is needed
                    if original_width <= max_width and original_height <= max_height:
                        if options['dry_run']:
                            self.stdout.write(f'  ⏭️  {model_name} {instance.id} {field_name}: Already within limits ({original_width}x{original_height})')
                        model_skipped += 1
                        continue
                    
                    if options['dry_run']:
                        self.stdout.write(f'  📋 Would resize: {model_name} {instance.id} {field_name} from {original_width}x{original_height} to max {max_width}x{max_height}')
                        model_resized += 1
                        continue
                    
                    try:
                        with transaction.atomic():
                            # Resize the image
                            resize_image_field(
                                instance, 
                                field_name, 
                                max_width=max_width, 
                                max_height=max_height, 
                                quality=resize_settings['quality']
                            )
                            
                            # Save the instance
                            instance.save()
                            
                            # Get new dimensions
                            new_field = getattr(instance, field_name)
                            new_dimensions = get_image_dimensions(new_field)
                            
                            if new_dimensions:
                                new_width, new_height = new_dimensions
                                self.stdout.write(
                                    self.style.SUCCESS(f'  ✅ {model_name} {instance.id} {field_name}: {original_width}x{original_height} → {new_width}x{new_height}')
                                )
                            else:
                                self.stdout.write(
                                    self.style.SUCCESS(f'  ✅ {model_name} {instance.id} {field_name}: Resized successfully')
                                )
                            
                            model_resized += 1
                            
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'  ❌ {model_name} {instance.id} {field_name}: Error - {e}')
                        )
                        model_errors += 1
            
            total_resized += model_resized
            total_skipped += model_skipped
            total_errors += model_errors
            
            self.stdout.write(f'  📊 {model_name}: {model_resized} resized, {model_skipped} skipped, {model_errors} errors')
        
        self.stdout.write('\n' + '='*50)
        if options['dry_run']:
            self.stdout.write('📋 Dry run completed - no images were actually resized')
        else:
            self.stdout.write('🎉 Image resizing completed!')
        
        self.stdout.write(f'📊 Summary: {total_resized} resized, {total_skipped} skipped, {total_errors} errors')
        
        if total_resized > 0:
            self.stdout.write('\n💡 Tips:')
            self.stdout.write('• The resized images should now be much smaller in file size')
            self.stdout.write('• This should help with production deployment timeouts')
            self.stdout.write('• Consider running this command periodically for new uploads') 