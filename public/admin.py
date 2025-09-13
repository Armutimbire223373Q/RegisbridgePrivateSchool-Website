from django.contrib import admin
from django.utils.html import format_html
from .models import NewsPost


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = (
        "thumb",
        "title",
        "category",
        "author",
        "is_published",
        "published_date",
        "created_at",
    )
    list_filter = ("category", "is_published", "published_date", "created_at")
    search_fields = ("title", "content", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("is_published",)
    date_hierarchy = "published_date"

    fieldsets = (
        (
            "Content",
            {"fields": ("title", "slug", "content", "excerpt", "featured_image")},
        ),
        ("Metadata", {"fields": ("category", "author", "is_published")}),
        (
            "Timestamps",
            {
                "fields": ("published_date", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def thumb(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="height:32px;width:48px;object-fit:cover;border-radius:4px;" />',
                obj.featured_image.url,
            )
        return format_html(
            '<div style="height:32px;width:48px;background:#e5e7eb;border-radius:4px;"></div>'
        )

    thumb.short_description = "Image"
