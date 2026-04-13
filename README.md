# LMS Backend with Django

A Learning Management System backend built with Django REST Framework, featuring role-based authentication for Students, Tutors, and Admins.

## Features

- **Role-based Authentication**: Three user types (Student, Tutor, Admin)
- **JWT Authentication**: Secure token-based authentication
- **Custom User Model**: Extended user model with role-specific profiles
- **RESTful API**: Clean API endpoints for frontend integration
- **CORS Support**: Configured for Vite frontend integration

## Project Structure

```
lms_backend/
├── authentication/            # Authentication app
│   ├── models.py              # User models (Student, Tutor, Admin)
│   ├── views.py               # API views
│   ├── serializers.py         # DRF serializers
│   ├── urls.py                # URL routing
│   ├── admin.py               # Django admin configuration
│   └── management/commands/   # Custom commands
├── lms_backend/              # Django project settings
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL config
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Setup Instructions

### 1. Navigate to Backend Directory

```bash
cd lms_backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Sample Users

```bash
python manage.py create_sample_users
```

This will create three sample users:
- **Admin**: admin@lms.com / admin123
- **Tutor**: tutor@lms.com / tutor123  
- **Student**: student@lms.com / student123

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 8. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Refresh JWT token

### User Profile
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile
- `GET /api/auth/user-info/` - Get current user info
- `POST /api/auth/change-password/` - Change password

### Admin Only
- `GET /api/auth/users/` - Get users by role (admin only)

## User Roles

### Student
- Can enroll in courses
- Access learning materials
- Submit assignments
- View grades

### Tutor
- Create and manage courses
- Upload learning materials
- Grade assignments
- Communicate with students

### Admin
- Manage all users
- System configuration
- Analytics and reports
- Full system access

## Frontend Integration

The backend is configured to work with your Vite frontend running on `http://localhost:5173`. CORS is enabled for development.

### Example API Usage

```javascript
// Login
const response = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'student@lms.com',
    password: 'student123'
  })
});

const data = await response.json();
// Store tokens for authenticated requests
localStorage.setItem('access_token', data.tokens.access);
localStorage.setItem('refresh_token', data.tokens.refresh);
```

## Next Steps

1. Start the Django server: `python manage.py runserver`
2. Start your Vite frontend: `npm run dev` (in algaddaftech directory)
3. Test the authentication endpoints
4. Integrate the API with your React frontend
5. Add course management features
6. Implement file uploads for assignments
7. Add real-time notifications

## Development Notes

- The system uses SQLite for development (easily changeable to PostgreSQL/MySQL)
- JWT tokens expire after 1 hour (configurable)
- Profile pictures are stored in the `media/` directory
- All API responses are in JSON format
- Error handling is implemented for common scenarios







