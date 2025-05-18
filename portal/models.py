from django.db import models

# Create your models here.
class Message(models.Model):
    sender = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
