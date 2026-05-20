from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.forms.widgets import ClearableFileInput
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Testimony, MinistryJoinRequest, EventRegistration, PrayerRequest, ContactMessage, Event, Ministry, News, Sermon, DonationMethod, Hero, Church, ChurchAdmin, EventSpeaker, EventScheduleItem, EventHeroMedia

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


# --- Local Admin Dashboard Forms (no Django admin) ---
INPUT_CLASS = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#1e3a8a] text-gray-900 placeholder-gray-500'
CHECKBOX_CLASS = 'rounded border-gray-300 text-[#1e3a8a] focus:ring-[#1e3a8a]'


class LocalAdminEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'details', 'start_date', 'end_date', 'location', 'address',
            'event_type', 'requires_registration', 'registration_url', 'max_attendees', 'registration_deadline', 'registration_fee',
            'is_featured', 'is_public', 'is_big_event', 'show_qr_code'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Event title'}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 4}),
            'details': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 10, 'placeholder': 'Write the full event details here. This is the long text on the event page.'}),
            'start_date': forms.DateTimeInput(attrs={'class': INPUT_CLASS, 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': INPUT_CLASS, 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. Main Auditorium or City, Country'}),
            'address': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 2, 'placeholder': 'Full street address (shown in Everything You Need To Know)'}),
            'event_type': forms.Select(attrs={'class': INPUT_CLASS}),
            'requires_registration': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'registration_url': forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://forms.google.com/... or your registration page URL'}),
            'max_attendees': forms.NumberInput(attrs={'class': INPUT_CLASS}),
            'registration_deadline': forms.DateTimeInput(attrs={'class': INPUT_CLASS, 'type': 'datetime-local'}),
            'registration_fee': forms.NumberInput(attrs={'class': INPUT_CLASS, 'step': '0.01'}),
            'is_featured': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'is_public': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'is_big_event': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'show_qr_code': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }
        labels = {
            'title': 'Event title',
            'description': 'Description (short summary for cards and hero)',
            'details': 'Event Details (full description)',
            'start_date': 'Start date & time',
            'end_date': 'End date & time',
            'location': 'Location (name or venue)',
            'address': 'Full address',
            'is_big_event': 'Use big event page (hero, Everything You Need To Know, Date/Time/Location, Meet Our Anointed Ministers, Event Schedule)',
        }
        help_texts = {
            'start_date': 'Shown as date and time on the event page (e.g. April 17, 2026 · 3:58 AM - 5:54 AM).',
            'end_date': 'End time appears next to start time in "Everything You Need To Know".',
            'location': 'Shown in "Everything You Need To Know" and on the event card.',
            'address': 'Shown under Location in "Everything You Need To Know".',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dt_format = '%Y-%m-%dT%H:%M'
        for name in ('start_date', 'end_date', 'registration_deadline'):
            if name in self.fields:
                self.fields[name].input_formats = [dt_format, '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']


class LocalAdminEventHeroMediaForm(forms.ModelForm):
    class Meta:
        model = EventHeroMedia
        fields = ('image', 'video', 'order')
        widgets = {
            'image': forms.FileInput(attrs={
                'class': INPUT_CLASS,
                'accept': 'image/*',
                'data-compress-image': 'true',
            }),
            'video': forms.FileInput(attrs={
                'class': INPUT_CLASS,
                'accept': 'video/*',
                'data-compress-video': 'true',
            }),
            'order': forms.NumberInput(attrs={'class': INPUT_CLASS}),
        }
        help_texts = {
            'order': 'Display order (0 = first).',
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            from .media_utils import compress_image_upload
            compressed = compress_image_upload(image)
            if compressed:
                return compressed
        return image

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            from .media_utils import compress_video_upload
            compressed = compress_video_upload(video)
            if compressed:
                return compressed
        return video

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('image') and not cleaned.get('video'):
            raise forms.ValidationError('Add either an image or a video.')
        return cleaned


class LocalAdminEventSpeakerForm(forms.ModelForm):
    class Meta:
        model = EventSpeaker
        fields = ('name', 'photo', 'title', 'bio')
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Speaker name'}),
            'photo': forms.FileInput(attrs={'class': INPUT_CLASS, 'accept': 'image/*'}),
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. Senior Pastor'}),
            'bio': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3}),
        }


