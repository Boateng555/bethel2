# 🖼️ Railway Media Upload Guide

## Problem
The live site shows placeholder text instead of actual images because the production database doesn't have the media files uploaded to ImageKit.

## Solution
We need to upload all local media files to ImageKit and update the database URLs.

## Step 1: Prepare Media Files
Run this locally to copy all media files:
```bash
python copy_media_for_railway.py
```

## Step 2: Deploy to Railway
Commit and push the changes:
```bash
git add .
git commit -m "Add media upload management command"
git push origin main
```

## Step 3: Run Upload Command on Railway
Once deployed, run this command on Railway:

### Option A: Using Railway CLI (Recommended)
```bash
railway run python manage.py upload_media_to_imagekit
```

### Option B: Using Railway Dashboard
1. Go to your Railway project dashboard
2. Click on your service
3. Go to "Deployments" tab
4. Click on the latest deployment
5. Go to "Logs" tab
6. Click "Open Shell"
7. Run: `python manage.py upload_media_to_imagekit`

### Option C: Dry Run First
To see what would be uploaded without actually uploading:
```bash
railway run python manage.py upload_media_to_imagekit --dry-run
```

## Step 4: Verify Upload
After the upload completes:
1. Check your ImageKit dashboard to see uploaded files
2. Visit your live site to see images loading
3. Check church logos, event images, hero media, etc.

## Troubleshooting

### If upload fails:
1. **Check environment variables** on Railway:
   - `IMAGEKIT_PUBLIC_KEY`
   - `IMAGEKIT_PRIVATE_KEY` 
   - `IMAGEKIT_URL_ENDPOINT`

2. **Check ImageKit credentials**:
   - Verify your ImageKit account is active
   - Check API key permissions

3. **Check file permissions**:
   - Ensure media files are readable
   - Check file sizes (ImageKit has limits)

### If images still don't show:
1. **Clear browser cache**
2. **Check browser console** for errors
3. **Verify ImageKit URLs** in database
4. **Check CORS settings** if needed

## Manual Upload Alternative
If the automated upload doesn't work, you can manually upload files through the Django admin:
1. Go to your live site admin
2. Edit each church/event/ministry
3. Upload images through the admin interface
4. Save changes

## Expected Results
After successful upload:
- ✅ Church logos display properly
- ✅ Event images show correctly
- ✅ Hero media carousel works
- ✅ All media files load from ImageKit URLs
- ✅ No more placeholder text

## Files Created
- `core/management/commands/upload_media_to_imagekit.py` - Django management command
- `copy_media_for_railway.py` - Local media preparation script
- `RAILWAY_MEDIA_UPLOAD_GUIDE.md` - This guide 