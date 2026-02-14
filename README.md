# Task Management API

A RESTful API for task management built with Django and Django REST Framework.

## Features

- 🔐 User authentication with token-based auth
- ✅ CRUD operations for tasks
- 📁 Project management
- 🏷️ Task categorization by status and priority
- 🔍 Filtering, searching, and pagination
- 📊 Project statistics (task counts)
- 📚 Automatic API documentation with Swagger/ReDoc

## Tech Stack

- **Backend:** Django 4.2, Django REST Framework
- **Database:** SQLite (development), PostgreSQL (production)
- **Authentication:** Token-based authentication
- **Documentation:** drf-yasg (Swagger/ReDoc)

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `POST /api/auth/logout/` - Logout user
- `GET /api/auth/me/` - Get current user

### Tasks
- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create a task
- `GET /api/tasks/{id}/` - Get task details
- `PUT /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task

### Projects
- `GET /api/projects/` - List all projects
- `POST /api/projects/` - Create a project
- `GET /api/projects/{id}/` - Get project with tasks
- `PUT /api/projects/{id}/` - Update project
- `DELETE /api/projects/{id}/` - Delete project

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/username/task-management-api.git
cd task-management-api