class LocalAdminEventScheduleItemForm(forms.ModelForm):
    class Meta:
        model = EventScheduleItem
        fields = ('day', 'start_time', 'end_time', 'title', 'description', 'speaker', 'speaker_2', 'location')
        widgets = {
            'day': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. Day 1 or Sunday'}),
            'start_time': forms.TimeInput(attrs={'class': INPUT_CLASS, 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': INPUT_CLASS, 'type': 'time'}),
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Session title'}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 2}),
            'speaker': forms.Select(attrs={'class': INPUT_CLASS}),
            'speaker_2': forms.Select(attrs={'class': INPUT_CLASS}),
            'location': forms.TextInput(attrs={'class': INPUT_CLASS}),
        }

    def __init__(self, *args, event=None, **kwargs):
        super().__init__(*args, **kwargs)
        if event is not None:
            qs = EventSpeaker.objects.filter(event=event).order_by('name')
            if 'speaker' in self.fields:
                self.fields['speaker'].queryset = qs
            if 'speaker_2' in self.fields:
                self.fields['speaker_2'].queryset = qs


class LocalAdminMinistryForm(forms.ModelForm):
    class Meta:
        model = Ministry
        fields = [
            'name', 'description', 'ministry_type', 'leader_name', 'contact_email', 'contact_phone',
            'image', 'is_active', 'is_featured', 'is_public'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 4}),
            'ministry_type': forms.Select(attrs={'class': INPUT_CLASS}),
            'leader_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'contact_email': forms.EmailInput(attrs={'class': INPUT_CLASS}),
            'contact_phone': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'image': forms.FileInput(attrs={'class': INPUT_CLASS}),
            'is_active': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'is_featured': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'is_public': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }


class LocalAdminNewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'excerpt', 'date', 'image', 'is_featured', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'content': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 6}),
            'excerpt': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 2}),
            'date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'image': forms.FileInput(attrs={'class': INPUT_CLASS}),
            'is_featured': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'is_public': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }


class LocalAdminSermonForm(forms.ModelForm):
    class Meta:
        model = Sermon
        fields = [
            'title', 'preacher', 'description', 'date', 'scripture_reference', 'scripture_text',
            'audio_file', 'video_file', 'thumbnail', 'link', 'duration', 'language',
            'is_featured', 'is_public'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'preacher': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 4}),
            'date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'scripture_reference': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'scripture_text': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 2}),
            'audio_file': forms.FileInput(attrs={'class': INPUT_CLASS}),
            'video_file': forms.FileInput(attrs={'class': INPUT_CLASS}),
            'thumbnail': forms.FileInput(attrs={'class': INPUT_CLASS}),
            'link': forms.URLInput(attrs={'class': INPUT_CLASS}),
            'duration': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. 45:30'}),
            'language': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'is_featured': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'is_public': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }


class LocalAdminDonationMethodForm(forms.ModelForm):
    class Meta:
        model = DonationMethod
        fields = ['name', 'payment_type', 'external_link', 'account_info', 'description', 'is_active', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'payment_type': forms.Select(attrs={'class': INPUT_CLASS}),
            'external_link': forms.URLInput(attrs={'class': INPUT_CLASS}),
            'account_info': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 4}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'is_default': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
        }


