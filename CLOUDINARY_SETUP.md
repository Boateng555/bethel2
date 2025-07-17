# Cloudinary Setup Guide

## Overview
Your Django project is already configured to use Cloudinary for media file storage in production. This guide will help you set it up.

## Current Configuration
Your `settings.py` is already configured to:
- Use local storage for development (DEBUG=True)
- Automatically switch to Cloudinary for production when environment variables are set
- Fall back to local storage if Cloudinary credentials are missing

## Step 1: Create Cloudinary Account
1. Go to [cloudinary.com](https://cloudinary.com)
2. Sign up for a free account
3. Verify your email

## Step 2: Get Your Credentials
1. Log into your Cloudinary Dashboard
2. Note down these values:
   - **Cloud Name** (e.g., `your-cloud-name`)
   - **API Key** (e.g., `123456789012345`)
   - **API Secret** (e.g., `abcdefghijklmnopqrstuvwxyz`)

## Step 3: Set Environment Variables in Railway

### Option A: Using Railway CLI
```bash
# Install Railway CLI if you haven't already
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Set environment variables
railway variables set CLOUDINARY_CLOUD_NAME=your-cloud-name
railway variables set CLOUDINARY_API_KEY=your-api-key
railway variables set CLOUDINARY_API_SECRET=your-api-secret
```

### Option B: Using Railway Dashboard
1. Go to your Railway project dashboard
2. Click on your service
3. Go to the "Variables" tab
4. Add these environment variables:
   - `CLOUDINARY_CLOUD_NAME` = your cloud name
   - `CLOUDINARY_API_KEY` = your API key
   - `CLOUDINARY_API_SECRET` = your API secret

## Step 4: Deploy
After setting the environment variables, deploy your project:
```bash
git add .
git commit -m "Configure Cloudinary for production"
git push
```

Railway will automatically redeploy with the new environment variables.

## Step 5: Verify Setup
After deployment, check your Railway logs to see:
- `☁️ Using Cloudinary storage for production` - Success!
- `⚠️ Cloudinary not configured, using local storage` - Check your environment variables

## How It Works
- **Development**: Uses local storage (`/media/` folder)
- **Production**: Uses Cloudinary CDN for faster image delivery
- **Automatic**: No code changes needed, just environment variables

## Benefits of Cloudinary
- **CDN**: Faster image loading worldwide
- **Optimization**: Automatic image optimization
- **Transformations**: On-the-fly image resizing, cropping, etc.
- **Backup**: Automatic backup of your media files
- **Analytics**: Track image usage and performance

## Testing
To test locally with Cloudinary:
1. Create a `.env` file in your project root
2. Add your Cloudinary credentials:
   ```
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   DJANGO_DEBUG=False
   ```
3. Restart your Django server

## Troubleshooting
- **Images not showing**: Check that environment variables are set correctly
- **Upload errors**: Verify API credentials have upload permissions
- **Slow loading**: Cloudinary CDN should be faster than local storage

## Free Tier Limits
Cloudinary free tier includes:
- 25 GB storage
- 25 GB bandwidth per month
- 25,000 transformations per month
- Perfect for most church websites! 