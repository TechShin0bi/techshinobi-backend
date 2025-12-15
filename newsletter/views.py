from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import Subscriber
from .serializers import SubscriberSerializer

class SubscribeView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = SubscriberSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            # Check if email already exists
            subscriber, created = Subscriber.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )
            
            if not created:
                if subscriber.is_active:
                    return Response(
                        {'detail': 'This email is already subscribed to our newsletter.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    # Reactivate unsubscribed email
                    subscriber.is_active = True
                    subscriber.save()
                    
                    # Send welcome back email
                    self._send_welcome_email(subscriber, is_returning=True)
                    
                    return Response(
                        {'detail': 'Successfully resubscribed to our newsletter!'},
                        status=status.HTTP_200_OK
                    )
            
            # For new subscribers
            self._send_welcome_email(subscriber)
            
            return Response(
                {'detail': 'Successfully subscribed to our newsletter! Check your email for a welcome message.'},
                status=status.HTTP_201_CREATED
            )
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _send_welcome_email(self, subscriber, is_returning=False):
        """Helper method to send welcome email to subscribers"""
        try:
            # Generate unsubscribe URL
            site_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'https://yourdomain.com'
            unsubscribe_url = f"{site_url}/unsubscribe/{subscriber.unsubscribe_token}"
            
            subject = 'Welcome back to TechShinobi Newsletter!' if is_returning else 'Welcome to TechShinobi Newsletter!'
            
            context = {
                'site_url': site_url,
                'unsubscribe_url': unsubscribe_url,
                'is_returning': is_returning
            }
            
            html_message = render_to_string(
                'emails/newsletter_welcome.html',
                context
            )
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscriber.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but don't fail the subscription
            print(f"Error sending welcome email to {subscriber.email}: {e}")

class UnsubscribeView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'detail': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            validate_email(email)
            email = email.lower().strip()
            
            try:
                subscriber = Subscriber.objects.get(email=email, is_active=True)
                subscriber.is_active = False
                subscriber.save()
                return Response(
                    {'detail': 'Successfully unsubscribed from our newsletter.'},
                    status=status.HTTP_200_OK
                )
            except Subscriber.DoesNotExist:
                return Response(
                    {'detail': 'This email is not subscribed to our newsletter.'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except ValidationError:
            return Response(
                {'detail': 'Please enter a valid email address.'},
                status=status.HTTP_400_BAD_REQUEST
            )
