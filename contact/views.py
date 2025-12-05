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