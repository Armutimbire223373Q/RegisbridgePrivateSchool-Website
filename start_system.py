"""
Start script for the complete Regisbridge College Management System
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Run a command and return the process"""
    print(f"🚀 Running: {command}")
    return subprocess.Popen(
        command,
        cwd=cwd,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

def check_port(port):
    """Check if a port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0

def main():
    """Main startup function"""
    print("🎓 Starting Regisbridge College Management System...")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Error: main.py not found. Please run from the project root.")
        sys.exit(1)
    
    # Check if frontend directory exists
    if not Path("frontend").exists():
        print("❌ Error: frontend directory not found.")
        sys.exit(1)
    
    processes = []
    
    try:
        # Start FastAPI backend
        print("\n🔧 Starting FastAPI Backend...")
        if not check_port(8001):
            print("⚠️  Port 8001 is already in use. Backend may already be running.")
        else:
            backend_process = run_command("python start_server.py")
            processes.append(("Backend", backend_process))
            time.sleep(3)  # Give backend time to start
        
        # Start React frontend
        print("\n🎨 Starting React Frontend...")
        if not check_port(3000):
            print("⚠️  Port 3000 is already in use. Frontend may already be running.")
        else:
            frontend_process = run_command("npm run dev", cwd="frontend")
            processes.append(("Frontend", frontend_process))
            time.sleep(3)  # Give frontend time to start
        
        # Display access information
        print("\n" + "=" * 60)
        print("🎉 Regisbridge College Management System is starting!")
        print("=" * 60)
        print("📊 Access Points:")
        print("  • API Documentation: http://localhost:8001/docs")
        print("  • Admin Interface:   http://localhost:8001/admin")
        print("  • Frontend:          http://localhost:3000")
        print("  • Health Check:      http://localhost:8001/health")
        print("\n🔧 Services:")
        for name, process in processes:
            if process.poll() is None:
                print(f"  ✅ {name}: Running (PID: {process.pid})")
            else:
                print(f"  ❌ {name}: Failed to start")
        
        print("\n💡 Tips:")
        print("  • Press Ctrl+C to stop all services")
        print("  • Check logs for any errors")
        print("  • Visit /docs for API documentation")
        
        print("\n⏳ Services are starting up... Please wait a moment.")
        print("   You can check the status by visiting the URLs above.")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
                # Check if any process has died
                for name, process in processes:
                    if process.poll() is not None:
                        print(f"\n❌ {name} has stopped unexpectedly!")
                        return_code = process.returncode
                        stdout, stderr = process.communicate()
                        if stderr:
                            print(f"Error: {stderr}")
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down services...")
            
    except Exception as e:
        print(f"\n❌ Error starting system: {e}")
        sys.exit(1)
    
    finally:
        # Clean up processes
        for name, process in processes:
            if process.poll() is None:
                print(f"🛑 Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        print("✅ All services stopped.")

if __name__ == "__main__":
    main()
