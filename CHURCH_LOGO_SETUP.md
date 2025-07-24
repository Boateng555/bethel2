# Church Logo Setup Guide

## Overview
The Bethel platform now supports multiple levels of logo management:

1. **Global Navigation Logo**: A single logo that appears on ALL church pages (managed by global admins)
2. **Individual Church Navigation Logo**: Specific to each church (overrides global logo if set)
3. **Regular Church Logo**: Used for cards, about pages, and general display

## Priority System
The navigation logo priority is:
1. **Global Navigation Logo** (if set) - appears on ALL churches
2. **Individual Church Navigation Logo** (if set) - appears only on that church
3. **Individual Church Regular Logo** (if set) - appears only on that church
4. **Default Bethel Logo** - fallback for all churches

## How to Add a Custom Church Logo

### For Global Admins (Global Navigation Logo):
1. Go to the Django Admin panel
2. Navigate to **Core > Global Settings**
3. Upload a logo in the **Global Navigation Logo** field
4. This logo will appear on ALL church pages
5. Save the changes

### For Global Admins (Individual Church Logos):
1. Go to the Django Admin panel
2. Navigate to **Core > Churches**
3. Select the church you want to add a logo to
4. You'll see two logo sections:
   - **Church Information**: Contains the regular logo field and preview
   - **Navigation Logo**: Contains the navigation-specific logo field and preview

### For Local Church Admins:
1. Go to your church's local admin panel (`/local-admin/`)
2. Navigate to **Churches** and select your church
3. Upload logos in both sections:
   - **Logo**: For general use (cards, about pages, etc.)
   - **Navigation Logo**: Specifically for the navigation bar (will override global logo for this church only)
4. Save the changes

**Note**: Local church admins cannot change the global navigation logo. Only global admins can manage the global logo.

## Logo Requirements

### Regular Logo (General Use):
- **Format**: PNG, JPG, or JPEG
- **Size**: 200x200 pixels or larger (will be automatically resized)
- **Shape**: Any shape (will be displayed as appropriate for the context)
- **Background**: Transparent or solid color
- **File Size**: Under 2MB
- **Use**: Cards, about pages, general display

### Global Navigation Logo (All Churches):
- **Format**: PNG, JPG, or JPEG
- **Size**: 200x200 pixels or larger (will be automatically resized)
- **Shape**: Square or circular (will be displayed as a circle)
- **Background**: Transparent or solid color
- **File Size**: Under 2MB
- **Use**: Navigation bar on ALL church pages
- **Display**: 32x32 pixels in navigation bar
- **Management**: Only global admins can change this

### Individual Church Navigation Logo:
- **Format**: PNG, JPG, or JPEG
- **Size**: 200x200 pixels or larger (will be automatically resized)
- **Shape**: Square or circular (will be displayed as a circle)
- **Background**: Transparent or solid color
- **File Size**: Under 2MB
- **Use**: Navigation bar for specific church only
- **Display**: 32x32 pixels in navigation bar
- **Override**: Takes precedence over global logo for that church only

### Display Priority:
1. **Global Navigation Logo** (if set) - appears on ALL churches
2. **Individual Church Navigation Logo** (if set) - overrides global for that church only
3. **Individual Church Regular Logo** (if no navigation logo) - appears in navigation bar
4. **Default Bethel Logo** (if no custom logos) - appears in navigation bar

## Technical Details

### File Storage:
- Global navigation logos are stored in the `global/nav_logos/` directory
- Regular logos are stored in the `churches/logos/` directory
- Individual navigation logos are stored in the `churches/nav_logos/` directory
- Files are automatically optimized and resized for web use
- The system supports both local file storage and cloud storage (ImageKit)

### Code Implementation:
- The `GlobalSettings` model manages global navigation logos
- The `logo` field is part of the `Church` model for general use
- The `nav_logo` field is specifically for individual church navigation bar display
- Templates check for `global_settings.global_nav_logo` first, then `church.nav_logo`, then `church.logo`, then default Bethel logo
- Methods: `global_settings.get_global_nav_logo_url()`, `church.get_logo_url()`, and `church.get_nav_logo_url()`

## Troubleshooting

### Logo Not Displaying:
1. Check that the logo file was uploaded successfully
2. Verify the file format is supported (PNG, JPG, JPEG)
3. Ensure the file size is under 2MB
4. Check browser cache and refresh the page

### Logo Looks Distorted:
1. Upload a square image (1:1 aspect ratio)
2. Use a high-resolution image (200x200 pixels or larger)
3. The system will automatically crop and resize the image

### Admin Preview Not Working:
1. Check that the logo file exists in the media directory
2. Verify file permissions are correct
3. Ensure the media files are being served properly

## Support
If you encounter any issues with logo upload or display, please contact the system administrator. 