from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Project
from .serializers import ProjectSerializer
from django_filters.rest_framework import DjangoFilterBackend

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['featured']
    search_fields = ['title', 'description', 'technologies']
    ordering_fields = ['display_order', 'created_at', 'title']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Optionally filter out non-featured projects from list view
        if self.action == 'list' and not self.request.query_params.get('featured'):
            return queryset
        return queryset