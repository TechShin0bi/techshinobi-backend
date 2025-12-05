from django.urls import path
from .views import ContactView, ContactDetailView

urlpatterns = [
    path('', ContactView.as_view(), name='contact-list'),
    path('<int:pk>/', ContactDetailView.as_view(), name='contact-detail'),
]