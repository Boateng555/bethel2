from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def smart_url(value):
    """
    Returns the URL for a media field, handling both local paths and full URLs.
    If the value is already a full URL (starts with http), return it as-is.
    Otherwise, return the .url property (for local files).
    """
    if value and str(value).startswith('http'):
        return value
    return value

@register.filter
def smart_media_url(field):
    """
    Returns the appropriate URL for a media field.
    If the field contains a full URL, return it directly.
    Otherwise, return the .url property.
    """
    if not field:
        return ''
    
    field_str = str(field)
    if field_str.startswith('http'):
        return field_str
    else:
        # For local files, we need to get the .url property
        # This is a bit tricky in a template filter, so we'll handle it differently
        return field_str 

@register.filter
def first_with_image(queryset):
    """
    Returns the first item from a queryset that has an image.
    Useful for finding the first media item with an image.
    """
    if not queryset:
        return None
    
    for item in queryset:
        if hasattr(item, 'image') and item.image:
            return item
        elif hasattr(item, 'get_image_url') and item.get_image_url():
            return item
    
    # If no item with image found, return the first item
    return queryset.first() if queryset.exists() else None