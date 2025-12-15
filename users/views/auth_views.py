import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from core.settings import DEFAULT_FROM_EMAIL

from users.serializers import UserRegistrationSerializer

logger = logging.getLogger(__name__)

class UserRegistrationView(APIView):
    """
    Register a new user and send welcome email
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = serializer.save()
            self._send_welcome_email(user)
            
            return Response(
                {"detail": "User registered successfully. Welcome email sent."},
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Error during user registration: {str(e)}")
            return Response(
                {"error": "Failed to register user. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_welcome_email(self, user):
        """Send welcome email to the new user"""
        subject = "Welcome to Our Platform!"
        message = render_to_string('emails/welcome.html', {
            'user': user,
        })
        
        send_mail(
            subject=subject,
            message="Welcome to our platform!",
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False,
        )