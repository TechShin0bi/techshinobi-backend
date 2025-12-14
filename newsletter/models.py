from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator
from utils.models import BaseModel

class Subscriber(BaseModel):
    email = models.EmailField(
        max_length=255,
        unique=True,
        validators=[EmailValidator(message='Please enter a valid email address.')]
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'
        ordering = ['-subscribed_at']
        db_table = 'newsletter_subscribers'
    
    def __str__(self):
        return self.email
