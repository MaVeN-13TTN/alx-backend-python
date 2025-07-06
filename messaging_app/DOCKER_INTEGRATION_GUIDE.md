# Docker Integration Guide for Jenkins Pipeline

## Overview

This guide explains how the Jenkins pipeline builds and pushes Docker images for the ALX Backend Python messaging app to Docker Hub.

## Docker Integration Features

### 🏗️ **Automated Docker Build**

- Builds Docker image using the existing Dockerfile
- Creates two tags: build-specific (`build-${BUILD_NUMBER}`) and `latest`
- Only builds if all tests pass successfully

### 🔍 **Security Scanning**

- Basic container security checks
- Verifies non-root user execution
- Reports image size and metadata
- Inspects container configuration

### 📤 **Docker Hub Push**

- Secure authentication using Jenkins credentials
- Pushes both tagged versions to Docker Hub
- Automatic cleanup of Docker Hub credentials

### 🧹 **Resource Management**

- Cleans up local images to save disk space
- Removes dangling images
- Optimized for CI/CD environments

## Prerequisites

### 1. Docker Hub Account Setup

1. **Create Docker Hub Account**

   ```
   https://hub.docker.com/
   ```

2. **Create Repository**

   - Repository name: `alx-messaging-app`
   - Visibility: Public (recommended for this project)
   - Description: `ALX Backend Python Messaging App - Django REST API`

3. **Generate Access Token**
   - Go to: Account Settings → Security → Access Tokens
   - Token name: `Jenkins Pipeline Access`
   - Permissions: Read, Write, Delete
   - **Important**: Copy the token immediately (shown only once)

### 2. Jenkins Configuration

#### Install Required Plugins

```
• Docker Plugin
• Docker Pipeline Plugin
• Docker Commons Plugin
```

#### Add Docker Hub Credentials

1. Navigate to: **Manage Jenkins** → **Manage Credentials** → **Global**
2. Click **Add Credentials**
3. Configure:
   - **Kind**: Username with password
   - **Scope**: Global
   - **Username**: Your Docker Hub username
   - **Password**: Your Docker Hub access token
   - **ID**: `dockerhub-credentials`
   - **Description**: Docker Hub Access Token

### 3. Docker Access for Jenkins

The Jenkins container needs Docker access. The setup script configures this automatically:

```bash
# Docker socket mount (current setup)
-v /var/run/docker.sock:/var/run/docker.sock
```

## Pipeline Docker Stages

### Stage 1: Docker Build

```groovy
stage('Docker Build') {
    when {
        expression {
            currentBuild.currentResult == 'SUCCESS'
        }
    }
    steps {
        script {
            sh """
                docker build -t ${DOCKERHUB_CREDENTIALS_USR}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG} .
                docker build -t ${DOCKERHUB_CREDENTIALS_USR}/${DOCKER_IMAGE_NAME}:${DOCKER_LATEST_TAG} .
            """
        }
    }
}
```

**Features:**

- Only runs if previous stages passed
- Creates build-specific tag (`username/alx-messaging-app:123`)
- Creates latest tag (`username/alx-messaging-app:latest`)
- Uses secure credential handling

### Stage 2: Docker Security Scan

```groovy
stage('Docker Security Scan') {
    steps {
        script {
            sh """
                # Image inspection
                docker inspect ${DOCKERHUB_CREDENTIALS_USR}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG}

                # Security check - non-root user
                docker run --rm ${DOCKERHUB_CREDENTIALS_USR}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG} whoami
            """
        }
    }
}
```

**Security Checks:**

- ✅ Verifies non-root user execution (`appuser`)
- ✅ Reports image size and configuration
- ✅ Basic container health validation
- ✅ Generates inspection metadata

### Stage 3: Docker Push

```groovy
stage('Docker Push') {
    steps {
        script {
            sh """
                # Secure login
                echo '${DOCKERHUB_CREDENTIALS_PSW}' | docker login docker.io -u '${DOCKERHUB_CREDENTIALS_USR}' --password-stdin

                # Push images
                docker push ${DOCKERHUB_CREDENTIALS_USR}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG}
                docker push ${DOCKERHUB_CREDENTIALS_USR}/${DOCKER_IMAGE_NAME}:${DOCKER_LATEST_TAG}

                # Secure logout
                docker logout docker.io
            """
        }
    }
}
```

**Security Features:**

- 🔒 Uses Jenkins credential variables
- 🔒 Secure login with stdin password
- 🔒 Automatic logout after push
- 🔒 No password exposure in logs

### Stage 4: Docker Cleanup

```groovy
stage('Docker Cleanup') {
    steps {
        script {
            sh """
                # Remove local images
                docker rmi ${DOCKERHUB_CREDENTIALS_USR}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG}
                docker rmi ${DOCKERHUB_CREDENTIALS_USR}/${DOCKER_IMAGE_NAME}:${DOCKER_LATEST_TAG}

                # Clean dangling images
                docker image prune -f
            """
        }
    }
}
```

**Cleanup Benefits:**

