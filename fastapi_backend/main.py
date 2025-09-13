"""
FastAPI Backend for Regisbridge College Management System
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path to access Django models
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'regisbridge.settings.base')

import django
django.setup()

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn

from api.routers import auth, students, teachers, parents, grades, attendance, fees, dashboard
from api.database import get_db
from api.auth import get_current_user
from api.models import User

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Regisbridge FastAPI Backend...")
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
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(students.router, prefix="/api/v1/students", tags=["Students"])
app.include_router(teachers.router, prefix="/api/v1/teachers", tags=["Teachers"])
app.include_router(parents.router, prefix="/api/v1/parents", tags=["Parents"])
app.include_router(grades.router, prefix="/api/v1/grades", tags=["Grades"])
app.include_router(attendance.router, prefix="/api/v1/attendance", tags=["Attendance"])
app.include_router(fees.router, prefix="/api/v1/fees", tags=["Fees"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Regisbridge College Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "regisbridge-api"}

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

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
