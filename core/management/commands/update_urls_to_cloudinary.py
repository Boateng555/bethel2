from django.core.management.base import BaseCommand
from django.conf import settings
import os
from core.models import Church, News, Ministry, Sermon, HeroMedia, Event, EventSpeaker, AboutPage, LeadershipPage

class Command(BaseCommand):
    help = 'Update database URLs to point to Cloudinary'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Updating database URLs to Cloudinary...')
        
        # Cloudinary base URL
        cloudinary_base = "https://res.cloudinary.com/dhzdusb5k/image/upload/v1752764497/bethel"
        
        updated_count = 0
        
        # Update Church logos
        self.stdout.write('\n📋 Updating Church logos...')
        churches = Church.objects.all()
        for church in churches:
            if church.logo and str(church.logo) and not str(church.logo).startswith('http'):
                filename = os.path.basename(str(church.logo))
                new_url = f"{cloudinary_base}/churches/logos/{filename}"
                self.stdout.write(f"  {church.name}: {church.logo} -> {new_url}")
                church.logo = new_url
                church.save()
                updated_count += 1
        
        # Update News images
        self.stdout.write('\n📋 Updating News images...')
        news_items = News.objects.all()
        for news in news_items:
            if news.image and str(news.image) and not str(news.image).startswith('http'):
                filename = os.path.basename(str(news.image))
                new_url = f"{cloudinary_base}/news/{filename}"
                self.stdout.write(f"  {news.title}: {news.image} -> {new_url}")
                news.image = new_url
                news.save()
                updated_count += 1
        
        # Update Ministry images
        self.stdout.write('\n📋 Updating Ministry images...')
        ministries = Ministry.objects.all()
        for ministry in ministries:
            if ministry.image and str(ministry.image) and not str(ministry.image).startswith('http'):
                filename = os.path.basename(str(ministry.image))
                new_url = f"{cloudinary_base}/ministries/{filename}"
                self.stdout.write(f"  {ministry.name}: {ministry.image} -> {new_url}")
                ministry.image = new_url
                ministry.save()
                updated_count += 1
        
        # Update Sermon thumbnails
        self.stdout.write('\n📋 Updating Sermon thumbnails...')
        sermons = Sermon.objects.all()
        for sermon in sermons:
            if sermon.thumbnail and str(sermon.thumbnail) and not str(sermon.thumbnail).startswith('http'):
                filename = os.path.basename(str(sermon.thumbnail))
                new_url = f"{cloudinary_base}/sermons/thumbnails/{filename}"
                self.stdout.write(f"  {sermon.title}: {sermon.thumbnail} -> {new_url}")
                sermon.thumbnail = new_url
                sermon.save()
                updated_count += 1
        
        # Update HeroMedia images
        self.stdout.write('\n📋 Updating HeroMedia images...')
        hero_media = HeroMedia.objects.all()
        for media in hero_media:
            if media.image and str(media.image) and not str(media.image).startswith('http'):
                filename = os.path.basename(str(media.image))
                new_url = f"{cloudinary_base}/hero/{filename}"
                self.stdout.write(f"  {media.title}: {media.image} -> {new_url}")
                media.image = new_url
                media.save()
                updated_count += 1
        
        # Update Event images
        self.stdout.write('\n📋 Updating Event images...')
        events = Event.objects.all()
        for event in events:
            if event.image and str(event.image) and not str(event.image).startswith('http'):
                filename = os.path.basename(str(event.image))
                new_url = f"{cloudinary_base}/events/{filename}"
                self.stdout.write(f"  {event.title}: {event.image} -> {new_url}")
                event.image = new_url
                event.save()
                updated_count += 1
        
        # Update EventSpeaker images
        self.stdout.write('\n📋 Updating EventSpeaker images...')
        speakers = EventSpeaker.objects.all()
        for speaker in speakers:
            if speaker.photo and str(speaker.photo) and not str(speaker.photo).startswith('http'):
                filename = os.path.basename(str(speaker.photo))
                new_url = f"{cloudinary_base}/events/speakers/{filename}"
                self.stdout.write(f"  {speaker.name}: {speaker.photo} -> {new_url}")
                speaker.photo = new_url
                speaker.save()
                updated_count += 1
        
        # Update AboutPage images
        self.stdout.write('\n📋 Updating AboutPage images...')
        about_pages = AboutPage.objects.all()
        for page in about_pages:
            for field_name in ['logo', 'founder_image', 'extra_image']:
                field = getattr(page, field_name, None)
                if field and str(field) and not str(field).startswith('http'):
                    filename = os.path.basename(str(field))
                    new_url = f"{cloudinary_base}/about/{filename}"
                    self.stdout.write(f"  {page.title} {field_name}: {field} -> {new_url}")
                    setattr(page, field_name, new_url)
                    updated_count += 1
            page.save()
        
        # Update LeadershipPage images
        self.stdout.write('\n📋 Updating LeadershipPage images...')
        leadership_pages = LeadershipPage.objects.all()
        for page in leadership_pages:
            for field_name in ['chairman_image', 'vice_chairman_image', 'board_image', 'team_image', 
                              'leadership_photo_1', 'leadership_photo_2', 'leadership_photo_3']:
                field = getattr(page, field_name, None)
                if field and str(field) and not str(field).startswith('http'):
                    filename = os.path.basename(str(field))
                    new_url = f"{cloudinary_base}/leadership/{filename}"
                    self.stdout.write(f"  {page.title} {field_name}: {field} -> {new_url}")
                    setattr(page, field_name, new_url)
                    updated_count += 1
            page.save()
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Database URLs updated successfully!'))
        self.stdout.write(f'Updated {updated_count} URLs to point to Cloudinary.')
        self.stdout.write('All media files now point to Cloudinary URLs.') 