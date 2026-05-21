from django.conf import settings as django_settings
from .models import GlobalSettings
from .push_notifications import webpush_enabled
from .pwa_utils import public_static_url

# Default SEO description used when a page doesn't set meta_description
DEFAULT_META_DESCRIPTION = (
    "Bethel Prayer Ministry International – Find a church near you, events, ministries, "
    "sermons, and news. Join us for worship and community."
)


def global_settings(request):
    """Add global settings and default SEO values to all template contexts."""
    try:
        settings = GlobalSettings.get_settings()
        gs = settings
        footer_copyright = getattr(gs, "footer_copyright", "© 2026 Bethel")
        if isinstance(footer_copyright, str) and "2025" in footer_copyright:
            footer_copyright = footer_copyright.replace("2025", "2026")
        if not isinstance(footer_copyright, str):
            footer_copyright = "© 2026 Bethel"
        footer_links = gs.get_footer_links() if hasattr(gs, "get_footer_links") else []
        if not isinstance(footer_links, list):
            footer_links = []
        # Use site description from admin as default meta description when set
        meta_desc = getattr(gs, "site_description", None) or DEFAULT_META_DESCRIPTION
        if not isinstance(meta_desc, str) or not meta_desc.strip():
            meta_desc = DEFAULT_META_DESCRIPTION
        # Global nav logo URL (absolute + cache-bust so updated logo shows immediately)
        global_nav_logo_url = ""
        if getattr(gs, "global_nav_logo", None):
            try:
                url = gs.get_global_nav_logo_url() if hasattr(gs, "get_global_nav_logo_url") else ""
                if url:
                    url = str(url).strip()
                    if not url.startswith("http"):
                        url = request.build_absolute_uri(url)
                    # Cache-bust so browser loads new image after admin change
                    sep = "&" if "?" in url else "?"
                    ts = getattr(gs, "updated_at", None)
                    global_nav_logo_url = f"{url}{sep}v={int(ts.timestamp()) if ts else id(gs)}"
                else:
                    global_nav_logo_url = ""
            except Exception:
                pass
    except Exception:
        gs = None
        footer_copyright = "© 2026 Bethel"
        footer_links = []
        meta_desc = DEFAULT_META_DESCRIPTION
        global_nav_logo_url = ""
    google_site_verification = getattr(django_settings, "GOOGLE_SITE_VERIFICATION", None) or ""
    if not global_nav_logo_url:
        global_nav_logo_url = public_static_url('/static/img/bethel_logo.png')
    return {
        "global_settings": gs,
        "meta_description": meta_desc,
        "footer_copyright": footer_copyright,
        "footer_links": footer_links,
        "global_nav_logo_url": global_nav_logo_url,
        "google_site_verification": google_site_verification,
        "webpush_enabled": webpush_enabled(),
        "pwa_apple_touch_icon": public_static_url('/static/img/apple-touch-icon.png'),
        "pwa_favicon": public_static_url('/static/img/favicon-32.png'),
        "pwa_icon_192": public_static_url('/static/img/icon-192.png'),
        "pwa_icon_512": public_static_url('/static/img/icon-512.png'),
    } 