from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import (
    GradeScale, GradeLevel, AssessmentType, Assessment,
    Grade, ReportCard, SubjectGrade
)

class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = [
            'class_group', 'subject', 'assessment_type', 'name',
            'description', 'max_score', 'date_conducted'
        ]
        widgets = {
            'date_conducted': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Filter subjects based on teacher's assignments
            if user.groups.filter(name='Teachers').exists():
                self.fields['subject'].queryset = user.teaching_subjects.all()
            
            # Filter class groups based on teacher's assignments
            if user.groups.filter(name='Teachers').exists():
                self.fields['class_group'].queryset = user.teaching_classes.all()

class BulkGradeForm(forms.Form):
    assessment = forms.ModelChoiceField(queryset=Assessment.objects.none())
    
    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher:
            # Filter assessments based on teacher's subjects and classes
            self.fields['assessment'].queryset = Assessment.objects.filter(
                subject__in=teacher.teaching_subjects.all(),
                class_group__in=teacher.teaching_classes.all()
            )

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['score', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_score(self):
        score = self.cleaned_data['score']
        max_score = self.instance.assessment.max_score if self.instance else 100
        if score > max_score:
            raise ValidationError(_(
                f'Score cannot exceed maximum score of {max_score}'
            ))
        return score

class ReportCardGenerationForm(forms.Form):
    term = forms.ModelChoiceField(queryset=None)  # Will be set in __init__
    class_group = forms.ModelChoiceField(queryset=None)  # Will be set in __init__
    students = forms.ModelMultipleChoiceField(queryset=None)  # Will be set in __init__
    include_attendance = forms.BooleanField(required=False, initial=True)
    include_teacher_remarks = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['term'].queryset = school.terms.all()
            self.fields['class_group'].queryset = school.class_groups.all()
            self.fields['students'].queryset = school.students.all()

    def clean(self):
        cleaned_data = super().clean()
        class_group = cleaned_data.get('class_group')
        students = cleaned_data.get('students')

        if class_group and students:
            # Verify all selected students belong to the selected class
            invalid_students = students.exclude(student_profile__class_group=class_group)
            if invalid_students.exists():
                student_names = ", ".join([s.get_full_name() for s in invalid_students])
                raise ValidationError(_(
                    f'The following students do not belong to the selected class: {student_names}'
                ))

        return cleaned_data

class ReportCardApprovalForm(forms.ModelForm):
    class Meta:
        model = ReportCard
        fields = ['status', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_status(self):
        status = self.cleaned_data['status']
        if status == 'published' and not self.instance.approved_by:
            raise ValidationError(_('Report card must be approved before publishing'))
        return status

class SubjectGradeForm(forms.ModelForm):
    class Meta:
        model = SubjectGrade
        fields = ['teacher_remarks']
        widgets = {
            'teacher_remarks': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Calculate and display the current grade
            self.instance.calculate_final_grade()
            self.fields['current_grade'] = forms.CharField(
                initial=f"{self.instance.final_grade} ({self.instance.grade_point})",
                disabled=True,
                required=False
            ) 