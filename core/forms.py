from django import forms
from django.forms.widgets import ClearableFileInput
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Testimony, MinistryJoinRequest, EventRegistration, PrayerRequest, ContactMessage

class TestimonyForm(forms.ModelForm):
    """Form for users to submit testimonies"""
    
    class Meta:
        model = Testimony
        fields = ['author_name', 'author_email', 'title', 'content', 'location', 'category', 'is_anonymous']
        widgets = {
            'author_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 placeholder-gray-500',
                'placeholder': 'Your name (or leave blank for anonymous)'
            }),
            'author_email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 placeholder-gray-500',
                'placeholder': 'your.email@example.com'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 placeholder-gray-500',
                'placeholder': 'Brief title for your testimony'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 placeholder-gray-500',
                'rows': 6,
                'placeholder': 'Share your testimony here...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 placeholder-gray-500',
                'placeholder': 'City, Country (optional)'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make author_name not required if user wants to be anonymous
        self.fields['author_name'].required = False
        self.fields['location'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        is_anonymous = cleaned_data.get('is_anonymous')
        author_name = cleaned_data.get('author_name')
        
        # If not anonymous, require author name
        if not is_anonymous and not author_name:
            raise forms.ValidationError("Please provide your name or check 'Share anonymously'")
        
        return cleaned_data 

class MinistryJoinRequestForm(forms.ModelForm):
    class Meta:
        model = MinistryJoinRequest
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone (optional)'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Why do you want to join? (optional)', 'rows': 3}),
        }

class PrayerRequestForm(forms.ModelForm):
    class Meta:
        model = PrayerRequest
        fields = ['name', 'email', 'phone', 'title', 'request', 'category', 'is_anonymous', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone (optional)'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief title for your prayer request'}),
            'request': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Share your prayer request here...', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        is_anonymous = cleaned_data.get('is_anonymous')
        
        if not name and not is_anonymous:
            raise forms.ValidationError(
                "Please provide your name or check 'Share anonymously'"
            )
        
        return cleaned_data

class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ['first_name', 'last_name', 'email', 'phone', 'dietary_restrictions', 'special_needs', 'additional_notes']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-medium-blue focus:border-transparent', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-medium-blue focus:border-transparent', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-medium-blue focus:border-transparent', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-medium-blue focus:border-transparent', 'placeholder': 'Phone Number (optional)'}),
            'dietary_restrictions': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-medium-blue focus:border-transparent', 'placeholder': 'Any dietary restrictions? (optional)', 'rows': 2}),
            'special_needs': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-medium-blue focus:border-transparent', 'placeholder': 'Any special needs or accommodations? (optional)', 'rows': 2}),
            'additional_notes': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-medium-blue focus:border-transparent', 'placeholder': 'Additional notes or questions? (optional)', 'rows': 3}),
        } 

class CustomImageWidget(ClearableFileInput):
    """
    Custom widget for ImageField that removes the auto-generated thumbnail
    and shows only the file input and a full-size preview when an image exists.
    """
    # Temporarily use default template to fix admin error
    # template_name = 'admin/widgets/custom_image_widget.html'
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        
        # Get the current value (image URL if exists)
        if value and hasattr(value, 'url'):
            context['widget']['image_url'] = value.url
            context['widget']['image_name'] = value.name
        else:
            context['widget']['image_url'] = None
            context['widget']['image_name'] = None
        
        return context

class CustomImageField(forms.ImageField):
    """
    Custom ImageField that uses the CustomImageWidget
    """
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = CustomImageWidget()
        super().__init__(*args, **kwargs)

class EnhancedImageWidget(ClearableFileInput):
    """
    Enhanced widget for ImageField with configurable sizes and better customization
    """
    # Temporarily use default template to fix admin error
    # template_name = 'admin/widgets/custom_image_widget.html'
    
    def __init__(self, max_height=600, show_info=True, *args, **kwargs):
        self.max_height = max_height
        self.show_info = show_info
        super().__init__(*args, **kwargs)
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        
        # Get the current value (image URL if exists)
        if value and hasattr(value, 'url'):
            context['widget']['image_url'] = value.url
            context['widget']['image_name'] = value.name
        else:
            context['widget']['image_url'] = None
            context['widget']['image_name'] = None
        
        # Add custom attributes
        context['widget']['max_height'] = self.max_height
        context['widget']['show_info'] = self.show_info
            
        return context

class EnhancedImageField(forms.ImageField):
    """
    Enhanced ImageField with configurable sizes and better customization
    """
    def __init__(self, max_height=600, show_info=True, *args, **kwargs):
        kwargs['widget'] = EnhancedImageWidget(max_height=max_height, show_info=show_info)
        super().__init__(*args, **kwargs) 

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number (optional)'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject of your message'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your message...', 'rows': 6}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Full Name',
            'email': 'Email Address',
            'phone': 'Phone Number (optional)',
            'subject': 'Subject',
            'message': 'Message',
            'category': 'Category',
        }
        help_texts = {
            'name': 'Your full name',
            'email': 'Your email address',
            'phone': 'Phone number (optional)',
            'subject': 'Subject of your message',
            'message': 'Your message',
            'category': 'Select the category that best fits your inquiry',
        } 