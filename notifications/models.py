from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class NotificationType(models.Model):
    """Types of notifications"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    template_subject = models.CharField(
        max_length=200, help_text="Email subject template"
    )
    template_body = models.TextField(help_text="Email body template")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Notification(models.Model):
    """System notifications for users"""

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("NORMAL", "Normal"),
        ("HIGH", "High"),
        ("URGENT", "Urgent"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SENT", "Sent"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
    ]

    # Recipient
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )

    # Notification details
    notification_type = models.ForeignKey(
        NotificationType, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default="NORMAL"
    )

    # Content type for generic relations
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    # Delivery settings
    send_email = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=False)
    send_push = models.BooleanField(default=False)

    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"

    @property
    def is_read(self):
        """Check if notification has been read"""
        return hasattr(self, "user_notification") and self.user_notification.is_read

    @property
    def is_overdue(self):
        """Check if scheduled notification is overdue"""
        if self.scheduled_at:
            return timezone.now() > self.scheduled_at
        return False

    def mark_as_sent(self):
        """Mark notification as sent"""
        self.status = "SENT"
        self.sent_at = timezone.now()
        self.save()

    def mark_as_failed(self):
        """Mark notification as failed"""
        self.status = "FAILED"
        self.save()


class UserNotification(models.Model):
    """User-specific notification settings and read status"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_notifications",
    )
    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, related_name="user_notifications"
    )

    # Read status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # User preferences
    is_muted = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "notification"]
        ordering = ["-created_at"]
        verbose_name = "User Notification"
        verbose_name_plural = "User Notifications"

    def __str__(self):
        return f"{self.user.username} - {self.notification.title}"

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()

    def mark_as_unread(self):
        """Mark notification as unread"""
        self.is_read = False
        self.read_at = None
        self.save()


class NotificationTemplate(models.Model):
    """Email and SMS notification templates"""

    TEMPLATE_TYPE_CHOICES = [
        ("EMAIL", "Email"),
        ("SMS", "SMS"),
        ("PUSH", "Push Notification"),
    ]

    name = models.CharField(max_length=100, unique=True)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES)
    subject = models.CharField(max_length=200, blank=True)
    body = models.TextField()

    # Variables that can be used in templates
    variables = models.JSONField(default=dict, help_text="Available template variables")

    # Settings
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Notification Template"
        verbose_name_plural = "Notification Templates"

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"

    def render_template(self, context):
        """Render template with given context"""
        try:
            from django.template import Template, Context

            template = Template(self.body)
            return template.render(Context(context))
        except Exception as e:
            return f"Template rendering error: {str(e)}"


class NotificationPreference(models.Model):
    """User notification preferences"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )

    # Email preferences
    email_notifications = models.BooleanField(default=True)
    email_frequency = models.CharField(
        max_length=20,
        choices=[
            ("IMMEDIATE", "Immediate"),
            ("DAILY", "Daily Digest"),
            ("WEEKLY", "Weekly Digest"),
        ],
        default="IMMEDIATE",
    )

    # SMS preferences
    sms_notifications = models.BooleanField(default=False)
    sms_phone = models.CharField(max_length=20, blank=True)

    # Push notification preferences
    push_notifications = models.BooleanField(default=True)

    # Category preferences
    academic_notifications = models.BooleanField(default=True)
    attendance_notifications = models.BooleanField(default=True)
    fee_notifications = models.BooleanField(default=True)
    general_notifications = models.BooleanField(default=True)

    # Quiet hours
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Notification Preference"
        verbose_name_plural = "Notification Preferences"

    def __str__(self):
        return f"Preferences for {self.user.username}"

    @property
    def is_in_quiet_hours(self):
        """Check if current time is in quiet hours"""
        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False

        now = timezone.now().time()
        start = self.quiet_hours_start
        end = self.quiet_hours_end

        if start <= end:
            return start <= now <= end
        else:  # Quiet hours span midnight
            return now >= start or now <= end
