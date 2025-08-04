# Global Hero Settings Guide

## Overview

The Global Settings page now includes comprehensive hero management functionality. This allows you to configure the hero banner that appears on the main global site homepage.

## What's New

### 1. Dedicated Global Hero Settings Section
- **Global Hero**: Select which hero banner to display on the main global site
- **Hero Preview**: Visual preview of the selected hero with title, subtitle, and background media
- **Rotation Settings**: Configure automatic hero rotation
- **Fallback Options**: Set fallback behavior when selected hero is inactive

### 2. Enhanced Hero Management Fields

#### Global Hero Selection
- Dropdown shows only global heroes (no church association)
- Automatically filtered to show available global heroes
- Clear help text explaining the purpose

#### Hero Rotation Settings
- **Enable Rotation**: Toggle automatic rotation of multiple heroes
- **Rotation Interval**: Set how often heroes rotate (minimum 3 seconds)
- **Fallback Enabled**: Show fallback hero if selected hero is inactive

#### Visual Preview
- Shows hero title and subtitle
- Displays background image or video indicator
- Shows hero status (active/inactive) and order
- Styled preview with proper formatting

## How to Use

### 1. Access Global Settings
1. Go to Django Admin
2. Navigate to "Settings" section
3. Click on "Global Settings"

### 2. Configure Global Hero
1. In the "Global Hero Settings" section:
   - Select a hero from the dropdown (only global heroes shown)
   - View the preview to see how it will appear
   - Configure rotation settings if desired

### 3. Hero Rotation (Optional)
1. Check "Enable rotation" to activate automatic hero rotation
2. Set rotation interval (in seconds, minimum 3)
3. Enable fallback to show alternative hero if main hero is inactive

### 4. Save Changes
- Click "Save" to apply your hero settings
- Changes will be reflected on the main global site homepage

## Creating Global Heroes

To create heroes that can be used in Global Settings:

1. Go to "Heroes" section in admin
2. Create a new hero with **no church association** (leave church field empty)
3. Set the hero as active
4. Add background media (image or video)
5. Configure title, subtitle, and buttons
6. The hero will now appear in the Global Settings dropdown

## Technical Details

### Database Changes
- Added `global_hero_rotation_enabled` field
- Added `global_hero_rotation_interval` field  
- Added `global_hero_fallback_enabled` field
- Migration: `0037_add_global_hero_settings.py`

### Admin Enhancements
- Custom form filtering for global heroes only
- Enhanced preview with styling
- Organized fieldsets for better UX
- Helpful descriptions and tooltips

### Model Methods
- `get_form()` method filters hero dropdown
- `global_hero_preview()` method creates styled preview
- Enhanced field validation and help text

## Best Practices

1. **Hero Selection**: Choose heroes with no church association for global use
2. **Rotation**: Use rotation for variety, but keep interval reasonable (5-10 seconds)
3. **Fallback**: Always enable fallback to ensure something is displayed
4. **Media**: Use high-quality images/videos for best visual impact
5. **Content**: Keep titles and subtitles concise and engaging

## Troubleshooting

### No Heroes Available
- Create global heroes (no church association)
- Ensure heroes are marked as active
- Check that heroes have proper media content

### Preview Not Showing
- Verify hero has background media (image or video)
- Check that hero is active
- Ensure proper file permissions for media

### Rotation Not Working
- Verify rotation is enabled
- Check rotation interval (minimum 3 seconds)
- Ensure multiple active heroes exist for rotation

## Future Enhancements

Potential improvements for future versions:
- Hero scheduling (show different heroes at different times)
- A/B testing for hero effectiveness
- Analytics tracking for hero performance
- Advanced rotation algorithms
- Hero templates and themes 