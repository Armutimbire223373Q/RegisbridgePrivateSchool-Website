import os
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from students.models import StudentProfile
from teachers.models import Subject
from grades.models import Term


def assignment_file_path(instance, filename):
    """Generate file path for assignment files"""
    return f"assignments/{instance.subject.code}/{instance.term.name}/{filename}"


def submission_file_path(instance, filename):
    """Generate file path for submission files"""
    return f"submissions/{instance.assignment.subject.code}/{instance.student.admission_number}/{filename}"


class Assignment(models.Model):
    """Assignment created by teachers"""

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("PUBLISHED", "Published"),
        ("CLOSED", "Closed"),
        ("ARCHIVED", "Archived"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="assignments"
    )
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="assignments")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignments_created",
    )

    # Assignment details
    due_date = models.DateTimeField()
    max_marks = models.PositiveIntegerField(default=100)
    instructions = models.TextField(blank=True)
    rubric = models.TextField(blank=True, help_text="Grading criteria")

    # File attachments
    attachment = models.FileField(
        upload_to=assignment_file_path,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx", "txt", "jpg", "png"]
            )
        ],
    )

    # Settings
    allow_late_submission = models.BooleanField(default=False)
    late_penalty = models.PositiveIntegerField(
        default=0, help_text="Penalty percentage for late submissions"
    )
    allow_resubmission = models.BooleanField(default=False)
    max_submissions = models.PositiveIntegerField(default=1)

    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-due_date", "subject__name"]
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"

    def __str__(self):
        return f"{self.title} - {self.subject.name} ({self.term.name})"

    @property
    def is_overdue(self):
        """Check if assignment is overdue"""
        return timezone.now() > self.due_date

    @property
    def submission_count(self):
        """Get total number of submissions"""
        return self.submissions.count()

    @property
    def graded_count(self):
        """Get number of graded submissions"""
        return self.submissions.filter(is_graded=True).count()

    def get_submission_for_student(self, student):
        """Get submission for a specific student"""
        return self.submissions.filter(student=student).first()


class AssignmentSubmission(models.Model):
    """Student submission for an assignment"""

    STATUS_CHOICES = [
        ("SUBMITTED", "Submitted"),
        ("LATE", "Late"),
        ("GRADED", "Graded"),
        ("RETURNED", "Returned"),
    ]

    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="submissions"
    )
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="assignment_submissions"
    )

    # Submission content
    content = models.TextField(blank=True)
    attachment = models.FileField(
        upload_to=submission_file_path,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx", "txt", "jpg", "png"]
            )
        ],
    )

    # Submission details
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="SUBMITTED"
    )

    # Grading
    marks_obtained = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submissions_graded",
    )
    graded_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    is_late = models.BooleanField(default=False)
    submission_number = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ["assignment", "student", "submission_number"]
        ordering = ["-submitted_at"]
        verbose_name = "Assignment Submission"
        verbose_name_plural = "Assignment Submissions"

    def __str__(self):
        return f"{self.student} - {self.assignment.title} (Submission {self.submission_number})"

    def save(self, *args, **kwargs):
        # Check if submission is late
        if self.submitted_at and self.assignment.due_date:
            self.is_late = self.submitted_at > self.assignment.due_date

        # Auto-assign status based on grading
        if self.marks_obtained is not None:
            self.status = "GRADED"

        super().save(*args, **kwargs)

    @property
    def percentage(self):
        """Calculate percentage score"""
        if self.marks_obtained and self.assignment.max_marks:
            return (self.marks_obtained / self.assignment.max_marks) * 100
        return 0

    @property
    def final_marks(self):
        """Calculate final marks with late penalty"""
        if not self.marks_obtained:
            return 0

        if self.is_late and self.assignment.late_penalty > 0:
            penalty = (self.assignment.late_penalty / 100) * self.marks_obtained
            return max(0, self.marks_obtained - penalty)

        return self.marks_obtained

    def grade_submission(self, marks, feedback, graded_by):
        """Grade the submission"""
        self.marks_obtained = marks
        self.feedback = feedback
        self.graded_by = graded_by
        self.graded_at = timezone.now()
        self.status = "GRADED"
        self.save()


class AssignmentComment(models.Model):
    """Comments on assignments or submissions"""

    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="comments"
    )
    submission = models.ForeignKey(
        AssignmentSubmission,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignment_comments",
    )

    content = models.TextField()
    is_private = models.BooleanField(
        default=False, help_text="Private comments only visible to teachers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Assignment Comment"
        verbose_name_plural = "Assignment Comments"

    def __str__(self):
        return f"Comment by {self.author} on {self.assignment.title}"
