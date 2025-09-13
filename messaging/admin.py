from django.contrib import admin
from .models import Thread, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "created_at")
    filter_horizontal = ("participants",)
    inlines = [MessageInline]
