# ImageKit.io Setup Guide

## Overview
ImageKit.io is a powerful image optimization and CDN service that will help you serve images faster and more efficiently than Cloudinary.

## Why ImageKit.io?
- **Better Performance**: Faster CDN with global edge locations
- **Advanced Optimization**: Automatic image compression and format conversion
- **Real-time Transformations**: Resize, crop, and transform images on-the-fly
- **Free Tier**: 20GB storage, 20GB bandwidth per month
- **Better Pricing**: More generous limits than Cloudinary

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
railway variables set IMAGEKIT_PUBLIC_KEY=your_public_key
railway variables set IMAGEKIT_PRIVATE_KEY=your_private_key
railway variables set IMAGEKIT_URL_ENDPOINT=your_url_endpoint
```

### Option B: Using Railway Dashboard
1. Go to your Railway project dashboard
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

## Step 5: Deploy to Railway
```bash
git add .
git commit -m "Switch to ImageKit.io for media storage"
git push origin main
```

Railway will automatically redeploy with the new ImageKit configuration.

## Step 6: Verify Setup
After deployment, check your Railway logs to see:
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
- **Better Free Tier**: 20GB storage vs Cloudinary's 25GB

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
- Perfect for most church websites!

## Migration from Cloudinary
If you're switching from Cloudinary:
1. Your existing Cloudinary images will continue to work
2. New uploads will go to ImageKit
3. You can gradually migrate existing images using the upload script
4. No downtime or data loss during migration 