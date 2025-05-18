from django.db import models
from school.models import Student

# Create your models here.

class Bus(models.Model):
    number = models.CharField(max_length=20)
    driver_name = models.CharField(max_length=100)
    capacity = models.IntegerField()

class Route(models.Model):
    name = models.CharField(max_length=100)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)

class Stop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    order = models.IntegerField()

class StudentTransportAssignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)

class GPSLog(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
