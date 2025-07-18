@echo off
echo 🚀 Starting Local Development Server
echo ==================================================
echo.

REM Set environment variable for local development
set DJANGO_DEBUG=True

echo ✅ Environment configured for local development
echo 📦 Using SQLite database
echo 🖼️ Using local file storage
echo.
echo 🌐 Server will be available at: http://127.0.0.1:8000
echo ⏹️ Press Ctrl+C to stop the server
echo ==================================================
echo.

REM Start Django development server
python manage.py runserver

pause 