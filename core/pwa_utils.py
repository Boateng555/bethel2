"""Public asset URLs for PWA / Home Screen icons."""
from django.conf import settings


def public_static_url(path: str, cache_bust: str = '2') -> str:
    """Absolute HTTPS URL on the canonical public domain."""
    if not path.startswith('/'):
        path = '/' + path
    domain = getattr(settings, 'CANONICAL_PUBLIC_DOMAIN', '').strip()
    if not domain:
        domain = 'bethelprayerministryinternational.com'
    url = f'https://{domain.rstrip("/")}{path}'
    if cache_bust:
        sep = '&' if '?' in url else '?'
        url = f'{url}{sep}v={cache_bust}'
    return url
