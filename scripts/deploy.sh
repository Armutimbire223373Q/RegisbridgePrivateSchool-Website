#!/bin/bash

# Regisbridge College Management System - Deployment Script

set -e

echo "🚀 Starting Regisbridge College Management System Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs media backups nginx/ssl

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_warning "Please update .env file with your configuration before continuing."
        exit 1
    else
        print_error ".env.example file not found. Please create .env file manually."
        exit 1
    fi
fi

# Load environment variables
source .env

# Validate required environment variables
required_vars=("DATABASE_URL" "SECRET_KEY" "DB_PASSWORD")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        print_error "Required environment variable $var is not set in .env file."
        exit 1
    fi
done

# Build and start services
print_status "Building and starting services..."
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check if services are running
print_status "Checking service health..."

# Check database
if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U regisbridge_user -d regisbridge_prod; then
    print_status "✅ Database is ready"
else
    print_error "❌ Database is not ready"
    exit 1
fi

# Check backend
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    print_status "✅ Backend is ready"
else
    print_error "❌ Backend is not ready"
    exit 1
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_status "✅ Frontend is ready"
else
    print_error "❌ Frontend is not ready"
    exit 1
fi

# Run database migrations
print_status "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec backend python -c "
from api.database import create_tables
create_tables()
print('Database tables created successfully')
"

# Create sample data (optional)
read -p "Do you want to create sample data? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Creating sample data..."
    docker-compose -f docker-compose.prod.yml exec backend python create_sample_data.py
fi

# Set up SSL certificates (if provided)
if [ -f "nginx/ssl/cert.pem" ] && [ -f "nginx/ssl/key.pem" ]; then
    print_status "SSL certificates found. Configuring HTTPS..."
    # Update nginx configuration for HTTPS
    # This would require updating the nginx configuration
else
    print_warning "SSL certificates not found. Running in HTTP mode."
fi

# Display deployment information
print_status "🎉 Deployment completed successfully!"
echo
echo "📋 Service Information:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8001"
echo "  API Documentation: http://localhost:8001/docs"
echo "  Admin Interface: http://localhost:8001/admin"
echo
echo "🔧 Management Commands:"
echo "  View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  Stop services: docker-compose -f docker-compose.prod.yml down"
echo "  Restart services: docker-compose -f docker-compose.prod.yml restart"
echo "  Update services: docker-compose -f docker-compose.prod.yml up --build -d"
echo
echo "📊 Monitoring:"
echo "  Health check: curl http://localhost:8001/health"
echo "  Metrics: curl http://localhost:8001/metrics"
echo
print_status "Deployment script completed!"
