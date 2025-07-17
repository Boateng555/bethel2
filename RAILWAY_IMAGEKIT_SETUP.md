# Railway ImageKit Setup

## Quick Setup for Railway

### Step 1: Go to Railway Dashboard
1. Visit [railway.app](https://railway.app)
2. Login to your account
3. Find your Bethel project

### Step 2: Add Environment Variables
1. Click on your project
2. Go to the **Variables** tab
3. Add these 3 environment variables:

```
IMAGEKIT_PUBLIC_KEY=public_IEJhHLyqZ2J9lqJFcIZF2AOFJKQ=
IMAGEKIT_PRIVATE_KEY=private_ODyStF26VuvPNYuHJyYYoeQePkU=
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/144671b7r
```

### Step 3: Deploy
Railway will automatically redeploy when you add the variables.

### Step 4: Check Your Site
Visit: https://web-production-158c.up.railway.app/

## What This Does
- Configures your site to use ImageKit for media storage
- Your existing Cloudinary images will continue to work
- New uploads will go to ImageKit
- Better performance and reliability

## Next Steps
Once the environment variables are set, we can:
1. Upload your existing media to ImageKit
2. Test the new setup
3. Optimize image delivery

## Troubleshooting
If images don't show:
1. Clear browser cache (Ctrl+F5)
2. Check Railway logs for errors
3. Verify environment variables are set correctly 