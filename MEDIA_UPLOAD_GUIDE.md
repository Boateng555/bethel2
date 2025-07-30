# Media Upload Guide

## Overview
Your local media files are stored on your computer, but the live site uses **ImageKit** (cloud storage). They're not connected automatically.

## How It Works

### Local Development
- Images are stored in the `media/` folder on your computer
- Fast access during development
- No internet connection required

### Production
- Images are uploaded to ImageKit cloud storage
- Faster loading for website visitors
- Global CDN for better performance

## Uploading Images

### Through Django Admin
1. Go to http://127.0.0.1:8000/admin/
2. Login with your superuser account
3. Navigate to the model you want to add images to
4. Click "Add" or edit an existing item
5. Upload your image file
6. Save the changes

### What Happens
- **Local**: Image is saved to `media/` folder
- **Production**: Image is uploaded to ImageKit automatically
- Images should now appear with ImageKit URLs

## Setting Up ImageKit (Production Only)

You need ImageKit credentials:
1. Go to [ImageKit Dashboard](https://imagekit.io/dashboard)
2. Sign up for a free account
3. Go to **Developer Options** → **API Keys**
4. Copy these values:
   - **Public Key** (starts with `pk_`)
   - **Private Key** (starts with `private_`)
   - **URL Endpoint** (e.g., `https://ik.imagekit.io/your_username`)

### Set Environment Variables

#### Windows PowerShell
```powershell
$env:IMAGEKIT_PUBLIC_KEY="your_public_key"
$env:IMAGEKIT_PRIVATE_KEY="your_private_key"
$env:IMAGEKIT_URL_ENDPOINT="your_url_endpoint"
```

#### Linux/macOS
```bash
export IMAGEKIT_PUBLIC_KEY="your_public_key"
export IMAGEKIT_PRIVATE_KEY="your_private_key"
export IMAGEKIT_URL_ENDPOINT="your_url_endpoint"
```

### Production Deployment
If you want the live site to automatically use ImageKit:
1. Add these environment variables to your production environment:
   - `IMAGEKIT_PUBLIC_KEY`
   - `IMAGEKIT_PRIVATE_KEY`
   - `IMAGEKIT_URL_ENDPOINT`
2. Deploy your changes
3. New uploads will automatically go to ImageKit

## Migration Options

### Option 1: Manual Upload
- Upload images one by one through the admin interface
- Good for small numbers of images
- Ensures proper organization

### Option 2: Automated Script
- Upload all local files to ImageKit at once
- Use the provided migration scripts
- Faster for large numbers of images

### Option 3: Environment Variables
- Make live site use ImageKit for all uploads
- Existing local files remain local
- New uploads go to cloud storage

## Troubleshooting

### Images Not Showing
- **Local**: Check that images exist in `media/` folder
- **Production**: Check that ImageKit credentials are correct
- **URLs**: Verify image URLs are accessible

### Upload Errors
- **File size**: Check file size limits (ImageKit: 25MB per file)
- **File type**: Ensure file type is supported (jpg, png, gif, etc.)
- **Permissions**: Verify ImageKit credentials have upload permissions

### Performance Issues
- **Slow loading**: ImageKit CDN should be faster than local storage
- **Connection errors**: Check network connectivity
- **ImageKit errors**: Check your credentials are correct 