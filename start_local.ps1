# PowerShell script to start local development server
Write-Host "🚀 Starting Local Development Server" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan

# Set environment variables for local development
$env:DJANGO_DEBUG = "True"

# Remove any Railway-specific environment variables that might interfere
if ($env:DATABASE_URL) {
    Write-Host "⚠️ DATABASE_URL found - this will be ignored for local development" -ForegroundColor Yellow
}

Write-Host "✅ Environment configured for local development" -ForegroundColor Green
Write-Host "📦 Using SQLite database" -ForegroundColor Blue
Write-Host "🖼️ Using local file storage" -ForegroundColor Blue
Write-Host ""
Write-Host "🌐 Server will be available at: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "⏹️ Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Start Django development server
try {
    python manage.py runserver
}
catch {
    Write-Host "❌ Server failed to start: $_" -ForegroundColor Red
}
finally {
    Write-Host ""
    Write-Host "👋 Server stopped" -ForegroundColor Green
} 