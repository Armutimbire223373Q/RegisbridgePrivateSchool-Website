#!/bin/bash

# Regisbridge College Management System - Backup Script

set -e

# Configuration
BACKUP_DIR="/backups"
DB_NAME="regisbridge_prod"
DB_USER="regisbridge_user"
DB_HOST="db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="regisbridge_backup_${TIMESTAMP}.sql"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create backup directory if it doesn't exist
mkdir -p ${BACKUP_DIR}

print_status "Starting backup process..."

# Database backup
print_status "Creating database backup..."
pg_dump -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} > ${BACKUP_DIR}/${BACKUP_FILE}

if [ $? -eq 0 ]; then
    print_status "✅ Database backup created: ${BACKUP_FILE}"
    
    # Compress backup
    gzip ${BACKUP_DIR}/${BACKUP_FILE}
    print_status "✅ Backup compressed: ${BACKUP_FILE}.gz"
    
    # Get backup size
    BACKUP_SIZE=$(du -h ${BACKUP_DIR}/${BACKUP_FILE}.gz | cut -f1)
    print_status "Backup size: ${BACKUP_SIZE}"
    
else
    print_error "❌ Database backup failed"
    exit 1
fi

# Media files backup (if they exist)
if [ -d "/app/media" ]; then
    print_status "Creating media files backup..."
    tar -czf ${BACKUP_DIR}/media_backup_${TIMESTAMP}.tar.gz -C /app media
    print_status "✅ Media files backup created"
fi

# Clean up old backups
print_status "Cleaning up old backups (older than ${RETENTION_DAYS} days)..."
find ${BACKUP_DIR} -name "regisbridge_backup_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete
find ${BACKUP_DIR} -name "media_backup_*.tar.gz" -type f -mtime +${RETENTION_DAYS} -delete
print_status "✅ Old backups cleaned up"

# List current backups
print_status "Current backups:"
ls -lh ${BACKUP_DIR}/*.gz 2>/dev/null || print_warning "No backup files found"

print_status "🎉 Backup process completed successfully!"
