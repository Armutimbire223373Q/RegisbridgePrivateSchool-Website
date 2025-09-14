"""
Security configuration and utilities
"""

import os
from typing import List
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security constants
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

# CORS origins (should be configured via environment variables)
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173", 
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# File upload security
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = {
    'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    'document': ['pdf', 'doc', 'docx', 'txt'],
    'spreadsheet': ['xls', 'xlsx', 'csv']
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def validate_file_upload(filename: str, file_size: int, file_type: str = 'document') -> bool:
    """Validate file upload security"""
    # Check file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large"
        )
    
    # Check file extension
    file_extension = filename.lower().split('.')[-1]
    allowed_extensions = ALLOWED_FILE_TYPES.get(file_type, [])
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    return True

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks"""
    import re
    # Remove path separators and special characters
    filename = re.sub(r'[^\w\-_\.]', '', filename)
    # Remove leading dots
    filename = filename.lstrip('.')
    # Ensure filename is not empty
    if not filename:
        filename = 'unnamed_file'
    return filename

# Rate limiting configuration
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 3600  # 1 hour

# Input validation
def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 8:
        return False
    
    # Check for at least one uppercase, lowercase, digit, and special character
    import re
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True

# SQL Injection prevention (already handled by SQLAlchemy ORM)
def validate_sql_input(input_string: str) -> bool:
    """Additional validation for SQL inputs"""
    dangerous_patterns = ['--', ';', 'DROP', 'DELETE', 'UPDATE', 'INSERT', 'EXEC', 'UNION']
    input_upper = input_string.upper()
    return not any(pattern in input_upper for pattern in dangerous_patterns)
