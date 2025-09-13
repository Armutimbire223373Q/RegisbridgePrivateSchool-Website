"""
Database configuration and connection management for FastAPI
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

# Database URL from environment or Django settings
DATABASE_URL = config('DATABASE_URL', default='sqlite:///../db.sqlite3')

# Create SQLAlchemy engine
if DATABASE_URL.startswith('postgres'):
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )
else:
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_db():
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_django_db():
    """
    Get Django database connection for direct model access
    """
    from django.db import connection
    return connection
