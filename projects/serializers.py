from rest_framework import serializers
from .models import Project, ProjectImage

class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ['image', 'caption', 'display_order']

class ProjectSerializer(serializers.ModelSerializer):
    images = ProjectImageSerializer(many=True, read_only=True)
    technologies = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'short_description',
            'image', 'demo_url', 'source_code_url', 'technologies',
            'featured', 'display_order', 'created_at', 'updated_at', 'images'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_technologies(self, obj):
        return [tech.strip() for tech in obj.technologies.split(',') if tech.strip()]