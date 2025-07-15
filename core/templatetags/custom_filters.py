from django import template
from django.conf import settings
register = template.Library()

@register.filter
def dict_get(d, key):
    return d.get(key, '')

@register.filter
def first_with_image(media_list):
    """Return the first media item that has an image"""
    for media in media_list:
        if hasattr(media, 'image') and media.image:
            return media
    return None

@register.filter
def cloudinary_url(image_field):
    """Get the proper Cloudinary URL for an image field"""
    if not image_field:
        return ''
    
    # If using Cloudinary, return the Cloudinary URL
    if hasattr(settings, 'CLOUDINARY_STORAGE'):
        return image_field.url
    
    # Otherwise return the regular URL
    return image_field.url 