#!/bin/bash

# Jenkins Docker Setup Script for ALX Backend Python Project
# This script sets up Jenkins in a Docker container with all necessary plugins

set -e

echo "🚀 Setting up Jenkins for ALX Backend Python Project..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Docker is available and running"

# Stop and remove existing Jenkins container if it exists
if docker ps -a | grep -q jenkins; then
    print_warning "Existing Jenkins container found. Stopping and removing..."
    docker stop jenkins 2>/dev/null || true
    docker rm jenkins 2>/dev/null || true
    print_success "Existing Jenkins container removed"
fi

# Create Jenkins volume if it doesn't exist
if ! docker volume ls | grep -q jenkins_home; then
    print_status "Creating Jenkins volume..."
    docker volume create jenkins_home
    print_success "Jenkins volume created"
else
    print_status "Jenkins volume already exists"
fi

# Pull the latest Jenkins LTS image
print_status "Pulling Jenkins LTS image..."
docker pull jenkins/jenkins:lts

# Run Jenkins container
print_status "Starting Jenkins container..."
docker run -d \
    --name jenkins \
    --restart unless-stopped \
    -p 8080:8080 \
    -p 50000:50000 \
    -v jenkins_home:/var/jenkins_home \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -e JAVA_OPTS="-Djenkins.install.runSetupWizard=false" \
    jenkins/jenkins:lts

# Wait for Jenkins to start
print_status "Waiting for Jenkins to start..."
sleep 30

# Check if Jenkins is running
if docker ps | grep -q jenkins; then
    print_success "Jenkins container is running"
else
    print_error "Failed to start Jenkins container"
    exit 1
fi

# Get the initial admin password
print_status "Retrieving Jenkins initial admin password..."
INITIAL_PASSWORD=$(docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null || echo "Password not found")

# Display setup information
echo ""
echo "======================================"
echo "🎉 Jenkins Setup Complete!"
echo "======================================"
echo ""
echo "📍 Jenkins URL: http://localhost:8080"
echo "🔑 Initial Admin Password: $INITIAL_PASSWORD"
echo ""
echo "📋 Next Steps:"
echo "1. Open http://localhost:8080 in your browser"
echo "2. Use the password above to unlock Jenkins"
echo "3. Install suggested plugins or select specific plugins:"
echo "   - Git Plugin"
echo "   - Pipeline Plugin"
echo "   - ShiningPanda Plugin"
echo "   - HTML Publisher Plugin"
echo "   - JUnit Plugin"
echo "   - Workspace Cleanup Plugin"
echo "4. Create an admin user"
echo "5. Configure Jenkins URL"
echo ""
echo "🔧 Required Plugins for This Project:"
echo "   • Git Plugin (for GitHub integration)"
echo "   • Pipeline Plugin (for Jenkinsfile support)"
echo "   • ShiningPanda Plugin (for Python environment)"
echo "   • HTML Publisher Plugin (for test reports)"
echo "   • JUnit Plugin (for test results)"
echo ""
echo "📚 Project Information:"
echo "   • Repository: alx-backend-python"
echo "   • Project Directory: messaging_app"
echo "   • Jenkinsfile Location: messaging_app/Jenkinsfile"
echo "   • Main Branch: main"
echo ""
echo "🛠️  GitHub Credentials Setup:"
echo "1. Generate a Personal Access Token in GitHub"
echo "2. Go to Jenkins → Manage Jenkins → Manage Credentials"
echo "3. Add new 'Username with password' credential"
echo "4. ID: 'github-credentials'"
echo "5. Username: Your GitHub username"
echo "6. Password: Your Personal Access Token"
echo ""
echo "📊 Pipeline Features:"
echo "   ✅ Automated testing with pytest"
echo "   ✅ Code coverage reporting"
echo "   ✅ Django system checks"
echo "   ✅ Security validation"
echo "   ✅ HTML test reports"
echo "   ✅ Parallel test execution"
echo ""

# Save setup info to file
cat > jenkins_setup_info.txt << EOF
Jenkins Setup Information
========================
Date: $(date)
Jenkins URL: http://localhost:8080
Initial Admin Password: $INITIAL_PASSWORD
Container Name: jenkins
Volume: jenkins_home

Docker Commands:
- Start: docker start jenkins
- Stop: docker stop jenkins
- Logs: docker logs jenkins
- Shell: docker exec -it jenkins bash

Project Information:
- Repository: alx-backend-python
- Directory: messaging_app
- Jenkinsfile: messaging_app/Jenkinsfile
EOF

print_success "Setup information saved to jenkins_setup_info.txt"

# Check Jenkins status
sleep 10
if curl -s http://localhost:8080 > /dev/null; then
    print_success "Jenkins is accessible at http://localhost:8080"
else
    print_warning "Jenkins may still be starting up. Please wait a few more minutes."
fi

echo ""
print_success "Jenkins setup script completed successfully!"
echo "Check jenkins_setup_info.txt for detailed information."
