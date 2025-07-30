# ImageKit.io Setup Guide

## Overview
ImageKit.io is a powerful image optimization and CDN service that will help you serve images faster and more efficiently.

## Why ImageKit?

### Performance Benefits
- **Global CDN**: Faster image loading worldwide
- **Automatic Optimization**: Compresses images automatically
- **Format Conversion**: Serves WebP/AVIF when supported

### Features
- **Real-time Transformations**: Resize, crop, filter on-the-fly
- **Analytics**: Track image usage and performance
- **Better Free Tier**: 20GB storage

### Cost Benefits
- **Free Tier**: 20GB storage, 20GB bandwidth/month
- **Better Pricing**: More generous limits
- **No Credit Card Required**: Start with free tier

## Step 1: Create ImageKit Account
1. Go to [imagekit.io](https://imagekit.io)
2. Click "Get Started Free"
3. Sign up with your email
4. Verify your email address

## Step 2: Get Your Credentials
1. Log into your ImageKit Dashboard
2. Go to **Developer Options** → **API Keys**
3. Note down these values:
   - **Public Key** (e.g., `pk_abc123def456`)
   - **Private Key** (e.g., `private_xyz789uvw012`)
   - **URL Endpoint** (e.g., `https://ik.imagekit.io/your_username`)

## Step 3: Set Environment Variables in Production

### Option A: Using CLI
```bash
# Install CLI if you haven't already
npm install -g @deployment/cli

# Login to deployment platform
deployment login

# Link to your project
deployment link

# Set environment variables
deployment variables set IMAGEKIT_PUBLIC_KEY=your_public_key
deployment variables set IMAGEKIT_PRIVATE_KEY=your_private_key
deployment variables set IMAGEKIT_URL_ENDPOINT=your_url_endpoint
```

### Option B: Using Deployment Dashboard
1. Go to your deployment project dashboard
2. Click on your service
3. Go to the "Variables" tab
4. Add these environment variables:
   - `IMAGEKIT_PUBLIC_KEY` = your public key
   - `IMAGEKIT_PRIVATE_KEY` = your private key
   - `IMAGEKIT_URL_ENDPOINT` = your URL endpoint

## Step 4: Upload Media to ImageKit
After setting the environment variables, run the upload script:

```bash
# Set environment variables locally (for testing)
$env:IMAGEKIT_PUBLIC_KEY="your_public_key"
$env:IMAGEKIT_PRIVATE_KEY="your_private_key"
$env:IMAGEKIT_URL_ENDPOINT="your_url_endpoint"

# Run the upload script
python upload_media_to_imagekit.py
```

## Step 5: Deploy to Production
```bash
git add .
git commit -m "Switch to ImageKit.io for media storage"
git push origin main
```

Your deployment platform will automatically redeploy with the new ImageKit configuration.

## Step 6: Verify Setup
After deployment, check your deployment logs to see:
- `🖼️ Using ImageKit for production` - Success!
- `⚠️ ImageKit not configured, using local storage` - Check your environment variables

## How It Works
- **Development**: Uses local storage (`/media/` folder)
- **Production**: Uses ImageKit CDN for faster image delivery
- **Automatic**: No code changes needed, just environment variables

## Benefits of ImageKit
- **CDN**: Faster image loading worldwide
- **Optimization**: Automatic image optimization and compression
- **Transformations**: On-the-fly image resizing, cropping, etc.
- **Analytics**: Track image usage and performance
- **Better Free Tier**: 20GB storage

## Testing
To test locally with ImageKit:
1. Create a `.env` file in your project root
2. Add your ImageKit credentials:
   ```
   IMAGEKIT_PUBLIC_KEY=your_public_key
   IMAGEKIT_PRIVATE_KEY=your_private_key
   IMAGEKIT_URL_ENDPOINT=your_url_endpoint
   DJANGO_DEBUG=False
   ```
3. Run the upload script: `python upload_media_to_imagekit.py`

## Troubleshooting
- **Images not showing**: Check that environment variables are set correctly
- **Upload errors**: Verify API credentials have upload permissions
- **Slow loading**: ImageKit CDN should be faster than local storage

## Free Tier Limits
ImageKit free tier includes:
- 20 GB storage
- 20 GB bandwidth per month
- 20,000 transformations per month
- 25 MB max file size
- Perfect for most church websites!

## Migration

### From Local Storage
- Existing local images continue to work
- New uploads go to ImageKit
- Use management commands to migrate existing images 