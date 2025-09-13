from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from students.models import StudentProfile, ClassRoom
from teachers.models import Subject


class AcademicYear(models.Model):
    """Academic year (e.g., 2024-2025)"""

    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            # Deactivate other academic years
            AcademicYear.objects.exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)


class Term(models.Model):
    """Academic term (e.g., Term 1, Term 2, Term 3)"""

    TERM_CHOICES = [
        ("TERM1", "Term 1"),
        ("TERM2", "Term 2"),
        ("TERM3", "Term 3"),
    ]

    name = models.CharField(max_length=10, choices=TERM_CHOICES)
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.CASCADE, related_name="terms"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        unique_together = ["name", "academic_year"]
        ordering = ["academic_year", "name"]

    def __str__(self):
        return f"{self.get_name_display()} - {self.academic_year.name}"


class AssessmentType(models.Model):
    """Types of assessments (e.g., Exam, Assignment, Project)"""

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    weight = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Weight as percentage of total grade",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.weight}%)"


class Assessment(models.Model):
    """Individual assessment instance"""

    title = models.CharField(max_length=200)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="assessments"
    )
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name="assessments"
    )
    assessment_type = models.ForeignKey(
        AssessmentType, on_delete=models.CASCADE, related_name="assessments"
    )
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="assessments")
    total_marks = models.PositiveIntegerField()
    due_date = models.DateField()
    instructions = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-due_date", "subject__name"]

    def __str__(self):
        return f"{self.title} - {self.subject.name} ({self.classroom.name})"


class Grade(models.Model):
    """Individual student grade for an assessment"""

    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="grades"
    )
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="grades"
    )
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="grades_given",
    )
    graded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["student", "assessment"]
        ordering = ["assessment__due_date", "student__admission_number"]

    def __str__(self):
        return f"{self.student} - {self.assessment.title}: {self.marks_obtained}/{self.assessment.total_marks}"

    @property
    def percentage(self):
        """Calculate percentage score"""
        if self.assessment.total_marks > 0:
            return (self.marks_obtained / self.assessment.total_marks) * 100
        return 0

    @property
    def letter_grade(self):
        """Convert percentage to letter grade"""
        percentage = self.percentage
        if percentage >= 80:
            return "A"
        elif percentage >= 70:
            return "B"
        elif percentage >= 60:
            return "C"
        elif percentage >= 50:
            return "D"
        else:
            return "F"


class StudentTermGrade(models.Model):
    """Aggregated term grade for a student in a subject"""

    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="term_grades"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="student_term_grades"
    )
    term = models.ForeignKey(
        Term, on_delete=models.CASCADE, related_name="student_grades"
    )
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    letter_grade = models.CharField(max_length=2, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ["student", "subject", "term"]
        ordering = ["term", "subject__name", "student__admission_number"]

    def __str__(self):
        return f"{self.student} - {self.subject.name} - {self.term.name}: {self.letter_grade}"

    def calculate_term_grade(self):
        """Calculate and update term grade based on assessments"""
        grades = Grade.objects.filter(
            student=self.student,
            assessment__subject=self.subject,
            assessment__term=self.term,
        )

        if grades.exists():
            total_weighted_marks = 0
            total_weight = 0

            for grade in grades:
                weight = grade.assessment.assessment_type.weight
                total_weighted_marks += (
                    grade.marks_obtained / grade.assessment.total_marks
                ) * weight
                total_weight += weight

            if total_weight > 0:
                self.percentage = (total_weighted_marks / total_weight) * 100
                self.letter_grade = self._get_letter_grade(self.percentage)
                self.save()

    def _get_letter_grade(self, percentage):
        """Convert percentage to letter grade"""
        if percentage >= 80:
            return "A"
        elif percentage >= 70:
            return "B"
        elif percentage >= 60:
            return "C"
        elif percentage >= 50:
            return "D"
        else:
            return "F"
