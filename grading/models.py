from django.db import models
from django.conf import settings
from school.models import Student
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

# Create your models here.

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name

class GradeScale(models.Model):
    """Defines the grading scale used by the school"""
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class GradeLevel(models.Model):
    """Individual grade levels within a scale (e.g., A+, A, A-, etc.)"""
    scale = models.ForeignKey(GradeScale, on_delete=models.CASCADE, related_name='levels')
    letter = models.CharField(max_length=3)  # e.g., "A+", "B-"
    minimum_score = models.DecimalField(max_digits=5, decimal_places=2)
    maximum_score = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2)  # e.g., 4.0, 3.7
    description = models.CharField(max_length=50, blank=True)  # e.g., "Excellent", "Good"

    class Meta:
        ordering = ['-minimum_score']
        unique_together = [
            ['scale', 'letter'],
            ['scale', 'minimum_score'],
            ['scale', 'maximum_score']
        ]

    def clean(self):
        if self.minimum_score >= self.maximum_score:
            raise ValidationError(_('Minimum score must be less than maximum score'))

    def __str__(self):
        return f"{self.letter} ({self.minimum_score}-{self.maximum_score})"

class AssessmentType(models.Model):
    """Types of assessments (e.g., Quiz, Test, Exam, Assignment)"""
    name = models.CharField(max_length=50)
    weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Weight in percentage (0-100)"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.weight}%)"

class Assessment(models.Model):
    """Individual assessment instance"""
    class_group = models.ForeignKey('school.ClassGroup', on_delete=models.CASCADE)
    subject = models.ForeignKey('school.Subject', on_delete=models.CASCADE)
    assessment_type = models.ForeignKey(AssessmentType, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    max_score = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=100
    )
    date_conducted = models.DateField()
    term = models.ForeignKey('school.Term', on_delete=models.CASCADE)
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_conducted', 'subject']

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.class_group})"

class Grade(models.Model):
    """Individual student grades for assessments"""
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='student_grades')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    remarks = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='graded_grades'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'assessment']

    def clean(self):
        if self.score > self.assessment.max_score:
            raise ValidationError(_(
                f'Score cannot exceed maximum score of {self.assessment.max_score}'
            ))

    def get_percentage(self):
        return (self.score / self.assessment.max_score) * 100

    def get_letter_grade(self):
        percentage = self.get_percentage()
        grade_scale = GradeScale.objects.get(is_active=True)
        grade_level = grade_scale.levels.filter(
            minimum_score__lte=percentage,
            maximum_score__gte=percentage
        ).first()
        return grade_level.letter if grade_level else 'N/A'

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.assessment.name}: {self.score}"

class ReportCard(models.Model):
    """Term/Semester report cards"""
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='report_cards')
    term = models.ForeignKey('school.Term', on_delete=models.CASCADE)
    class_group = models.ForeignKey('school.ClassGroup', on_delete=models.CASCADE)
    average_gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    generated_pdf = models.FileField(upload_to='report_cards/')
    comments = models.TextField(blank=True)
    attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True
    )
    generated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_report_cards'
    )
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='approved_report_cards'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('pending_approval', 'Pending Approval'),
            ('approved', 'Approved'),
            ('published', 'Published')
        ],
        default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['student', 'term']
        ordering = ['-term', 'student__last_name', 'student__first_name']

    def calculate_gpa(self):
        """Calculate GPA based on all grades in the term"""
        grades = Grade.objects.filter(
            student=self.student,
            assessment__term=self.term
        ).select_related('assessment')

        total_weight = Decimal('0')
        weighted_gpa = Decimal('0')

        for grade in grades:
            percentage = grade.get_percentage()
            grade_level = GradeLevel.objects.filter(
                scale__is_active=True,
                minimum_score__lte=percentage,
                maximum_score__gte=percentage
            ).first()
            
            if grade_level:
                weight = grade.assessment.assessment_type.weight
                weighted_gpa += grade_level.grade_point * weight
                total_weight += weight

        if total_weight > 0:
            self.average_gpa = weighted_gpa / total_weight
            self.save()
        
        return self.average_gpa

    def __str__(self):
        return f"Report Card - {self.student.get_full_name()} ({self.term})"

class SubjectGrade(models.Model):
    """Final grades for each subject in a term"""
    report_card = models.ForeignKey(ReportCard, on_delete=models.CASCADE)
    subject = models.ForeignKey('school.Subject', on_delete=models.CASCADE)
    final_grade = models.CharField(max_length=3)  # Letter grade
    grade_point = models.DecimalField(max_digits=3, decimal_places=2)
    teacher_remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ['report_card', 'subject']

    def calculate_final_grade(self):
        """Calculate final grade based on all assessments in the subject"""
        grades = Grade.objects.filter(
            student=self.report_card.student,
            assessment__term=self.report_card.term,
            assessment__subject=self.subject
        ).select_related('assessment', 'assessment__assessment_type')

        total_weight = Decimal('0')
        weighted_score = Decimal('0')

        for grade in grades:
            weight = grade.assessment.assessment_type.weight
            weighted_score += grade.get_percentage() * weight
            total_weight += weight

        if total_weight > 0:
            final_percentage = weighted_score / total_weight
            grade_level = GradeLevel.objects.filter(
                scale__is_active=True,
                minimum_score__lte=final_percentage,
                maximum_score__gte=final_percentage
            ).first()
            
            if grade_level:
                self.final_grade = grade_level.letter
                self.grade_point = grade_level.grade_point
                self.save()

    def __str__(self):
        return f"{self.subject.name}: {self.final_grade}"
