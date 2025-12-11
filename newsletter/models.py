from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator

class Subscriber(models.Model):
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
    
    def __str__(self):
        return self.email
