# Complete ImageKit.io Setup Guide

## Overview
This guide will help you set up ImageKit.io as your image hosting service for the Django project. ImageKit provides better performance, advanced optimization, and a generous free tier.

## What's Been Done
✅ **Completed Steps:**
1. ✅ Installed `django-imagekit` and `imagekitio` dependencies
2. ✅ Added `imagekit` to `INSTALLED_APPS`
3. ✅ Configured `IMAGEKIT_CONFIG` in settings
4. ✅ Created custom `ImageKitStorage` backend
5. ✅ Updated storage logic to prioritize ImageKit over Cloudinary
6. ✅ Added fallback to Cloudinary if ImageKit not configured

## Next Steps (You Need to Do)

### Step 1: Get ImageKit Credentials
1. Go to [imagekit.io](https://imagekit.io)
2. Sign up for a free account
3. Go to **Developer Options** → **API Keys**
4. Copy these values:
   - **Public Key** (starts with `pk_`)
   - **Private Key** (starts with `private_`)
   - **URL Endpoint** (e.g., `https://ik.imagekit.io/your_username`)

### Step 2: Set Environment Variables in Railway

#### Option A: Using Railway CLI
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

#### Option B: Using Railway Dashboard
1. Go to your Railway project dashboard
2. Click on your service
3. Go to the "Variables" tab
4. Add these environment variables:
   - `IMAGEKIT_PUBLIC_KEY` = your public key
   - `IMAGEKIT_PRIVATE_KEY` = your private key
   - `IMAGEKIT_URL_ENDPOINT` = your URL endpoint

### Step 3: Test the Setup
After setting the environment variables, run:
```bash
python test_imagekit_setup.py
```

You should see:
```
✅ ImageKit storage backend initialized successfully
🖼️ Using ImageKit for production
```

### Step 4: Upload Existing Media (Optional)
If you want to migrate existing images to ImageKit:
```bash
python upload_media_to_imagekit.py
```

### Step 5: Deploy to Railway
```bash
git add .
git commit -m "Complete ImageKit integration"
git push origin main
```

## How It Works

### Storage Priority
1. **Development**: Uses local storage (`/media/` folder)
2. **Production with ImageKit**: Uses ImageKit CDN
3. **Production without ImageKit**: Falls back to Cloudinary
4. **No cloud storage**: Falls back to local storage

### Automatic Configuration
- No code changes needed for new uploads
- Existing Cloudinary images continue to work
- New uploads automatically go to ImageKit
- Seamless migration with no downtime

## Benefits of ImageKit

### Performance
- **Global CDN**: Faster image loading worldwide
- **Automatic Optimization**: Compresses images automatically
- **Format Conversion**: Serves WebP/AVIF when supported

### Features
- **Real-time Transformations**: Resize, crop, filter on-the-fly
- **Analytics**: Track image usage and performance
- **Better Free Tier**: 20GB storage vs Cloudinary's 25GB

### Cost
- **Free Tier**: 20GB storage, 20GB bandwidth/month
- **Better Pricing**: More generous limits than Cloudinary
- **No Credit Card Required**: Start with free tier

## Testing Your Setup

### Local Testing
1. Create a `.env` file in your project root:
   ```
   IMAGEKIT_PUBLIC_KEY=your_public_key
   IMAGEKIT_PRIVATE_KEY=your_private_key
   IMAGEKIT_URL_ENDPOINT=your_url_endpoint
   DJANGO_DEBUG=False
   ```

2. Run the test script:
   ```bash
   python test_imagekit_setup.py
   ```

### Production Testing
1. After deployment, check Railway logs for:
   - `🖼️ Using ImageKit for production` - Success!
   - `⚠️ ImageKit not configured, using Cloudinary` - Check credentials

2. Upload a test image through the admin interface
3. Verify the image URL points to ImageKit domain

## Troubleshooting

### Common Issues

**Images not showing:**
- Check that environment variables are set correctly
- Verify ImageKit credentials have proper permissions
- Check Railway logs for storage backend messages

**Upload errors:**
- Ensure API credentials have upload permissions
- Check file size limits (ImageKit free tier: 25MB per file)
- Verify network connectivity

**Slow loading:**
- ImageKit CDN should be faster than local storage
- Check if images are being served from CDN
- Verify ImageKit URL endpoint is correct

### Support
- [ImageKit Documentation](https://docs.imagekit.io/)
- [ImageKit Free Tier Limits](https://imagekit.io/pricing)
- [Django ImageKit Documentation](https://django-imagekit.readthedocs.io/)

## Migration Notes

### From Cloudinary
- Existing Cloudinary images continue to work
- New uploads go to ImageKit
- No data loss during migration
- Gradual migration possible

### From Local Storage
- All new uploads go to ImageKit
- Existing local files remain in `/media/`
- Use upload script to migrate existing files

## Free Tier Limits
ImageKit free tier includes:
- 20 GB storage
- 20 GB bandwidth per month
- 20,000 transformations per month
- 25 MB max file size
- Perfect for most church websites!

## Next Steps After Setup
1. Test image uploads through admin interface
2. Monitor ImageKit dashboard for usage
3. Consider setting up image transformations
4. Configure backup strategy if needed 