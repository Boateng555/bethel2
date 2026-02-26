from .models import GlobalSettings

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
        footer_copyright = getattr(gs, "footer_copyright", "© 2025 Bethel")
        footer_links = gs.get_footer_links() if hasattr(gs, "get_footer_links") else []
    except Exception:
        gs = None
        footer_copyright = "© 2025 Bethel"
        footer_links = []
    # Default meta description for pages that don't override (SEO)
    meta_desc = DEFAULT_META_DESCRIPTION
    return {
        "global_settings": gs,
        "meta_description": meta_desc,
        "footer_copyright": footer_copyright,
        "footer_links": footer_links,
    } 