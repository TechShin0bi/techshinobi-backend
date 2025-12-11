from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
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
                    return Response(
                        {'detail': 'Successfully resubscribed to our newsletter!'},
                        status=status.HTTP_200_OK
                    )
            
            return Response(
                {'detail': 'Successfully subscribed to our newsletter!'},
                status=status.HTTP_201_CREATED
            )
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
