from django.contrib import admin
from .models import (
    NotificationType,
    Notification,
    UserNotification,
    NotificationTemplate,
    NotificationPreference,
)


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "template_type", "is_active")
    list_filter = ("template_type", "is_active")
    search_fields = ("name", "subject")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "recipient",
        "notification_type",
        "priority",
        "status",
        "scheduled_at",
        "sent_at",
        "created_at",
    )
    list_filter = ("priority", "status", "scheduled_at", "sent_at", "created_at")
    search_fields = ("title", "message", "recipient__username")
    readonly_fields = ("created_at", "updated_at", "sent_at")
    actions = ("mark_as_sent", "mark_as_failed", "cancel_notifications")

    def mark_as_sent(self, request, queryset):
        updated = 0
        for n in queryset:
            n.mark_as_sent()
            updated += 1
        self.message_user(request, f"Marked {updated} notifications as sent.")

    def mark_as_failed(self, request, queryset):
        count = queryset.update(status="FAILED")
        self.message_user(request, f"Marked {count} notifications as failed.")

    def cancel_notifications(self, request, queryset):
        count = queryset.update(status="CANCELLED")
        self.message_user(request, f"Cancelled {count} notifications.")

    mark_as_sent.short_description = "Mark selected as sent"
    mark_as_failed.short_description = "Mark selected as failed"
    cancel_notifications.short_description = "Cancel selected notifications"


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "notification", "is_read", "read_at", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "notification__title")
    actions = ("mark_read", "mark_unread")

    def mark_read(self, request, queryset):
        updated = 0
        for un in queryset:
            if not un.is_read:
                un.mark_as_read()
                updated += 1
        self.message_user(request, f"Marked {updated} as read.")

    def mark_unread(self, request, queryset):
        updated = 0
        for un in queryset:
            if un.is_read:
                un.mark_as_unread()
                updated += 1
        self.message_user(request, f"Marked {updated} as unread.")

    mark_read.short_description = "Mark selected as read"
    mark_unread.short_description = "Mark selected as unread"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "email_notifications",
        "sms_notifications",
        "push_notifications",
        "email_frequency",
    )
    list_filter = (
        "email_notifications",
        "sms_notifications",
        "push_notifications",
        "email_frequency",
    )
    search_fields = ("user__username", "user__email")
