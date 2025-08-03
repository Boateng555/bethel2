# 🌍 Global Hero Management Guide

## Overview
The Global Hero feature allows you to set a hero banner that appears on the main global Bethel website homepage. This hero is separate from individual church heroes and is managed by Global Admins.

## ✅ How It Works

### 1. **Global Hero Selection**
- Navigate to **Django Admin** → **Global Settings**
- In the **Global Settings** section, you'll see the **Global Hero** dropdown
- Select any existing hero banner to make it the global hero
- Save the settings to apply the change

### 2. **Creating Global Heroes**
- Navigate to **Django Admin** → **Heroes** (Global Admin section)
- Click **"Add Hero"** to create a new global hero
- Fill in the required fields:
  - **Title**: The main headline
  - **Subtitle**: Supporting text
  - **Background Type**: Choose between Image or Video
  - **Background Image/Video**: Upload your media
  - **Button Settings**: Configure call-to-action buttons
  - **Status**: Set as Active to make it available

### 3. **Adding Multiple Media Items**
- After creating a hero, you can add multiple images/videos
- In the **Hero Media** section, add multiple media items
- Set the **Order** field to control display sequence
- Images and videos will appear in a carousel on the homepage

## 🎯 Step-by-Step Instructions

### Step 1: Create a Global Hero
1. Go to **Django Admin** → **Heroes**
2. Click **"Add Hero"**
3. Fill in the hero details:
   ```
   Title: "Welcome to Bethel Prayer Ministry International"
   Subtitle: "Join us in spreading the gospel worldwide"
   Background Type: Image
   Background Image: [Upload your image]
   Primary Button Text: "Find a Church"
   Primary Button Link: "/church-list"
   Secondary Button Text: "Watch Online"
   Secondary Button Link: "/watch"
   Is Active: ✓ (checked)
   Order: 1
   ```
4. Click **"Save"**

### Step 2: Add Multiple Media Items
1. After saving, you'll see the **Hero Media** section
2. Click **"Add another Hero Media"**
3. Upload additional images or videos
4. Set the order for each item (1, 2, 3, etc.)
5. Save again

### Step 3: Set as Global Hero
1. Go to **Django Admin** → **Global Settings**
2. In the **Global Settings** section, find **Global Hero**
3. Select your newly created hero from the dropdown
4. Click **"Save"**

### Step 4: Verify on Website
1. Visit your website homepage
2. The global hero should now be displayed
3. If you added multiple media items, they should appear in a carousel

## 🔧 Multiple Heroes Management

### Creating Multiple Global Heroes
You can create as many global heroes as you want:

1. **Create Hero 1**: "Welcome Message"
2. **Create Hero 2**: "Special Event"
3. **Create Hero 3**: "Ministry Highlight"

### Switching Between Heroes
- Go to **Global Settings**
- Change the **Global Hero** selection
- Save to immediately switch the displayed hero

### Hero Organization Tips
- Use descriptive titles for easy identification
- Set different orders for organization
- Keep inactive heroes for future use
- Use the **Order** field to organize your hero list

## 📱 Hero Media Best Practices

### Image Requirements
- **Recommended Size**: 1920x1080 pixels (16:9 ratio)
- **Format**: JPG, PNG, or WebP
- **File Size**: Under 2MB for fast loading
- **Quality**: High quality, professional images

### Video Requirements
- **Format**: MP4
- **Duration**: 10-30 seconds (loop automatically)
- **File Size**: Under 10MB
- **Quality**: 720p or 1080p

### Content Guidelines
- Use high-quality, professional images
- Ensure text is readable over backgrounds
- Keep button text short and clear
- Test on different screen sizes

## 🎨 Customization Options

### Button Configuration
- **Primary Button**: Main call-to-action (e.g., "Find a Church")
- **Secondary Button**: Secondary action (e.g., "Watch Online")
- **Custom Links**: Point to any page on your site

### Background Options
- **Image Background**: Static image with overlay text
- **Video Background**: Dynamic video with overlay text
- **Multiple Media**: Carousel of images/videos

### Display Settings
- **Active/Inactive**: Control visibility
- **Order**: Control display sequence
- **Auto-play**: Videos play automatically
- **Loop**: Videos loop continuously

## 🔍 Troubleshooting

### Hero Not Appearing
1. Check if the hero is set as **Active**
2. Verify it's selected in **Global Settings**
3. Clear browser cache
4. Check if the hero has media content

### Media Not Loading
1. Verify file formats are supported
2. Check file sizes are within limits
3. Ensure media files are properly uploaded
4. Check server storage configuration

### Performance Issues
1. Optimize image sizes
2. Compress video files
3. Use WebP format for images
4. Consider CDN for media delivery

## 📊 Testing Checklist

Before going live, verify:
- [ ] Hero appears on homepage
- [ ] All media items load correctly
- [ ] Buttons link to correct pages
- [ ] Responsive design works on mobile
- [ ] Video autoplay works (if applicable)
- [ ] Carousel navigation works (if multiple items)
- [ ] Loading times are acceptable

## 🚀 Advanced Features

### Hero Rotation
- Create multiple heroes
- Switch between them periodically
- Use for seasonal content or special events

### A/B Testing
- Create different hero versions
- Test different messages or designs
- Monitor engagement metrics

### Content Scheduling
- Plan hero content in advance
- Coordinate with church events
- Maintain consistent branding

---

## 💡 Pro Tips

1. **Keep it Simple**: Don't overcrowd the hero with too much text
2. **High Quality**: Always use professional, high-resolution images
3. **Mobile First**: Ensure your hero looks great on mobile devices
4. **Fast Loading**: Optimize media files for quick loading
5. **Consistent Branding**: Maintain your church's visual identity
6. **Regular Updates**: Keep content fresh and relevant
7. **Call to Action**: Make buttons clear and actionable

---

**Need Help?** Contact your system administrator or refer to the technical documentation for advanced configuration options. 