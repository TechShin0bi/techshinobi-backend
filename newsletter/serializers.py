from rest_framework import serializers
from .models import Subscriber

class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ['email', 'subscribed_at', 'is_active']
        read_only_fields = ['subscribed_at', 'is_active']
        extra_kwargs = {
            'email': {'required': True}
        }
    
    def validate_email(self, value):
        return value.lower().strip()
