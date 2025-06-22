# Multi-Container Docker Setup Guide

This guide explains how to set up and run the Django Messaging App using Docker Compose with MySQL database in a multi-container environment.

## 📋 Overview

The application consists of two main services:

- **Web Service**: Django application with REST API
- **Database Service**: MySQL 8.0 database for data persistence

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Django Web    │    │   MySQL DB      │
│   Container     │◄──►│   Container     │
│   Port: 8000    │    │   Port: 3306    │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┘
              Docker Network
           (messaging_network)
```

## 📁 Project Structure

```
messaging_app/
├── docker-compose.yml          # Multi-container orchestration
├── .env                       # Environment variables (not in Git)
├── Dockerfile                 # Django app container config
├── requirements.txt           # Python dependencies
├── init.sql                  # Database initialization script
├── containerization.md       # Docker setup guide
├── multi-container-setup.md  # This file
├── messaging_app/            # Django project
│   └── settings.py           # Updated with MySQL config
├── chats/                    # Django app
└── manage.py                 # Django management script
```

## 🐳 Docker Compose Configuration

### Services Overview

#### 1. Database Service (`db`)

- **Image**: MySQL 8.0
- **Container Name**: `messaging_db`
- **Port**: 3306
- **Features**:
  - Environment-based configuration
  - Data persistence with Docker volumes
  - Health checks for service readiness
  - Custom initialization script

#### 2. Web Service (`web`)

- **Build**: Custom Dockerfile
- **Container Name**: `messaging_web`
- **Port**: 8000
- **Features**:
  - Depends on database health
  - Environment variable configuration
  - Volume mounting for development
  - Automatic migrations and static file collection

### Network & Volumes

- **Custom Network**: `messaging_network` (bridge driver)
- **Persistent Volumes**:
  - `mysql_data`: Database files
  - `static_volume`: Django static files

## 🔧 Environment Configuration

### `.env` File Structure

```env
# Django Configuration
DEBUG=True
SECRET_KEY=your-super-secret-key-change-this-in-production
DB_ENGINE=django.db.backends.mysql

# MySQL Database Configuration
MYSQL_DATABASE=messaging_app_db
MYSQL_USER=messaging_user
MYSQL_PASSWORD=secure_password_123
MYSQL_ROOT_PASSWORD=root_password_123
```

### Key Environment Variables

| Variable         | Purpose           | Example                |
| ---------------- | ----------------- | ---------------------- |
| `DEBUG`          | Django debug mode | `True` for development |
| `SECRET_KEY`     | Django secret key | Random secure string   |
| `MYSQL_DATABASE` | Database name     | `messaging_app_db`     |
| `MYSQL_USER`     | Database user     | `messaging_user`       |
| `MYSQL_PASSWORD` | User password     | `secure_password_123`  |
| `DB_HOST`        | Database host     | `db` (service name)    |

## 🚀 Quick Start Guide

### Prerequisites

1. **Docker & Docker Compose installed**
2. **Git repository cloned**
3. **No services running on ports 3306 and 8000**

### Step-by-Step Setup

#### 1. Stop Conflicting Services

```bash
# Stop MySQL service if running on host
sudo systemctl stop mysql

# Check if ports are free
sudo lsof -i :3306
sudo lsof -i :8000
```

#### 2. Environment Setup

```bash
# Navigate to project directory
cd messaging_app

# Verify .env file exists
ls -la .env

# Check docker-compose.yml
cat docker-compose.yml
```

#### 3. Build and Start Services

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

#### 4. Verify Services

```bash
# Check running containers
docker-compose ps

# View logs
docker-compose logs -f

# Check specific service logs
docker-compose logs web
docker-compose logs db
```

## 🔍 Service Health Verification

### Database Health Check

```bash
# Check MySQL container health
docker-compose exec db mysqladmin ping -h localhost

# Connect to MySQL
docker-compose exec db mysql -u messaging_user -p messaging_app_db
```

### Web Service Health Check

```bash
# Test API endpoint
curl -I http://localhost:8000/api/auth/register/

# Register a test user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepass123",
    "confirm_password": "securepass123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

## 🧪 Testing Database Integration

### 1. User Registration Test

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dockeruser",
    "email": "docker@example.com",
    "password": "mysecurepass123",
    "confirm_password": "mysecurepass123",
    "first_name": "Docker",
    "last_name": "User"
  }'
