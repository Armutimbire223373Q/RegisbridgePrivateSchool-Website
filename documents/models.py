from django.db import models
from school.models import Student

# Create your models here.

class IDCard(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    pdf = models.FileField(upload_to='id_cards/', blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)

class TransferCertificate(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    pdf = models.FileField(upload_to='transfer_certificates/', blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)

class LeavingCertificate(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    pdf = models.FileField(upload_to='leaving_certificates/', blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)

class AdmissionLetter(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    pdf = models.FileField(upload_to='admission_letters/', blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)
