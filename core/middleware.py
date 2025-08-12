from django.utils.deprecation import MiddlewareMixin

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