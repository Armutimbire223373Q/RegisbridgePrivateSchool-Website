from django import forms
from .models import (
    TeacherProfile, Subject, Class, ClassSubject,
    Assignment, AssignmentSubmission
)

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['teacher_id', 'qualification', 'specialization', 'phone', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 4}),
        }

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'description', 'teacher']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'grade_level', 'section', 'academic_year', 'subjects', 'students']
        widgets = {
            'subjects': forms.SelectMultiple(attrs={'class': 'select2'}),
            'students': forms.SelectMultiple(attrs={'class': 'select2'}),
        }

class ClassSubjectForm(forms.ModelForm):
    class Meta:
        model = ClassSubject
        fields = ['class_name', 'subject', 'teacher', 'schedule']
        widgets = {
            'schedule': forms.Textarea(attrs={'rows': 4}),
        }

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['file', 'grade', 'feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 4}),
            'grade': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 0.1}),
        } 