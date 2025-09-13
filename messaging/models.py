from django.conf import settings
from django.db import models


class Thread(models.Model):
    title = models.CharField(max_length=150)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="threads_created",
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="threads"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class Message(models.Model):
    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages_sent"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="messages_read", blank=True
    )

    class Meta:
        ordering = ("created_at",)

    def __str__(self) -> str:
        return f"{self.sender}: {self.content[:30]}"
