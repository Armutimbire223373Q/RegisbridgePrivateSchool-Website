#!/usr/bin/env python3
"""
Startup script for the complete Regisbridge College Management System
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command, 
            cwd=cwd, 
            shell=shell, 
            check=True, 
            capture_output=True, 
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python
    success, output = run_command("python --version")
    if not success:
        print("❌ Python is not installed or not in PATH")
        return False
    print(f"✅ Python: {output.strip()}")
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("❌ Please run this script from the project root directory")
        return False
    
    print("✅ Project structure looks good")
    return True

def start_django():
    """Start Django backend"""
    print("\n🚀 Starting Django backend...")
    
    # Check if virtual environment exists
    if not Path("venv").exists():
        print("❌ Virtual environment not found. Please run: python -m venv venv")
        return False
    
    # Activate virtual environment and start Django
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        django_cmd = "python manage.py runserver 0.0.0.0:8000"
    else:  # Linux/Mac
        activate_cmd = "source venv/bin/activate"
        django_cmd = "python manage.py runserver 0.0.0.0:8000"
    
    print("Starting Django server on http://localhost:8000")
    try:
        subprocess.Popen(
            f"{activate_cmd} && {django_cmd}",
            shell=True,
            cwd=Path.cwd()
        )
        time.sleep(3)  # Give Django time to start
        print("✅ Django backend started")
        return True
    except Exception as e:
        print(f"❌ Failed to start Django: {e}")
        return False

def start_fastapi():
    """Start FastAPI backend"""
    print("\n🚀 Starting FastAPI backend...")
    
    fastapi_dir = Path("fastapi_backend")
    if not fastapi_dir.exists():
        print("❌ FastAPI backend directory not found")
        return False
    
    # Check if FastAPI virtual environment exists
    fastapi_venv = fastapi_dir / "venv"
    if not fastapi_venv.exists():
        print("❌ FastAPI virtual environment not found. Please run: cd fastapi_backend && python -m venv venv")
        return False
    
    # Start FastAPI
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        fastapi_cmd = "python start_server.py"
    else:  # Linux/Mac
        activate_cmd = "source venv/bin/activate"
        fastapi_cmd = "python start_server.py"
    
    print("Starting FastAPI server on http://localhost:8001")
    try:
        subprocess.Popen(
            f"{activate_cmd} && {fastapi_cmd}",
            shell=True,
            cwd=fastapi_dir
        )
        time.sleep(3)  # Give FastAPI time to start
        print("✅ FastAPI backend started")
        return True
    except Exception as e:
        print(f"❌ Failed to start FastAPI: {e}")
        return False

def start_frontend():
    """Start React frontend"""
    print("\n🚀 Starting React frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        print("❌ Frontend dependencies not installed. Please run: cd frontend && npm install")
        return False
    
    print("Starting React development server on http://localhost:3000")
    try:
        subprocess.Popen(
            "npm run dev",
            shell=True,
            cwd=frontend_dir
        )
        time.sleep(5)  # Give React time to start
        print("✅ React frontend started")
        return True
    except Exception as e:
        print(f"❌ Failed to start React frontend: {e}")
        return False

def main():
    """Main startup function"""
    print("🎓 Regisbridge College Management System Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start services
    services_started = 0
    
    if start_django():
        services_started += 1
    
    if start_fastapi():
        services_started += 1
    
    if start_frontend():
        services_started += 1
    
    print("\n" + "=" * 50)
    if services_started == 3:
        print("🎉 All services started successfully!")
        print("\n📱 Access your application:")
        print("   • Frontend: http://localhost:3000")
        print("   • Django Admin: http://localhost:8000/admin")
        print("   • FastAPI Docs: http://localhost:8001/docs")
        print("   • FastAPI ReDoc: http://localhost:8001/redoc")
        print("\n🛑 To stop all services, press Ctrl+C")
    else:
        print(f"⚠️  Only {services_started}/3 services started successfully")
        print("Please check the error messages above and try again")
        sys.exit(1)
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        print("✅ All services stopped")

if __name__ == "__main__":
    main()
