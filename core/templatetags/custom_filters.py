from django import template
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