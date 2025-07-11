from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import (
    Church, Event, Ministry, News, Sermon, DonationMethod, 
    Convention, Hero, ChurchAdmin, HeroMedia
)
from django.utils import timezone
from datetime import timedelta
import uuid

class Command(BaseCommand):
    help = 'Create demo data for the Bethel platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--churches',
            type=int,
            default=3,
            help='Number of demo churches to create'
        )
        parser.add_argument(
            '--add-hero-media',
            action='store_true',
            help='Add Hero Media to existing churches that don\'t have hero content'
        )

    def handle(self, *args, **options):
        if options['add_hero_media']:
            self.add_hero_media_to_existing_churches()
        else:
            self.create_demo_data(options['churches'])

    def add_hero_media_to_existing_churches(self):
        """Add Hero Media to existing churches that don't have hero content"""
        churches_without_hero = Church.objects.filter(
            is_active=True,
            is_approved=True
        ).exclude(
            hero__isnull=False
        )
        
        if not churches_without_hero.exists():
            self.stdout.write(
                self.style.SUCCESS('All active churches already have hero content!')
            )
            return
        
        self.stdout.write(f'Found {churches_without_hero.count()} churches without hero content.')
        
        for church in churches_without_hero:
            # Create default hero
            hero = Hero.objects.create(
                church=church,
                title=f'Welcome to {church.name}',
                subtitle=f'Join us in worship and fellowship in {church.city}, {church.country}',
                background_type='image',
                primary_button_text='Plan Your Visit',
                primary_button_link=f'/church/{church.id}/about/',
                secondary_button_text='Watch Online',
                secondary_button_link=f'/church/{church.id}/sermons/',
                is_active=True,
                order=1
            )
            
            # Create sample Hero Media (you can customize these)
            HeroMedia.objects.create(
                hero=hero,
                image=None,  # No image by default, admin can add
                video=None,  # No video by default, admin can add
                order=1
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created hero for {church.name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully added hero content to {churches_without_hero.count()} churches! '
                f'Admins can now add images/videos through the Hero admin section.'
            )
        )

    def create_demo_data(self, num_churches):
        """Create demo data for the platform"""
        self.stdout.write('Creating demo churches and data...')
        
        # Create demo churches
        churches = self.create_demo_churches()
        
        # Create demo data for each church
        for church in churches:
            self.create_demo_data_for_church(church)
        
        # Create global hero content
        self.create_global_hero()
        
        # Create a global convention
        self.create_global_convention()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created demo data!')
        )

    def create_demo_churches(self):
        """Create demo churches from around the world"""
        churches_data = [
            {
                'name': 'Bethel Prayer Ministry - Bremen',
                'slug': 'bremen',
                'address': 'Am Markt 1, 28195 Bremen',
                'city': 'Bremen',
                'state_province': 'Bremen',
                'country': 'Germany',
                'postal_code': '28195',
                'phone': '+49 421 123456',
                'email': 'bremen@bethelprayer.org',
                'website': 'https://bremen.bethelprayer.org',
                'pastor_name': 'Pastor Hans Mueller',
                'description': 'A vibrant community serving Bremen and surrounding areas with prayer, worship, and ministry.',
                'is_active': True,
                'is_approved': True,
                'is_featured': True,
                'latitude': 53.0793,
                'longitude': 8.8017,
            },
            {
                'name': 'Bethel Prayer Ministry - Accra',
                'slug': 'accra',
                'address': 'Ring Road Central, Accra',
                'city': 'Accra',
                'state_province': 'Greater Accra',
                'country': 'Ghana',
                'postal_code': '00233',
                'phone': '+233 20 123456',
                'email': 'accra@bethelprayer.org',
                'website': 'https://accra.bethelprayer.org',
                'pastor_name': 'Pastor Kwame Mensah',
                'description': 'Serving the people of Accra with powerful prayer ministry and community outreach.',
                'is_active': True,
                'is_approved': True,
                'is_featured': True,
                'latitude': 5.5600,
                'longitude': -0.2057,
            },
            {
                'name': 'Bethel Prayer Ministry - London',
                'slug': 'london',
                'address': '123 Oxford Street, London',
                'city': 'London',
                'state_province': 'England',
                'country': 'United Kingdom',
                'postal_code': 'W1D 1BS',
                'phone': '+44 20 1234 5678',
                'email': 'london@bethelprayer.org',
                'website': 'https://london.bethelprayer.org',
                'pastor_name': 'Pastor Sarah Johnson',
                'description': 'A multicultural church serving London with prayer, worship, and community service.',
                'is_active': True,
                'is_approved': True,
                'is_featured': False,
                'latitude': 51.5074,
                'longitude': -0.1278,
            },
            {
                'name': 'Bethel Prayer Ministry - New York',
                'slug': 'new-york',
                'address': '456 Broadway, New York',
                'city': 'New York',
                'state_province': 'New York',
                'country': 'United States',
                'postal_code': '10013',
                'phone': '+1 212 123 4567',
                'email': 'newyork@bethelprayer.org',
                'website': 'https://newyork.bethelprayer.org',
                'pastor_name': 'Pastor Michael Davis',
                'description': 'Serving the diverse community of New York with prayer ministry and outreach programs.',
                'is_active': True,
                'is_approved': True,
                'is_featured': False,
                'latitude': 40.7128,
                'longitude': -74.0060,
            },
            {
                'name': 'Bethel Prayer Ministry - Lagos',
                'slug': 'lagos',
                'address': '789 Victoria Island, Lagos',
                'city': 'Lagos',
                'state_province': 'Lagos',
                'country': 'Nigeria',
                'postal_code': '101241',
                'phone': '+234 1 234 5678',
                'email': 'lagos@bethelprayer.org',
                'website': 'https://lagos.bethelprayer.org',
                'pastor_name': 'Pastor Grace Okechukwu',
                'description': 'A dynamic church serving Lagos with powerful prayer ministry and community development.',
                'is_active': True,
                'is_approved': True,
                'is_featured': False,
                'latitude': 6.5244,
                'longitude': 3.3792,
            },
        ]
        
        churches = []
        for data in churches_data:
            church, created = Church.objects.get_or_create(
                slug=data['slug'],
                defaults=data
            )
            if created:
                self.stdout.write(f'Created church: {church.name}')
            churches.append(church)
        
        return churches

    def create_demo_data_for_church(self, church):
        """Create demo data for a specific church"""
        
        # Create church-specific hero
        Hero.objects.get_or_create(
            church=church,
            defaults={
                'title': f"Welcome to {church.name}",
                'subtitle': f"Join us for worship, fellowship, and spiritual growth in {church.city}, {church.country}",
                'background_type': 'image',
                'primary_button_text': 'Plan Your Visit',
                'primary_button_link': f'/church/{church.id}/about/',
                'secondary_button_text': 'Watch Online',
                'secondary_button_link': f'/church/{church.id}/sermons/',
                'is_active': True,
                'order': 1,
            }
        )
        
        # Create events
        events_data = [
            {
                'title': f'Sunday Service at {church.name}',
                'description': f'Join us for our weekly Sunday service at {church.name}. All are welcome!',
                'start_date': timezone.now() + timedelta(days=7),
                'end_date': timezone.now() + timedelta(days=7, hours=2),
                'location': church.address,
                'event_type': 'service',
                'is_featured': True,
                'is_public': True,
            },
            {
                'title': f'Bible Study - {church.name}',
                'description': f'Weekly Bible study session at {church.name}. Deep dive into God\'s word.',
                'start_date': timezone.now() + timedelta(days=3),
                'end_date': timezone.now() + timedelta(days=3, hours=1, minutes=30),
                'location': church.address,
                'event_type': 'study',
                'is_featured': True,
                'is_public': True,
            },
            {
                'title': f'Prayer Meeting - {church.name}',
                'description': f'Join our prayer meeting at {church.name}. Come and pray with us.',
                'start_date': timezone.now() + timedelta(days=5),
                'end_date': timezone.now() + timedelta(days=5, hours=1),
                'location': church.address,
                'event_type': 'prayer',
                'is_featured': False,
                'is_public': True,
            },
        ]
        
        for event_data in events_data:
            Event.objects.get_or_create(
                title=event_data['title'],
                church=church,
                defaults=event_data
            )
        
        # Create ministries
        ministries_data = [
            {
                'name': 'Youth Ministry',
                'description': f'Engaging young people in faith and community at {church.name}',
                'is_active': True,
            },
            {
                'name': 'Music Ministry',
                'description': f'Leading worship through music and praise at {church.name}',
                'is_active': True,
            },
            {
                'name': 'Children\'s Ministry',
                'description': f'Nurturing children in faith and love at {church.name}',
                'is_active': True,
            },
            {
                'name': 'Outreach Ministry',
                'description': f'Serving our community and sharing God\'s love at {church.name}',
                'is_active': True,
            },
        ]
        
        for ministry_data in ministries_data:
            Ministry.objects.get_or_create(
                name=ministry_data['name'],
                church=church,
                defaults=ministry_data
            )
        
        # Create news
        news_data = [
            {
                'title': f'New Pastor Joins {church.name}',
                'content': f'We are excited to welcome our new pastor to {church.name}. Join us in celebration!',
                'is_public': True,
            },
            {
                'title': f'Community Outreach at {church.name}',
                'content': f'{church.name} is organizing a community outreach program to serve our neighbors.',
                'is_public': True,
            },
        ]
        
        for news_data_item in news_data:
            News.objects.get_or_create(
                title=news_data_item['title'],
                church=church,
                defaults=news_data_item
            )
        
        # Create sermons
        sermons_data = [
            {
                'title': f'Faith and Community - {church.name}',
                'speaker': church.pastor_name,
                'description': f'A powerful message about faith and building community at {church.name}',
                'date': timezone.now() - timedelta(days=7),
                'is_featured': True,
                'is_public': True,
            },
            {
                'title': f'God\'s Love - {church.name}',
                'speaker': church.pastor_name,
                'description': f'Understanding God\'s unconditional love for us at {church.name}',
                'date': timezone.now() - timedelta(days=14),
                'is_featured': True,
                'is_public': True,
            },
        ]
        
        for sermon_data in sermons_data:
            Sermon.objects.get_or_create(
                title=sermon_data['title'],
                church=church,
                defaults=sermon_data
            )
        
        # Create donation methods
        donation_methods_data = [
            {
                'name': 'Bank Transfer',
                'payment_type': 'bank_transfer',
                'account_info': f'Account: {church.name}\nIBAN: DE12345678901234567890\nBIC: DEUTDEDB123',
                'description': 'Direct bank transfer to our church account',
                'is_active': True,
            },
            {
                'name': 'PayPal',
                'payment_type': 'paypal',
                'account_info': f'paypal.me/{church.slug}',
                'description': 'Quick and secure online payments',
                'is_active': True,
            },
        ]
        
        for donation_data in donation_methods_data:
            DonationMethod.objects.get_or_create(
                name=donation_data['name'],
                church=church,
                defaults=donation_data
            )

    def create_global_hero(self):
        """Create global hero content"""
        Hero.objects.get_or_create(
            title="Welcome to Bethel Prayer Ministry",
            subtitle="Connecting churches worldwide through prayer and ministry",
            is_active=True,
            defaults={
                'primary_button_text': 'Find a Church Near You',
                'primary_button_link': '/churches/',
            }
        )

    def create_global_convention(self):
        """Create a global convention"""
        # Get Bremen church for the convention
        bremen_church = Church.objects.filter(slug='bremen').first()
        if bremen_church:
            Convention.objects.get_or_create(
                title="2025 Europe Prayer Convention",
                description="Join us for a powerful 3-day prayer convention in Bremen, Germany. Experience unity in prayer with believers from across Europe.",
                host_church=bremen_church,
                start_date=timezone.now() + timedelta(days=90),
                end_date=timezone.now() + timedelta(days=93),
                location="Bremen Conference Center",
                address="Am Markt 1, 28195 Bremen, Germany",
                max_attendees=500,
                registration_fee=50.00,
                registration_deadline=timezone.now() + timedelta(days=60),
            ) 