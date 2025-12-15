
from django.contrib.auth.models import AbstractUser, PermissionsMixin
import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone
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

class PasswordResetToken(models.Model):
    """Model to store password reset tokens and OTP"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens'
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = _('Password Reset Token')
        verbose_name_plural = _('Password Reset Tokens')
        ordering = ['-created_at']

    def __str__(self):
        return f"Password reset token for {self.user.email}"

    def is_valid(self):
        """Check if the token is valid (not used and not expired)"""
        now = timezone.now()
        return not self.is_used and now < self.expires_at

    def generate_otp(self):
        """Generate a 6-digit OTP"""
        import random
        self.otp = f"{random.randint(0, 999999):06d}"
        self.otp_verified = False
        self.save()
        return self.otp
        
    def verify_otp(self, otp):
        """Verify the provided OTP and mark as verified if correct.
        
        Args:
            otp (str): The OTP to verify
            
        Returns:
            bool: True if OTP is valid and not expired, False otherwise
        """
        if not self.is_valid():
            return False
            
        if not self.otp or not otp:
            return False
            
        if self.otp == otp:
            self.otp_verified = True
            self.save()
            return True
            
        return False

    @classmethod
    def create_for_user(cls, user):
        """Create a new password reset token for a user"""
        # Delete any existing tokens for this user
        cls.objects.filter(user=user).delete()
        
        # Create new token that expires in 1 hour
        return cls.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=1)
        )
