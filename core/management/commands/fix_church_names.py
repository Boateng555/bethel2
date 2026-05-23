from django.core.management.base import BaseCommand

from core.models import Church, clean_church_name


class Command(BaseCommand):
    help = 'Fix duplicate words in church names (e.g. Assembly Assembly → Assembly).'

    def handle(self, *args, **options):
        updated = 0
        for church in Church.objects.all():
            cleaned = clean_church_name(church.name)
            if cleaned != church.name:
                self.stdout.write(f'  {church.name!r} → {cleaned!r}')
                church.name = cleaned
                church.save(update_fields=['name'])
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'Done. Updated {updated} church name(s).'))
