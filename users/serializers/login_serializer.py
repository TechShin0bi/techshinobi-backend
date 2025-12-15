from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework import serializers
from auth_kit.jwt_auth import jwt_encode
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from django.utils import timezone

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Validate login credentials.
        Returns the validated data if successful.
        """
        username = attrs.get('username')
        password = attrs.get('password')
        # Basic validation
        if not username or not password:
            raise serializers.ValidationError(_('Both username and password are required.'))
            
        # Store the credentials for the view to use
        attrs['username'] = username
        attrs['password'] = password
        return attrs

    def authenticate_user(self):
        """
        Authenticate user and return user and tokens.
        This method should be called after the serializer is validated.
        """
        if not hasattr(self, 'validated_data'):
            raise serializers.ValidationError(_('Serializer must be validated first.'))
            
        username = self.validated_data['username']
        password = self.validated_data['password']
        request = self.context.get('request')
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        if not user:
            self._handle_failed_login_attempt(request)
            raise serializers.ValidationError(_('Invalid username or password. Please try again.'))
            
        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError(_('This account is inactive.'))
            
        # Generate tokens and convert them to strings
        access_token, refresh_token = jwt_encode(user)
        
        # Convert token objects to strings for JSON serialization
        access_token_str = str(access_token)
        refresh_token_str = str(refresh_token)
        
        return {
            'user': user,
            'tokens': {
                'access': access_token_str,
                'refresh': refresh_token_str,
                'access_expiration': (timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME).isoformat(),
                'refresh_expiration': (timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME).isoformat(),
            },
        }
