import os
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.core.files.base import ContentFile
from django.conf import settings

def resize_image(image_field, max_width=800, max_height=600, quality=85):
    """
    Resize an image to fit within max_width and max_height while maintaining aspect ratio
    Returns a ContentFile with the resized image
    """
    if not image_field:
        return None
    
    try:
        # Open the image
        img = Image.open(image_field)
        
        # Convert to RGB if necessary (for JPEG compatibility)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Calculate new dimensions while maintaining aspect ratio
        width, height = img.size
        
        if width <= max_width and height <= max_height:
            # Image is already smaller than max dimensions
            return None
        
        # Calculate new dimensions
        ratio = min(max_width / width, max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        # Resize the image
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        buffer = BytesIO()
        
        # Determine format and save
        file_extension = os.path.splitext(image_field.name)[1].lower()
        if file_extension in ['.jpg', '.jpeg']:
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
        elif file_extension == '.png':
            img.save(buffer, format='PNG', optimize=True)
        elif file_extension == '.webp':
            img.save(buffer, format='WEBP', quality=quality)
        else:
            # Default to JPEG
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
        
        buffer.seek(0)
        
        # Create ContentFile
        filename = os.path.basename(image_field.name)
        return ContentFile(buffer.getvalue(), name=filename)
        
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None

def resize_image_field(instance, field_name, max_width=800, max_height=600, quality=85):
    """
    Resize an image field on a model instance
    """
    field = getattr(instance, field_name)
    if not field:
        return
    
    # Check if the field has a file
    if hasattr(field, 'file') and field.file:
        resized_image = resize_image(field, max_width, max_height, quality)
        if resized_image:
            # Save the resized image back to the field
            setattr(instance, field_name, resized_image)

def get_image_dimensions(image_field):
    """
    Get the dimensions of an image
    """
    if not image_field:
        return None
    
    try:
        img = Image.open(image_field)
        return img.size
    except Exception as e:
        print(f"Error getting image dimensions: {e}")
        return None

def optimize_image_for_web(image_field, max_size_kb=500):
    """
    Optimize image for web by reducing quality until file size is under max_size_kb
    """
    if not image_field:
        return None
    
    try:
        img = Image.open(image_field)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Start with high quality and reduce until file size is acceptable
        for quality in range(95, 10, -5):
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            buffer.seek(0)
            
            # Check file size
            file_size_kb = len(buffer.getvalue()) / 1024
            
            if file_size_kb <= max_size_kb:
                buffer.seek(0)
                filename = os.path.basename(image_field.name)
                return ContentFile(buffer.getvalue(), name=filename)
        
        # If we get here, use the lowest quality
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=10, optimize=True)
        buffer.seek(0)
        filename = os.path.basename(image_field.name)
        return ContentFile(buffer.getvalue(), name=filename)
        
    except Exception as e:
        print(f"Error optimizing image: {e}")
        return None 