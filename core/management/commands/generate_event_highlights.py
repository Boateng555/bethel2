from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Event, EventHighlight

class Command(BaseCommand):
    help = 'Generate EventHighlight for every past Event that does not already have a highlight.'

    def handle(self, *args, **options):
        now = timezone.now()
        past_events = Event.objects.filter(start_date__lt=now)
        created_count = 0
        for event in past_events:
            # Check if a highlight already exists for this event
            if not EventHighlight.objects.filter(event=event).exists():
                # Get first image from hero media if available
                first_image = None
                if event.hero_media.exists():
                    first_media = event.hero_media.first()
                    if first_media.image:
                        first_image = first_media.image
                
                EventHighlight.objects.create(
                    event=event,
                    church=event.church,
                    title=event.title,
                    description=event.description,
                    year=event.start_date.year,
                    image=first_image,
                    is_public=True
                )
                self.stdout.write(self.style.SUCCESS(f'Created highlight for event: {event.title} ({event.start_date.year})'))
                created_count += 1
        if created_count == 0:
            self.stdout.write(self.style.WARNING('No new highlights were created. All past events already have highlights.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Total highlights created: {created_count}')) 