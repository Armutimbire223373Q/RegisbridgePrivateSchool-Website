# 🚀 FastAPI Backend for Regisbridge College Management System

A modern, high-performance FastAPI backend that provides RESTful APIs for the Regisbridge College Management System. This backend integrates seamlessly with the existing Django models and provides a comprehensive API for frontend applications.

## ✨ Features

### 🔐 **Authentication & Authorization**
- JWT-based authentication
- Role-based access control (Admin, Teacher, Student, Parent, Boarding Staff)
- Secure password hashing with bcrypt
- Token refresh functionality

### 📊 **Core APIs**
- **Students**: Complete student management with profiles, academic records, and status tracking
- **Teachers**: Teacher profiles, specializations, and professional information
- **Parents**: Parent profiles with student relationships and contact information
- **Grades**: Grade management with assessment tracking and statistics
- **Attendance**: Daily attendance tracking with comprehensive reporting
- **Fees**: Fee structure management and invoice processing
- **Dashboard**: Real-time statistics and analytics

### 🛠️ **Technical Features**
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Pydantic**: Data validation and serialization with type hints
- **Django Integration**: Seamless integration with existing Django models
- **CORS Support**: Cross-origin resource sharing for frontend integration
- **Pagination**: Efficient data pagination for large datasets
- **Filtering & Search**: Advanced filtering and search capabilities
- **Error Handling**: Comprehensive error handling with detailed responses

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (or SQLite for development)
- Django backend running (for model access)

### Installation

1. **Clone and navigate to the FastAPI backend:**
   ```bash
   cd fastapi_backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   ```bash
   # Create .env file
   echo "SECRET_KEY=your-secret-key" > .env
   echo "DATABASE_URL=postgres://user:password@localhost:5432/regisbridge" >> .env
   ```

5. **Run the server:**
   ```bash
   python start_server.py
   ```

The API will be available at `http://localhost:8001`

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

### Authentication
All API endpoints (except login) require authentication via JWT token:

```bash
# Login to get token
curl -X POST "http://localhost:8001/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "your_username", "password": "your_password"}'

# Use token in subsequent requests
curl -X GET "http://localhost:8001/api/v1/students/" \
     -H "Authorization: Bearer your_jwt_token"
```

### Core Endpoints

#### Students
- `GET /api/v1/students/` - List all students with pagination
- `GET /api/v1/students/{id}` - Get specific student
- `POST /api/v1/students/` - Create new student
- `PUT /api/v1/students/{id}` - Update student
- `DELETE /api/v1/students/{id}` - Delete student

#### Teachers
- `GET /api/v1/teachers/` - List all teachers
- `GET /api/v1/teachers/{id}` - Get specific teacher
- `POST /api/v1/teachers/` - Create new teacher
- `PUT /api/v1/teachers/{id}` - Update teacher
- `DELETE /api/v1/teachers/{id}` - Delete teacher

#### Parents
- `GET /api/v1/parents/` - List all parents
- `GET /api/v1/parents/{id}` - Get specific parent
- `POST /api/v1/parents/` - Create new parent
- `PUT /api/v1/parents/{id}` - Update parent
- `DELETE /api/v1/parents/{id}` - Delete parent

#### Grades
- `GET /api/v1/grades/` - List all grades
- `GET /api/v1/grades/{id}` - Get specific grade
- `POST /api/v1/grades/` - Create new grade
- `PUT /api/v1/grades/{id}` - Update grade
- `DELETE /api/v1/grades/{id}` - Delete grade
- `GET /api/v1/grades/statistics/student/{id}` - Student grade statistics

#### Attendance
- `GET /api/v1/attendance/` - List attendance records
- `GET /api/v1/attendance/{id}` - Get specific attendance record
- `POST /api/v1/attendance/` - Create attendance record
- `PUT /api/v1/attendance/{id}` - Update attendance record
- `DELETE /api/v1/attendance/{id}` - Delete attendance record
- `GET /api/v1/attendance/statistics/student/{id}` - Student attendance statistics

#### Fees
- `GET /api/v1/fees/structures` - List fee structures
- `GET /api/v1/fees/structures/{id}` - Get specific fee structure
- `POST /api/v1/fees/structures` - Create fee structure
- `PUT /api/v1/fees/structures/{id}` - Update fee structure
- `DELETE /api/v1/fees/structures/{id}` - Delete fee structure
- `GET /api/v1/fees/invoices` - List invoices
- `GET /api/v1/fees/statistics/overview` - Fee statistics

#### Dashboard
- `GET /api/v1/dashboard/stats` - General dashboard statistics
- `GET /api/v1/dashboard/student-stats` - Student statistics
- `GET /api/v1/dashboard/attendance-stats` - Attendance statistics
- `GET /api/v1/dashboard/fee-stats` - Fee statistics
- `GET /api/v1/dashboard/teacher-stats` - Teacher statistics

## 🔧 Configuration

### Environment Variables
```bash
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@localhost:5432/regisbridge
DEBUG=True
```

### Database Configuration
The FastAPI backend uses the same database as the Django backend. Make sure the Django backend is properly configured and migrated.

## 🐳 Docker Deployment

### Using Docker Compose
```bash
# Start all services (Django + FastAPI + Frontend + Database)
docker-compose -f docker-compose.api.yml up -d

# View logs
docker-compose -f docker-compose.api.yml logs -f fastapi

# Stop services
docker-compose -f docker-compose.api.yml down
```

### Individual Docker Build
```bash
# Build FastAPI image
docker build -t regisbridge-fastapi ./fastapi_backend

# Run container
docker run -p 8001:8001 regisbridge-fastapi
```

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=api
```

### Manual Testing
Use the interactive API documentation at `http://localhost:8001/docs` to test endpoints manually.

## 📊 Performance

### Features
- **Async Support**: Full async/await support for high concurrency
- **Connection Pooling**: Efficient database connection management
- **Caching**: Redis integration for caching (optional)
- **Rate Limiting**: Built-in rate limiting for API protection
- **Compression**: Gzip compression for responses

### Monitoring
- Health check endpoint: `GET /health`
- Detailed logging with structured logs
- Performance metrics (when monitoring is configured)

## 🔒 Security

### Features
- JWT token authentication
- Password hashing with bcrypt
- CORS configuration
- Rate limiting
- Input validation with Pydantic
- SQL injection protection (via Django ORM)

### Best Practices
- Always use HTTPS in production
- Rotate JWT secrets regularly
- Implement proper error handling
- Validate all input data
- Use environment variables for secrets

## 🤝 Integration

### With Django Backend
The FastAPI backend integrates seamlessly with the Django backend by:
- Using the same database and models
- Sharing authentication system
- Maintaining data consistency
- Providing additional API endpoints

### With Frontend
The API is designed to work with modern frontend frameworks:
- React/Vue.js/Angular support
- CORS enabled for cross-origin requests
- JSON responses with consistent structure
- Real-time updates support (WebSocket ready)

## 📝 API Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... },
  "pagination": { ... } // For paginated responses
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "detail": "Detailed error information"
}
```

## 🚀 Development

### Adding New Endpoints
1. Create new router in `api/routers/`
2. Add Pydantic models in `api/models.py`
3. Implement business logic
4. Add to main app in `main.py`
5. Update documentation

### Code Style
- Follow PEP 8 guidelines
- Use type hints throughout
- Write comprehensive docstrings
- Include error handling
- Add tests for new features

## 📞 Support

For questions or issues:
1. Check the API documentation at `/docs`
2. Review the logs for error details
3. Ensure Django backend is running
4. Verify database connectivity

---

**Built with ❤️ using FastAPI, Django, and modern Python practices.**
