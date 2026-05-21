"""Helpers for live stream embed URLs (YouTube, Facebook, etc.)."""
import re
from urllib.parse import quote, urlparse, urlunparse


def facebook_page_live_url(page_id_or_slug: str) -> str:
    """Build a Facebook Page /live URL from admin page ID or username."""
    raw = (page_id_or_slug or '').strip().strip('/')
    if not raw:
        return ''
    if raw.isdigit():
        return f'https://www.facebook.com/profile.php?id={raw}&sk=live'
    return f'https://www.facebook.com/{raw}/live'


def normalize_facebook_url(url: str) -> str:
    """Normalize common Facebook URL variants."""
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
    path = parsed.path.rstrip('/')
    if '/videos/' in path or '/watch' in path:
        url = urlunparse((parsed.scheme, parsed.netloc, path, '', '', ''))
        return url

    # Page home link (facebook.com/YourPage) — use /live for embeds
    if re.match(r'^/[^/]+$', path) and path.lower() not in ('/watch', '/share', '/login'):
        url = urlunparse((parsed.scheme, parsed.netloc, path + '/live', '', '', ''))
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
