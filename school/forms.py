from django import forms
from django.contrib.auth.models import User
from .models import Employee, EmployeeDocument, LeaveRequest, PerformanceReview, TrainingProgram

# ... existing code ...

class EmployeeForm(forms.ModelForm):
    """Form for creating and updating employee information."""
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'department', 'designation', 'date_joined',
            'status', 'contact_number', 'emergency_contact', 'address',
            'salary'
        ]
        widgets = {
            'date_joined': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id:
            # Check if employee_id exists for other employees
            if Employee.objects.filter(employee_id=employee_id).exclude(id=self.instance.id if self.instance else None).exists():
                raise forms.ValidationError('This Employee ID is already in use.')
        return employee_id

class EmployeeDocumentForm(forms.ModelForm):
    """Form for uploading employee documents."""
    class Meta:
        model = EmployeeDocument
        fields = ['document_type', 'title', 'file', 'notes']
        
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Limit file size to 5MB
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must not exceed 5MB.')
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            ext = str(file.name).lower()[-4:]
            if ext not in allowed_extensions:
                raise forms.ValidationError('Only PDF, DOC, DOCX, JPG, JPEG and PNG files are allowed.')
        return file

class LeaveRequestForm(forms.ModelForm):
    """Form for submitting leave requests."""
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError('End date must be after start date.')
                
            # Check for overlapping leave requests
            employee = self.instance.employee if self.instance else None
            if employee:
                overlapping = LeaveRequest.objects.filter(
                    employee=employee,
                    status__in=['PENDING', 'APPROVED'],
                    start_date__lte=end_date,
                    end_date__gte=start_date
                ).exclude(id=self.instance.id if self.instance else None)
                
                if overlapping.exists():
                    raise forms.ValidationError('You already have an overlapping leave request for this period.')
        
        return cleaned_data

class PerformanceReviewForm(forms.ModelForm):
    """Form for submitting performance reviews."""
    class Meta:
        model = PerformanceReview
        fields = [
            'employee', 'review_date', 'performance_score',
            'strengths', 'areas_for_improvement', 'goals', 'comments'
        ]
        widgets = {
            'review_date': forms.DateInput(attrs={'type': 'date'}),
            'strengths': forms.Textarea(attrs={'rows': 3}),
            'areas_for_improvement': forms.Textarea(attrs={'rows': 3}),
            'goals': forms.Textarea(attrs={'rows': 3}),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }
        
    def clean_review_date(self):
        review_date = self.cleaned_data.get('review_date')
        if review_date:
            # Check if a review already exists for this date
            employee = self.instance.employee if self.instance else None
            if employee:
                existing_review = PerformanceReview.objects.filter(
                    employee=employee,
                    review_date=review_date
                ).exclude(id=self.instance.id if self.instance else None)
                
                if existing_review.exists():
                    raise forms.ValidationError('A performance review already exists for this date.')
        return review_date

class TrainingProgramForm(forms.ModelForm):
    class Meta:
        model = TrainingProgram
        fields = ['title', 'description', 'start_date', 'end_date', 
                 'capacity', 'instructor', 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date")
        return cleaned_data 