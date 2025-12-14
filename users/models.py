
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.manager import UserManager
from utils.models import BaseModel


class User(AbstractUser, BaseModel, PermissionsMixin):
    """
    Custom User model with email as the unique identifier and soft delete support.
    """
    
    blocked_at = models.DateTimeField(null=True, blank=True)
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']
    
    objects = UserManager()
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'users'
        
    def __str__(self):
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        return self.username
