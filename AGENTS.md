# 🤖 AGENTS.md - Development Guide

This file contains essential information for AI development agents working on the Regisbridge College Management System.

## 🚀 Quick Start Commands

### Development
```bash
# Start development server
python manage.py runserver

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Check for issues
python manage.py check
python manage.py check --deploy
```

### Code Quality
```bash
# Code formatting
black .
isort .

# Linting
flake8

# Type checking (if implemented)
mypy .
```

## 📁 Project Structure

```
regisbridge/
├── regisbridge/           # Project settings
│   ├── settings/
│   │   ├── base.py       # Base settings
│   │   └── production.py # Production settings
│   ├── urls.py
│   └── wsgi.py
├── users/                # Custom user model and auth
├── students/             # Student management
├── teachers/             # Teacher management  
├── parents/              # Parent management
├── grades/               # Grade and assessment system
├── core_attendance/      # Attendance tracking
├── core_timetable/       # Timetable management
├── fees/                 # Fee management
├── messaging/            # Internal messaging
├── notifications/        # Notification system
├── public/               # Public content (news, etc.)
├── dashboard/            # Role-based dashboards
└── static/               # Static files
```

## 🔧 Configuration

### Environment Variables
- Copy `.env.example` to `.env` for local development
- Update variables as needed for your environment

### Database
- Development: SQLite (default)
- Production: PostgreSQL (recommended)

### Static Files
- Development: Served by Django
- Production: Served by Nginx

## 🛠️ Development Guidelines

### Code Style
- Follow Django best practices
- Use type hints where appropriate
- Write descriptive docstrings
- Keep functions focused and small

### Model Conventions
- Use descriptive field names
- Include help_text for admin interface
- Add __str__ methods for all models
- Use proper field types and constraints

### Security
- Never commit secrets to git
- Use environment variables for sensitive data
- Follow Django security best practices
- Enable HTTPS in production

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test students

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Guidelines
- Write tests for all models and views
- Use Django's TestCase classes
- Create fixtures for test data
- Test both positive and negative cases

## 🚀 Deployment

### Development Deployment
```bash
python manage.py runserver
```

### Production Deployment
```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

## 📊 Monitoring

### Health Checks
```bash
# System health
python manage.py check

# Database status
python manage.py dbshell

# View logs
docker-compose -f docker-compose.prod.yml logs -f web
```

## 🔍 Troubleshooting

### Common Issues

1. **Migration Conflicts**: Delete migration files and recreate
2. **Static Files**: Run `python manage.py collectstatic`
3. **Database Issues**: Check DATABASE_URL environment variable
4. **Permission Errors**: Ensure proper user roles are set

### Debug Commands
```bash
# Django shell
python manage.py shell

# Database shell
python manage.py dbshell

# Show migrations status
python manage.py showmigrations
```

## 📚 Key Features Implemented

- ✅ User authentication with role-based access
- ✅ Student, teacher, and parent management
- ✅ Grade and assessment system
- ✅ Attendance tracking
- ✅ Timetable management
- ✅ Fee management and invoicing
- ✅ Internal messaging system
- ✅ Notification system
- ✅ Public content management
- ✅ RESTful API endpoints
- ✅ Role-based dashboards

## 🔜 Next Development Steps

### Phase 1: Enhanced Features
- Assignment submission system
- Exam scheduling
- Grade analytics and reporting
- PDF/Excel report generation

### Phase 2: Advanced Features  
- Email and SMS notifications
- Payment gateway integration
- Mobile app API enhancements
- Bulk data import/export

### Phase 3: Production Features
- Advanced monitoring and logging
- Automated testing and CI/CD
- Performance optimization
- Advanced security features

---

**For Questions**: Create an issue in the repository or contact the development team.
