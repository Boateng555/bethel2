from django.core.management.base import BaseCommand
from core.models import (
    Church, News, Ministry, Sermon, HeroMedia, Event, 
    EventSpeaker, AboutPage, LeadershipPage, LocalAboutPage, 
    LocalLeadershipPage, EventHighlight, EventHeroMedia, Hero
)
import cloudinary
import cloudinary.uploader
import os
from PIL import Image
import io
import base64

class Command(BaseCommand):
    help = 'Fix images on production by adding placeholder images where missing'

    def handle(self, *args, **options):
        self.stdout.write("🔧 FIXING PRODUCTION IMAGES")
        self.stdout.write("=" * 60)
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
            api_key=os.environ.get('CLOUDINARY_API_KEY'),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET')
        )
        
        # Create a simple placeholder image
        def create_placeholder_image(text, size=(400, 300)):
            """Create a placeholder image with text"""
            img = Image.new('RGB', size, color='#1e3a8a')
            
            # Add text (simplified - in production you'd use proper font)
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            # Try to use a default font
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            # Calculate text position
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            
            draw.text((x, y), text, fill='white', font=font)
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            return img_byte_arr
        
        def upload_placeholder(folder, filename, text):
            """Upload a placeholder image to Cloudinary"""
            try:
                image_data = create_placeholder_image(text)
                
                result = cloudinary.uploader.upload(
                    image_data,
                    folder=folder,
                    public_id=filename,
                    resource_type="image",
                    format="png"
                )
                
                return result['secure_url']
            except Exception as e:
                self.stdout.write(f"❌ Error uploading placeholder: {e}")
                return None
        
        # Fix Churches
        self.stdout.write("\n🏛️  FIXING CHURCHES")
        churches = Church.objects.all()
        for church in churches:
            if not church.logo:
                self.stdout.write(f"  Adding logo for {church.name}")
                logo_url = upload_placeholder(
                    "churches/logos", 
                    f"placeholder_{church.id}", 
                    f"{church.name} Logo"
                )
                if logo_url:
                    church.logo = logo_url
                    church.save()
            
            if not church.banner_image:
                self.stdout.write(f"  Adding banner for {church.name}")
                banner_url = upload_placeholder(
                    "churches/banners", 
                    f"placeholder_{church.id}", 
                    f"{church.name} Banner"
                )
                if banner_url:
                    church.banner_image = banner_url
                    church.save()
        
        # Fix News
        self.stdout.write("\n📰 FIXING NEWS")
        news_articles = News.objects.all()
        for news in news_articles:
            if not news.image:
                self.stdout.write(f"  Adding image for {news.title}")
                image_url = upload_placeholder(
                    "news", 
                    f"placeholder_{news.id}", 
                    f"{news.title}"
                )
                if image_url:
                    news.image = image_url
                    news.save()
        
        # Fix Ministries
        self.stdout.write("\n⛪ FIXING MINISTRIES")
        ministries = Ministry.objects.all()
        for ministry in ministries:
            if not ministry.image:
                self.stdout.write(f"  Adding image for {ministry.name}")
                image_url = upload_placeholder(
                    "ministries", 
                    f"placeholder_{ministry.id}", 
                    f"{ministry.name}"
                )
                if image_url:
                    ministry.image = image_url
                    ministry.save()
        
        # Fix Sermons
        self.stdout.write("\n📖 FIXING SERMONS")
        sermons = Sermon.objects.all()
        for sermon in sermons:
            if not sermon.thumbnail:
                self.stdout.write(f"  Adding thumbnail for {sermon.title}")
                thumbnail_url = upload_placeholder(
                    "sermons/thumbnails", 
                    f"placeholder_{sermon.id}", 
                    f"{sermon.title}"
                )
                if thumbnail_url:
                    sermon.thumbnail = thumbnail_url
                    sermon.save()
        
        # Fix Event Speakers
        self.stdout.write("\n🎤 FIXING EVENT SPEAKERS")
        speakers = EventSpeaker.objects.all()
        for speaker in speakers:
            if not speaker.photo:
                self.stdout.write(f"  Adding photo for {speaker.name}")
                photo_url = upload_placeholder(
                    "speakers", 
                    f"placeholder_{speaker.id}", 
                    f"{speaker.name}"
                )
                if photo_url:
                    speaker.photo = photo_url
                    speaker.save()
        
        # Fix Event Highlights
        self.stdout.write("\n🌟 FIXING EVENT HIGHLIGHTS")
        highlights = EventHighlight.objects.all()
        for highlight in highlights:
            if not highlight.image:
                self.stdout.write(f"  Adding image for {highlight.title}")
                image_url = upload_placeholder(
                    "highlights", 
                    f"placeholder_{highlight.id}", 
                    f"{highlight.title}"
                )
                if image_url:
                    highlight.image = image_url
                    highlight.save()
        
        # Fix Event Hero Media
        self.stdout.write("\n🎬 FIXING EVENT HERO MEDIA")
        event_hero_media = EventHeroMedia.objects.all()
        for media in event_hero_media:
            if not media.image:
                self.stdout.write(f"  Adding image for event hero media {media.id}")
                image_url = upload_placeholder(
                    "event_hero", 
                    f"placeholder_{media.id}", 
                    "Event Hero"
                )
                if image_url:
                    media.image = image_url
                    media.save()
        
        # Fix Hero Media
        self.stdout.write("\n🏆 FIXING HERO MEDIA")
        hero_media = HeroMedia.objects.all()
        for media in hero_media:
            if not media.image:
                self.stdout.write(f"  Adding image for hero media {media.id}")
                image_url = upload_placeholder(
                    "hero", 
                    f"placeholder_{media.id}", 
                    "Hero Image"
                )
                if image_url:
                    media.image = image_url
                    media.save()
        
        # Fix About Pages
        self.stdout.write("\n📄 FIXING ABOUT PAGES")
        about_pages = AboutPage.objects.all()
        for about in about_pages:
            if not about.logo:
                self.stdout.write(f"  Adding logo for about page")
                logo_url = upload_placeholder(
                    "about", 
                    "placeholder_logo", 
                    "About Logo"
                )
                if logo_url:
                    about.logo = logo_url
                    about.save()
            
            if not about.founder_image:
                self.stdout.write(f"  Adding founder image for about page")
                founder_url = upload_placeholder(
                    "about", 
                    "placeholder_founder", 
                    "Founder"
                )
                if founder_url:
                    about.founder_image = founder_url
                    about.save()
            
            if not about.extra_image:
                self.stdout.write(f"  Adding extra image for about page")
                extra_url = upload_placeholder(
                    "about", 
                    "placeholder_extra", 
                    "Extra Image"
                )
                if extra_url:
                    about.extra_image = extra_url
                    about.save()
        
        # Fix Leadership Pages
        self.stdout.write("\n👥 FIXING LEADERSHIP PAGES")
        leadership_pages = LeadershipPage.objects.all()
        for leadership in leadership_pages:
            if not leadership.chairman_image:
                self.stdout.write(f"  Adding chairman image for leadership page")
                chairman_url = upload_placeholder(
                    "leadership", 
                    "placeholder_chairman", 
                    "Chairman"
                )
                if chairman_url:
                    leadership.chairman_image = chairman_url
                    leadership.save()
            
            if not leadership.vice_chairman_image:
                self.stdout.write(f"  Adding vice chairman image for leadership page")
                vice_chairman_url = upload_placeholder(
                    "leadership", 
                    "placeholder_vice_chairman", 
                    "Vice Chairman"
                )
                if vice_chairman_url:
                    leadership.vice_chairman_image = vice_chairman_url
                    leadership.save()
            
            if not leadership.board_image:
                self.stdout.write(f"  Adding board image for leadership page")
                board_url = upload_placeholder(
                    "leadership", 
                    "placeholder_board", 
                    "Board"
                )
                if board_url:
                    leadership.board_image = board_url
                    leadership.save()
            
            if not leadership.team_image:
                self.stdout.write(f"  Adding team image for leadership page")
                team_url = upload_placeholder(
                    "leadership", 
                    "placeholder_team", 
                    "Team"
                )
                if team_url:
                    leadership.team_image = team_url
                    leadership.save()
        
        # Fix Local About Pages
        self.stdout.write("\n🏘️  FIXING LOCAL ABOUT PAGES")
        local_about_pages = LocalAboutPage.objects.all()
        for about in local_about_pages:
            if not about.about_photo_1:
                self.stdout.write(f"  Adding photo 1 for local about page")
                photo_url = upload_placeholder(
                    "local_about", 
                    f"placeholder_photo1_{about.id}", 
                    "About Photo 1"
                )
                if photo_url:
                    about.about_photo_1 = photo_url
                    about.save()
            
            if not about.founder_image:
                self.stdout.write(f"  Adding founder image for local about page")
                founder_url = upload_placeholder(
                    "local_about", 
                    f"placeholder_founder_{about.id}", 
                    "Founder"
                )
                if founder_url:
                    about.founder_image = founder_url
                    about.save()
            
            if not about.extra_image:
                self.stdout.write(f"  Adding extra image for local about page")
                extra_url = upload_placeholder(
                    "local_about", 
                    f"placeholder_extra_{about.id}", 
                    "Extra Image"
                )
                if extra_url:
                    about.extra_image = extra_url
                    about.save()
        
        # Fix Local Leadership Pages
        self.stdout.write("\n👨‍👩‍👧‍👦 FIXING LOCAL LEADERSHIP PAGES")
        local_leadership_pages = LocalLeadershipPage.objects.all()
        for leadership in local_leadership_pages:
            if not leadership.pastor_image:
                self.stdout.write(f"  Adding pastor image for local leadership page")
                pastor_url = upload_placeholder(
                    "local_leadership", 
                    f"placeholder_pastor_{leadership.id}", 
                    "Pastor"
                )
                if pastor_url:
                    leadership.pastor_image = pastor_url
                    leadership.save()
            
            if not leadership.assistant_pastor_image:
                self.stdout.write(f"  Adding assistant pastor image for local leadership page")
                assistant_url = upload_placeholder(
                    "local_leadership", 
                    f"placeholder_assistant_{leadership.id}", 
                    "Assistant Pastor"
                )
                if assistant_url:
                    leadership.assistant_pastor_image = assistant_url
                    leadership.save()
            
            if not leadership.board_image:
                self.stdout.write(f"  Adding board image for local leadership page")
                board_url = upload_placeholder(
                    "local_leadership", 
                    f"placeholder_board_{leadership.id}", 
                    "Board"
                )
                if board_url:
                    leadership.board_image = board_url
                    leadership.save()
            
            if not leadership.team_image:
                self.stdout.write(f"  Adding team image for local leadership page")
                team_url = upload_placeholder(
                    "local_leadership", 
                    f"placeholder_team_{leadership.id}", 
                    "Team"
                )
                if team_url:
                    leadership.team_image = team_url
                    leadership.save()
        
        self.stdout.write("\n✅ PRODUCTION IMAGE FIX COMPLETE!")
        self.stdout.write("Images should now be visible on your website.")
        self.stdout.write("Please clear your browser cache and test again.") 