- 💾 Saves disk space on Jenkins agent
- 🧹 Removes dangling/unused images
- ⚡ Prevents disk space issues
- 🔄 Keeps CI environment clean

## Docker Environment Variables

The pipeline uses these environment variables:

```groovy
environment {
    DOCKER_IMAGE_NAME = "alx-messaging-app"
    DOCKER_TAG = "${BUILD_NUMBER}"
    DOCKER_LATEST_TAG = "latest"
    DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
    DOCKER_REGISTRY = "docker.io"
}
```

## Image Naming Convention

### Tags Created

1. **Build-specific**: `username/alx-messaging-app:${BUILD_NUMBER}`

   - Example: `johndoe/alx-messaging-app:42`
   - Unique for each build
   - Allows rollback to specific versions

2. **Latest**: `username/alx-messaging-app:latest`
   - Always points to most recent successful build
   - Used for deployments and testing

### Repository Structure

```
Docker Hub Repository: username/alx-messaging-app
├── latest (latest successful build)
├── 1 (first build)
├── 2 (second build)
├── 3 (third build)
└── ... (subsequent builds)
```

## Dockerfile Overview

The existing Dockerfile is optimized for the messaging app:

```dockerfile
FROM python:3.10-slim

# Security: Non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Optimizations
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Application setup
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

**Security Features:**

- ✅ Runs as non-root user (`appuser`)
- ✅ Minimal base image (`python:3.10-slim`)
- ✅ No unnecessary packages
- ✅ Proper file permissions

## Local Testing

### Test Docker Build Locally

```bash
cd messaging_app

# Run extended tests with Docker
./run_tests_with_docker.sh

# Or manual Docker test
docker build -t test-messaging-app .
docker run --rm test-messaging-app python manage.py check
```

### Test Container Locally

```bash
# Build image
docker build -t alx-messaging-app-local .

# Run container
docker run -p 8000:8000 alx-messaging-app-local

# Test in another terminal
curl http://localhost:8000/api/
```

## Deployment

### Pull and Run from Docker Hub

```bash
# Pull latest image
docker pull yourusername/alx-messaging-app:latest

# Run container
docker run -d \
  --name messaging-app \
  -p 8000:8000 \
  -e DJANGO_SECRET_KEY="your-secret-key" \
  -e DJANGO_DEBUG="False" \
  yourusername/alx-messaging-app:latest

# Check logs
docker logs messaging-app

# Test API
curl http://localhost:8000/api/
```

### Production Deployment with Docker Compose

```yaml
version: "3.8"
services:
  web:
    image: yourusername/alx-messaging-app:latest
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
      - DJANGO_DEBUG=False
      - DATABASE_URL=${DATABASE_URL}
    restart: unless-stopped
```

## Monitoring and Maintenance

### Build Monitoring

- Monitor Docker Hub repository for new images
- Check image sizes for optimization opportunities
- Review security scan results

### Cleanup Strategy

```bash
# Remove old images (keep last 10 builds)
docker images yourusername/alx-messaging-app --format "table {{.Tag}}" | tail -n +11 | xargs -I {} docker rmi yourusername/alx-messaging-app:{}
```

### Security Best Practices

- 🔒 Rotate Docker Hub access tokens regularly
- 🔒 Monitor repository access logs
- 🔒 Use private repositories for sensitive applications
- 🔒 Scan images for vulnerabilities regularly

## Troubleshooting

### Common Issues

#### 1. Docker Build Fails

```bash
# Check Dockerfile syntax
docker build --no-cache -t test .

# Check build context
ls -la
cat .dockerignore
```

#### 2. Push Permission Denied

```bash
# Verify credentials in Jenkins
# Check Docker Hub repository exists
# Verify access token permissions
```

#### 3. Jenkins Docker Access

```bash
# Check Docker socket access
docker exec jenkins docker version

# Fix permissions if needed
docker exec jenkins usermod -aG docker jenkins
```

#### 4. Image Size Too Large

```bash
# Optimize Dockerfile
# Use multi-stage builds
# Clean up package caches
# Use .dockerignore effectively
```

## CI/CD Integration

### GitHub Integration

- Push updated Jenkinsfile to GitHub
- Pipeline automatically detects changes
- Manual trigger available in Jenkins dashboard

### Automated Deployment

Extend pipeline for automatic deployment:

```groovy
stage('Deploy to Staging') {
    when {
        branch 'main'
    }
    steps {
        sh """
            docker pull ${DOCKERHUB_CREDENTIALS_USR}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG}
            docker stop staging-app || true
            docker rm staging-app || true
            docker run -d --name staging-app -p 8001:8000 ${DOCKERHUB_CREDENTIALS_USR}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG}
        """
    }
}
```

## Summary

The Docker integration provides:

✅ **Automated image building** from source code  
✅ **Security scanning** and validation  
✅ **Secure push** to Docker Hub registry  
✅ **Resource management** and cleanup  
✅ **Version tagging** for deployment tracking  
✅ **Production-ready** container images

This setup ensures reliable, secure, and efficient Docker image management as part of the CI/CD pipeline.
