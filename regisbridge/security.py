"""
Security configurations and utilities for Regisbridge
"""

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def role_required(*roles):
    """
    Decorator to require specific user roles
    Usage: @role_required('ADMIN', 'TEACHER')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Authentication required")
            
            if request.user.role not in roles:
                logger.warning(
                    f"Access denied for user {request.user.username} "
                    f"with role {request.user.role} to {view_func.__name__}"
                )
                raise PermissionDenied("Insufficient permissions")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Decorator to require admin role"""
    return role_required('ADMIN')(view_func)


def teacher_required(view_func):
    """Decorator to require teacher role"""
    return role_required('TEACHER')(view_func)


def student_required(view_func):
    """Decorator to require student role"""
    return role_required('STUDENT')(view_func)


def parent_required(view_func):
    """Decorator to require parent role"""
    return role_required('PARENT')(view_func)


def staff_required(view_func):
    """Decorator to require staff role (admin, teacher, or boarding staff)"""
    return role_required('ADMIN', 'TEACHER', 'BOARDING_STAFF')(view_func)


class SecurityMiddleware:
    """
    Custom security middleware for additional protection
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add security headers
        response = self.get_response(request)
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response['Content-Security-Policy'] = csp
        
        return response


def log_security_event(event_type, user, details=None):
    """
    Log security events for monitoring
    """
    logger.info(
        f"Security Event: {event_type} - User: {user.username if user.is_authenticated else 'Anonymous'} - "
        f"Details: {details or 'N/A'}"
    )


def check_user_permissions(user, resource_type, resource_id=None):
    """
    Check if user has permissions to access a specific resource
    """
    if not user.is_authenticated:
        return False
    
    # Admin has access to everything
    if user.role == 'ADMIN':
        return True
    
    # Role-based access control
    if resource_type == 'student_profile':
        if user.role == 'STUDENT':
            try:
                return user.student_profile.id == resource_id
            except:
                return False
        elif user.role == 'PARENT':
            try:
                parent_profile = user.parent_profile
                return parent_profile.students.filter(id=resource_id).exists()
            except:
                return False
        elif user.role == 'TEACHER':
            # Teachers can access students in their classes
            try:
                teacher_profile = user.teacher_profile
                return StudentProfile.objects.filter(
                    id=resource_id,
                    classroom__teachers=teacher_profile
                ).exists()
            except:
                return False
    
    elif resource_type == 'grade':
        if user.role == 'STUDENT':
            try:
                grade = Grade.objects.get(id=resource_id)
                return grade.student.user == user
            except:
                return False
        elif user.role == 'PARENT':
            try:
                grade = Grade.objects.get(id=resource_id)
                parent_profile = user.parent_profile
                return parent_profile.students.filter(id=grade.student.id).exists()
            except:
                return False
        elif user.role == 'TEACHER':
            try:
                grade = Grade.objects.get(id=resource_id)
                teacher_profile = user.teacher_profile
                return grade.assessment.subject in teacher_profile.subjects.all()
            except:
                return False
    
    elif resource_type == 'invoice':
        if user.role == 'STUDENT':
            try:
                invoice = Invoice.objects.get(id=resource_id)
                return invoice.student.user == user
            except:
                return False
        elif user.role == 'PARENT':
            try:
                invoice = Invoice.objects.get(id=resource_id)
                parent_profile = user.parent_profile
                return parent_profile.students.filter(id=invoice.student.id).exists()
            except:
                return False
    
    return False


def sanitize_input(data):
    """
    Sanitize user input to prevent XSS and other attacks
    """
    import html
    import re
    
    if isinstance(data, str):
        # HTML escape
        data = html.escape(data)
        
        # Remove potentially dangerous characters
        data = re.sub(r'[<>"\']', '', data)
        
        # Limit length
        data = data[:1000]
    
    return data


def validate_file_upload(file):
    """
    Validate uploaded files for security
    """
    import os
    from django.core.exceptions import ValidationError
    
    # Allowed file types
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt']
    allowed_mime_types = [
        'image/jpeg', 'image/png', 'image/gif',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
    ]
    
    # Check file extension
    file_extension = os.path.splitext(file.name)[1].lower()
    if file_extension not in allowed_extensions:
        raise ValidationError(f"File type {file_extension} is not allowed")
    
    # Check MIME type
    if file.content_type not in allowed_mime_types:
        raise ValidationError(f"MIME type {file.content_type} is not allowed")
    
    # Check file size (5MB limit)
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError("File size exceeds 5MB limit")
    
    return True


def rate_limit_check(user, action, limit=10, window=60):
    """
    Check if user has exceeded rate limit for an action
    """
    from django.core.cache import cache
    from django.utils import timezone
    
    if not user.is_authenticated:
        return False
    
    cache_key = f"rate_limit_{user.id}_{action}"
    current_count = cache.get(cache_key, 0)
    
    if current_count >= limit:
        log_security_event('RATE_LIMIT_EXCEEDED', user, f"Action: {action}")
        return False
    
    # Increment counter
    cache.set(cache_key, current_count + 1, window)
    return True


def audit_log(user, action, resource_type, resource_id=None, details=None):
    """
    Create audit log entry for security monitoring
    """
    from django.utils import timezone
    
    log_entry = {
        'timestamp': timezone.now().isoformat(),
        'user_id': user.id if user.is_authenticated else None,
        'username': user.username if user.is_authenticated else 'Anonymous',
        'action': action,
        'resource_type': resource_type,
        'resource_id': resource_id,
        'details': details,
        'ip_address': getattr(user, 'ip_address', None)
    }
    
    logger.info(f"Audit Log: {log_entry}")


# Import models for permission checking
try:
    from students.models import StudentProfile
    from grades.models import Grade
    from fees.models import Invoice
except ImportError:
    # Models not available during initial setup
    pass


