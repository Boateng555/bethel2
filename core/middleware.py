import os
from django.http import HttpResponse
from django.conf import settings

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