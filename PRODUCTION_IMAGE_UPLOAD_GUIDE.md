# 🖼️ Production Image Upload Guide

## The Problem
When you upload images through the local admin interface (`/local-admin/`), they only save to your local database. The production site on Railway has a separate database, so these images don't appear on the live site.

## The Solution
Upload images directly through the **production admin interface** on Railway.

## Step 1: Access Production Admin
1. Go to your live site: `https://web-production-158c.up.railway.app/`
2. Add `/admin/` to the URL: `https://web-production-158c.up.railway.app/admin/`
3. Login with your admin credentials

## Step 2: Upload Images for Each Content Type

### For Churches:
1. Go to **Churches** section
2. Click on a church to edit it
3. Upload the church logo in the **Logo** field
4. Click **Save**

### For News:
1. Go to **News** section
2. Click on a news item to edit it (or create a new one)
3. Upload an image in the **Image** field
4. Click **Save**

### For Ministries:
1. Go to **Ministries** section
2. Click on a ministry to edit it (or create a new one)
3. Upload an image in the **Image** field
4. Click **Save**

### For Sermons:
1. Go to **Sermons** section
2. Click on a sermon to edit it (or create a new one)
3. Upload a thumbnail in the **Thumbnail** field
4. Upload a video in the **Video** field (if applicable)
5. Click **Save**

### For Events:
1. Go to **Events** section
2. Click on an event to edit it (or create a new one)
3. Upload an image in the **Image** field
4. Click **Save**

### For Hero Media:
1. Go to **Heroes** section
2. Click on a hero to edit it (or create a new one)
3. Upload images/videos in the **Hero Media** section
4. Click **Save**

## Step 3: Verify Uploads
1. Visit your live site: `https://web-production-158c.up.railway.app/`
2. Check that images are now displaying correctly
3. Test on different devices and browsers

## Alternative: Use Local Admin for Content, Production Admin for Images

### Option A: Content + Images Together
1. Create/edit content through local admin (`/local-admin/`)
2. Copy the content details (title, description, etc.)
3. Go to production admin (`https://web-production-158c.up.railway.app/admin/`)
4. Create the same content and upload images there

### Option B: Separate Content and Images
1. Create all content through local admin
2. Upload only images through production admin
3. Link the images to existing content

## Troubleshooting

### If images still don't show:
1. **Clear browser cache** - Press Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
2. **Try incognito/private mode** to bypass cache
3. **Check browser console** for errors (F12 → Console tab)
4. **Verify Cloudinary URLs** - Images should have URLs starting with `https://res.cloudinary.com/`

### If you can't access production admin:
1. **Check your admin credentials** - Make sure you have admin access
2. **Contact support** if you forgot your password
3. **Check Railway logs** for any deployment issues

## Best Practices

1. **Upload images first** - Upload images before creating content
2. **Use appropriate sizes** - Images should be reasonable sizes (under 5MB)
3. **Use descriptive names** - Name your image files descriptively
4. **Test regularly** - Check your live site after each upload
5. **Backup important images** - Keep local copies of important images

## Quick Checklist

- [ ] Access production admin: `https://web-production-158c.up.railway.app/admin/`
- [ ] Upload church logos
- [ ] Upload news images
- [ ] Upload ministry images
- [ ] Upload sermon thumbnails/videos
- [ ] Upload event images
- [ ] Upload hero media
- [ ] Test live site
- [ ] Test on mobile devices
- [ ] Clear browser cache if needed

## Need Help?

If you're still having issues:
1. Check the Railway deployment logs
2. Verify Cloudinary credentials are set correctly
3. Contact support with specific error messages 