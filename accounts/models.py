from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class User(AbstractUser):
    """Custom User model."""
    # Add custom fields
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    # User type fields
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_staff_member = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return self.get_full_name() or self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
