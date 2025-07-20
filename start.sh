#!/bin/bash

echo "🚀 Starting Bethel Prayer Ministry Application..."

# Set environment variables
export PYTHONUNBUFFERED=1
export WEB_CONCURRENCY=1

# Function to check database connectivity
check_database() {
    echo "🔍 Checking database connectivity..."
    python manage.py check --database default 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Database connection successful"
        return 0
    else
        echo "⚠️ Database connection failed, continuing with startup..."
        return 1
    fi
}

# Function to run migrations with retry
run_migrations() {
    echo "🔄 Running database migrations..."
    for i in {1..3}; do
        echo "Migration attempt $i/3..."
        python manage.py migrate --noinput
        if [ $? -eq 0 ]; then
            echo "✅ Migrations completed successfully"
            return 0
        else
            echo "⚠️ Migration attempt $i failed"
            if [ $i -lt 3 ]; then
                echo "Waiting 5 seconds before retry..."
                sleep 5
            fi
        fi
    done
    echo "❌ All migration attempts failed, continuing anyway..."
    return 1
}

# Function to collect static files
collect_static() {
    echo "📦 Collecting static files..."
    python manage.py collectstatic --noinput
    if [ $? -eq 0 ]; then
        echo "✅ Static files collected successfully"
    else
        echo "⚠️ Static file collection failed, continuing anyway..."
    fi
}

# Main startup sequence
echo "🔧 Starting initialization..."

# Check if we're on Railway
if [ -n "$RAILWAY_ENVIRONMENT_NAME" ]; then
    echo "🚂 Running on Railway environment: $RAILWAY_ENVIRONMENT_NAME"
    export IS_RAILWAY=true
else
    echo "💻 Running in local environment"
    export IS_RAILWAY=false
fi

# Try to check database (but don't fail if it doesn't work)
check_database

# Try to run migrations (but don't fail if they don't work)
run_migrations

# Collect static files
collect_static

# Start the application
echo "🌐 Starting Gunicorn server..."
echo "   - Workers: 1"
echo "   - Timeout: 30s"
echo "   - Port: 8080"
echo "   - Host: 0.0.0.0"

exec gunicorn backend.wsgi:application \
    --bind 0.0.0.0:8080 \
    --workers 1 \
    --timeout 30 \
    --keep-alive 1 \
    --max-requests 100 \
    --max-requests-jitter 25 \
    --access-logfile - \
    --error-logfile - \
    --log-level warning \
    --preload-app false \
    --worker-tmp-dir /dev/shm 