from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import User

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """Send welcome email to new users."""
    if created:
        subject = 'Welcome to Regisbridge Private School'
        message = f'Hi {instance.get_full_name()},\n\nWelcome to Regisbridge Private School! Your account has been created successfully.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.email]
        
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            # Log the error but don't prevent user creation
            print(f"Error sending welcome email: {e}")
