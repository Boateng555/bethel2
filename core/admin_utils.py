from django.utils.html import format_html
from django.utils.safestring import mark_safe

class EnhancedImagePreviewMixin:
    """
    Mixin to provide enhanced image preview methods for Django admin
    """
    
    def create_image_preview_method(self, field_name, max_width=400, max_height=400, 
                                   border_radius=12, is_circular=False, title=None):
        """
        Create a dynamic image preview method for the given field
        
        Args:
            field_name: Name of the image field
            max_width: Maximum width of the preview image
            max_height: Maximum height of the preview image
            border_radius: Border radius for the image (use 50% for circular)
            is_circular: Whether the image should be circular
            title: Custom title for the preview
        """
        
        def preview_method(obj):
            """Dynamic preview method for the image field"""
            image_field = getattr(obj, field_name, None)
            if image_field:
                # Get the URL method if it exists, otherwise use the field directly
                url_method = getattr(obj, f'get_{field_name}_url', None)
                image_url = url_method() if url_method else image_field.url
                
                # Determine border radius
                radius = '50%' if is_circular else f'{border_radius}px'
                
                # Create the preview HTML with proper CSS classes
                preview_html = format_html(
                    '<div class="image-preview-container" style="text-align: center; margin: 10px 0;">'
                    '<img src="{}" class="enhanced-image-preview" style="max-width: {}px; max-height: {}px; '
                    'border-radius: {}; box-shadow: 0 6px 20px rgba(0,0,0,0.15); '
                    'object-fit: cover; cursor: pointer; transition: transform 0.2s ease-in-out;" '
                    'onclick="window.open(this.src, \'_blank\')" '
                    'title="Click to view full size" />'
                    '<div class="image-preview-overlay">'
                    '<div class="overlay-content">'
                    '<span class="overlay-icon">🔍</span>'
                    '<span class="overlay-text">Click to view full size</span>'
                    '</div>'
                    '</div>'
                    '</div>',
                    image_url, max_width, max_height, radius
                )
                return preview_html
            else:
                return f"No {field_name.replace('_', ' ').title()} uploaded"
        
        # Set the method name and description
        method_name = f'{field_name}_preview'
        preview_method.__name__ = method_name
        preview_method.short_description = title or f"{field_name.replace('_', ' ').title()} Preview"
        
        return preview_method
    
    def add_image_preview_fields(self, admin_class, image_fields_config):
        """
        Add image preview fields to an admin class
        
        Args:
            admin_class: The admin class to add preview fields to
            image_fields_config: List of dicts with field configuration
                Example: [
                    {'field_name': 'logo', 'max_width': 300, 'max_height': 300},
                    {'field_name': 'nav_logo', 'max_width': 200, 'max_height': 200, 'is_circular': True},
                ]
        """
        for config in image_fields_config:
            field_name = config['field_name']
            max_width = config.get('max_width', 400)
            max_height = config.get('max_height', 400)
            border_radius = config.get('border_radius', 12)
            is_circular = config.get('is_circular', False)
            title = config.get('title')
            
            # Create the preview method
            preview_method = self.create_image_preview_method(
                field_name, max_width, max_height, border_radius, is_circular, title
            )
            
            # Add the method to the admin class
            setattr(admin_class, f'{field_name}_preview', preview_method)
            
            # Add to readonly_fields if not already there
            if not hasattr(admin_class, 'readonly_fields'):
                admin_class.readonly_fields = []
            elif not isinstance(admin_class.readonly_fields, (list, tuple)):
                admin_class.readonly_fields = list(admin_class.readonly_fields)
            
            if f'{field_name}_preview' not in admin_class.readonly_fields:
                admin_class.readonly_fields = list(admin_class.readonly_fields) + [f'{field_name}_preview']

class LargeImagePreviewMixin:
    """
    Mixin for very large image previews (600px+)
    """
    
    def create_large_image_preview(self, field_name, max_width=800, max_height=600, title=None):
        """Create a large image preview method"""
        return self.create_image_preview_method(
            field_name, max_width, max_height, 12, False, title
        )

class CircularImagePreviewMixin:
    """
    Mixin for circular image previews (profile pictures, logos)
    """
    
    def create_circular_image_preview(self, field_name, size=200, title=None):
        """Create a circular image preview method"""
        return self.create_image_preview_method(
            field_name, size, size, 50, True, title
        )

# Example usage:
"""
# In your admin.py file:

from .admin_utils import EnhancedImagePreviewMixin

class MyModelAdmin(EnhancedImagePreviewMixin, admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configure image preview fields
        image_config = [
            {
                'field_name': 'logo',
                'max_width': 300,
                'max_height': 300,
                'title': 'Company Logo Preview'
            },
            {
                'field_name': 'profile_picture',
                'max_width': 200,
                'max_height': 200,
                'is_circular': True,
                'title': 'Profile Picture'
            },
            {
                'field_name': 'banner_image',
                'max_width': 800,
                'max_height': 400,
                'title': 'Banner Image Preview'
            }
        ]
        
        # Add the preview fields
        self.add_image_preview_fields(self, image_config)
""" 