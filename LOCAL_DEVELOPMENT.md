# Local Development Guide

This guide explains how to set up and run the Bethel project locally.

## Quick Start

### Option 1: PowerShell Script (Recommended)
```powershell
.\start_local.ps1
```

### Option 2: Batch File (Windows)
```cmd
start_local_fixed.bat
```

### Option 3: Python Script
```bash
python start_local_server.py
```

### Option 4: Manual Setup
```powershell
# Set environment variable
$env:DJANGO_DEBUG = "True"

# Start server
python manage.py runserver
```

## Environment Configuration

The project automatically detects whether it's running locally or in production:

- **Local Development** (`DEBUG=True`):
  - Uses SQLite database (`db.sqlite3`)
  - Uses local file storage (`media/` folder)
  - Ignores Railway environment variables

- **Production** (`DEBUG=False`):
  - Uses Railway PostgreSQL database
  - Uses Cloudinary for image storage
  - Uses Railway environment variables

## Verification

To check if your local environment is configured correctly:

```bash
python check_local_env.py
```

You should see:
- ✅ Local development environment is configured correctly!
- 📦 Using SQLite database
- 🖼️ Using local file storage

## Troubleshooting

### Issue: Still connecting to Railway database
**Solution**: Set the environment variable in your current shell:
```powershell
$env:DJANGO_DEBUG = "True"
```

### Issue: Images not showing locally
**Solution**: Make sure you have images in the `media/` folder. The local server serves images from the local filesystem.

### Issue: Database connection errors
**Solution**: Make sure `db.sqlite3` exists. If not, run:
```bash
python manage.py migrate
```

## File Structure

```
bethel/
├── db.sqlite3          # Local SQLite database
├── media/              # Local media files
├── start_local.ps1     # PowerShell startup script
├── start_local_fixed.bat # Windows batch startup script
├── start_local_server.py # Python startup script
└── check_local_env.py  # Environment verification script
```

## Development Workflow

1. **Start local server**: Use one of the convenience scripts above
2. **Make changes**: Edit code, templates, etc.
3. **Test locally**: Visit http://127.0.0.1:8000
4. **Commit changes**: `git add . && git commit -m "message"`
5. **Deploy**: `git push` (automatically deploys to Railway)

## Notes

- The local server runs on `http://127.0.0.1:8000`
- Local development uses SQLite, which is faster for development
- Images uploaded locally are stored in the `media/` folder
- The production environment on Railway uses PostgreSQL and Cloudinary 