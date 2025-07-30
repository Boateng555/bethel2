from rest_framework import serializers
from .models import Event, Ministry, News, NewsletterSignup

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class MinistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Ministry
        fields = '__all__'

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'

class NewsletterSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSignup
        fields = '__all__' 