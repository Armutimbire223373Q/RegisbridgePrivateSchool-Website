from django.db import models
from school.models import Student

# Create your models here.

class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments_payments')
    amount = models.FloatField()
    method = models.CharField(max_length=50)  # e.g., Ecocash, Bank
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)  # e.g., Success, Failed
    transaction_id = models.CharField(max_length=100, blank=True)

class Receipt(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='payments_receipts')
    pdf = models.FileField(upload_to='receipts/', blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)
