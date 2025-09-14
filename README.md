# 🎓 Regisbridge College Management System

A comprehensive, modern college management system built with React and FastAPI, featuring role-based access control, student management, teacher profiles, parent portals, and more.

## ✨ Features

### 🎯 Core Functionality
- **Student Management** - Complete student profiles with academic records
- **Teacher Management** - Teacher profiles with subject assignments
- **Parent Portal** - Parent accounts linked to student records
- **Grade Management** - Academic assessments and progress tracking
- **Attendance System** - Daily attendance tracking and reporting
- **Fee Management** - Payment processing and invoice generation
- **Messaging System** - Internal communication platform
- **Dashboard Analytics** - Real-time statistics and insights

### 🔐 Security & Access Control
- **JWT Authentication** - Secure token-based authentication
- **Role-Based Access** - Admin, Teacher, Student, Parent, Boarding Staff
- **Protected Routes** - Role-specific page access
- **Secure API** - RESTful API with proper validation

### 🎨 User Experience
- **Modern UI** - Clean, responsive design with Tailwind CSS
- **Mobile Responsive** - Works on all device sizes
- **Real-time Updates** - Hot module replacement for development
- **Intuitive Navigation** - Easy-to-use interface
- **Loading States** - Smooth user experience

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd regisbridge
   ```

2. **Install Backend Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

4. **Start the Backend**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001 --reload
   ```

5. **Start the Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

6. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001/docs
   - Admin Interface: http://localhost:8001/admin

## 🔑 Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Teacher | teacher1 | teacher123 |
| Student | student1 | student123 |
| Parent | parent1 | parent123 |

## 🏗️ Architecture

### Frontend (React + TypeScript)
- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite for fast development
- **Styling**: Tailwind CSS with custom components
- **State Management**: React Context API
- **Routing**: React Router DOM
- **Icons**: Lucide React
- **HTTP Client**: Fetch API

### Backend (FastAPI + Python)
- **Framework**: FastAPI with async support
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL
- **Authentication**: JWT tokens with bcrypt hashing
- **API Documentation**: Auto-generated with Swagger UI
- **Validation**: Pydantic models
- **Database Migrations**: Alembic

### Database Schema
- **Users** - Authentication and basic user info
- **Students** - Student profiles and academic records
- **Teachers** - Teacher profiles and subject assignments
- **Parents** - Parent information and student relationships
- **Grades** - Academic assessments and grade tracking
- **Attendance** - Daily attendance records
- **Fees** - Payment and invoice management
- **Messages** - Internal communication system

## 📁 Project Structure

```
regisbridge/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── contexts/       # React context providers
│   │   └── App.tsx         # Main application component
│   ├── public/             # Static assets
│   └── package.json        # Frontend dependencies
├── api/                    # FastAPI backend
│   ├── routers/           # API route handlers
│   ├── models.py          # Pydantic models
│   ├── auth.py            # Authentication logic
│   └── database.py        # Database configuration
├── models/                 # SQLAlchemy database models
│   ├── user.py            # User model
│   ├── student.py         # Student model
│   ├── teacher.py         # Teacher model
│   └── ...
├── main.py                # FastAPI application entry point
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## 🔧 Development

### Backend Development
```bash
# Start development server
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Run tests
pytest

# Check code formatting
black .
isort .
```

### Frontend Development
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Run linting
npm run lint
```

## 🌐 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user

### Students
- `GET /api/v1/students/` - List students
- `POST /api/v1/students/` - Create student
- `GET /api/v1/students/{id}` - Get student
- `PUT /api/v1/students/{id}` - Update student
- `DELETE /api/v1/students/{id}` - Delete student

### Teachers
- `GET /api/v1/teachers/` - List teachers
- `POST /api/v1/teachers/` - Create teacher
- `GET /api/v1/teachers/{id}` - Get teacher
- `PUT /api/v1/teachers/{id}` - Update teacher
- `DELETE /api/v1/teachers/{id}` - Delete teacher

### Parents
- `GET /api/v1/parents/` - List parents
- `POST /api/v1/parents/` - Create parent
- `GET /api/v1/parents/{id}` - Get parent
- `PUT /api/v1/parents/{id}` - Update parent
- `DELETE /api/v1/parents/{id}` - Delete parent

### Dashboard
- `GET /api/v1/dashboard/stats` - Get dashboard statistics

## 🎨 UI Components

### Layout Components
- **Layout** - Main application layout with sidebar navigation
- **Header** - Top navigation with user menu
- **Sidebar** - Role-based navigation menu

### Page Components
- **Dashboard** - Analytics and quick actions
- **Students** - Student management interface
- **Teachers** - Teacher management interface
- **Parents** - Parent management interface
- **Grades** - Grade and assessment management
- **Attendance** - Attendance tracking interface
- **Fees** - Fee management interface
- **Messages** - Internal messaging system
- **Profile** - User profile management

### Common Components
- **Modal** - Reusable modal dialogs
- **Table** - Data tables with sorting and filtering
- **Forms** - Form components with validation
- **Cards** - Information display cards

## 🔒 Security Features

- **JWT Authentication** - Secure token-based authentication
- **Password Hashing** - bcrypt for password security
- **Role-Based Access** - Granular permission system
- **CORS Protection** - Cross-origin request security
- **Input Validation** - Pydantic model validation
- **SQL Injection Protection** - SQLAlchemy ORM protection

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d --build
```

### Manual Deployment
1. **Backend**: Deploy FastAPI with Gunicorn/Uvicorn
2. **Frontend**: Build and serve static files with Nginx
3. **Database**: Configure PostgreSQL for production
4. **Environment**: Set production environment variables

## 📊 Performance

- **Frontend**: Vite for fast development and building
- **Backend**: FastAPI with async support for high performance
- **Database**: SQLAlchemy with connection pooling
- **Caching**: Redis for session and data caching
- **CDN**: Static asset delivery optimization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation at `/docs`

## 🎯 Roadmap

### Phase 1: Core Features ✅
- [x] User authentication and authorization
- [x] Student management
- [x] Teacher management
- [x] Parent portal
- [x] Basic dashboard

### Phase 2: Advanced Features 🚧
- [ ] Grade analytics and reporting
- [ ] PDF report generation
- [ ] Email notifications
- [ ] Mobile app integration
- [ ] Advanced search and filtering

### Phase 3: Enterprise Features 📋
- [ ] Multi-tenant support
- [ ] Advanced analytics
- [ ] Integration APIs
- [ ] Custom reporting
- [ ] Advanced security features

---

**Built with ❤️ for modern education management**