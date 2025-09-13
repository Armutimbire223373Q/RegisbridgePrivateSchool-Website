from django.db import models
from django.utils import timezone
from students.models import StudentProfile, GradeLevel


class FeeStructure(models.Model):
    TUITION = "TUITION"
    BOARDING = "BOARDING"
    OTHER = "OTHER"
    TYPE_CHOICES = ((TUITION, "Tuition"), (BOARDING, "Boarding"), (OTHER, "Other"))

    grade_level = models.ForeignKey(
        GradeLevel, on_delete=models.CASCADE, related_name="fee_structures"
    )
    fee_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    term = models.CharField(max_length=20, help_text="e.g. Term 1 / 2025")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("grade_level", "fee_type", "term")
        ordering = ("grade_level__name", "fee_type")

    def __str__(self) -> str:
        return f"{self.grade_level} - {self.fee_type} - {self.term}: {self.amount}"


class Invoice(models.Model):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PAID = "PAID"
    PARTIAL = "PARTIAL"
    CANCELLED = "CANCELLED"
    STATUS_CHOICES = (
        (DRAFT, "Draft"),
        (ISSUED, "Issued"),
        (PAID, "Paid"),
        (PARTIAL, "Partially Paid"),
        (CANCELLED, "Cancelled"),
    )

    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="invoices"
    )
    term = models.CharField(max_length=20)
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=DRAFT)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ("-issue_date",)

    def __str__(self) -> str:
        return f"INV-{self.id} {self.student} {self.term} ({self.status})"


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="lines")
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.description} - {self.amount}"


class Payment(models.Model):
    CASH = "CASH"
    BANK = "BANK"
    MOBILE = "MOBILE"
    METHOD_CHOICES = ((CASH, "Cash"), (BANK, "Bank"), (MOBILE, "Mobile Money"))

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="payments"
    )
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    reference = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ("-date",)

    def __str__(self) -> str:
        return f"PAY-{self.id} {self.amount} for INV-{self.invoice_id}"


class Receipt(models.Model):
    payment = models.OneToOneField(
        Payment, on_delete=models.CASCADE, related_name="receipt"
    )
    number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"RCT-{self.number}"


# Create your models here.
