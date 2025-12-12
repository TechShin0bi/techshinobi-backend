# blog/serializers.py
from rest_framework import serializers
from .models import BlogPost, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['author', 'created_at', 'updated_at']


class BlogPostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'author', 'created_at', 
                 'updated_at', 'is_published', 'comments', 'comment_count']
        read_only_fields = ['author', 'created_at', 'updated_at']
    
    def get_comment_count(self, obj):
        return obj.comments.filter(is_active=True).count()


class BlogPostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'is_published']