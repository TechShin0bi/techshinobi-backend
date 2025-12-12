# blog/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import BlogPost, Comment
from .serializers import (
    BlogPostSerializer, 
    BlogPostCreateUpdateSerializer,
    CommentSerializer,
    UserSerializer
)

User = get_user_model()

class BlogPostListCreateView(generics.ListCreateAPIView):
    queryset = BlogPost.objects.filter(is_published=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BlogPostCreateUpdateSerializer
        return BlogPostSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class BlogPostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogPost.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BlogPostCreateUpdateSerializer
        return BlogPostSerializer
    
    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return BlogPost.objects.all()
        return BlogPost.objects.filter(is_published=True)


class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        post = generics.get_object_or_404(
            BlogPost, 
            id=self.kwargs['id'],
            is_published=True
        )
        serializer.save(author=self.request.user, post=post)


class CommentUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Comment.objects.all()
        return Comment.objects.filter(author=self.request.user)