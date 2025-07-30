# 🖼️ ImageKit Production Setup Guide

## Overview
This guide will help you set up ImageKit.io for production deployment of your Bethel Church website. ImageKit provides better performance, CDN delivery, and image optimization.

## Why ImageKit?
- **Better Performance**: Global CDN with faster image loading
- **Image Optimization**: Automatic compression and format conversion
- **Real-time Transformations**: Resize, crop, and transform images on-the-fly
- **Free Tier**: 20GB storage, 20GB bandwidth per month
- **Better Pricing**: More generous limits than other services

## Step 1: Get ImageKit Credentials

### 1.1 Sign Up for ImageKit
1. Go to [imagekit.io](https://imagekit.io)
2. Click "Get Started Free"
3. Sign up with your email
4. Verify your email address

### 1.2 Get Your API Keys
1. Log into your ImageKit Dashboard
2. Go to **Developer Options** → **API Keys**
3. Note down these values:
   - **Public Key** (e.g., `pk_abc123def456`)
   - **Private Key** (e.g., `private_xyz789uvw012`)
   - **URL Endpoint** (e.g., `https://ik.imagekit.io/your_username`)

## Step 2: Set Up Environment Variables

### Option A: Using Deployment Dashboard (Recommended)
1. Go to your deployment project dashboard
2. Click on your service
3. Go to the **Variables** tab
4. Add these environment variables:

```
IMAGEKIT_PUBLIC_KEY=your_public_key_here
IMAGEKIT_PRIVATE_KEY=your_private_key_here
IMAGEKIT_URL_ENDPOINT=your_url_endpoint_here
```

### Option B: Using CLI
```bash
# Install CLI
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

## Step 3: Deploy to Production

### 3.1 Commit Your Changes
```bash
git add .
git commit -m "Add ImageKit production setup"
git push origin main
```

### 3.2 Monitor Deployment
1. Your deployment platform will automatically redeploy
2. Check the deployment logs
3. Look for: `🖼️ Using ImageKit for storage`

## Step 4: Test the Setup

### 4.1 Check Deployment Logs
In your deployment dashboard, check the logs for:
- ✅ `🖼️ Using ImageKit for storage` - Success!
- ❌ `⚙️ Using local storage (ImageKit keys missing)` - Check environment variables

### 4.2 Test Image Upload
1. Visit your live site: `https://your-domain.com/admin/`
2. Log in to Django admin
3. Upload an image to any model (Church, Event, etc.)
4. Check that the image URL points to ImageKit domain (`ik.imagekit.io`)

### 4.3 Verify Image Loading
1. Visit your live site
2. Check that images load correctly
3. Verify image URLs contain `ik.imagekit.io`

## Step 5: Upload Existing Media (Optional)

If you want to migrate existing images to ImageKit:

### 5.1 Run Upload Command
```bash
# On Production (using CLI)
deployment run python manage.py upload_media_to_imagekit

# Or in deployment dashboard shell
python manage.py upload_media_to_imagekit
```

### 5.2 Dry Run First
```bash
# See what would be uploaded without actually uploading
python manage.py upload_media_to_imagekit --dry-run
```

## Troubleshooting

### Common Issues

**Images not showing:**
- Check that environment variables are set correctly in your deployment
- Verify ImageKit credentials have proper permissions
- Check deployment logs for storage backend messages

**Upload errors:**
- Ensure API credentials have upload permissions
- Check file size limits (ImageKit free tier: 25MB per file)
- Verify network connectivity

**Slow loading:**
- ImageKit CDN should be faster than local storage
- Check if images are being served from CDN
- Verify ImageKit URL endpoint is correct

### Environment Variable Checklist
- [ ] `IMAGEKIT_PUBLIC_KEY` is set
- [ ] `IMAGEKIT_PRIVATE_KEY` is set  
- [ ] `IMAGEKIT_URL_ENDPOINT` is set
- [ ] All variables are in deployment dashboard
- [ ] No extra spaces or quotes in values

### Testing Commands
```bash
# Test storage configuration
python test_storage.py

# Test image uploads
python test_image_upload.py

# Test ImageKit setup
python setup_imagekit_production.py
```

## Benefits of ImageKit

### Performance
- **Global CDN**: Faster image loading worldwide
- **Automatic Optimization**: Compresses images automatically
- **Format Conversion**: Serves WebP/AVIF when supported

### Features
- **Real-time Transformations**: Resize, crop, filter on-the-fly
- **Analytics**: Track image usage and performance
- **Better Free Tier**: 20GB storage

### Cost
- **Free Tier**: 20GB storage, 20GB bandwidth/month
- **Better Pricing**: More generous limits
- **No Credit Card Required**: Start with free tier

## Free Tier Limits
ImageKit free tier includes:
- 20 GB storage
- 20 GB bandwidth per month
- 20,000 transformations per month
- 25 MB max file size
- Perfect for most church websites!

## Support Resources
- [ImageKit Documentation](https://docs.imagekit.io/)
- [ImageKit Free Tier Limits](https://imagekit.io/pricing)
- [Django ImageKit Documentation](https://django-imagekit.readthedocs.io/)

## Next Steps After Setup
1. Test image uploads through admin interface
2. Monitor ImageKit dashboard for usage
3. Consider setting up image transformations
4. Configure backup strategy if needed
5. Monitor performance improvements

---

**Need Help?** If you encounter any issues during setup, check the troubleshooting section above or refer to the ImageKit documentation. 