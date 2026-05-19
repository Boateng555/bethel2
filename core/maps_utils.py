"""Google Maps URL helpers."""
from urllib.parse import quote


def maps_url_for_address(text):
    """Return a Google Maps search URL for a plain-text address, or empty string."""
    if not text or not str(text).strip():
        return ''
    return f'https://www.google.com/maps/search/?api=1&query={quote(str(text).strip())}'
