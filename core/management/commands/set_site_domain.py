"""
Set the Django Site domain from SITE_DOMAIN env var (for sitemap/SEO).
Run after deploy: python manage.py set_site_domain
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = "Set the default Site domain from SITE_DOMAIN (used by sitemap and SEO)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            help='Override: domain to set (e.g. www.bethel.org). Otherwise uses SITE_DOMAIN from settings.',
        )

    def handle(self, *args, **options):
        domain = options.get('domain') or getattr(settings, 'SITE_DOMAIN', '') or ''
        if not domain:
            self.stdout.write(
                self.style.WARNING(
                    'No domain set. Set SITE_DOMAIN in .env or pass --domain=www.yoursite.com'
                )
            )
            return
        site, created = Site.objects.update_or_create(
            id=settings.SITE_ID,
            defaults={
                'domain': domain,
                'name': domain.split('.')[0].replace('www', 'Bethel').strip('.-') or 'Bethel',
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Site (id={settings.SITE_ID}) set to domain={site.domain}, name={site.name}"))
