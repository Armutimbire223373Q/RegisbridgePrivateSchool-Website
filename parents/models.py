from django.db import models
from django.conf import settings
from students.models import StudentProfile


class Parent(models.Model):
    RELATIONSHIP_CHOICES = [
        ("FATHER", "Father"),
        ("MOTHER", "Mother"),
        ("GUARDIAN", "Guardian"),
        ("SIBLING", "Sibling"),
        ("OTHER", "Other"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="parent_profile",
    )
    students = models.ManyToManyField(
        StudentProfile, related_name="parents", blank=True
    )
    relationship = models.CharField(
        max_length=20, choices=RELATIONSHIP_CHOICES, default="GUARDIAN"
    )

    # Contact Information
    phone_number = models.CharField(max_length=20, blank=True)
    alternative_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="Kenya")

    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)

    # Additional Information
    occupation = models.CharField(max_length=100, blank=True)
    employer = models.CharField(max_length=100, blank=True)
    is_primary_contact = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]
        verbose_name = "Parent"
        verbose_name_plural = "Parents"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_relationship_display()}"

    def get_primary_student(self):
        """Get the primary student if this parent is the primary contact"""
        if self.is_primary_contact and self.students.exists():
            return self.students.first()
        return None

    def can_access_student(self, student):
        """Check if parent has access to student information"""
        return self.students.filter(id=student.id).exists()
