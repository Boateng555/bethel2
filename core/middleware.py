import os
from django.http import HttpResponse
from django.conf import settings

import re
from urllib.parse import urlparse
# Try to import user_agents, but don't fail if not available
try:
    from user_agents import parse
    USER_AGENTS_AVAILABLE = True
except ImportError:
    USER_AGENTS_AVAILABLE = False
    parse = None

import geoip2.database
import geoip2.errors
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class DatabaseIndependentMiddleware:
    """
    Middleware to handle requests when database is unavailable.
    Serves static content and basic functionality without database access.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.db_independent_mode = os.environ.get('DATABASE_INDEPENDENT_MODE', '0') == '1'
        
    def __call__(self, request):
        # Check if we're in database-independent mode
        if self.db_independent_mode:
            return self.handle_db_independent_request(request)
        
        # Check if database is available
        if not self.is_database_available():
            return self.handle_db_unavailable_request(request)
        
        return self.get_response(request)
    
    def is_database_available(self):
        """Quick check if database is available"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception:
            return False
    
    def handle_db_independent_request(self, request):
        """Handle requests when in database-independent mode"""
        path = request.path.strip('/')
        
        # Allow health check endpoints
        if path in ['health', 'startup-health', 'fallback']:
            return self.get_response(request)
        
        # Serve static fallback for all other requests
        return self.serve_static_fallback(request)
    
    def handle_db_unavailable_request(self, request):
        """Handle requests when database becomes unavailable"""
        path = request.path.strip('/')
        
        # Allow health check and fallback endpoints
        if path in ['health', 'startup-health', 'fallback']:
            return self.get_response(request)
        
        # For API endpoints, return JSON error
        if path.startswith('api/') or request.path.startswith('/api/'):
            return HttpResponse(
                '{"error": "Database temporarily unavailable", "status": "maintenance"}',
                content_type='application/json',
                status=503
            )
        
        # For all other requests, serve static fallback
        return self.serve_static_fallback(request)
    
    def serve_static_fallback(self, request):
        """Serve the static fallback page"""
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Bethel Prayer Ministry International - Service Update</title>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .container { 
                    max-width: 600px; 
                    background: white; 
                    padding: 40px; 
                    border-radius: 15px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    text-align: center;
                }
                .logo { 
                    font-size: 2.5em; 
                    color: #1e3a8a; 
                    font-weight: bold; 
                    margin-bottom: 10px; 
                }
                .subtitle { 
                    color: #666; 
                    margin-bottom: 30px; 
                    font-size: 1.1em;
                }
                .status { 
                    background: #f0f9ff; 
                    border: 2px solid #0ea5e9; 
                    padding: 20px; 
                    border-radius: 10px; 
                    margin-bottom: 30px; 
                }
                .status h3 { 
                    margin-top: 0; 
                    color: #0c4a6e; 
                    font-size: 1.3em;
                }
                .contact { 
                    background: #fef3c7; 
                    border: 2px solid #f59e0b; 
                    padding: 20px; 
                    border-radius: 10px; 
                    margin-bottom: 30px;
                }
                .contact h3 { 
                    margin-top: 0; 
                    color: #92400e; 
                    font-size: 1.2em;
                }
                .contact p { 
                    margin: 8px 0; 
                    color: #78350f;
                }
                .refresh-btn { 
                    background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); 
                    color: white; 
                    padding: 12px 24px; 
                    border: none; 
                    border-radius: 8px; 
                    cursor: pointer; 
                    font-size: 16px; 
                    font-weight: 600;
                    transition: transform 0.2s;
                }
                .refresh-btn:hover { 
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(30, 58, 138, 0.3);
                }
                .auto-refresh { 
                    color: #666; 
                    font-size: 14px; 
                    margin-top: 20px;
                }
                .prayer-icon {
                    font-size: 3em;
                    margin-bottom: 20px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="prayer-icon">🙏</div>
                <div class="logo">Bethel Prayer Ministry International</div>
                <div class="subtitle">Connecting believers worldwide through prayer and fellowship</div>
                
                <div class="status">
                    <h3>🔄 Service Maintenance</h3>
                    <p>We're currently performing essential maintenance on our database systems to improve your experience.</p>
                    <p>Our team is working diligently to restore full service as quickly as possible.</p>
                </div>
                
                <div class="contact">
                    <h3>📞 Need Immediate Assistance?</h3>
                    <p><strong>Email:</strong> info@bethelprayer.org</p>
                    <p><strong>Prayer Requests:</strong> We're still accepting prayer requests via email</p>
                    <p><strong>Emergency Contact:</strong> Available through our prayer network</p>
                </div>
                
                <button class="refresh-btn" onclick="window.location.reload()">
                    🔄 Refresh Page
                </button>
                
                <div class="auto-refresh">
                    <p>This page will automatically refresh every 30 seconds</p>
                    <p>© 2024 Bethel Prayer Ministry International</p>
                </div>
            </div>
            
            <script>
                // Auto-refresh every 30 seconds
                setTimeout(function() {
                    window.location.reload();
                }, 30000);
                
                // Show countdown
                let countdown = 30;
                setInterval(function() {
                    countdown--;
                    if (countdown <= 0) {
                        countdown = 30;
                    }
                }, 1000);
            </script>
        </body>
        </html>
        """
        
        return HttpResponse(html_content, content_type='text/html') 

class AnalyticsMiddleware:
    """
    Middleware to track visitor analytics - Production Safe Version
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only try analytics if all dependencies are available
        if not all([USER_AGENTS_AVAILABLE, GEOIP2_AVAILABLE, ANALYTICS_AVAILABLE]):
            return self.get_response(request)
        
        try:
            # Try to import analytics models
            from .analytics_models import VisitorSession, PageView, AnalyticsSettings
            
            # Check if analytics is enabled
            try:
                settings = AnalyticsSettings.objects.first()
                if not settings or not settings.enable_tracking:
                    return self.get_response(request)
            except:
                return self.get_response(request)
            
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Anonymize IP for privacy
            if ip:
                ip_parts = ip.split('.')
                if len(ip_parts) == 4:
                    ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0"
            
            # Parse user agent
            user_agent_string = request.META.get('HTTP_USER_AGENT', '')
            if USER_AGENTS_AVAILABLE and user_agent_string:
                user_agent = parse(user_agent_string)
                browser = user_agent.browser.family
                os_name = user_agent.os.family
                device = user_agent.device.family
            else:
                browser = 'Unknown'
                os_name = 'Unknown'
                device = 'Unknown'
            
            # Get geolocation
            country = None
            city = None
            if GEOIP2_AVAILABLE and ip:
                try:
                    # This would require a GeoIP database file
                    # For now, we'll skip geolocation
                    pass
                except:
                    pass
            
            # Get referrer
            referrer = request.META.get('HTTP_REFERER', '')
            if referrer:
                try:
                    parsed_referrer = urlparse(referrer)
                    referrer_domain = parsed_referrer.netloc
                except:
                    referrer_domain = ''
            else:
                referrer_domain = ''
            
            # Create or get session
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            
            # Get or create visitor session
            session, created = VisitorSession.objects.get_or_create(
                session_id=session_id,
                defaults={
                    'ip_address': ip,
                    'user_agent': user_agent_string,
                    'browser': browser,
                    'os': os_name,
                    'device': device,
                    'country': country,
                    'city': city,
                    'referrer_domain': referrer_domain,
                }
            )
            
            # Record page view
            PageView.objects.create(
                session=session,
                url=request.path,
                method=request.method,
                referrer=referrer,
            )
            
        except Exception as e:
            # If anything goes wrong, just continue without analytics
            pass
        
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