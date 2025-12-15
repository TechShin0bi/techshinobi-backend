# users/management/commands/test_email.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import time

class Command(BaseCommand):
    help = 'Test email sending'

    def handle(self, *args, **options):
        try:
            # Add a small delay to prevent rate limiting
            time.sleep(2)
            
            # Test HTML email with OTP template
            html_message = render_to_string('emails/password_reset_otp.html', {
                'user': {'username': 'Test User', 'get_full_name': 'Test User'},
                'otp': '123456'
            })
            
            send_mail(
                'Test Email from Tech Shinobi',
                'This is a test email from Tech Shinobi.',
                settings.DEFAULT_FROM_EMAIL,
                ['your-email@example.com'],  # Replace with your actual email
                html_message=html_message,
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS('Test email sent successfully!'))
            self.stdout.write(self.style.WARNING('Check your Mailtrap inbox at: https://mailtrap.io/inbox'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error sending test email: {str(e)}'))
            self.stdout.write(self.style.WARNING('Note: Mailtrap has a rate limit of 2 emails per 10 seconds on the free plan.'))