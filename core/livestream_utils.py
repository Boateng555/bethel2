"""Helpers for live stream embed URLs (YouTube, Facebook, etc.)."""
from urllib.parse import quote


def normalize_facebook_url(url: str) -> str:
    """Normalize common Facebook URL variants."""
    from urllib.parse import urlparse, urlunparse

    url = (url or '').strip()
    if not url:
        return ''
    if url.startswith('http://'):
        url = 'https://' + url[7:]
    elif not url.startswith('https://'):
        if url.startswith('www.') or 'facebook.com' in url:
            url = 'https://' + url
    url = url.replace('://m.facebook.com/', '://www.facebook.com/')
    url = url.replace('://facebook.com/', '://www.facebook.com/')

    parsed = urlparse(url)
    if '/videos/' in parsed.path or '/watch' in parsed.path:
        url = urlunparse((parsed.scheme, parsed.netloc, parsed.path.rstrip('/'), '', '', ''))
    return url


def facebook_embed_url_from_input(url: str, width: int = 1280, height: int = 720) -> str:
    """
    Convert a Facebook video/live page URL into an iframe embed URL.

    Users often paste watch links (e.g. facebook.com/watch?v=...) which cannot be
    used as iframe src directly. Facebook requires the plugins/video.php or
    plugins/livestreamplayer.php endpoint.
    """
    raw = normalize_facebook_url(url)
    if not raw:
        return ''

    if 'facebook.com/plugins/' in raw:
        return raw

    encoded = quote(raw, safe='')
    lower = raw.lower()

    # Page live stream (/pagename/live, live_videos, etc.)
    if (
        '/live' in lower
        or 'live_videos' in lower
        or lower.rstrip('/').endswith('/live')
    ):
        return (
            f'https://www.facebook.com/plugins/livestreamplayer.php?'
            f'href={encoded}&width={width}&height={height}'
        )

    return (
        f'https://www.facebook.com/plugins/video.php?'
        f'href={encoded}&show_text=false&width={width}&height={height}'
    )
