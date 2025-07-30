# Local Development Guide

## Overview
This guide will help you set up and run the Bethel Prayer Ministry Django project locally on your computer.

## Prerequisites
- Python 3.8 or higher
- Git
- A code editor (VS Code, PyCharm, etc.)

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd bethel
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```bash
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Run Database Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Start Development Server
```bash
python manage.py runserver
```

Your site will be available at: http://127.0.0.1:8000/

## Project Structure

```
bethel/
├── backend/           # Django settings and configuration
├── core/             # Main Django app with models, views, etc.
├── templates/        # HTML templates
├── static/          # CSS, JS, images
├── media/           # User-uploaded files (local development)
├── requirements.txt # Python dependencies
└── manage.py       # Django management script
```

## Development Workflow

### Making Changes
1. Create a new branch for your feature
2. Make your changes
3. Test locally
4. Commit and push your changes

### Database Changes
If you modify models:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files
After modifying CSS/JS:
```bash
python manage.py collectstatic
```

## Environment Differences

### Local Development
- Uses SQLite database
- Uses local storage for media files
- Debug mode enabled
- Detailed error pages

### Production
- Uses PostgreSQL database
- Uses local file storage for images
- Debug mode disabled
- Optimized for performance

## Common Issues

### Port Already in Use
If port 8000 is busy:
```bash
python manage.py runserver 8001
```

### Database Issues
Reset the database:
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Static Files Not Loading
```bash
python manage.py collectstatic --clear
```

## Testing

### Run Tests
```bash
python manage.py test
```

### Run Specific Tests
```bash
python manage.py test core.tests
```

## Debugging

### Django Debug Toolbar
The project includes Django Debug Toolbar for local development. It will automatically appear when `DEBUG=True`.

### Logging
Check the console output for detailed error messages and SQL queries.

## Deployment Preparation

Before deploying:
1. Set `DEBUG=False` in production
2. Update `ALLOWED_HOSTS` with your domain
3. Set up environment variables for production
4. Configure your production database
5. Media storage is handled locally

## Support

If you encounter issues:
1. Check the Django documentation
2. Review the project's README.md
3. Check the deployment guides in the project
4. Look at the error logs in the console 