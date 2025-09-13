from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class ReportTemplate(models.Model):
    """Report templates for different types of reports"""

    REPORT_TYPE_CHOICES = [
        ("ACADEMIC", "Academic Report"),
        ("ATTENDANCE", "Attendance Report"),
        ("FINANCIAL", "Financial Report"),
        ("PERFORMANCE", "Performance Report"),
        ("CUSTOM", "Custom Report"),
    ]

    FORMAT_CHOICES = [
        ("PDF", "PDF"),
        ("EXCEL", "Excel"),
        ("CSV", "CSV"),
        ("HTML", "HTML"),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default="PDF")

    # Template configuration
    template_file = models.FileField(upload_to="report_templates/", blank=True)
    template_content = models.TextField(
        blank=True, help_text="Template content for dynamic reports"
    )

    # Parameters and filters
    parameters = models.JSONField(
        default=dict, help_text="Report parameters and default values"
    )
    filters = models.JSONField(
        default=dict, help_text="Available filters for the report"
    )

    # Settings
    is_active = models.BooleanField(default=True)
    requires_permission = models.BooleanField(default=True)
    auto_generate = models.BooleanField(
        default=False, help_text="Generate automatically on schedule"
    )

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Report Template"
        verbose_name_plural = "Report Templates"

    def __str__(self):
        return f"{self.name} ({self.get_format_display()})"

    def get_parameters(self):
        """Get report parameters with default values"""
        return self.parameters or {}

    def get_filters(self):
        """Get available filters for the report"""
        return self.filters or {}


class Report(models.Model):
    """Generated reports"""

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("GENERATING", "Generating"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
    ]

    template = models.ForeignKey(
        ReportTemplate, on_delete=models.CASCADE, related_name="reports"
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports_generated",
    )

    # Report details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    parameters = models.JSONField(
        default=dict, help_text="Parameters used for report generation"
    )

    # File and status
    file = models.FileField(upload_to="generated_reports/", blank=True)
    file_size = models.PositiveIntegerField(
        null=True, blank=True, help_text="File size in bytes"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    # Generation details
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Report"
        verbose_name_plural = "Reports"

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    @property
    def generation_time(self):
        """Calculate report generation time"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def file_size_mb(self):
        """Get file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0

    def start_generation(self):
        """Start report generation"""
        self.status = "GENERATING"
        self.started_at = timezone.now()
        self.save()

    def complete_generation(self, file_path, file_size):
        """Complete report generation"""
        self.status = "COMPLETED"
        self.completed_at = timezone.now()
        self.file = file_path
        self.file_size = file_size
        self.save()

    def fail_generation(self, error_message):
        """Mark report generation as failed"""
        self.status = "FAILED"
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save()


class ScheduledReport(models.Model):
    """Scheduled report generation"""

    FREQUENCY_CHOICES = [
        ("DAILY", "Daily"),
        ("WEEKLY", "Weekly"),
        ("MONTHLY", "Monthly"),
        ("QUARTERLY", "Quarterly"),
        ("YEARLY", "Yearly"),
        ("CUSTOM", "Custom"),
    ]

    name = models.CharField(max_length=200)
    template = models.ForeignKey(
        ReportTemplate, on_delete=models.CASCADE, related_name="scheduled_reports"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="scheduled_reports",
    )

    # Schedule settings
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    next_run = models.DateTimeField()

    # Recipients
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="scheduled_reports_received"
    )
    send_email = models.BooleanField(default=True)
    email_subject = models.CharField(max_length=200, blank=True)
    email_message = models.TextField(blank=True)

    # Parameters
    parameters = models.JSONField(
        default=dict, help_text="Default parameters for the report"
    )

    # Status
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(
        max_length=20, choices=Report.STATUS_CHOICES, blank=True
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["next_run"]
        verbose_name = "Scheduled Report"
        verbose_name_plural = "Scheduled Reports"

    def __str__(self):
        return f"{self.name} ({self.frequency})"

    @property
    def is_overdue(self):
        """Check if scheduled report is overdue"""
        return timezone.now() > self.next_run

    def calculate_next_run(self):
        """Calculate next run time based on frequency"""
        from datetime import timedelta

        if self.last_run:
            base_date = self.last_run
        else:
            base_date = timezone.now()

        if self.frequency == "DAILY":
            next_run = base_date + timedelta(days=1)
        elif self.frequency == "WEEKLY":
            next_run = base_date + timedelta(weeks=1)
        elif self.frequency == "MONTHLY":
            next_run = base_date + timedelta(days=30)
        elif self.frequency == "QUARTERLY":
            next_run = base_date + timedelta(days=90)
        elif self.frequency == "YEARLY":
            next_run = base_date + timedelta(days=365)
        else:
            next_run = base_date + timedelta(days=1)

        self.next_run = next_run
        self.save()


class ReportAccess(models.Model):
    """User access to reports"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="report_access"
    )
    report = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name="access_permissions"
    )

    # Access details
    can_view = models.BooleanField(default=True)
    can_download = models.BooleanField(default=True)
    can_share = models.BooleanField(default=False)

    # Access tracking
    accessed_at = models.DateTimeField(null=True, blank=True)
    download_count = models.PositiveIntegerField(default=0)

    # Metadata
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="report_access_granted",
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "report"]
        verbose_name = "Report Access"
        verbose_name_plural = "Report Access"

    def __str__(self):
        return f"{self.user.username} - {self.report.title}"

    def mark_accessed(self):
        """Mark report as accessed"""
        self.accessed_at = timezone.now()
        self.save()

    def increment_download(self):
        """Increment download count"""
        self.download_count += 1
        self.save()
