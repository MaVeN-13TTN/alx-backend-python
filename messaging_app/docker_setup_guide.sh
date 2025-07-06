#!/bin/bash

# Docker Hub Setup Guide for Jenkins Pipeline
# This script provides guidance for setting up Docker Hub integration

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🐳 Docker Hub Integration Setup Guide"
echo "====================================="
echo ""

print_status "This guide will help you set up Docker Hub integration for the Jenkins pipeline."
echo ""

# Check if user has Docker Hub account
echo "📋 Prerequisites:"
echo "1. Docker Hub account (https://hub.docker.com/)"
echo "2. Jenkins with Docker plugin installed"
echo "3. Docker installed on Jenkins agent"
echo ""

# Step 1: Docker Hub Account
print_status "Step 1: Docker Hub Account Setup"
echo "1. Create a Docker Hub account at https://hub.docker.com/"
echo "2. Create a new repository for your messaging app:"
echo "   - Repository name: alx-messaging-app"
echo "   - Visibility: Public (or Private if you have a paid account)"
echo "   - Description: ALX Backend Python Messaging App"
echo ""

# Step 2: Docker Hub Access Token
print_status "Step 2: Generate Docker Hub Access Token"
echo "1. Go to Docker Hub → Account Settings → Security"
echo "2. Click 'New Access Token'"
echo "3. Token description: 'Jenkins Pipeline Access'"
echo "4. Access permissions: Read, Write, Delete"
echo "5. Copy the generated token (you won't see it again!)"
echo ""

# Step 3: Jenkins Credentials
print_status "Step 3: Add Docker Hub Credentials to Jenkins"
echo "1. Open Jenkins dashboard: http://localhost:8080"
echo "2. Go to: Manage Jenkins → Manage Credentials"
echo "3. Click on 'Global' domain"
echo "4. Click 'Add Credentials'"
echo "5. Configure as follows:"
echo "   - Kind: Username with password"
echo "   - Scope: Global"
echo "   - Username: Your Docker Hub username"
echo "   - Password: Your Docker Hub access token"
echo "   - ID: dockerhub-credentials"
echo "   - Description: Docker Hub Access Token"
echo "6. Click 'OK'"
echo ""

# Step 4: Docker Plugin
print_status "Step 4: Install Required Jenkins Plugins"
echo "Ensure these plugins are installed:"
echo "• Docker Plugin"
echo "• Docker Pipeline Plugin"
echo "• Docker Commons Plugin"
echo ""
echo "To install:"
echo "1. Go to: Manage Jenkins → Manage Plugins"
echo "2. Search for and install the plugins above"
echo "3. Restart Jenkins if required"
echo ""

# Step 5: Docker on Jenkins Agent
print_status "Step 5: Configure Docker Access for Jenkins"
echo "The Jenkins container needs access to Docker. Options:"
echo ""
echo "Option A: Docker Socket Mount (Current setup)"
echo "   Your current setup should work if you used the provided setup script."
echo ""
echo "Option B: Docker-in-Docker (Advanced)"
echo "   For production environments, consider Docker-in-Docker setup."
echo ""

# Step 6: Test Docker Access
print_status "Step 6: Test Docker Access in Jenkins"
echo "Create a simple test job to verify Docker access:"
echo ""
echo "1. Create new 'Freestyle project' named 'docker-test'"
echo "2. Add build step: 'Execute shell'"
echo "3. Add command: 'docker --version && docker info'"
echo "4. Save and run the job"
echo "5. Check console output for Docker version and info"
echo ""

# Pipeline Configuration Summary
print_status "Pipeline Configuration Summary"
echo "The updated Jenkinsfile includes these Docker stages:"
echo ""
echo "🔧 Docker Build:"
echo "   - Builds image with build number tag and 'latest' tag"
echo "   - Uses existing Dockerfile in messaging_app directory"
echo ""
echo "🔍 Docker Security Scan:"
echo "   - Basic security checks"
echo "   - Verifies non-root user execution"
echo "   - Image size reporting"
echo ""
echo "📤 Docker Push:"
echo "   - Pushes both tagged and latest images to Docker Hub"
echo "   - Uses secure credential handling"
echo "   - Automatic login/logout"
echo ""
echo "🧹 Docker Cleanup:"
echo "   - Removes local images to save disk space"
echo "   - Cleans up dangling images"
echo ""

# Troubleshooting
print_status "Common Issues and Solutions"
echo ""
echo "❌ 'permission denied while trying to connect to Docker daemon'"
echo "   Solution: Ensure Jenkins user has Docker permissions"
echo "   Command: docker exec jenkins usermod -aG docker jenkins"
echo ""
echo "❌ 'denied: requested access to the resource is denied'"
echo "   Solution: Check Docker Hub credentials in Jenkins"
echo "   Verify: Username and access token are correct"
echo ""
echo "❌ 'no space left on device'"
echo "   Solution: Clean up Docker images regularly"
echo "   Commands: docker system prune -a -f"
echo ""

# Verification Steps
print_status "Verification Steps"
echo "After setup, verify the integration:"
echo ""
echo "1. Run the Jenkins pipeline manually"
echo "2. Check build logs for Docker stages"
echo "3. Verify image appears in your Docker Hub repository"
echo "4. Test pulling the image:"
echo "   docker pull yourusername/alx-messaging-app:latest"
echo ""

# Security Best Practices
print_warning "Security Best Practices"
echo "🔒 Use access tokens, not passwords"
echo "🔒 Limit token permissions to minimum required"
echo "🔒 Rotate access tokens regularly"
echo "🔒 Monitor Docker Hub activity"
echo "🔒 Use private repositories for sensitive applications"
echo ""

print_success "Docker Hub integration setup guide completed!"
echo ""
echo "📁 Files updated:"
echo "   • messaging_app/Jenkinsfile (extended with Docker stages)"
echo "   • messaging_app/docker_setup_guide.sh (this guide)"
echo ""
echo "🚀 Next steps:"
echo "1. Follow the steps above to configure Docker Hub credentials"
echo "2. Update the Jenkinsfile in your GitHub repository"
echo "3. Run the pipeline and monitor the Docker build process"
echo ""
echo "For detailed pipeline documentation, see:"
echo "   • JENKINS_IMPLEMENTATION_GUIDE.md"
echo "   • JENKINS_README.md"
