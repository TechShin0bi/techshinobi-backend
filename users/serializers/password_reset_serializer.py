from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from users.models import PasswordResetToken

User = get_user_model()

class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Check if user with this email exists"""
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("No user found with this email address."))
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(
        required=True,
        min_length=8,
        style={'input_type': 'password'},
        write_only=True
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )

    def validate(self, data):
        """Check that the two password fields match"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": _("Passwords don't match.")})
        return data


class PasswordResetVerifyOTPSerializer(serializers.Serializer):
    """Serializer for verifying OTP during password reset"""
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6)

    def validate(self, data):
        """Validate that the OTP is valid for the given email"""
        email = data.get('email')
        otp = data.get('otp')

        try:
            user = User.objects.get(email=email)
            reset_token = PasswordResetToken.objects.filter(
                user=user,
                is_used=False
            ).latest('created_at')

            if not reset_token.verify_otp(otp):
                raise serializers.ValidationError({"otp": _("Invalid or expired OTP.")})

            # Include the reset token in the validated data
            data['reset_token'] = reset_token
            return data

        except User.DoesNotExist:
            raise serializers.ValidationError({"email": _("No user found with this email address.")})
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError({"otp": _("No valid reset token found. Please request a new OTP.")})
