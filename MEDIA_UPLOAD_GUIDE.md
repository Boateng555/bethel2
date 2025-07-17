# Media Upload Guide for Live Site

## Why Your Media Isn't Showing on the Live Site

Your local media files are stored on your computer, but the live site uses **Cloudinary** (cloud storage). They're not connected automatically.

## Solution 1: Manual Upload (Easiest)

### Step 1: Access Live Site Admin
- Go to: `https://web-production-158c.up.railway.app/admin/`
- Login with your admin credentials

### Step 2: Upload Media
1. **Churches**: Edit each church → Upload logo
2. **Heroes**: Edit each hero → Upload images/videos  
3. **News**: Edit news items → Upload images
4. **Sermons**: Edit sermons → Upload thumbnails/videos
5. **Ministries**: Edit ministries → Upload images

### Step 3: Check Live Site
- Visit your live site to see the uploaded media
- Images should now appear with Cloudinary URLs

## Solution 2: Automated Upload (Advanced)

### Prerequisites
You need Cloudinary credentials:
1. Go to [Cloudinary Dashboard](https://cloudinary.com/console)
2. Get your credentials:
   - Cloud Name
   - API Key  
   - API Secret

### Set Environment Variables
```bash
# Windows PowerShell
$env:CLOUDINARY_CLOUD_NAME="your_cloud_name"
$env:CLOUDINARY_API_KEY="your_api_key"
$env:CLOUDINARY_API_SECRET="your_api_secret"

# Then run the upload script
python quick_media_upload.py
```

## Solution 3: Railway Environment Variables

If you want the live site to automatically use Cloudinary:

1. Go to your Railway project dashboard
2. Set these environment variables:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
   - `DJANGO_DEBUG=False`

## What Each Solution Does

- **Manual Upload**: Upload files directly via admin interface
- **Automated Script**: Upload all local files to Cloudinary at once
- **Railway Variables**: Make live site use Cloudinary for all uploads

## Recommended Approach

1. **Start with Manual Upload** - It's the most reliable
2. **Use the admin interface** to upload your important media
3. **Check the live site** to confirm everything appears
4. **Consider automated script** for bulk uploads later

## Troubleshooting

- **Images still not showing**: Clear browser cache
- **Upload errors**: Check file size limits
- **Admin access issues**: Verify your admin credentials
- **Cloudinary errors**: Check your credentials are correct

## File Types Supported

- **Images**: JPG, PNG, GIF, WebP
- **Videos**: MP4, AVI, MOV, WebM
- **Max file size**: Usually 100MB per file 