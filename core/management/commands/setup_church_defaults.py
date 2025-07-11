from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import Church, Ministry, DonationMethod, Hero, Event, News


class Command(BaseCommand):
    help = 'Set up default functionality for churches (ministries, donations, hero, events, news)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--church-id',
            type=str,
            help='Specific church ID to set up (optional)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Set up all churches',
        )

    def handle(self, *args, **options):
        if options['church_id']:
            try:
                churches = [Church.objects.get(id=options['church_id'])]
                self.stdout.write(f"Setting up church: {churches[0].name}")
            except Church.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Church with ID {options['church_id']} not found"))
                return
        elif options['all']:
            churches = Church.objects.all()
            self.stdout.write(f"Setting up {churches.count()} churches")
        else:
            self.stdout.write(self.style.ERROR("Please specify --church-id or --all"))
            return

        for church in churches:
            self.setup_church(church)

    def setup_church(self, church):
        """Set up default functionality for a church"""
        self.stdout.write(f"Setting up {church.name}...")

        # Check if church already has ministries
        if not Ministry.objects.filter(church=church).exists():
            self.create_default_ministries(church)
            self.stdout.write("  ✓ Created default ministries")

        # Check if church already has donation methods
        if not DonationMethod.objects.filter(church=church).exists():
            self.create_default_donations(church)
            self.stdout.write("  ✓ Created default donation methods")

        # Check if church already has hero section
        if not Hero.objects.filter(church=church).exists():
            self.create_default_hero(church)
            self.stdout.write("  ✓ Created default hero section")

        # Check if church already has events
        if not Event.objects.filter(church=church).exists():
            self.create_default_events(church)
            self.stdout.write("  ✓ Created default events")

        # Check if church already has news
        if not News.objects.filter(church=church).exists():
            self.create_default_news(church)
            self.stdout.write("  ✓ Created default news")

        self.stdout.write(self.style.SUCCESS(f"✓ Completed setup for {church.name}"))

    def create_default_ministries(self, church):
        """Create default ministries for a church"""
        default_ministries = [
            {
                'name': 'Youth Ministry',
                'description': 'Engaging young people in faith and fellowship',
                'ministry_type': 'youth',
                'leader_name': 'Youth Leader',
                'is_active': True,
                'is_public': True
            },
            {
                'name': 'Women\'s Ministry',
                'description': 'Supporting and empowering women in their faith journey',
                'ministry_type': 'women',
                'leader_name': 'Women\'s Ministry Leader',
                'is_active': True,
                'is_public': True
            },
            {
                'name': 'Men\'s Ministry',
                'description': 'Building strong men of faith and character',
                'ministry_type': 'men',
                'leader_name': 'Men\'s Ministry Leader',
                'is_active': True,
                'is_public': True
            },
            {
                'name': 'Children\'s Ministry',
                'description': 'Nurturing children in faith and biblical values',
                'ministry_type': 'children',
                'leader_name': 'Children\'s Ministry Leader',
                'is_active': True,
                'is_public': True
            },
            {
                'name': 'Music Ministry',
                'description': 'Leading worship through music and praise',
                'ministry_type': 'music',
                'leader_name': 'Music Ministry Leader',
                'is_active': True,
                'is_public': True
            },
            {
                'name': 'Prayer Ministry',
                'description': 'Intercessory prayer and spiritual support',
                'ministry_type': 'prayer',
                'leader_name': 'Prayer Ministry Leader',
                'is_active': True,
                'is_public': True
            },
            {
                'name': 'Outreach Ministry',
                'description': 'Serving the community and sharing the gospel',
                'ministry_type': 'outreach',
                'leader_name': 'Outreach Ministry Leader',
                'is_active': True,
                'is_public': True
            }
        ]
        
        for ministry_data in default_ministries:
            Ministry.objects.create(church=church, **ministry_data)

    def create_default_donations(self, church):
        """Create default donation methods for a church"""
        default_donations = [
            {
                'name': 'General Fund',
                'payment_type': 'other',
                'account_info': 'Contact the church office for donation information',
                'description': 'General church fund for operational expenses',
                'is_active': True,
                'is_default': True
            },
            {
                'name': 'Building Fund',
                'payment_type': 'other',
                'account_info': 'Contact the church office for building fund donations',
                'description': 'Fund for church building and maintenance projects',
                'is_active': True,
                'is_default': False
            },
            {
                'name': 'Missions Fund',
                'payment_type': 'other',
                'account_info': 'Contact the church office for missions support',
                'description': 'Supporting local and international missions',
                'is_active': True,
                'is_default': False
            }
        ]
        
        for donation_data in default_donations:
            DonationMethod.objects.create(church=church, **donation_data)

    def create_default_hero(self, church):
        """Create default hero section for a church"""
        Hero.objects.create(
            church=church,
            title=f'Welcome to {church.name}',
            subtitle=f'Join us in worship and fellowship in {church.city}, {church.country}',
            background_type='image',
            primary_button_text='Plan Your Visit',
            primary_button_link='/visit',
            secondary_button_text='Watch Online',
            secondary_button_link='/watch',
            is_active=True,
            order=1
        )

    def create_default_events(self, church):
        """Create default events for a church"""
        # Get next Sunday
        today = timezone.now().date()
        days_until_sunday = (6 - today.weekday()) % 7
        next_sunday = today + timedelta(days=days_until_sunday)
        
        # Create weekly Sunday service
        Event.objects.create(
            church=church,
            title='Sunday Service',
            description=f'Join us for our weekly Sunday worship service at {church.name}',
            start_date=timezone.make_aware(datetime.combine(next_sunday, datetime.min.time().replace(hour=10, minute=0))),
            end_date=timezone.make_aware(datetime.combine(next_sunday, datetime.min.time().replace(hour=12, minute=0))),
            location=church.name,
            address=church.get_full_address(),
            event_type='service',
            is_public=True
        )
        
        # Create weekly prayer meeting
        next_wednesday = today + timedelta(days=(2 - today.weekday()) % 7)
        Event.objects.create(
            church=church,
            title='Prayer Meeting',
            description=f'Join us for our weekly prayer meeting at {church.name}',
            start_date=timezone.make_aware(datetime.combine(next_wednesday, datetime.min.time().replace(hour=19, minute=0))),
            end_date=timezone.make_aware(datetime.combine(next_wednesday, datetime.min.time().replace(hour=20, minute=30))),
            location=church.name,
            address=church.get_full_address(),
            event_type='prayer',
            is_public=True
        )

    def create_default_news(self, church):
        """Create default news for a church"""
        News.objects.create(
            church=church,
            title=f'Welcome to {church.name}',
            content=f'We are excited to welcome you to {church.name} in {church.city}, {church.country}. Join us as we grow together in faith and fellowship.',
            excerpt=f'Welcome to {church.name} - a place of worship, community, and spiritual growth.',
            date=timezone.now().date(),
            is_public=True
        ) 