```

**Expected Response:**

```json
{
  "user_id": "uuid-here",
  "username": "dockeruser",
  "email": "docker@example.com",
  "message": "User registered successfully"
}
```

### 2. Authentication Test

```bash
# Login to get JWT token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dockeruser",
    "password": "mysecurepass123"
  }'
```

### 3. Database Query Test

```bash
# List users (requires JWT token)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/users/
```

## 🛠️ Development Workflow

### Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart specific service
docker-compose restart web

# View real-time logs
docker-compose logs -f web

# Execute commands in containers
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec db mysql -u root -p

# Rebuild after code changes
docker-compose down
docker-compose up --build
```

### Development with Volume Mounting

For live code reloading during development, the `docker-compose.yml` includes volume mounting:

```yaml
volumes:
  - .:/app # Mount current directory to container
```

This allows you to edit code locally and see changes immediately in the container.

## 📊 Service Dependencies

### Dependency Chain

```
1. Network Creation
2. Volume Creation
3. Database Service Start
4. Database Health Check
5. Web Service Start (waits for DB health)
6. Application Migrations
7. Static Files Collection
8. Django Server Start
```

### Health Check Details

The database service includes a health check:

```yaml
healthcheck:
  test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
  timeout: 20s
  retries: 10
```

The web service waits for database health:

```yaml
depends_on:
  db:
    condition: service_healthy
```

## 🔒 Security Features

### 1. Environment Variable Security

- Sensitive data in `.env` file
- `.env` excluded from Git via `.gitignore`
- No hardcoded secrets in containers

### 2. Container Security

- Non-root user in web container
- Minimal base images
- Network isolation

### 3. Database Security

- Custom user with limited privileges
- No root user exposure
- Password-protected access

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Conflicts

**Problem**: `bind: address already in use`

**Solution**:

```bash
# Find process using port
sudo lsof -i :3306
sudo lsof -i :8000

# Stop conflicting services
sudo systemctl stop mysql
# or kill specific process
sudo kill -9 PID
```

#### 2. Database Connection Errors

**Problem**: Django can't connect to MySQL

**Solutions**:

```bash
# Check database container health
docker-compose logs db

# Verify environment variables
docker-compose exec web env | grep DB_

# Test database connectivity
docker-compose exec web python manage.py dbshell
```

#### 3. Migration Issues

**Problem**: Migration failures

**Solutions**:

```bash
# Run migrations manually
docker-compose exec web python manage.py migrate

# Reset database (development only)
docker-compose down -v
docker-compose up --build
```

#### 4. Permission Issues

**Problem**: File permission errors

**Solutions**:

```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Rebuild containers
docker-compose down
docker-compose up --build
```

### Debugging Commands

```bash
# Check container status
docker-compose ps

# Inspect container details
docker-compose exec web bash
docker-compose exec db bash

# Check environment variables
docker-compose exec web printenv

# Test database connection
docker-compose exec web python manage.py shell
>>> from django.db import connection
>>> connection.ensure_connection()
```

## 📈 Production Considerations

### 1. Environment Variables

- Use secure secret keys
- Change default passwords
- Set `DEBUG=False`

### 2. Database Configuration

- Use production MySQL settings
- Configure proper backup strategy
- Set up database monitoring

### 3. Web Server

- Replace Django dev server with Gunicorn/uWSGI
- Add reverse proxy (Nginx)
- Configure SSL/TLS

### 4. Docker Optimizations

- Use multi-stage builds
- Minimize image sizes
- Implement proper health checks

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Database Configuration](https://docs.djangoproject.com/en/5.2/ref/settings/#databases)
- [MySQL Docker Hub](https://hub.docker.com/_/mysql)
- [Django REST Framework](https://www.django-rest-framework.org/)

## 🎯 Next Steps

1. **Add Redis**: For caching and session storage
2. **Implement Nginx**: As reverse proxy
3. **Add Monitoring**: With Prometheus/Grafana
4. **Set up CI/CD**: Automated testing and deployment
5. **Configure Backup**: Database backup strategy

## 📝 Summary

This multi-container setup provides:

- ✅ **Isolated Services**: Database and web application in separate containers
- ✅ **Environment Flexibility**: Easy configuration via environment variables
- ✅ **Development Ready**: Live code reloading and debugging capabilities
- ✅ **Production Ready**: Scalable architecture with proper dependency management
- ✅ **Data Persistence**: MySQL data survives container restarts
- ✅ **Network Security**: Isolated container network communication
- ✅ **Health Monitoring**: Built-in health checks for service reliability

The messaging app is now ready for development, testing, and deployment in a containerized environment! 🚀
