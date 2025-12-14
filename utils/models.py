from django.conf import settings
from django.db import models
from django.db.models.fields import uuid
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from utils.manager import SoftDeleteManager

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        null=True,
        related_name='%(app_label)s_%(class)s_last_updated',
    )

    deleted_at = models.DateTimeField(null=True)
    
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        null=True,
        related_name='%(app_label)s_%(class)s_deleted',
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # includes deleted

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Get the current user from the request if available
        try:
            request = getattr(self, '_request', None)
            if request and hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user
                # Set created_by if this is a new instance
                if not self.pk:
                    self.created_by = user
                # Always update last_updated_by
                self.last_updated_by = user
        except (AttributeError, ObjectDoesNotExist):
            pass
            
        super().save(*args, **kwargs)
    
    def update(self, *args, **kwargs):
        # Get the current user from the request if available
        try:
            request = getattr(self, '_request', None)
            if request and hasattr(request, 'user') and request.user.is_authenticated:
                self.last_updated_by = request.user
        except (AttributeError, ObjectDoesNotExist):
            pass
            
        super().update(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Set deleted_by if user is authenticated
        try:
            request = getattr(self, '_request', None)
            if request and hasattr(request, 'user') and request.user.is_authenticated:
                self.deleted_by = request.user
        except (AttributeError, ObjectDoesNotExist):
            pass
            
        self.deleted_at = timezone.now()
        self.save()
