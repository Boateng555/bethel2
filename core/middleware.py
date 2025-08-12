import os
from django.http import HttpResponse
from django.conf import settings

import re
from urllib.parse import urlparse
from user_agents import parse
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
    """Middleware to track visitor analytics"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Initialize GeoIP reader if available
        self.geoip_reader = None
        try:
            # You can download GeoLite2-City.mmdb from MaxMind
            geoip_path = getattr(settings, 'GEOIP_PATH', None)
            if geoip_path:
                self.geoip_reader = geoip2.database.Reader(geoip_path)
        except Exception:
            pass
    
    def __call__(self, request):
        # Skip tracking for admin, static files, and API calls
        if self._should_skip_tracking(request):
            return self.get_response(request)
        
        # Track the visit
        self._track_visit(request)
        
        response = self.get_response(request)
        return response
    
    def _should_skip_tracking(self, request):
        """Determine if we should skip tracking for this request"""
        skip_patterns = [
            r'^/admin/',
            r'^/static/',
            r'^/media/',
            r'^/api/',
            r'^/favicon\.ico$',
            r'^/robots\.txt$',
        ]
        
        path = request.path
        for pattern in skip_patterns:
            if re.match(pattern, path):
                return True
        
        return False
    
    def _track_visit(self, request):
        """Track the current visit"""
        try:
            from .analytics_models import VisitorSession, PageView, AnalyticsSettings
            
            # Check if tracking is enabled
            settings = AnalyticsSettings.get_settings()
            if not settings.enable_tracking:
                return
            
            # Get or create session
            session = self._get_or_create_session(request, settings)
            if not session:
                return
            
            # Create page view
            self._create_page_view(request, session)
            
        except Exception as e:
            # Log error but don't break the request
            print(f"Analytics tracking error: {e}")
    
    def _get_or_create_session(self, request, analytics_settings):
        """Get existing session or create new one"""
        from .analytics_models import VisitorSession
        
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        # Try to get existing active session
        try:
            session = VisitorSession.objects.get(session_id=session_id)
            
            # Update last activity
            session.last_activity = timezone.now()
            session.page_views_count += 1
            session.save()
            
            return session
            
        except VisitorSession.DoesNotExist:
            # Create new session
            return self._create_new_session(request, session_id, analytics_settings)
    
    def _create_new_session(self, request, session_id, analytics_settings):
        """Create a new visitor session"""
        from .analytics_models import VisitorSession
        
        # Get IP address
        ip_address = self._get_client_ip(request)
        
        # Parse user agent
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        user_agent = parse(user_agent_string)
        
        # Get geographic data
        country = city = region = ''
        if analytics_settings.track_geolocation and self.geoip_reader:
            try:
                response = self.geoip_reader.city(ip_address)
                country = response.country.name or ''
                city = response.city.name or ''
                region = response.subdivisions.most_specific.name or ''
            except (geoip2.errors.AddressNotFoundError, ValueError):
                pass
        
        # Determine device type
        device_type = 'other'
        if user_agent.is_mobile:
            device_type = 'mobile'
        elif user_agent.is_tablet:
            device_type = 'tablet'
        elif user_agent.is_pc:
            device_type = 'desktop'
        
        # Get referrer
        referrer = request.META.get('HTTP_REFERER', '')
        referrer_domain = ''
        if referrer and analytics_settings.track_referrers:
            try:
                parsed = urlparse(referrer)
                referrer_domain = parsed.netloc
            except:
                pass
        
        # Determine church context
        church = None
        if hasattr(request, 'church'):
            church = request.church
        
        # Create session
        session = VisitorSession.objects.create(
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent_string if analytics_settings.track_user_agent else '',
            country=country,
            city=city,
            region=region,
            device_type=device_type,
            browser=user_agent.browser.family if analytics_settings.track_user_agent else '',
            browser_version=user_agent.browser.version_string if analytics_settings.track_user_agent else '',
            os=user_agent.os.family if analytics_settings.track_user_agent else '',
            referrer=referrer,
            referrer_domain=referrer_domain,
            church=church,
            page_views_count=1
        )
        
        return session
    
    def _create_page_view(self, request, session):
        """Create a page view record"""
        from .analytics_models import PageView
        
        # Get page info
        url = request.build_absolute_uri()
        path = request.path
        page_title = getattr(request, 'page_title', '')
        view_name = getattr(request.resolver_match, 'view_name', '') if hasattr(request, 'resolver_match') and request.resolver_match else ''
        
        # Determine church context
        church = None
        if hasattr(request, 'church'):
            church = request.church
        
        # Create page view
        PageView.objects.create(
            session=session,
            url=url,
            path=path,
            page_title=page_title,
            view_name=view_name,
            church=church
        )
    
    def _get_client_ip(self, request):
        """Get the client's real IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 