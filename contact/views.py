from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Contact
from .serializers import ContactSerializer

class ContactView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to submit the form

    def post(self, request, format=None):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()
            
            # Send confirmation email to sender
            try:
                # Confirmation to sender
                sender_subject = 'Thank You for Contacting TechShinobi!'
                sender_context = {
                    'name': contact.name,
                    'subject': contact.subject,
                    'message': contact.message,
                    'email': contact.email
                }
                
                html_message = render_to_string(
                    'emails/contact_confirmation.html',
                    sender_context
                )
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject=sender_subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[contact.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                # Notification to admin
                admin_subject = f'New Contact Form Submission: {contact.subject}'
                admin_context = {
                    'name': contact.name,
                    'subject': contact.subject,
                    'message': contact.message,
                    'email': contact.email,
                    'admin_email': settings.ADMIN_EMAIL,
                    'admin_name': 'Admin'
                }
                
                admin_html = render_to_string(
                    'emails/admin_contact_notification.html',
                    admin_context
                )
                admin_plain = strip_tags(admin_html)
                
                send_mail(
                    subject=admin_subject,
                    message=admin_plain,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    html_message=admin_html,
                    fail_silently=False,
                )
                
            except Exception as e:
                # Log the error but don't fail the request
                print(f"Error sending email: {e}")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContactDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can view/update

    def get_object(self, pk):
        try:
            return Contact.objects.get(pk=pk)
        except Contact.DoesNotExist:
            return None

    def get(self, request, pk, format=None):
        contact = self.get_object(pk)
        if contact is None:
            return Response(
                {"error": "Contact not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        # Mark as read when viewed
        if contact.status != 'read':
            contact.mark_as_read()
        serializer = ContactSerializer(contact)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        contact = self.get_object(pk)
        if contact is None:
            return Response(
                {"error": "Contact not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ContactSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)