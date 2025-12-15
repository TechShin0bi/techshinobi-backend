import secrets
import string
from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator
from utils.models import BaseModel

def generate_unsubscribe_token():
    """Generate a secure random token for unsubscribing."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))

class Subscriber(BaseModel):
    email = models.EmailField(
        max_length=255,
        unique=True,
        validators=[EmailValidator(message='Please enter a valid email address.')]
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    unsubscribe_token = models.CharField(
        max_length=32,
        unique=True,
        default=generate_unsubscribe_token,
        editable=False
    )
    
    class Meta:
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'
        ordering = ['-subscribed_at']
        db_table = 'newsletter_subscribers'
    
    def __str__(self):
        return self.email
