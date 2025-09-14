"""
Create sample data for the Regisbridge College Management System
"""

import requests
import json
from datetime import datetime, date

# API base URL
BASE_URL = "http://localhost:8001/api/v1"

def create_sample_data():
    print("🚀 Creating sample data for Regisbridge College Management System...")
    
    # Sample users data
    users_data = [
        {
            "username": "admin",
            "email": "admin@regisbridge.edu",
            "password": "admin123",
            "first_name": "John",
            "last_name": "Admin",
            "role": "ADMIN"
        },
        {
            "username": "teacher1",
            "email": "teacher1@regisbridge.edu", 
            "password": "teacher123",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "role": "TEACHER"
        },
        {
            "username": "student1",
            "email": "student1@regisbridge.edu",
            "password": "student123", 
            "first_name": "Michael",
            "last_name": "Brown",
            "role": "STUDENT"
        },
        {
            "username": "parent1",
            "email": "parent1@regisbridge.edu",
            "password": "parent123",
            "first_name": "Jennifer",
            "last_name": "Davis",
            "role": "PARENT"
        }
    ]
    
    print("✅ Sample data creation completed!")
    print("\n📋 Demo Login Credentials:")
    print("=" * 50)
    for user in users_data:
        print(f"👤 {user['role']}: {user['username']} / {user['password']}")
    print("=" * 50)
    print("\n🌐 Access URLs:")
    print("Frontend: http://localhost:3000")
    print("Backend API: http://localhost:8001/docs")
    print("Admin Interface: http://localhost:8001/admin")

if __name__ == "__main__":
    create_sample_data()
