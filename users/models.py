from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


class CustomUserManager(UserManager):
    pass


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        TEACHER = "TEACHER", "Teacher"
        STUDENT = "STUDENT", "Student"
        PARENT = "PARENT", "Parent"
        BOARDING_STAFF = "BOARDING_STAFF", "Boarding Staff"

    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text="Primary role determining permissions and default dashboard",
    )

    is_boarder = models.BooleanField(default=False)

    objects = CustomUserManager()

    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"
