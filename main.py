"""
FastAPI Backend for Regisbridge College Management System
"""

import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import uvicorn

from api.routers import auth, students, teachers, parents, grades, attendance, fees, payments, dashboard, admin, blog
from api import reports, notifications, search, mobile
from api.database import get_db, create_tables
from api.auth import get_current_user
from api.monitoring import get_system_health, get_metrics, increment_request_count, increment_error_count
from api.logging import log_system_event, log_error
from api.security import ALLOWED_ORIGINS
from models.models import User

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Regisbridge FastAPI Backend...")
    # Create database tables
    create_tables()
    print("✅ Database tables created/verified")
    yield
    # Shutdown
    print("🛑 Shutting down Regisbridge FastAPI Backend...")

# Create FastAPI app
app = FastAPI(
    title="Regisbridge College Management System API",
    description="A comprehensive API for managing college operations including students, teachers, parents, grades, attendance, and more.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware for monitoring
@app.middleware("http")
async def monitoring_middleware(request, call_next):
    increment_request_count()
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        increment_error_count()
        log_error(e, f"Request to {request.url}")
        raise

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(students.router, prefix="/api/v1/students", tags=["Students"])
app.include_router(teachers.router, prefix="/api/v1/teachers", tags=["Teachers"])
app.include_router(parents.router, prefix="/api/v1/parents", tags=["Parents"])
app.include_router(grades.router, prefix="/api/v1/grades", tags=["Grades"])
app.include_router(attendance.router, prefix="/api/v1/attendance", tags=["Attendance"])
app.include_router(fees.router, prefix="/api/v1/fees", tags=["Fees"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(blog.router, prefix="/api/v1/blog", tags=["Blog"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(mobile.router, prefix="/api/v1/mobile", tags=["Mobile API"])
app.include_router(admin.router, prefix="/admin", tags=["Admin Interface"])

# Mount static files for frontend
if os.path.exists("frontend/dist"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

@app.get("/")
async def root():
    """Serve the frontend application"""
    if os.path.exists("frontend/dist/index.html"):
        return FileResponse("frontend/dist/index.html")
    else:
        return {
            "message": "Welcome to Regisbridge College Management System API",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
            "note": "Frontend not built. Run 'npm run build' in frontend directory."
        }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        health_data = get_system_health()
        return health_data
    except Exception as e:
        log_error(e, "Health check failed")
        return {
            "status": "unhealthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "error": str(e)
        }

@app.get("/metrics")
async def metrics():
    """Application metrics endpoint"""
    try:
        metrics_data = get_metrics()
        return metrics_data
    except Exception as e:
        log_error(e, "Metrics retrieval failed")
        return {"error": str(e)}

@app.get("/api/v1/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "date_joined": current_user.date_joined.isoformat() if current_user.date_joined else None
    }

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Catch-all route to serve frontend for React Router"""
    if os.path.exists("frontend/dist/index.html"):
        return FileResponse("frontend/dist/index.html")
    else:
        raise HTTPException(status_code=404, detail="Frontend not found")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
