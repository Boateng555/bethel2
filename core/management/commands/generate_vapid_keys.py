"""Generate VAPID keys for Web Push and print .env lines."""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generate WEBPUSH VAPID public/private keys for .env'

    def handle(self, *args, **options):
        try:
            from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
            from py_vapid import Vapid
            from py_vapid.utils import b64urlencode

            vapid = Vapid()
            vapid.generate_keys()
            public_bytes = vapid.public_key.public_bytes(
                Encoding.X962,
                PublicFormat.UncompressedPoint,
            )
            public_key = b64urlencode(public_bytes)
            private_key = vapid.private_pem()
            if isinstance(private_key, bytes):
                private_key = private_key.decode('utf-8')
        except ImportError:
            self.stderr.write('Install pywebpush first: pip install pywebpush')
            return
        except Exception as exc:
            self.stderr.write(f'Key generation failed: {exc}')
            return

        self.stdout.write(self.style.SUCCESS('Add these to your .env file:\n'))
        self.stdout.write(f'WEBPUSH_VAPID_PUBLIC_KEY={public_key}')
        self.stdout.write('WEBPUSH_VAPID_PRIVATE_KEY="' + private_key.replace('\n', '\\n') + '"')
        self.stdout.write('WEBPUSH_VAPID_ADMIN_EMAIL=admin@bethelprayerministryinternational.com')
