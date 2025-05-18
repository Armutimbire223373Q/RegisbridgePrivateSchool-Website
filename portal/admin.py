from django.contrib import admin
from .models import StudentProfile, Attendance, Grade
# Register your models here.
admin.site.register(StudentProfile)
admin.site.register(Attendance)
admin.site.register(Grade)