class LocalAdminHeroForm(forms.ModelForm):
    class Meta:
        model = Hero
        fields = [
            'title', 'subtitle', 'background_type', 'background_image', 'background_video',
            'primary_button_text', 'primary_button_link', 'secondary_button_text', 'secondary_button_link',
            'is_active', 'order'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'subtitle': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 2}),
            'background_type': forms.Select(attrs={'class': INPUT_CLASS}),
            'background_image': forms.FileInput(attrs={'class': INPUT_CLASS}),
            'background_video': forms.FileInput(attrs={'class': INPUT_CLASS}),
            'primary_button_text': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'primary_button_link': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'secondary_button_text': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'secondary_button_link': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'is_active': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}),
            'order': forms.NumberInput(attrs={'class': INPUT_CLASS}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.background_image:
                name = self.instance.background_image.name
                self.fields['background_image'].help_text = f'Current: {name}. Leave blank to keep this file.'
            if self.instance.background_video:
                name = self.instance.background_video.name
                self.fields['background_video'].help_text = f'Current: {name}. Leave blank to keep this file.'

    def save(self, commit=True):
        instance = super().save(commit=False)
        # If no new file was uploaded, keep the existing file (form submission often sends empty for file inputs)
        if not self.cleaned_data.get('background_image') and instance.pk:
            try:
                orig = Hero.objects.get(pk=instance.pk)
                if orig.background_image:
                    instance.background_image = orig.background_image
            except Hero.DoesNotExist:
                pass
        if not self.cleaned_data.get('background_video') and instance.pk:
            try:
                orig = Hero.objects.get(pk=instance.pk)
                if orig.background_video:
                    instance.background_video = orig.background_video
            except Hero.DoesNotExist:
                pass
        if commit:
            instance.save()
        return instance


# --- User management (superuser only) ---
class UserAddForm(UserCreationForm):
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': INPUT_CLASS}))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASS}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASS}))
    is_staff = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}))
    is_superuser = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}))
    role = forms.ChoiceField(required=False, choices=[('', '— No church role —')] + list(ChurchAdmin.ROLE_CHOICES), widget=forms.Select(attrs={'class': INPUT_CLASS}))
    church = forms.ModelChoiceField(queryset=Church.objects.filter(is_approved=True).order_by('name'), required=False, empty_label='— Select church —', widget=forms.Select(attrs={'class': INPUT_CLASS}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_superuser')
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'password1': forms.PasswordInput(attrs={
                'class': INPUT_CLASS,
                'type': 'password',
                'autocomplete': 'new-password',
                'placeholder': '••••••••',
            }),
            'password2': forms.PasswordInput(attrs={
                'class': INPUT_CLASS,
                'type': 'password',
                'autocomplete': 'new-password',
                'placeholder': '••••••••',
            }),
        }

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.is_staff = self.cleaned_data.get('is_staff', False)
            user.is_superuser = self.cleaned_data.get('is_superuser', False)
            user.email = self.cleaned_data.get('email', '') or ''
            user.first_name = self.cleaned_data.get('first_name', '') or ''
            user.last_name = self.cleaned_data.get('last_name', '') or ''
            user.save()
        return user


class UserEditForm(forms.Form):
    is_staff = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}))
    is_superuser = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}))
    role = forms.ChoiceField(required=False, choices=[('', '— No church role —')] + list(ChurchAdmin.ROLE_CHOICES), widget=forms.Select(attrs={'class': INPUT_CLASS}))
    church = forms.ModelChoiceField(queryset=Church.objects.none(), required=False, empty_label='— Select church —', widget=forms.Select(attrs={'class': INPUT_CLASS}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['church'].queryset = Church.objects.filter(is_approved=True).order_by('name')
        if self.user:
            self.fields['is_staff'].initial = self.user.is_staff
            self.fields['is_superuser'].initial = self.user.is_superuser
            self.fields['is_active'].initial = self.user.is_active
            try:
                ca = ChurchAdmin.objects.get(user=self.user)
                self.fields['role'].initial = ca.role
                self.fields['church'].initial = ca.church
            except ChurchAdmin.DoesNotExist:
                pass


class SetPasswordFormCustom(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'type': 'password',
            'autocomplete': 'new-password',
            'placeholder': '••••••••',
        }),
        strip=False,
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'type': 'password',
            'autocomplete': 'new-password',
            'placeholder': '••••••••',
        }),
        strip=False,
    )


class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'type': 'password',
            'autocomplete': 'current-password',
            'placeholder': '••••••••',
        }),
        strip=False,
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'type': 'password',
            'autocomplete': 'new-password',
            'placeholder': '••••••••',
        }),
        strip=False,
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'type': 'password',
            'autocomplete': 'new-password',
            'placeholder': '••••••••',
        }),
        strip=False,
    )


# --- Church members (local admin: add/remove members for their church) ---
# Church Members: only Local Admin (no Moderator)
CHURCH_ROLE_CHOICES = [c for c in ChurchAdmin.ROLE_CHOICES if c[0] == 'local_admin']

class ChurchMemberAddForm(UserCreationForm):
    """Add a new member to the current church (local admin only)."""
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': INPUT_CLASS}))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASS}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASS}))
    role = forms.ChoiceField(choices=CHURCH_ROLE_CHOICES, initial='local_admin', widget=forms.Select(attrs={'class': INPUT_CLASS}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'password1': forms.PasswordInput(attrs={
                'class': INPUT_CLASS,
                'type': 'password',
                'autocomplete': 'new-password',
                'placeholder': '••••••••',
            }),
            'password2': forms.PasswordInput(attrs={
                'class': INPUT_CLASS,
                'type': 'password',
                'autocomplete': 'new-password',
                'placeholder': '••••••••',
            }),
        }

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.email = self.cleaned_data.get('email', '') or ''
            user.first_name = self.cleaned_data.get('first_name', '') or ''
            user.last_name = self.cleaned_data.get('last_name', '') or ''
            user.save()
        return user


class ChurchMemberEditForm(forms.Form):
    """Edit a church member's role and status."""
    role = forms.ChoiceField(choices=CHURCH_ROLE_CHOICES, widget=forms.Select(attrs={'class': INPUT_CLASS}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': CHECKBOX_CLASS})) 