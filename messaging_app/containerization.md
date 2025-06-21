# Containerization Guide - Messaging App

This guide explains how to containerize and run the Django Messaging App using Docker. The containerization provides a consistent environment across different systems and simplifies deployment.

## 📋 Prerequisites

- Docker installed on your system
- Git (for cloning the repository)
- Basic knowledge of Docker commands

### Installing Docker on Linux (Ubuntu 20.04)

```bash
# Update package index
sudo apt-get update

# Install required packages
sudo apt-get install apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up stable repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# Add user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
```

## 🏗️ Project Structure

```
messaging_app/
├── Dockerfile                 # Docker configuration
├── .dockerignore             # Files to exclude from Docker build
├── requirements.txt          # Python dependencies
├── containerization.md       # This file
├── manage.py                 # Django management script
├── messaging_app/            # Django project settings
├── chats/                    # Django app
└── db.sqlite3               # SQLite database (created after setup)
```

## 🐳 Docker Configuration

### Dockerfile Overview

The `Dockerfile` uses the following key configurations:

- **Base Image**: `python:3.10-slim` - Lightweight Python 3.10 image
- **Security**: Non-root user (`appuser`) for security best practices
- **Environment**: Optimized Python environment variables
- **Dependencies**: System packages (gcc, python3-dev) and Python packages
- **Port**: Exposes port 8000 for Django development server

### Key Features

1. **Multi-stage approach** for efficient builds
2. **Security hardening** with non-root user
3. **Optimized caching** with proper layer ordering
4. **Development-ready** with Django dev server

## 🚀 Quick Start

### 1. Clone and Navigate to Project

```bash
git clone <repository-url>
cd messaging_app
```

### 2. Build Docker Image

```bash
docker build -t messaging-app .
```

This command:

- Builds a Docker image tagged as `messaging-app`
- Installs all dependencies from `requirements.txt`
- Sets up the application environment
- Creates necessary directories

### 3. Run the Container

```bash
# Run in detached mode (background)
docker run -d --name messaging-app-container -p 8000:8000 messaging-app

# Or run in interactive mode (foreground)
docker run --name messaging-app-container -p 8000:8000 messaging-app
```

### 4. Verify Application is Running

```bash
# Check running containers
docker ps

# Check application logs
docker logs messaging-app-container

# Test API endpoint
curl -I http://localhost:8000/api/auth/register/
```

## 🛠️ Management Commands

### Container Management

```bash
# List all containers
docker ps -a

# Stop the container
docker stop messaging-app-container

# Start existing container
docker start messaging-app-container

# Remove container
docker rm messaging-app-container

# View real-time logs
docker logs -f messaging-app-container
```

### Image Management

```bash
# List Docker images
docker images

# Remove the image
docker rmi messaging-app

# Rebuild image (after code changes)
docker build -t messaging-app .
```

### Development Workflow

```bash
# Stop existing container
docker stop messaging-app-container && docker rm messaging-app-container

# Rebuild image with latest changes
docker build -t messaging-app .

# Run new container
docker run -d --name messaging-app-container -p 8000:8000 messaging-app
```

## 🔧 Advanced Usage

### Running with Custom Port

```bash
# Run on port 8080 instead of 8000
docker run -d --name messaging-app-container -p 8080:8000 messaging-app
```

### Running with Volume Mount (for Development)

```bash
# Mount local code directory for live development
docker run -d \
  --name messaging-app-container \
  -p 8000:8000 \
  -v $(pwd):/app \
  messaging-app
```

### Environment Variables

```bash
# Run with custom environment variables
docker run -d \
  --name messaging-app-container \
  -p 8000:8000 \
  -e DEBUG=True \
  -e DJANGO_SECRET_KEY=your-secret-key \
  messaging-app
```

### Database Persistence

```bash
# Run with persistent database volume
docker run -d \
  --name messaging-app-container \
  -p 8000:8000 \
  -v messaging-db:/app/db.sqlite3 \
  messaging-app
```

## 🧪 Testing the Application

### API Endpoints

Once the container is running, you can test the following endpoints:

- **User Registration**: `POST http://localhost:8000/api/auth/register/`
- **User Login**: `POST http://localhost:8000/api/auth/token/`
- **List Users**: `GET http://localhost:8000/api/users/`
- **Create Conversation**: `POST http://localhost:8000/api/conversations/`
- **Send Message**: `POST http://localhost:8000/api/messages/`

### Using Postman Collection

Import the `post_man-Collections` file into Postman and set the base URL to `http://localhost:8000`.

### Sample cURL Commands

```bash
# Register a new user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login to get JWT token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepassword123"
  }'
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**

   ```bash
   # Find process using port 8000
   sudo lsof -i :8000

   # Kill the process or use different port
   docker run -p 8080:8000 messaging-app
   ```

2. **Container Won't Start**

   ```bash
   # Check container logs
   docker logs messaging-app-container

   # Run in interactive mode to debug
   docker run -it messaging-app bash
   ```

3. **Database Issues**

   ```bash
   # Run migrations in container
   docker exec messaging-app-container python manage.py migrate

   # Create superuser
   docker exec -it messaging-app-container python manage.py createsuperuser
   ```

4. **Permission Issues**

   ```bash
   # Check if user is in docker group
   groups $USER

   # If not, add user to docker group and restart
   sudo usermod -aG docker $USER
   newgrp docker
   ```

### Logging and Debugging

```bash
# View detailed logs
docker logs --details messaging-app-container

# Execute commands in running container
docker exec -it messaging-app-container bash

# Inspect container configuration
docker inspect messaging-app-container
```

## 🔒 Security Considerations

1. **Non-root User**: The container runs as `appuser`, not root
2. **Minimal Base Image**: Uses `python:3.10-slim` to reduce attack surface
3. **No Secrets in Image**: Avoid hardcoding secrets in Dockerfile
4. **Environment Variables**: Use for sensitive configuration
5. **Network Security**: Only expose necessary ports

## 📈 Performance Optimization

1. **Image Size**: Uses slim base image and multi-stage builds
2. **Layer Caching**: Dependencies installed before copying code
3. **No Cache**: `pip install --no-cache-dir` to reduce image size
4. **Clean Up**: Removes unnecessary packages after installation

## 🔄 CI/CD Integration

This Docker setup is ready for CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Build Docker Image
  run: docker build -t messaging-app .

- name: Run Tests in Container
  run: docker run --rm messaging-app python manage.py test

- name: Deploy to Production
  run: docker tag messaging-app:latest registry/messaging-app:${{ github.sha }}
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Django Deployment](https://docs.djangoproject.com/en/5.2/howto/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/best-practices/)
- [Django REST Framework](https://www.django-rest-framework.org/)

## 📝 Notes

- The application runs on Django's development server (suitable for development/testing)
- For production, consider using Gunicorn or uWSGI with a reverse proxy
- Database migrations may need to be run manually in the container
- Static files are collected during the build process
