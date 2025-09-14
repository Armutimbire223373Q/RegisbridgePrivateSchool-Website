"""
Logging configuration for Regisbridge College Management System
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging
def setup_logging():
    """Setup comprehensive logging for the application"""
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for general logs
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error handler for errors
    error_handler = logging.FileHandler(log_dir / "errors.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Security handler for security events
    security_handler = logging.FileHandler(log_dir / "security.log")
    security_handler.setLevel(logging.WARNING)
    security_handler.setFormatter(detailed_formatter)
    
    security_logger = logging.getLogger("security")
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.WARNING)
    
    # API handler for API requests
    api_handler = logging.FileHandler(log_dir / "api.log")
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(detailed_formatter)
    
    api_logger = logging.getLogger("api")
    api_logger.addHandler(api_handler)
    api_logger.setLevel(logging.INFO)
    
    return root_logger

# Initialize logging
logger = setup_logging()

def log_security_event(event_type: str, user_id: int = None, ip_address: str = None, details: str = ""):
    """Log security-related events"""
    security_logger = logging.getLogger("security")
    message = f"SECURITY_EVENT: {event_type}"
    if user_id:
        message += f" | User: {user_id}"
    if ip_address:
        message += f" | IP: {ip_address}"
    if details:
        message += f" | Details: {details}"
    
    security_logger.warning(message)

def log_api_request(method: str, endpoint: str, user_id: int = None, status_code: int = None, duration: float = None):
    """Log API requests"""
    api_logger = logging.getLogger("api")
    message = f"API_REQUEST: {method} {endpoint}"
    if user_id:
        message += f" | User: {user_id}"
    if status_code:
        message += f" | Status: {status_code}"
    if duration:
        message += f" | Duration: {duration:.3f}s"
    
    api_logger.info(message)

def log_user_action(action: str, user_id: int, details: str = ""):
    """Log user actions"""
    logger.info(f"USER_ACTION: {action} | User: {user_id} | Details: {details}")

def log_system_event(event: str, details: str = ""):
    """Log system events"""
    logger.info(f"SYSTEM_EVENT: {event} | Details: {details}")

def log_error(error: Exception, context: str = ""):
    """Log errors with context"""
    logger.error(f"ERROR: {str(error)} | Context: {context}", exc_info=True)
