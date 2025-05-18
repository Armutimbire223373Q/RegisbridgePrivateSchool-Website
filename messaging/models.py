from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator

# Create your models here.

class MessageThread(models.Model):
    """A thread of messages between users or groups"""
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='message_threads')
    subject = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_group_thread = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} ({self.created_at.strftime('%Y-%m-%d')})"

    class Meta:
        ordering = ['-updated_at']

class Message(models.Model):
    """Individual messages within a thread"""
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_system_message = models.BooleanField(default=False)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"Message from {self.sender.get_full_name()} at {self.sent_at.strftime('%Y-%m-%d %H:%M')}"

class MessageAttachment(models.Model):
    """Files attached to messages"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(
        upload_to='message_attachments/%Y/%m/',
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png']
        )]
    )
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField()  # Size in bytes

    def __str__(self):
        return self.filename

class MessageRecipient(models.Model):
    """Tracks message read status for each recipient"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='recipients')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    read_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ['message', 'user']

class Announcement(models.Model):
    """School-wide or group-specific announcements"""
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]

    RECIPIENT_CHOICES = [
        ('all', _('Everyone')),
        ('staff', _('Staff Only')),
        ('teachers', _('Teachers Only')),
        ('students', _('Students Only')),
        ('parents', _('Parents Only')),
    ]

    title = models.CharField(max_length=255)
    body = models.TextField()
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    recipient_group = models.CharField(max_length=10, choices=RECIPIENT_CHOICES, default='all')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    send_email = models.BooleanField(default=False)
    send_sms = models.BooleanField(default=False)
    attachment = models.FileField(
        upload_to='announcements/%Y/%m/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
        )]
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"

class AnnouncementRecipient(models.Model):
    """Tracks who has read announcements"""
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='recipients')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['announcement', 'user']
