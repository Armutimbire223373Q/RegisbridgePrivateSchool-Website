from django.conf import settings
from django.db import models
from students.models import StudentProfile


class FeeStructure(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_boarding = models.BooleanField(default=False)

    def __str__(self) -> str:
        return (
            f"{self.name} ({'Boarding' if self.is_boarding else 'Day'}) - {self.amount}"
        )


class Invoice(models.Model):
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="invoices"
    )
    term = models.CharField(max_length=20)
    year = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "term", "year")

    def __str__(self) -> str:
        return f"Invoice {self.student} {self.term} {self.year}"


class Payment(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=30, default="CASH")
    reference = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self) -> str:
        return f"Payment {self.amount} for {self.invoice}"
