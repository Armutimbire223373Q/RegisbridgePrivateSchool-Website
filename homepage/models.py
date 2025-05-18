from django.db import models

# Create your models here.
class Announcement(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='announcement_images/', blank=True, null=True)
    
    def __str__(self):
        return self.title