from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse


class NewsPost(models.Model):
    """Model for news posts and announcements"""

    CATEGORY_CHOICES = [
        ("announcements", "Announcements"),
        ("events", "Events"),
        ("academic", "Academic"),
        ("sports", "Sports"),
        ("arts", "Arts & Culture"),
        ("community", "Community"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True, help_text="Short summary of the post")
    featured_image = models.ImageField(upload_to="news/", blank=True, null=True)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="announcements"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="news_posts"
    )
    is_published = models.BooleanField(default=False)
    published_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_date"]
        verbose_name = "News Post"
        verbose_name_plural = "News Posts"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("public:news_detail", kwargs={"slug": self.slug})

    @property
    def read_time(self):
        """Estimate reading time in minutes"""
        words_per_minute = 200
        word_count = len(self.content.split())
        return max(1, round(word_count / words_per_minute))
