import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from users.models import PasswordResetToken
from users.serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetVerifyOTPSerializer
)
from core.settings import DEFAULT_FROM_EMAIL

logger = logging.getLogger(__name__)
User = get_user_model()




class PasswordResetRequestView(APIView):
    """
    Request a password reset OTP via email.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.user
        
        try:
            # Create or get a password reset token
            reset_token = PasswordResetToken.create_for_user(user)
            otp = reset_token.generate_otp()
            
            # Send OTP email
            self._send_otp_email(user, otp)
            
            return Response(
                {"detail": _("OTP has been sent to your email.")},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error sending OTP email: {str(e)}")
            return Response(
                {"error": _("Failed to send OTP. Please try again later.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _send_otp_email(self, user, otp):
        """Send OTP email"""
        subject = _("Your Password Reset OTP")
        message = render_to_string('emails/password_reset_otp.html', {
            'user': user,
            'otp': otp,
        })
        
        send_mail(
            subject=subject,
            message=f"Your OTP is: {otp}",
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False,
        )


class PasswordResetVerifyOTPView(APIView):
    """
    Verify OTP for password reset.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetVerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        reset_token = serializer.validated_data['reset_token']
        
        # Mark OTP as verified
        reset_token.otp_verified = True
        reset_token.save()
        
        return Response(
            {"detail": _("OTP verified successfully.")},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with new password.
    Requires a verified OTP.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        new_password = serializer.validated_data['new_password']
        
        try:
            # Get the user and check for verified token
            user = User.objects.get(email=email)
            reset_token = PasswordResetToken.objects.filter(
                user=user,
                is_used=False,
                otp_verified=True,
                expires_at__gt=timezone.now()
            ).first()
            
            if not reset_token:
                return Response(
                    {"error": _("No valid password reset request found. Please request a new OTP.")},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update user's password
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            reset_token.is_used = True
            reset_token.save()
            
            return Response(
                {"detail": _("Password has been reset successfully.")},
                status=status.HTTP_200_OK
            )
            
        except User.DoesNotExist:
            return Response(
                {"error": _("No user found with this email address.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error resetting password: {str(e)}")
            return Response(
                {"error": _("Failed to reset password. Please try again.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )