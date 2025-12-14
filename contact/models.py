from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from utils.models import BaseModel

class Contact(BaseModel):
    READ_STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('replied', 'Replied'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=READ_STATUS_CHOICES,
        default='unread'
    )
    last_read_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, null=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"

    def mark_as_read(self, request=None):
        self.status = 'read'
        self.last_read_at = timezone.now()
        self.save(update_fields=['status', 'last_read_at'])

    def send_notification_email(self, request=None):
        subject = f"New Contact Form Submission: {self.subject}"
        html_message = render_to_string('emails/contact_notification.html', {
            'contact': self,
            'admin_url': request.build_absolute_uri(f'/admin/contact/contact/{self.id}/') if request else None,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.send_notification_email()

    class Meta:
        ordering = ['-created_at']
        db_table = 'contact_messages'