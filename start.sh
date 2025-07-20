#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
python manage.py wait_for_db

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Start the application
echo "Starting application..."
exec gunicorn backend.wsgi:application --config gunicorn.conf.py 