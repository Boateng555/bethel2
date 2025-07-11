from django import forms
from .models import Testimony, MinistryJoinRequest, EventRegistration

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