from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import cloudinary
import cloudinary.uploader
import os
import requests
from pathlib import Path

from core.models import Church, News, Ministry, Sermon, HeroMedia, EventHighlight, EventSpeaker
from core.models import AboutPage, LeadershipPage

class Command(BaseCommand):
    help = 'Upload all local media files to Cloudinary and update database URLs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without actually uploading',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write("🚀 Starting media upload to Cloudinary...")
        self.stdout.write("=" * 60)
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
        )
        
        self.stdout.write(f"☁️ Cloudinary configured: {settings.CLOUDINARY_STORAGE['CLOUD_NAME']}")
        
        success_count = 0
        error_count = 0
        
        # Upload Church logos
        self.stdout.write("\n📋 Processing Church logos...")
        churches = Church.objects.all()
        for church in churches:
            if church.logo and not 'res.cloudinary.com' in str(church.logo):
                try:
                    local_path = str(church.logo)
                    if dry_run:
                        self.stdout.write(f"  Would upload: {local_path}")
                        continue
                        
                    # Upload to Cloudinary
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="churches/logos",
                        public_id=f"church_{church.id}_logo",
                        overwrite=True
                    )
                    
                    # Update database
                    church.logo = result['secure_url']
                    church.save()
                    
                    self.stdout.write(f"  ✅ {church.name}: {result['secure_url']}")
                    success_count += 1
                    
                except Exception as e:
                    self.stdout.write(f"  ❌ {church.name}: Error - {e}")
                    error_count += 1
        
        # Upload News images
        self.stdout.write("\n📋 Processing News images...")
        news_items = News.objects.all()
        for news in news_items:
            if news.image and not 'res.cloudinary.com' in str(news.image):
                try:
                    local_path = str(news.image)
                    if dry_run:
                        self.stdout.write(f"  Would upload: {local_path}")
                        continue
                        
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="news",
                        public_id=f"news_{news.id}",
                        overwrite=True
                    )
                    
                    news.image = result['secure_url']
                    news.save()
                    
                    self.stdout.write(f"  ✅ {news.title}: {result['secure_url']}")
                    success_count += 1
                    
                except Exception as e:
                    self.stdout.write(f"  ❌ {news.title}: Error - {e}")
                    error_count += 1
        
        # Upload Ministry images
        self.stdout.write("\n📋 Processing Ministry images...")
        ministries = Ministry.objects.all()
        for ministry in ministries:
            if ministry.image and not 'res.cloudinary.com' in str(ministry.image):
                try:
                    local_path = str(ministry.image)
                    if dry_run:
                        self.stdout.write(f"  Would upload: {local_path}")
                        continue
                        
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="ministries",
                        public_id=f"ministry_{ministry.id}",
                        overwrite=True
                    )
                    
                    ministry.image = result['secure_url']
                    ministry.save()
                    
                    self.stdout.write(f"  ✅ {ministry.name}: {result['secure_url']}")
                    success_count += 1
                    
                except Exception as e:
                    self.stdout.write(f"  ❌ {ministry.name}: Error - {e}")
                    error_count += 1
        
        # Upload Sermon thumbnails
        self.stdout.write("\n📋 Processing Sermon thumbnails...")
        sermons = Sermon.objects.all()
        for sermon in sermons:
            if sermon.thumbnail and not 'res.cloudinary.com' in str(sermon.thumbnail):
                try:
                    local_path = str(sermon.thumbnail)
                    if dry_run:
                        self.stdout.write(f"  Would upload: {local_path}")
                        continue
                        
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="sermons/thumbnails",
                        public_id=f"sermon_{sermon.id}_thumbnail",
                        overwrite=True
                    )
                    
                    sermon.thumbnail = result['secure_url']
                    sermon.save()
                    
                    self.stdout.write(f"  ✅ {sermon.title}: {result['secure_url']}")
                    success_count += 1
                    
                except Exception as e:
                    self.stdout.write(f"  ❌ {sermon.title}: Error - {e}")
                    error_count += 1
        
        # Upload Hero Media
        self.stdout.write("\n📋 Processing Hero Media...")
        hero_media = HeroMedia.objects.all()
        for hero in hero_media:
            if hero.image and not 'res.cloudinary.com' in str(hero.image):
                try:
                    local_path = str(hero.image)
                    if dry_run:
                        self.stdout.write(f"  Would upload: {local_path}")
                        continue
                        
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="hero",
                        public_id=f"hero_{hero.id}",
                        overwrite=True
                    )
                    
                    hero.image = result['secure_url']
                    hero.save()
                    
                    self.stdout.write(f"  ✅ Hero {hero.id}: {result['secure_url']}")
                    success_count += 1
                    
                except Exception as e:
                    self.stdout.write(f"  ❌ Hero {hero.id}: Error - {e}")
                    error_count += 1
        
        # Upload Event Speakers
        self.stdout.write("\n📋 Processing Event Speakers...")
        speakers = EventSpeaker.objects.all()
        for speaker in speakers:
            if speaker.photo and not 'res.cloudinary.com' in str(speaker.photo):
                try:
                    local_path = str(speaker.photo)
                    if dry_run:
                        self.stdout.write(f"  Would upload: {local_path}")
                        continue
                        
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="events/speakers",
                        public_id=f"speaker_{speaker.id}",
                        overwrite=True
                    )
                    
                    speaker.photo = result['secure_url']
                    speaker.save()
                    
                    self.stdout.write(f"  ✅ {speaker.name}: {result['secure_url']}")
                    success_count += 1
                    
                except Exception as e:
                    self.stdout.write(f"  ❌ {speaker.name}: Error - {e}")
                    error_count += 1
        
        # Upload About Page images
        self.stdout.write("\n📋 Processing About Page images...")
        about_pages = AboutPage.objects.all()
        for about in about_pages:
            if about.logo and not 'res.cloudinary.com' in str(about.logo):
                try:
                    local_path = str(about.logo)
                    if dry_run:
                        self.stdout.write(f"  Would upload logo: {local_path}")
                        continue
                        
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="about",
                        public_id=f"about_logo_{about.id}",
                        overwrite=True
                    )
                    
                    about.logo = result['secure_url']
                    about.save()
                    
                    self.stdout.write(f"  ✅ Logo: {result['secure_url']}")
                    success_count += 1
                    
                except Exception as e:
                    self.stdout.write(f"  ❌ Logo: Error - {e}")
                    error_count += 1
            
            if about.founder_image and not 'res.cloudinary.com' in str(about.founder_image):
                try:
                    local_path = str(about.founder_image)
                    if dry_run:
                        self.stdout.write(f"  Would upload founder image: {local_path}")
                        continue
                        
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="about",
                        public_id=f"about_founder_{about.id}",
                        overwrite=True
                    )
                    
                    about.founder_image = result['secure_url']
                    about.save()
                    
                    self.stdout.write(f"  ✅ Founder Image: {result['secure_url']}")
                    success_count += 1
                    
                except Exception as e:
                    self.stdout.write(f"  ❌ Founder Image: Error - {e}")
                    error_count += 1
        
        # Upload Leadership Page images
        self.stdout.write("\n📋 Processing Leadership Page images...")
        leadership_pages = LeadershipPage.objects.all()
        for leadership in leadership_pages:
            if leadership.chairman_image and not 'res.cloudinary.com' in str(leadership.chairman_image):
                try:
                    local_path = str(leadership.chairman_image)
                    if dry_run:
                        self.stdout.write(f"  Would upload chairman image: {local_path}")
                        continue
                        
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="leadership",
                        public_id=f"leadership_chairman_{leadership.id}",
                        overwrite=True
                    )
                    
                    leadership.chairman_image = result['secure_url']
                    leadership.save()
                    
                    self.stdout.write(f"  ✅ Chairman: {result['secure_url']}")
                    success_count += 1
                    
                except Exception as e:
                    self.stdout.write(f"  ❌ Chairman: Error - {e}")
                    error_count += 1
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("🎉 Upload completed!")
        self.stdout.write(f"✅ Successfully uploaded: {success_count}")
        self.stdout.write(f"❌ Failed uploads: {error_count}")
        
        if not dry_run and success_count > 0:
            self.stdout.write("\n🎯 Next steps:")
            self.stdout.write("1. Visit your live site to see the images")
            self.stdout.write("2. If some images are still missing, run this command again")
            self.stdout.write("3. Check Cloudinary dashboard to verify uploads") 