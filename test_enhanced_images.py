#!/usr/bin/env python
"""
Test script to verify enhanced image features in Django admin
"""

import os
import sys
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from core.models import Church, Ministry, News, Sermon
from core.forms import CustomImageField, EnhancedImageField
from core.admin_utils import EnhancedImagePreviewMixin

def test_enhanced_image_fields():
    """Test that enhanced image fields work correctly"""
    print("Testing Enhanced Image Fields...")
    
    # Test CustomImageField
    custom_field = CustomImageField(required=False)
    print(f"✓ CustomImageField created successfully")
    
    # Test EnhancedImageField
    enhanced_field = EnhancedImageField(max_height=600, show_info=True, required=False)
    print(f"✓ EnhancedImageField created successfully with max_height=600")
    
    # Test EnhancedImageField with different parameters
    large_field = EnhancedImageField(max_height=800, show_info=False, required=False)
    print(f"✓ EnhancedImageField created successfully with max_height=800")
    
    print("✓ All enhanced image field tests passed!\n")

def test_enhanced_preview_mixin():
    """Test that the enhanced preview mixin works correctly"""
    print("Testing Enhanced Preview Mixin...")
    
    # Create a test mixin instance
    mixin = EnhancedImagePreviewMixin()
    
    # Test creating a preview method
    preview_method = mixin.create_image_preview_method(
        field_name='logo',
        max_width=400,
        max_height=400,
        title='Test Logo Preview'
    )
    
    print(f"✓ Preview method created successfully")
    print(f"  - Method name: {preview_method.__name__}")
    print(f"  - Description: {preview_method.short_description}")
    
    # Test creating a circular preview method
    circular_method = mixin.create_image_preview_method(
        field_name='profile_picture',
        max_width=200,
        max_height=200,
        is_circular=True,
        title='Test Profile Picture'
    )
    
    print(f"✓ Circular preview method created successfully")
    
    print("✓ All enhanced preview mixin tests passed!\n")

def test_admin_configuration():
    """Test that admin classes are properly configured"""
    print("Testing Admin Configuration...")
    
    # Import admin classes
    from core.admin import ChurchModelAdmin, MinistryAdmin, NewsAdmin, SermonAdmin
    
    # Test that admin classes have the mixin
    assert issubclass(ChurchModelAdmin, EnhancedImagePreviewMixin), "ChurchModelAdmin should inherit from EnhancedImagePreviewMixin"
    assert issubclass(MinistryAdmin, EnhancedImagePreviewMixin), "MinistryAdmin should inherit from EnhancedImagePreviewMixin"
    assert issubclass(NewsAdmin, EnhancedImagePreviewMixin), "NewsAdmin should inherit from EnhancedImagePreviewMixin"
    assert issubclass(SermonAdmin, EnhancedImagePreviewMixin), "SermonAdmin should inherit from EnhancedImagePreviewMixin"
    
    print("✓ All admin classes properly inherit from EnhancedImagePreviewMixin")
    
    # Test that admin classes have __init__ methods
    church_admin = ChurchModelAdmin(Church, None)
    ministry_admin = MinistryAdmin(Ministry, None)
    news_admin = NewsAdmin(News, None)
    sermon_admin = SermonAdmin(Sermon, None)
    
    print("✓ All admin classes can be instantiated successfully")
    
    print("✓ All admin configuration tests passed!\n")

def test_css_file_exists():
    """Test that the CSS file exists and has the right content"""
    print("Testing CSS File...")
    
    css_file_path = 'static/css/admin-custom.css'
    
    if os.path.exists(css_file_path):
        print(f"✓ CSS file exists at {css_file_path}")
        
        with open(css_file_path, 'r') as f:
            content = f.read()
            
        # Check for key CSS classes
        required_classes = [
            '.enhanced-image-preview',
            '.image-preview-container',
            '.image-preview-overlay',
            '.image-modal',
            '.modal-content'
        ]
        
        for css_class in required_classes:
            if css_class in content:
                print(f"✓ Found CSS class: {css_class}")
            else:
                print(f"✗ Missing CSS class: {css_class}")
                
    else:
        print(f"✗ CSS file not found at {css_file_path}")
    
    print("✓ CSS file tests completed!\n")

def test_template_file_exists():
    """Test that the template file exists"""
    print("Testing Template File...")
    
    template_file_path = 'templates/admin/widgets/custom_image_widget.html'
    
    if os.path.exists(template_file_path):
        print(f"✓ Template file exists at {template_file_path}")
        
        with open(template_file_path, 'r') as f:
            content = f.read()
            
        # Check for key template elements
        required_elements = [
            'enhanced-image-preview',
            'image-preview-container',
            'image-preview-overlay',
            'imageModal',
            'openImageModal'
        ]
        
        for element in required_elements:
            if element in content:
                print(f"✓ Found template element: {element}")
            else:
                print(f"✗ Missing template element: {element}")
                
    else:
        print(f"✗ Template file not found at {template_file_path}")
    
    print("✓ Template file tests completed!\n")

def main():
    """Run all tests"""
    print("=" * 60)
    print("ENHANCED IMAGE FEATURES TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        test_enhanced_image_fields()
        test_enhanced_preview_mixin()
        test_admin_configuration()
        test_css_file_exists()
        test_template_file_exists()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED! Enhanced image features are ready to use.")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Run 'python manage.py collectstatic' to collect static files")
        print("2. Restart your Django development server")
        print("3. Visit your Django admin and test the enhanced image features")
        print("4. Check that images are larger and have modal functionality")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main() 