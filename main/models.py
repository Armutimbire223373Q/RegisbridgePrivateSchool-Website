from django.db import models
from django.utils.text import slugify
from django.core.validators import MinLengthValidator, RegexValidator, FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import os

def validate_image_size(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB
        raise ValidationError(_("The maximum file size that can be uploaded is 5MB"))

def get_upload_path(instance, filename):
    return os.path.join('pages', str(instance.id), filename)

class Page(models.Model):
    """Base model for static pages."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text=_("A unique slug for the URL"))
    content = models.TextField(validators=[MinLengthValidator(10)])
    meta_description = models.CharField(max_length=160, blank=True)
    featured_image = models.ImageField(
        upload_to=get_upload_path,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']),
            validate_image_size
        ]
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_published']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def clean(self):
        if self.featured_image and not self.featured_image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            raise ValidationError(_("Only JPG, PNG, and GIF images are allowed."))

class AboutPage(models.Model):
    """Model for the About page content."""
    page = models.OneToOneField(Page, on_delete=models.CASCADE, related_name='about_page')
    mission_statement = models.TextField(
        validators=[MinLengthValidator(10)],
        default="Our mission is to provide quality education."
    )
    vision_statement = models.TextField(
        validators=[MinLengthValidator(10)],
        default="Our vision is to be a leading educational institution."
    )
    values = models.TextField(
        validators=[MinLengthValidator(10)],
        default="Excellence, Integrity, Innovation"
    )
    history = models.TextField(
        validators=[MinLengthValidator(10)],
        default="Our school has a rich history of academic excellence."
    )
    leadership_team = models.TextField(
        help_text="HTML content for leadership team section",
        validators=[MinLengthValidator(10)],
        default="Our leadership team is committed to excellence in education."
    )

    class Meta:
        verbose_name = _('About Page')
        verbose_name_plural = _('About Pages')

    def __str__(self):
        return self.page.title

    def clean(self):
        if not self.page.is_published:
            raise ValidationError(_("The associated page must be published."))

class AcademicsPage(models.Model):
    """Model for the Academics page content."""
    page = models.OneToOneField(Page, on_delete=models.CASCADE, related_name='academics_page')
    programs_overview = models.TextField(
        validators=[MinLengthValidator(10)],
        default="Our academic programs are designed to foster excellence."
    )
    curriculum_overview = models.TextField(
        validators=[MinLengthValidator(10)],
        default="Our curriculum is comprehensive and challenging."
    )
    faculty_highlight = models.TextField(
        validators=[MinLengthValidator(10)],
        default="Our faculty members are highly qualified and dedicated."
    )
    academic_support = models.TextField(
        validators=[MinLengthValidator(10)],
        default="We provide comprehensive academic support services."
    )

    class Meta:
        verbose_name = _('Academics Page')
        verbose_name_plural = _('Academics Pages')

    def __str__(self):
        return self.page.title

    def clean(self):
        if not self.page.is_published:
            raise ValidationError(_("The associated page must be published."))

class CurriculumPage(models.Model):
    """Model for the Curriculum page content."""
    page = models.OneToOneField(Page, on_delete=models.CASCADE, related_name='curriculum_page')
    GRADE_CHOICES = [
        ('elementary', 'Elementary School'),
        ('middle', 'Middle School'),
        ('high', 'High School'),
    ]
    
    grade_level = models.CharField(
        max_length=50,
        choices=GRADE_CHOICES,
        default='elementary',
        unique=True
    )
    subjects = models.TextField(
        validators=[MinLengthValidator(10)],
        default="Our curriculum includes core subjects and enrichment programs."
    )
    learning_outcomes = models.TextField(
        validators=[MinLengthValidator(10)],
        default="Students will develop critical thinking and problem-solving skills."
    )

    class Meta:
        verbose_name = _('Curriculum Page')
        verbose_name_plural = _('Curriculum Pages')
        ordering = ['grade_level']
        unique_together = ['page', 'grade_level']

    def __str__(self):
        return f"{self.page.title} - {self.get_grade_level_display()}"

    def clean(self):
        if not self.page.is_published:
            raise ValidationError(_("The associated page must be published."))

class StudentLifePage(models.Model):
    """Model for the Student Life page content."""
    page = models.OneToOneField(Page, on_delete=models.CASCADE, related_name='student_life_page')
    activities = models.TextField(
        validators=[MinLengthValidator(10)],
        default="We offer a wide range of extracurricular activities."
    )
    clubs = models.TextField(
        validators=[MinLengthValidator(10)],
        default="Join our diverse student clubs and organizations."
    )
    sports = models.TextField(
        validators=[MinLengthValidator(10)],
        default="Our sports program promotes teamwork and excellence."
    )

    class Meta:
        verbose_name = _('Student Life Page')
        verbose_name_plural = _('Student Life Pages')

    def __str__(self):
        return self.page.title

    def clean(self):
        if not self.page.is_published:
            raise ValidationError(_("The associated page must be published."))

class ContactPage(models.Model):
    """Model for the Contact page content."""
    page = models.OneToOneField(Page, on_delete=models.CASCADE, related_name='contact_page')
    address = models.TextField(
        validators=[MinLengthValidator(10)],
        default="123 School Street, City, State, ZIP"
    )
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        default="+1234567890"
    )
    email = models.EmailField(default="contact@regisbridge.com")
    office_hours = models.TextField(default="Monday to Friday: 8:00 AM - 4:00 PM")
    map_embed_code = models.TextField(
        blank=True,
        help_text="Google Maps embed code",
        validators=[MinLengthValidator(10)]
    )

    class Meta:
        verbose_name = _('Contact Page')
        verbose_name_plural = _('Contact Pages')

    def __str__(self):
        return self.page.title

    def clean(self):
        if not self.page.is_published:
            raise ValidationError(_("The associated page must be published."))

class FAQ(models.Model):
    """Model for Frequently Asked Questions."""
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('admissions', 'Admissions'),
        ('academics', 'Academics'),
        ('student_life', 'Student Life'),
        ('parents', 'Parents'),
    ]
    
    question = models.CharField(max_length=200)
    answer = models.TextField(
        validators=[MinLengthValidator(10)],
        default="Please contact us for more information."
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='general'
    )
    is_published = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_published']),
        ]

    def __str__(self):
        return self.question

    def clean(self):
        if self.order < 0:
            raise ValidationError(_("Order must be a positive number."))
