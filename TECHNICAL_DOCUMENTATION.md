# Bethel Church Management Platform - Technical Documentation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Database Schema](#database-schema)
3. [API Documentation](#api-documentation)
4. [Deployment Guide](#deployment-guide)
5. [Configuration Management](#configuration-management)
6. [Security Implementation](#security-implementation)
7. [Performance Optimization](#performance-optimization)
8. [Development Setup](#development-setup)
9. [Testing Strategy](#testing-strategy)
10. [Maintenance Procedures](#maintenance-procedures)
11. [Troubleshooting Guide](#troubleshooting-guide)
12. [API Reference](#api-reference)

---

## System Architecture

### Overview
The Bethel Church Management Platform is built on Django with a multi-tenant architecture supporting individual church websites and a global network site.

### Technology Stack
- **Backend**: Django 5.1.3 (Python)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Web Server**: Nginx + Gunicorn
- **Media Storage**: Local file system with optimization
- **Frontend**: Django templates with Bootstrap
- **Admin Interface**: Custom Django admin
- **Location Services**: IP geolocation APIs

### Multi-Tenant Architecture

#### Church Isolation
Each church operates in its own data context:
- **Data Segregation**: Church-specific data isolation
- **URL Structure**: `/church/{church_id}/` for church-specific pages
- **Admin Access**: Role-based permissions per church
- **Media Storage**: Organized by church ID

#### Global vs Local Content
- **Global Site**: Network-wide content and features
- **Local Sites**: Church-specific content and functionality
- **Content Sharing**: Local content can be featured globally
- **Smart Redirects**: Location-based church detection

### Core Components

#### Models Structure
```
Church (Core entity)
├── ChurchAdmin (User permissions)
├── Event (Church events)
├── Ministry (Church ministries)
├── News (Church news)
├── Sermon (Church sermons)
├── DonationMethod (Payment methods)
├── Hero (Homepage banners)
├── AboutPage (About pages)
├── LeadershipPage (Leadership pages)
└── GlobalSettings (System configuration)
```

#### View Architecture
- **Public Views**: Church and global website pages
- **Admin Views**: Role-based admin interfaces
- **API Views**: REST API endpoints
- **Utility Views**: Helper functions and utilities

---

## Database Schema

### Core Models

#### Church Model
```python
class Church(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    
    # Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    
    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True, null=True)
    shop_url = models.URLField(blank=True, null=True)
    
    # Church Info
    pastor_name = models.CharField(max_length=100, blank=True)
    denomination = models.CharField(max_length=100, default="Bethel")
    founded_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    
    # Service Times
    service_times = models.TextField(blank=True)
    sunday_service_1 = models.TimeField(null=True, blank=True)
    sunday_service_2 = models.TimeField(null=True, blank=True)
    wednesday_service = models.TimeField(null=True, blank=True)
    friday_service = models.TimeField(null=True, blank=True)
    other_services = models.TextField(blank=True)
    
    # Media
    logo = models.ImageField(upload_to='churches/logos/', blank=True, null=True)
    nav_logo = models.ImageField(upload_to='churches/nav_logos/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='churches/banners/', blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### ChurchAdmin Model
```python
class ChurchAdmin(models.Model):
    ROLE_CHOICES = [
        ('local_admin', 'Local Admin'),
        ('global_admin', 'Global Admin'),
        ('moderator', 'Moderator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    church = models.ForeignKey(Church, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='local_admin')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Event Model
```python
class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True)
    
    # Event Details
    event_type = models.CharField(max_length=50, choices=[
        ('service', 'Church Service'),
        ('prayer', 'Prayer Meeting'),
        ('youth', 'Youth Event'),
        ('women', 'Women\'s Fellowship'),
        ('men', 'Men\'s Fellowship'),
        ('convention', 'Convention'),
        ('conference', 'Conference'),
        ('outreach', 'Outreach'),
        ('other', 'Other'),
    ], default='service')
    
    # Registration
    requires_registration = models.BooleanField(default=False)
    max_attendees = models.IntegerField(null=True, blank=True)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    is_big_event = models.BooleanField(default=False)
    is_global_featured = models.BooleanField(default=False)
    global_feature_status = models.CharField(max_length=20, choices=[
        ('none', 'None'), ('pending', 'Pending'), 
        ('approved', 'Approved'), ('rejected', 'Rejected')
    ], default='none')
    
    show_qr_code = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Database Indexes
```python
# Church indexes
indexes = [
    models.Index(fields=['is_active']),
    models.Index(fields=['is_approved']),
    models.Index(fields=['is_featured']),
    models.Index(fields=['city', 'country']),
]

# Event indexes
indexes = [
    models.Index(fields=['start_date']),
    models.Index(fields=['church', 'is_public']),
    models.Index(fields=['is_global_featured']),
]
```

---

## API Documentation

### REST API Endpoints

#### Events API
```python
# List all events
GET /api/events/
Response: List of EventSerializer objects

# Get specific event
GET /api/events/{event_id}/
Response: EventSerializer object

# Create event (admin only)
POST /api/events/
Request: EventSerializer data
Response: Created EventSerializer object
```

#### Ministries API
```python
# List all ministries
GET /api/ministries/
Response: List of MinistrySerializer objects

# Get specific ministry
GET /api/ministries/{ministry_id}/
Response: MinistrySerializer object
```

#### News API
```python
# List all news
GET /api/news/
Response: List of NewsSerializer objects

# Get specific news
GET /api/news/{news_id}/
Response: NewsSerializer object
```

#### Newsletter Signup API
```python
# Create newsletter signup
POST /api/newsletter-signup/
Request: NewsletterSignupSerializer data
Response: Created NewsletterSignupSerializer object
```

### Serializers

#### EventSerializer
```python
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'start_date', 'end_date',
            'location', 'address', 'event_type', 'is_featured',
            'church', 'created_at'
        ]
```

#### MinistrySerializer
```python
class MinistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Ministry
        fields = [
            'id', 'name', 'description', 'ministry_type',
            'leader_name', 'contact_email', 'contact_phone',
            'image', 'is_active', 'is_featured', 'church'
        ]
```

---

## Deployment Guide

### Production Deployment

#### Server Requirements
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **Python**: 3.9+
- **Database**: PostgreSQL 12+
- **Web Server**: Nginx
- **Application Server**: Gunicorn
- **Memory**: Minimum 2GB RAM
- **Storage**: 20GB+ available space

#### Environment Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx

# Create application user
sudo useradd -m -s /bin/bash bethel
sudo usermod -aG sudo bethel
```

#### Database Setup
```sql
-- Create database and user
CREATE DATABASE bethel_db;
CREATE USER bethel_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE bethel_db TO bethel_user;
```

#### Application Deployment
```bash
# Clone repository
git clone https://github.com/your-repo/bethel-platform.git
cd bethel-platform

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp production.env.example production.env
# Edit production.env with your settings

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Create superuser
python manage.py createsuperuser
```

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /static/ {
        alias /path/to/your/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /path/to/your/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Gunicorn Configuration
```python
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
```

#### Systemd Service
```ini
# /etc/systemd/system/bethel.service
[Unit]
Description=Bethel Church Platform
After=network.target

[Service]
User=bethel
Group=bethel
WorkingDirectory=/path/to/bethel-platform
Environment=PATH=/path/to/bethel-platform/venv/bin
ExecStart=/path/to/bethel-platform/venv/bin/gunicorn --config gunicorn.conf.py backend.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi:application"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://bethel_user:password@db:5432/bethel_db
      - DJANGO_SECRET_KEY=your-secret-key
      - DJANGO_DEBUG=False
    depends_on:
      - db
    volumes:
      - ./media:/app/media
      - ./staticfiles:/app/staticfiles

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=bethel_db
      - POSTGRES_USER=bethel_user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./staticfiles:/app/staticfiles
      - ./media:/app/media
    depends_on:
      - web

volumes:
  postgres_data:
```

---

## Configuration Management

### Environment Variables

#### Required Variables
```bash
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://user:password@host:port/database
USE_PROD_DB=true

# Local Church Redirect
LOCAL_CHURCH_REDIRECT_ENABLED=True
LOCAL_CHURCH_REDIRECT_MIN_SCORE=100
LOCAL_CHURCH_REDIRECT_MAX_DISTANCE_KM=50
```

#### Optional Variables
```bash
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Media Storage
MEDIA_URL=/media/
MEDIA_ROOT=/path/to/media/

# Static Files
STATIC_URL=/static/
STATIC_ROOT=/path/to/staticfiles/
```

### Settings Configuration

#### Production Settings
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# Database
DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL'),
        conn_max_age=60,
        ssl_require=True
    )
}

# Security
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Static Files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
```

#### Development Settings
```python
# settings.py
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static Files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

## Security Implementation

### Authentication & Authorization

#### User Roles
```python
# Role-based permissions
ROLE_CHOICES = [
    ('local_admin', 'Local Admin'),
    ('global_admin', 'Global Admin'),
    ('moderator', 'Moderator'),
]

# Permission checking
def is_global_admin(user):
    return user.is_superuser or \
           user.churchadmin_set.filter(role='global_admin', is_active=True).exists()

def is_local_admin(user, church=None):
    if user.is_superuser:
        return True
    queryset = user.churchadmin_set.filter(role='local_admin', is_active=True)
    if church:
        queryset = queryset.filter(church=church)
    return queryset.exists()
```

#### Admin Mixins
```python
class LocalAdminMixin:
    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        
        # Filter by user's church
        user_church = request.user.churchadmin_set.filter(
            role='local_admin', 
            is_active=True
        ).first()
        
        if user_church and user_church.church:
            return super().get_queryset(request).filter(church=user_church.church)
        
        return super().get_queryset(request).none()

class GlobalAdminMixin:
    def get_queryset(self, request):
        if request.user.is_superuser or is_global_admin(request.user):
            return super().get_queryset(request)
        return super().get_queryset(request).none()
```

### Data Protection

#### Church Data Isolation
```python
# Church-specific data filtering
def get_church_data(request, church_id):
    church = get_object_or_404(Church, id=church_id, is_active=True)
    
    # Check if user has access to this church
    if not request.user.is_superuser:
        user_church = request.user.churchadmin_set.filter(
            role='local_admin', 
            is_active=True
        ).first()
        
        if not user_church or user_church.church != church:
            raise PermissionDenied
    
    return church
```

#### CSRF Protection
```python
# CSRF configuration
CSRF_TRUSTED_ORIGINS = [
    "https://your-domain.com",
    "https://www.your-domain.com",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # ... other middleware
]
```

### File Upload Security

#### Image Validation
```python
def validate_image_upload(image):
    # Check file size (10MB limit)
    if image.size > 10 * 1024 * 1024:
        raise ValidationError("Image file too large ( > 10MB )")
    
    # Check file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif']
    if image.content_type not in allowed_types:
        raise ValidationError("Unsupported image format")
    
    # Check file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError("Unsupported file extension")
```

#### Media Storage Security
```python
class LocalFileStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.location = settings.MEDIA_ROOT
    
    def get_available_name(self, name, max_length=None):
        # Ensure unique filenames
        if self.exists(name):
            dir_name, file_name = os.path.split(name)
            file_root, file_ext = os.path.splitext(file_name)
            name = os.path.join(dir_name, f"{file_root}_{uuid.uuid4().hex[:8]}{file_ext}")
        return name
```

---

## Performance Optimization

### Database Optimization

#### Query Optimization
```python
# Use select_related for foreign keys
events = Event.objects.select_related('church').filter(is_public=True)

# Use prefetch_related for many-to-many
churches = Church.objects.prefetch_related('ministries').filter(is_active=True)

# Use only() to limit fields
church_list = Church.objects.only('name', 'city', 'country').filter(is_active=True)
```

#### Database Indexes
```python
class Church(models.Model):
    # ... fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['is_approved']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['city', 'country']),
        ]
```

### Caching Strategy

#### Template Caching
```python
# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Template fragment caching
{% load cache %}
{% cache 300 "church_events" church.id %}
    <!-- Event list content -->
{% endcache %}
```

#### View Caching
```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def church_list(request):
    churches = Church.objects.filter(is_active=True)
    return render(request, 'core/church_list.html', {'churches': churches})
```

### Static File Optimization

#### WhiteNoise Configuration
```python
# Static file compression
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Cache headers
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

#### Image Optimization
```python
def optimize_image_for_web(image_path, max_width=1200, quality=85):
    """Optimize images for web delivery"""
    from PIL import Image
    
    with Image.open(image_path) as img:
        # Resize if too large
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)
        
        # Save with optimization
        img.save(image_path, quality=quality, optimize=True)
```

---

## Development Setup

### Local Development Environment

#### Prerequisites
- Python 3.9+
- PostgreSQL (optional, SQLite for development)
- Git
- Virtual environment tool

#### Setup Steps
```bash
# Clone repository
git clone https://github.com/your-repo/bethel-platform.git
cd bethel-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your local settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

#### Development Settings
```python
# settings.py (development)
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Use SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Disable SSL redirect in development
SECURE_SSL_REDIRECT = False
```

### Code Structure

#### Project Layout
```
bethel/
├── backend/                 # Django project settings
│   ├── settings.py         # Main settings file
│   ├── urls.py            # URL configuration
│   └── wsgi.py            # WSGI application
├── core/                   # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── admin.py           # Admin interface
│   ├── forms.py           # Form classes
│   ├── serializers.py     # API serializers
│   └── utils.py           # Utility functions
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── core/              # Core app templates
│   └── admin/             # Admin templates
├── static/                 # Static files
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript
│   └── img/               # Images
├── media/                  # User uploaded files
├── requirements.txt        # Python dependencies
└── manage.py              # Django management script
```

#### Model Organization
```python
# core/models.py
# Core entities
class Church(models.Model):
    # Church information and settings

class ChurchAdmin(models.Model):
    # User permissions and roles

# Content models
class Event(models.Model):
    # Church events and activities

class Ministry(models.Model):
    # Church ministries and groups

class News(models.Model):
    # Church news and announcements

class Sermon(models.Model):
    # Church sermons and messages

# Supporting models
class DonationMethod(models.Model):
    # Payment methods

class Hero(models.Model):
    # Homepage banners

class GlobalSettings(models.Model):
    # System-wide settings
```

---

## Testing Strategy

### Test Structure

#### Unit Tests
```python
# tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Church, ChurchAdmin, Event

class ChurchModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.church = Church.objects.create(
            name='Test Church',
            city='Test City',
            country='Test Country'
        )
    
    def test_church_creation(self):
        self.assertEqual(self.church.name, 'Test Church')
        self.assertTrue(self.church.is_active)
    
    def test_church_full_address(self):
        self.church.address = '123 Test St'
        self.church.state_province = 'Test State'
        self.church.postal_code = '12345'
        
        expected = '123 Test St, Test City, Test State, Test Country, 12345'
        self.assertEqual(self.church.get_full_address(), expected)
```

#### Integration Tests
```python
class ChurchViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.church = Church.objects.create(
            name='Test Church',
            city='Test City',
            country='Test Country',
            is_active=True,
            is_approved=True
        )
    
    def test_church_list_view(self):
        response = self.client.get('/churches/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Church')
    
    def test_church_detail_view(self):
        response = self.client.get(f'/church/{self.church.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Church')
```

#### Admin Tests
```python
class AdminTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        self.client.login(username='admin', password='adminpass123')
    
    def test_church_admin_list(self):
        response = self.client.get('/admin/core/church/')
        self.assertEqual(response.status_code, 200)
    
    def test_add_church(self):
        response = self.client.post('/admin/core/church/add/', {
            'name': 'New Church',
            'city': 'New City',
            'country': 'New Country',
            'is_active': True,
        })
        self.assertEqual(response.status_code, 302)  # Redirect after save
```

### Test Configuration

#### Test Settings
```python
# settings_test.py
from .settings import *

# Use in-memory database for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use console email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

#### Test Commands
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test core

# Run specific test class
python manage.py test core.tests.ChurchModelTest

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

---

## Maintenance Procedures

### Database Maintenance

#### Regular Backups
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="bethel_db"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump $DB_NAME > $BACKUP_DIR/bethel_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/bethel_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "bethel_*.sql.gz" -mtime +7 -delete

echo "Backup completed: bethel_$DATE.sql.gz"
```

#### Database Optimization
```sql
-- Analyze tables for query optimization
ANALYZE;

-- Vacuum tables to reclaim space
VACUUM ANALYZE;

-- Reindex tables
REINDEX DATABASE bethel_db;
```

### Log Management

#### Log Configuration
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/bethel/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

#### Log Rotation
```bash
# /etc/logrotate.d/bethel
/var/log/bethel/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 bethel bethel
    postrotate
        systemctl reload bethel
    endscript
}
```

### System Monitoring

#### Health Checks
```python
# views.py
def health_check(request):
    """System health check endpoint"""
    try:
        # Check database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check media directory
        import os
        media_path = settings.MEDIA_ROOT
        if not os.path.exists(media_path):
            os.makedirs(media_path)
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'media': 'accessible',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)
```

#### Monitoring Scripts
```bash
#!/bin/bash
# monitor.sh
HEALTH_URL="https://your-domain.com/health/"
LOG_FILE="/var/log/bethel/monitor.log"

# Check system health
response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $response -eq 200 ]; then
    echo "$(date): System healthy" >> $LOG_FILE
else
    echo "$(date): System unhealthy (HTTP $response)" >> $LOG_FILE
    # Send alert
    echo "Bethel platform is down!" | mail -s "System Alert" admin@your-domain.com
fi
```

---

## Troubleshooting Guide

### Common Issues

#### Database Connection Issues
```bash
# Check database status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U bethel_user -d bethel_db

# Reset database connection
sudo systemctl restart postgresql
```

#### Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check permissions
sudo chown -R www-data:www-data /path/to/staticfiles/
sudo chmod -R 755 /path/to/staticfiles/

# Check nginx configuration
sudo nginx -t
sudo systemctl reload nginx
```

#### Media Upload Issues
```bash
# Check media directory permissions
sudo chown -R www-data:www-data /path/to/media/
sudo chmod -R 755 /path/to/media/

# Check disk space
df -h

# Check file upload limits
# In nginx.conf:
client_max_body_size 10M;
```

#### Performance Issues

##### Database Performance
```sql
-- Check slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

##### Application Performance
```python
# Enable Django Debug Toolbar for development
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# Monitor query performance
from django.db import connection
from django.db import reset_queries
import time

def monitor_queries():
    reset_queries()
    start_time = time.time()
    
    # Your code here
    
    end_time = time.time()
    print(f"Execution time: {end_time - start_time}")
    print(f"Number of queries: {len(connection.queries)}")
```

### Error Logs

#### Django Error Logs
```bash
# Check Django logs
tail -f /var/log/bethel/django.log

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check system logs
sudo journalctl -u bethel -f
```

#### Common Error Messages

##### Database Errors
```
OperationalError: connection to server at "localhost" (127.0.0.1), port 5432 failed
```
**Solution**: Check PostgreSQL service status and connection settings

##### Permission Errors
```
PermissionError: [Errno 13] Permission denied
```
**Solution**: Check file and directory permissions

##### Memory Errors
```
MemoryError: Unable to allocate array
```
**Solution**: Optimize image processing or increase server memory

### Recovery Procedures

#### Database Recovery
```bash
# Restore from backup
pg_restore -d bethel_db /backups/bethel_20231201_120000.sql

# Reset migrations (if needed)
python manage.py migrate --fake-initial
```

#### Application Recovery
```bash
# Restart application
sudo systemctl restart bethel

# Clear cache
python manage.py clear_cache

# Reset static files
python manage.py collectstatic --noinput --clear
```

---

## API Reference

### Authentication

#### Session Authentication
```python
# Login
POST /admin/login/
{
    "username": "admin",
    "password": "password"
}

# Logout
POST /admin/logout/
```

### Church API

#### List Churches
```http
GET /api/churches/
Authorization: Session
```

**Response:**
```json
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "name": "Bethel Church",
            "city": "Hamburg",
            "country": "Germany",
            "is_active": true,
            "is_approved": true
        }
    ]
}
```

#### Get Church Details
```http
GET /api/churches/{church_id}/
Authorization: Session
```

**Response:**
```json
{
    "id": "uuid",
    "name": "Bethel Church",
    "slug": "bethel-hamburg",
    "address": "123 Main St",
    "city": "Hamburg",
    "country": "Germany",
    "phone": "+49 40 123456",
    "email": "info@bethel-hamburg.de",
    "website": "https://bethel-hamburg.de",
    "service_times": "Sunday 9:00 AM & 11:00 AM",
    "is_active": true,
    "is_approved": true,
    "created_at": "2023-01-01T00:00:00Z"
}
```

### Event API

#### List Events
```http
GET /api/events/
Authorization: Session
```

**Query Parameters:**
- `church_id`: Filter by church
- `event_type`: Filter by event type
- `start_date`: Filter by start date
- `is_featured`: Filter featured events

#### Create Event
```http
POST /api/events/
Authorization: Session
Content-Type: application/json
```

**Request Body:**
```json
{
    "church": "church-uuid",
    "title": "Sunday Service",
    "description": "Weekly worship service",
    "start_date": "2023-12-03T09:00:00Z",
    "end_date": "2023-12-03T11:00:00Z",
    "location": "Main Auditorium",
    "address": "123 Main St, Hamburg",
    "event_type": "service",
    "is_featured": true,
    "is_public": true
}
```

### Ministry API

#### List Ministries
```http
GET /api/ministries/
Authorization: Session
```

#### Create Ministry
```http
POST /api/ministries/
Authorization: Session
Content-Type: application/json
```

**Request Body:**
```json
{
    "church": "church-uuid",
    "name": "Youth Ministry",
    "description": "Ministry for young people",
    "ministry_type": "youth",
    "leader_name": "John Doe",
    "contact_email": "youth@church.com",
    "contact_phone": "+49 40 123456",
    "is_active": true,
    "is_featured": true
}
```

### Error Responses

#### Standard Error Format
```json
{
    "error": "Error message",
    "code": "ERROR_CODE",
    "details": {
        "field": "Field-specific error"
    }
}
```

#### Common Error Codes
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

---

*This technical documentation is maintained by the Bethel Church Management Platform development team. For updates or questions, contact the development team.* 