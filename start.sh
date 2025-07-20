#!/bin/bash

echo "🚀 Starting Bethel Prayer Ministry International..."
echo "📅 $(date)"
echo ""

# Set environment variables for better error handling
export PYTHONUNBUFFERED=1
export DJANGO_SETTINGS_MODULE=backend.settings

# Function to check if we can connect to database
check_database() {
    echo "🔍 Checking database connectivity..."
    python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Database connection successful')
    exit(0)
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
" 2>/dev/null
    return $?
}

# Function to start in database-independent mode
start_without_db() {
    echo "⚠️  Starting in database-independent mode..."
    echo "📝 This mode will serve static content and basic functionality"
    
    # Set environment variable to indicate database-independent mode
    export DATABASE_INDEPENDENT_MODE=1
    
    # Start Gunicorn with minimal workers and longer timeouts
    exec gunicorn backend.wsgi:application \
        --bind 0.0.0.0:$PORT \
        --workers 1 \
        --timeout 120 \
        --keep-alive 5 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --preload \
        --access-logfile - \
        --error-logfile - \
        --log-level info
}

# Function to start with database
start_with_db() {
    echo "✅ Database available, starting full application..."
    
    # Try to run migrations with retries
    echo "🔄 Running database migrations..."
    for i in {1..3}; do
        echo "Attempt $i of 3..."
        if python manage.py migrate --noinput; then
            echo "✅ Migrations completed successfully"
            break
        else
            echo "❌ Migration attempt $i failed"
            if [ $i -eq 3 ]; then
                echo "⚠️  All migration attempts failed, continuing anyway..."
            else
                echo "⏳ Waiting 5 seconds before retry..."
                sleep 5
            fi
        fi
    done
    
    # Try to collect static files
    echo "📁 Collecting static files..."
    python manage.py collectstatic --noinput || echo "⚠️  Static file collection failed, continuing..."
    
    # Start Gunicorn
    echo "🚀 Starting Gunicorn server..."
    exec gunicorn backend.wsgi:application \
        --bind 0.0.0.0:$PORT \
        --workers 1 \
        --timeout 60 \
        --keep-alive 5 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --preload \
        --access-logfile - \
        --error-logfile - \
        --log-level info
}

# Main startup logic
echo "🔧 Railway database optimizations applied"
echo "🖼️ Using ImageKit for storage"

# Check database connectivity with timeout
echo "🔍 Testing database connectivity..."
timeout 10 bash -c 'check_database'
db_status=$?

if [ $db_status -eq 0 ]; then
    echo "✅ Database is available"
    start_with_db
else
    echo "❌ Database is not available"
    echo "⚠️  Starting in database-independent mode"
    start_without_db
fi 