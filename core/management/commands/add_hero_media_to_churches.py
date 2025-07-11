from django.core.management.base import BaseCommand
from core.models import Church, Hero, HeroMedia


class Command(BaseCommand):
    help = 'Add Hero Media functionality to churches that don\'t have it'

    def handle(self, *args, **options):
        churches_without_hero_media = []
        churches_updated = 0
        
        for church in Church.objects.all():
            # Check if church has hero content
            existing_hero = Hero.objects.filter(church=church).first()
            
            if existing_hero:
                # Check if hero has media
                if not existing_hero.hero_media.exists():
                    # Create Hero Media for existing hero
                    HeroMedia.objects.create(
                        hero=existing_hero,
                        image=None,
                        video=None,
                        order=1
                    )
                    churches_updated += 1
                    self.stdout.write(f"Added Hero Media to existing hero for {church.name}")
            else:
                # Create new hero with media
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
                
                # Create Hero Media for the new hero
                HeroMedia.objects.create(
                    hero=hero,
                    image=None,
                    video=None,
                    order=1
                )
                churches_updated += 1
                self.stdout.write(f"Created new hero with Hero Media for {church.name}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {churches_updated} churches with Hero Media functionality.'
            )
        ) 