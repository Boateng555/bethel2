"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse

from core.sitemaps import (
    StaticViewSitemap,
    ChurchSitemap,
    ChurchPagesSitemap,
    EventSitemap,
    ChurchEventSitemap,
    MinistrySitemap,
    ChurchMinistrySitemap,
    NewsSitemap,
)
from core.views import church_detail_by_location

sitemaps = {
    'static': StaticViewSitemap,
    'churches': ChurchSitemap,
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
        "",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots.txt', robots_txt),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    # Location-based church URL (e.g. /churches/germany/hamburg/)
    path('churches/<str:country_slug>/<str:city_slug>/', church_detail_by_location, name='church_detail_by_location'),
    path('', include('core.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
