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
        Validate login credentials and user type.
        Returns the validated data if successful.
        """
        username = attrs.get('username')
        password = attrs.get('password')

        # Basic validation
        if not username or not password:
            raise serializers.ValidationError(_('Both username and password are required.'))
            
        # Get valid user types from the choices
        user_type_field = self.fields['user_type']
        valid_user_types = [choice[0] if isinstance(choice, (list, tuple)) else choice 
                          for choice in user_type_field.choices]
        
        # Convert user_type to int for comparison if it's a string
        try:
            user_type = int(user_type) if isinstance(user_type, str) else user_type
        except (ValueError, TypeError):
            raise serializers.ValidationError(_('Invalid user type format.'))
            
        # Validate user type
        if user_type not in valid_user_types:
            raise serializers.ValidationError(_('Invalid user type specified.'))
            
        # Store the credentials for the view to use
        attrs['username'] = username
        attrs['password'] = password
        attrs['user_type'] = user_type

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
        user_type = self.validated_data['user_type']
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
            'user_type': user_type,
        }
