"""
Database configuration and connection management for FastAPI
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config
from models.models import Base

# Database URL from environment
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

def get_db():
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all database tables
    """
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """
    Drop all database tables
    """
    Base.metadata.drop_all(bind=engine)
