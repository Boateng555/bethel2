"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse

from core.sitemaps import (
    StaticViewSitemap,
    ChurchSitemap,
    ChurchLocationSitemap,
    ChurchPagesSitemap,
    EventSitemap,
    ChurchEventSitemap,
    MinistrySitemap,
    ChurchMinistrySitemap,
    NewsSitemap,
)
from core.views import church_detail_by_location, custom_error_500, custom_error_404, custom_error_403, custom_error_400

# Sitemaps for SEO (churches/events/ministries/news included; new churches appear automatically)
sitemaps = {
    'static': StaticViewSitemap,
    'churches': ChurchSitemap,
    'church_locations': ChurchLocationSitemap,
    'church_pages': ChurchPagesSitemap,
    'events': EventSitemap,
    'church_events': ChurchEventSitemap,
    'ministries': MinistrySitemap,
    'church_ministries': ChurchMinistrySitemap,
    'news': NewsSitemap,
}


def robots_txt(request):
    """Serve robots.txt allowing crawlers and pointing to sitemap."""
    scheme = 'https' if request.is_secure() else 'http'
    host = request.get_host()
    sitemap_url = f"{scheme}://{host}/sitemap.xml"
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /local-admin/",
        "Disallow: /global-admin/",
        "Disallow: /accounts/",
        "Disallow: /api/",
        "Disallow: /newsletter-signup/",
        "",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_with_canonical_domain(request, **kwargs):
    """Serve sitemap using SITE_DOMAIN as the domain so URLs show your real domain, not example.com."""
    site_domain = getattr(settings, 'SITE_DOMAIN', '').strip()
    if site_domain:
        # Django sitemap uses get_current_site(request).domain; patch it so we use SITE_DOMAIN
        from types import SimpleNamespace
        _real_get_current_site = get_current_site
        _fake_site = SimpleNamespace(domain=site_domain, name=site_domain.split('.')[0] or 'Site')

        def _patched_get_current_site(req):
            return _fake_site

        import django.contrib.sites.shortcuts as shortcuts_module
        shortcuts_module.get_current_site = _patched_get_current_site
        try:
            return sitemap(request, **kwargs)
        finally:
            shortcuts_module.get_current_site = _real_get_current_site
    return sitemap(request, **kwargs)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots.txt', robots_txt),
    path('sitemap.xml', sitemap_with_canonical_domain, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    # Location-based church URL (e.g. /churches/germany/hamburg/) – before core.urls so it matches
    path('churches/<str:country_slug>/<str:city_slug>/', church_detail_by_location, name='church_detail_by_location'),
    path('', include('core.urls')),
]

# Serve media files in both development and production
import os
_media_root = settings.MEDIA_ROOT
urlpatterns += static(settings.MEDIA_URL, document_root=_media_root)
if settings.DEBUG:
    print("Media: serving from MEDIA_ROOT =", _media_root)
    print("Media: exists?", os.path.exists(_media_root))

# Custom error handlers so footer (copyright/links) comes from admin and updates everywhere
handler500 = custom_error_500
handler404 = custom_error_404
handler403 = custom_error_403
handler400 = custom_error_400
