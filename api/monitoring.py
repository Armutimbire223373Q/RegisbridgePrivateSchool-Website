"""
Monitoring and health check system for Regisbridge College Management System
"""

import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from models.models import User, StudentProfile, TeacherProfile, Parent

logger = logging.getLogger(__name__)

class SystemMonitor:
    """System monitoring and health checks"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
    
    def increment_request_count(self):
        """Increment request counter"""
        self.request_count += 1
    
    def increment_error_count(self):
        """Increment error counter"""
        self.error_count += 1
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Database health
            db_health = self._check_database_health()
            
            # Application metrics
            uptime = datetime.now() - self.start_time
            
            health_status = {
                "status": "healthy" if self._is_healthy(cpu_percent, memory.percent, db_health) else "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": uptime.total_seconds(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                    "disk_percent": disk.percent,
                    "disk_free_gb": round(disk.free / (1024**3), 2)
                },
                "application": {
                    "request_count": self.request_count,
                    "error_count": self.error_count,
                    "error_rate": round(self.error_count / max(self.request_count, 1) * 100, 2)
                },
                "database": db_health
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            db = next(get_db())
            
            # Test basic query
            start_time = time.time()
            user_count = db.query(User).count()
            query_time = time.time() - start_time
            
            # Get table counts
            student_count = db.query(StudentProfile).count()
            teacher_count = db.query(TeacherProfile).count()
            parent_count = db.query(Parent).count()
            
            return {
                "status": "healthy",
                "query_time_ms": round(query_time * 1000, 2),
                "user_count": user_count,
                "student_count": student_count,
                "teacher_count": teacher_count,
                "parent_count": parent_count
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def _is_healthy(self, cpu_percent: float, memory_percent: float, db_health: Dict[str, Any]) -> bool:
        """Determine if system is healthy based on metrics"""
        # CPU threshold
        if cpu_percent > 90:
            return False
        
        # Memory threshold
        if memory_percent > 90:
            return False
        
        # Database health
        if db_health.get("status") != "healthy":
            return False
        
        # Query performance threshold
        if db_health.get("query_time_ms", 0) > 1000:
            return False
        
        return True
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get application metrics"""
        uptime = datetime.now() - self.start_time
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "uptime_human": str(uptime).split('.')[0],
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": round(self.error_count / max(self.request_count, 1) * 100, 2),
            "requests_per_minute": round(self.request_count / (uptime.total_seconds() / 60), 2)
        }

# Global monitor instance
monitor = SystemMonitor()

def get_system_health() -> Dict[str, Any]:
    """Get system health status"""
    return monitor.get_system_health()

def get_metrics() -> Dict[str, Any]:
    """Get application metrics"""
    return monitor.get_metrics()

def increment_request_count():
    """Increment request counter"""
    monitor.increment_request_count()

def increment_error_count():
    """Increment error counter"""
    monitor.increment_error_count()
