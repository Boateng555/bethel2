# Hero Media Setup Guide

## Overview

Hero Media functionality has been successfully added to all churches in the Bethel platform. This allows churches to have multiple images and videos in their hero sections, displayed in a beautiful Swiper carousel.

## What's New

### ✅ **Complete Hero Media Coverage**

All hero sections across the platform now support multiple images/videos:

- **Global Homepage** - Hero Media + Swiper carousel
- **Big Events** - Hero Media + Swiper carousel  
- **Church Homepages** - Hero Media + Swiper carousel
- **Church Event Details** - Hero Media + Swiper carousel
- **Church Admin** - Hero Media integration

### ✅ **Admin Integration**

- **Church Admin**: Hero inline for creating/editing church heroes
- **Local Hero Admin**: Hero Media inline for managing multiple images/videos
- **Global Hero Admin**: Hero Media inline for global homepage
- **Event Admin**: Hero Media inline for event hero sections

### ✅ **Management Commands**

- `python manage.py add_hero_media_to_churches` - Add Hero Media to existing churches
- `python manage.py add_hero_media_to_churches --force` - Force update existing churches
- `python manage.py add_hero_media_to_churches --church-id <id>` - Update specific church

### ✅ **Status Checking**

- `python check_hero_media_status.py` - Check Hero Media status for all churches

## How to Use

### For Global Admins

1. **Create/Edit Churches**:
   - Go to `/admin/core/church/`
   - Create or edit a church
   - Configure hero in the "Church Heroes" inline
   - Save the church

2. **Add Hero Media**:
   - Go to `/admin/core/localhero/`
   - Edit the church's hero
   - Add multiple images/videos in the "Hero Media" section
   - Set the order for each media item

3. **Bulk Operations**:
   - Select churches in the admin
   - Use "Add Hero Media functionality" action
   - Automatically creates/updates hero content

### For Local Church Admins

1. **Manage Hero Content**:
   - Go to `/local-admin/` → "Hero Content Management"
   - Edit existing hero or create new one
   - Add multiple images/videos in the "Hero Media" section

2. **View Status**:
   - The local admin interface shows all Hero Media items
   - Displays thumbnails and order information

## Technical Implementation

### Models

- **Hero**: Main hero content (title, subtitle, buttons, etc.)
- **HeroMedia**: Individual media items (images/videos with order)

### Templates

- **Global Home**: `templates/core/home.html` - Swiper carousel
- **Church Home**: `templates/core/church_home.html` - Swiper carousel
- **Event Details**: `templates/core/church_event_detail.html` - Swiper carousel
- **Big Events**: `templates/core/big_event_detail.html` - Swiper carousel

### Views

- All hero views now prefetch `hero_media` for performance
- Fallback to old single background fields for backward compatibility

### Admin

- **HeroMediaInline**: Tabular inline for managing media items
- **HeroInline**: Stacked inline for church admin integration
- **Custom Actions**: Bulk operations for adding Hero Media

## Features

### 🎯 **Swiper Carousel**
- Auto-play with 5-second intervals
- Navigation arrows
- Pagination dots
- Smooth transitions
- Touch/swipe support

### 🎯 **Admin Features**
- Drag-and-drop file uploads
- Order management
- Image/video previews
- Bulk operations
- Status indicators

### 🎯 **Performance**
- Optimized database queries with prefetch
- Efficient media loading
- Responsive design

### 🎯 **Backward Compatibility**
- Existing single background images/videos still work
- Gradual migration path
- No breaking changes

## File Structure

```
core/
├── models.py              # Hero and HeroMedia models
├── admin.py               # Admin configurations
├── views.py               # Updated views with prefetch
├── management/
│   └── commands/
│       └── add_hero_media_to_churches.py  # Management command
└── templates/
    └── core/
        ├── home.html              # Global hero with Swiper
        ├── church_home.html       # Church hero with Swiper
        ├── church_event_detail.html  # Event hero with Swiper
        └── big_event_detail.html     # Big event hero with Swiper
```

## Status

### ✅ **Completed**
- [x] Hero Media model and migrations
- [x] Admin integration for all hero types
- [x] Swiper carousel implementation
- [x] Template updates for all hero sections
- [x] View optimizations with prefetch
- [x] Management commands for bulk operations
- [x] Status checking scripts
- [x] Backward compatibility
- [x] Performance optimizations

### 📊 **Current Status**
- **Total Churches**: 2
- **Churches with Hero**: 2 (100%)
- **Churches with Hero Media**: 2 (100%)
- **Churches with Media Files**: 2 (100%)

## Next Steps

1. **Add Content**: Go to `/admin/core/localhero/` and add images/videos to each church's hero
2. **Customize**: Adjust titles, subtitles, and button links for each church
3. **Test**: Visit each church's homepage to see the carousel in action
4. **Optimize**: Upload optimized images and videos for better performance

## Support

For questions or issues:
1. Check the admin interface for Hero Media status
2. Run `python check_hero_media_status.py` for detailed status
3. Use management commands for bulk operations
4. Review this documentation for implementation details

---

**🎉 Hero Media functionality is now fully implemented and ready for use!** 