# Hero Media Management Guide

## 🎯 Overview

The hero media system has been enhanced to allow you to add multiple images and videos to your hero sections, creating beautiful carousels that automatically cycle through your media content.

## ✨ What's New

- **Multiple Media Items**: You can now add up to 10 images/videos per hero
- **Easy Admin Interface**: Add 3 new media items at once in the admin
- **Better Organization**: Set display order for your media items
- **Enhanced Forms**: Clear labels and help text for better user experience

## 🚀 How to Add Hero Media

### Step 1: Access the Admin
1. Go to your Django Admin panel
2. Navigate to **"Local Heroes"** (for church-specific heroes)
3. Click on an existing hero or create a new one

### Step 2: Add Media Items
1. Scroll down to the **"Hero Media Items"** section
2. You'll see 3 empty forms ready for new media
3. For each media item:
   - **Hero Image**: Upload an image (recommended: 1920x1080px)
   - **Hero Video**: Upload a video file (MP4 recommended)
   - **Display Order**: Set the order (1 = first, 2 = second, etc.)

### Step 3: Save and View
1. Click **"Save"** to save your changes
2. Visit your church website to see the carousel in action

## 📋 Media Guidelines

### Images
- **Recommended size**: 1920x1080px (16:9 aspect ratio)
- **Supported formats**: JPG, PNG, GIF
- **File size**: Keep under 5MB for fast loading

### Videos
- **Recommended format**: MP4
- **Recommended resolution**: 1920x1080px
- **Duration**: 10-30 seconds work best for hero sections
- **File size**: Keep under 50MB

### Display Order
- **1**: First item shown in carousel
- **2**: Second item shown
- **3**: Third item shown
- And so on...

## 🎨 Carousel Features

### Automatic Cycling
- Media items automatically cycle through
- Smooth transitions between items
- Responsive design for all devices

### Priority System
- Videos take priority over images
- If both image and video are uploaded, video will be shown

### Fallback System
- If no hero media is added, falls back to hero background image/video
- Ensures your hero always has content

## 🔧 Admin Tips

### Adding More Media
- If you need more than 3 new items, save first, then edit again
- You can add up to 10 total media items per hero

### Reordering Media
- Change the "Display Order" field to reorder items
- Lower numbers appear first

### Deleting Media
- Use the delete checkbox next to each media item
- Or leave fields empty and save to remove items

## 🐛 Troubleshooting

### Media Not Showing
1. Check that the hero is **Active**
2. Verify media files are uploaded correctly
3. Ensure display order is set properly
4. Check file permissions on uploaded files

### Carousel Not Working
1. Make sure you have multiple media items
2. Check that media files are accessible
3. Verify JavaScript is enabled in browser

### Upload Issues
1. Check file size limits (5MB for images, 50MB for videos)
2. Ensure file format is supported
3. Check server storage permissions

## 📱 Mobile Optimization

### Responsive Design
- Carousel automatically adapts to screen size
- Touch-friendly navigation on mobile devices
- Optimized loading for slower connections

### Performance Tips
- Compress images before uploading
- Use appropriate video compression
- Consider mobile data usage for videos

## 🎯 Best Practices

### Content Strategy
- Use high-quality, professional images
- Keep videos short and engaging
- Maintain consistent branding
- Update content regularly

### Technical Optimization
- Optimize images for web (compress, resize)
- Use appropriate video formats and compression
- Test on different devices and browsers
- Monitor loading times

## 🔄 Event Hero Media

The same enhanced system is available for events:

1. Go to **"Events"** in the admin
2. Edit an event
3. Use the **"Event Media"** section
4. Add multiple images/videos for event carousels

## 📞 Support

If you encounter any issues:

1. Check this guide first
2. Verify file formats and sizes
3. Test with different browsers
4. Contact support if problems persist

---

**Happy creating! 🎉**

Your hero sections will now be more engaging and dynamic with multiple media items cycling through automatically. 