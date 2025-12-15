# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    
    # Blog posts
    path('posts/', views.BlogPostListCreateView.as_view(), name='post-list'),
    path('posts/<str:id>/', views.BlogPostRetrieveUpdateDestroyView.as_view(), name='post-detail'),
    
    # Comments
    path('posts/<str:id>/comments/', views.CommentCreateView.as_view(), name='comment-create'),
    path('comments/<str:pk>/', views.CommentUpdateDeleteView.as_view(), name='comment-detail'),
]