# 🚀 **Regisbridge College Management System - Deployment Guide**

This guide covers deployment of the Regisbridge system in both development and production environments.

## 📋 **Prerequisites**

### **System Requirements**
- **OS**: Ubuntu 20.04+ / CentOS 8+ / macOS 10.15+ / Windows 10+
- **Python**: 3.11+
- **RAM**: Minimum 4GB (8GB+ recommended)
- **Storage**: Minimum 20GB free space
- **Database**: PostgreSQL 13+ or MySQL 8.0+

### **Software Dependencies**
- Docker & Docker Compose
- Git
- Python 3.11+
- Virtual Environment (venv/conda)
- Node.js 16+ (for frontend assets)

## 🏗️ **Development Environment Setup**

### **1. Clone Repository**
```bash
git clone https://github.com/your-org/regisbridge.git
cd regisbridge
```

### **2. Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your local settings
```

### **5. Database Setup**
```bash
# Using SQLite (default)
python manage.py migrate

# Using PostgreSQL
# Update settings.py with your database configuration
python manage.py migrate
```

### **6. Create Superuser**
```bash
python manage.py createsuperuser
```

### **7. Run Development Server**
```bash
python manage.py runserver
```

## 🐳 **Docker Development Setup**

### **1. Start Services**
```bash
docker-compose up -d
```

### **2. Run Migrations**
```bash
docker-compose exec web python manage.py migrate
```

### **3. Create Superuser**
```bash
docker-compose exec web python manage.py createsuperuser
```

### **4. Access Services**
- **Web Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Database Admin**: http://localhost:8080
- **Email Testing**: http://localhost:8025
- **Celery Flower**: http://localhost:5555

## 🚀 **Production Deployment**

### **1. Server Preparation**

#### **Ubuntu 20.04+ Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx redis-server

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### **2. Production Environment Configuration**

#### **Create Production Settings**
```bash
# Create production settings directory
mkdir -p regisbridge/settings
cp regisbridge/settings.py regisbridge/settings/base.py
```

#### **Production Settings File** (`regisbridge/settings/production.py`)
```python
from .base import *
import os
import dj_database_url

# Security Settings
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com', 'your-server-ip']

# Database Configuration
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static and Media Files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# SSL/HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Redis Configuration
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/regisbridge/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### **3. Production Docker Deployment**

#### **Production Docker Compose** (`docker-compose.prod.yml`)
```yaml
version: '3.8'

services:
  web:
    build: .
    restart: always
    environment:
      - DEBUG=0
      - DJANGO_SETTINGS_MODULE=regisbridge.settings.production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - db
      - redis
    networks:
      - regisbridge_network

  db:
    image: postgres:15
    restart: always
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - regisbridge_network

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data
    networks:
      - regisbridge_network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - web
    networks:
      - regisbridge_network

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:

networks:
  regisbridge_network:
    driver: bridge
```

### **4. Nginx Configuration**

#### **Nginx Configuration** (`nginx/nginx.conf`)
```nginx
events {
    worker_connections 1024;
}

http {
    upstream django {
        server web:8000;
    }

    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        client_max_body_size 100M;

        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /app/staticfiles/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /app/media/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### **5. SSL Certificate Setup**

#### **Using Let's Encrypt (Free)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### **Using Self-Signed Certificate (Development)**
```bash
# Generate self-signed certificate
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem
```

### **6. Environment Variables**

#### **Production Environment File** (`.env.prod`)
```bash
# Django Settings
DEBUG=0
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/regisbridge
POSTGRES_DB=regisbridge
POSTGRES_USER=regisbridge_user
POSTGRES_PASSWORD=secure_password_here

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payment Gateways
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
PAYNOW_API_KEY=your-paynow-key

# Security
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

### **7. Deployment Commands**

#### **Initial Deployment**
```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

#### **Update Deployment**
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart services
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

## 🔧 **CI/CD Pipeline Setup**

### **GitHub Actions Workflow** (`.github/workflows/deploy.yml`)
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.KEY }}
        script: |
          cd /path/to/regisbridge
          git pull origin main
          docker-compose -f docker-compose.prod.yml down
          docker-compose -f docker-compose.prod.yml up -d --build
          docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
          docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

## 📊 **Monitoring and Maintenance**

### **1. Health Checks**
```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f web

# Check database connections
docker-compose -f docker-compose.prod.yml exec web python manage.py dbshell
```

### **2. Backup Strategy**
```bash
# Database backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres regisbridge > backup_$(date +%Y%m%d_%H%M%S).sql

# Media files backup
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/regisbridge"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U postgres regisbridge > $BACKUP_DIR/db_backup_$DATE.sql

# Media backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz media/

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### **3. Performance Monitoring**
```bash
# Install monitoring tools
pip install django-debug-toolbar django-silk

# Monitor with Django Silk
# Access: /silk/

# Monitor with Celery Flower
# Access: http://your-domain.com:5555
```

## 🚨 **Troubleshooting**

### **Common Issues and Solutions**

#### **1. Database Connection Issues**
```bash
# Check database status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U postgres -d regisbridge

# Reset database
sudo -u postgres dropdb regisbridge
sudo -u postgres createdb regisbridge
```

#### **2. Static Files Not Loading**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

#### **3. Permission Issues**
```bash
# Fix file permissions
sudo chown -R www-data:www-data /path/to/regisbridge
sudo chmod -R 755 /path/to/regisbridge

# Fix media directory permissions
sudo chmod -R 777 media/
```

## 📚 **Additional Resources**

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)
- [PostgreSQL Administration](https://www.postgresql.org/docs/current/admin.html)

---

**🎯 Next Steps:**
1. Set up your domain and DNS
2. Configure SSL certificates
3. Set up monitoring and alerting
4. Implement automated backups
5. Configure CI/CD pipeline
6. Set up staging environment

For support, create an issue in the repository or contact the development team.
