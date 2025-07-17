from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
import os
from core.models import Church, Hero, HeroMedia, News, Ministry, Sermon

class Command(BaseCommand):
    help = 'Sync local media files to Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without actually uploading',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No files will be uploaded'))
        
        self.stdout.write('Starting media sync to Cloudinary...')
        
        # Check if we're in production mode
        if settings.DEBUG:
            self.stdout.write(self.style.ERROR('This command should be run in production (DEBUG=False)'))
            return
        
        # Sync Churches
        self.sync_churches(dry_run)
        
        # Sync Heroes and Hero Media
        self.sync_heroes(dry_run)
        
        # Sync other models
        self.sync_news(dry_run)
        self.sync_ministries(dry_run)
        self.sync_sermons(dry_run)
        
        self.stdout.write(self.style.SUCCESS('Media sync completed!'))

    def sync_churches(self, dry_run):
        self.stdout.write('\nSyncing Churches...')
        churches = Church.objects.all()
        
        for church in churches:
            if church.logo and hasattr(church.logo, 'path'):
                local_path = church.logo.path
                if os.path.exists(local_path):
                    self.stdout.write(f'  Church: {church.name} - Logo exists locally')
                    if not dry_run:
                        # Re-save to trigger Cloudinary upload
                        church.logo.save(
                            os.path.basename(local_path),
                            File(open(local_path, 'rb')),
                            save=True
                        )
                        self.stdout.write(f'    ✅ Uploaded to Cloudinary')
                    else:
                        self.stdout.write(f'    📤 Would upload: {local_path}')
                else:
                    self.stdout.write(f'  Church: {church.name} - Logo file missing: {local_path}')

    def sync_heroes(self, dry_run):
        self.stdout.write('\nSyncing Heroes and Hero Media...')
        heroes = Hero.objects.all()
        
        for hero in heroes:
            self.stdout.write(f'  Hero: {hero.title}')
            hero_media = HeroMedia.objects.filter(hero=hero)
            
            for media in hero_media:
                # Handle image
                if media.image and hasattr(media.image, 'path'):
                    local_path = media.image.path
                    if os.path.exists(local_path):
                        self.stdout.write(f'    Image: {os.path.basename(local_path)}')
                        if not dry_run:
                            media.image.save(
                                os.path.basename(local_path),
                                File(open(local_path, 'rb')),
                                save=True
                            )
                            self.stdout.write(f'      ✅ Uploaded to Cloudinary')
                        else:
                            self.stdout.write(f'      📤 Would upload: {local_path}')
                    else:
                        self.stdout.write(f'    Image file missing: {local_path}')
                
                # Handle video
                if media.video and hasattr(media.video, 'path'):
                    local_path = media.video.path
                    if os.path.exists(local_path):
                        self.stdout.write(f'    Video: {os.path.basename(local_path)}')
                        if not dry_run:
                            media.video.save(
                                os.path.basename(local_path),
                                File(open(local_path, 'rb')),
                                save=True
                            )
                            self.stdout.write(f'      ✅ Uploaded to Cloudinary')
                        else:
                            self.stdout.write(f'      📤 Would upload: {local_path}')
                    else:
                        self.stdout.write(f'    Video file missing: {local_path}')

    def sync_news(self, dry_run):
        self.stdout.write('\nSyncing News...')
        news_items = News.objects.all()
        
        for news in news_items:
            if news.image and hasattr(news.image, 'path'):
                local_path = news.image.path
                if os.path.exists(local_path):
                    self.stdout.write(f'  News: {news.title} - Image exists')
                    if not dry_run:
                        news.image.save(
                            os.path.basename(local_path),
                            File(open(local_path, 'rb')),
                            save=True
                        )
                        self.stdout.write(f'    ✅ Uploaded to Cloudinary')
                    else:
                        self.stdout.write(f'    📤 Would upload: {local_path}')

    def sync_ministries(self, dry_run):
        self.stdout.write('\nSyncing Ministries...')
        ministries = Ministry.objects.all()
        
        for ministry in ministries:
            if ministry.image and hasattr(ministry.image, 'path'):
                local_path = ministry.image.path
                if os.path.exists(local_path):
                    self.stdout.write(f'  Ministry: {ministry.name} - Image exists')
                    if not dry_run:
                        ministry.image.save(
                            os.path.basename(local_path),
                            File(open(local_path, 'rb')),
                            save=True
                        )
                        self.stdout.write(f'    ✅ Uploaded to Cloudinary')
                    else:
                        self.stdout.write(f'    📤 Would upload: {local_path}')

    def sync_sermons(self, dry_run):
        self.stdout.write('\nSyncing Sermons...')
        sermons = Sermon.objects.all()
        
        for sermon in sermons:
            if sermon.thumbnail and hasattr(sermon.thumbnail, 'path'):
                local_path = sermon.thumbnail.path
                if os.path.exists(local_path):
                    self.stdout.write(f'  Sermon: {sermon.title} - Thumbnail exists')
                    if not dry_run:
                        sermon.thumbnail.save(
                            os.path.basename(local_path),
                            File(open(local_path, 'rb')),
                            save=True
                        )
                        self.stdout.write(f'    ✅ Uploaded to Cloudinary')
                    else:
                        self.stdout.write(f'    📤 Would upload: {local_path}')
            
            if sermon.video and hasattr(sermon.video, 'path'):
                local_path = sermon.video.path
                if os.path.exists(local_path):
                    self.stdout.write(f'  Sermon: {sermon.title} - Video exists')
                    if not dry_run:
                        sermon.video.save(
                            os.path.basename(local_path),
                            File(open(local_path, 'rb')),
                            save=True
                        )
                        self.stdout.write(f'    ✅ Uploaded to Cloudinary')
                    else:
                        self.stdout.write(f'    📤 Would upload: {local_path}') 