from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.conf import settings as django_settings


# Production domain(s) to always allow (fixes DisallowedHost when server has old ALLOWED_HOSTS)
_ALLOWED_PRODUCTION_HOSTS = frozenset([
    'bethelprayerministryinternational.com',
    'www.bethelprayerministryinternational.com',
])


class AllowProductionHostMiddleware:
    """
    Ensure production domain is in ALLOWED_HOSTS even if server env/settings are old.
    Add the request host to ALLOWED_HOSTS for this process when it matches a known production host.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = (request.META.get('HTTP_HOST') or '').split(':')[0].lower()
        if host in _ALLOWED_PRODUCTION_HOSTS and host not in django_settings.ALLOWED_HOSTS:
            django_settings.ALLOWED_HOSTS = list(django_settings.ALLOWED_HOSTS) + [host]
        return self.get_response(request)


class RedirectLocalAdminToDashboardMiddleware:
    """
    Church staff should not see the Django admin (database) interface. When they go to /admin/:
    - Superusers: see the full Django admin (platform/database management).
    - Everyone else: go to a simple "Church Admin Dashboard" entry page only (no database UI).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.rstrip('/')
        if path == '/admin' and request.user.is_authenticated:
            if request.user.is_superuser:
                # Superusers keep using Django admin for platform/database management
                return self.get_response(request)
            # All other staff: send to the church-only entry page (no Django admin)
            return redirect('/church-admin-entry/')
        return self.get_response(request)


class DatabaseIndependentMiddleware:
    """
    Middleware to ensure database operations are handled gracefully
    even if the primary database is unavailable.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add a flag to request to indicate if database is available
        request.db_available = True
        
        try:
            # Test database connection
            from django.db import connection
            connection.ensure_connection()
        except Exception:
            request.db_available = False
        
        response = self.get_response(request)
        return response 