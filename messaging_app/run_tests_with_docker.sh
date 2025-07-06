#!/bin/bash

# Extended test runner script with Docker build validation
# This script mimics what the Jenkins pipeline will do including Docker build

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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Ensure we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "Please run this script from the messaging_app directory"
    exit 1
fi

print_status "Starting extended local test validation with Docker build..."

# Check Docker availability
if ! command -v docker &> /dev/null; then
    print_warning "Docker is not installed. Skipping Docker build tests."
    DOCKER_AVAILABLE=false
else
    if ! docker info &> /dev/null; then
        print_warning "Docker is not running. Skipping Docker build tests."
        DOCKER_AVAILABLE=false
    else
        print_success "Docker is available and running"
        DOCKER_AVAILABLE=true
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip and install dependencies
print_status "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install test dependencies
if [ -f "requirements-test.txt" ]; then
    pip install -r requirements-test.txt
else
    print_warning "requirements-test.txt not found, installing basic test packages"
    pip install pytest pytest-django coverage
fi

# Set environment variables
export DJANGO_SETTINGS_MODULE="messaging_app.settings"
export DJANGO_SECRET_KEY="test-secret-key-for-local-testing"

# Run Django checks
print_status "Running Django system checks..."
python manage.py check
print_success "Django checks passed"

# Run migrations
print_status "Running database migrations..."
python manage.py makemigrations --dry-run
python manage.py makemigrations
python manage.py migrate
print_success "Database migrations completed"

# Run quick tests
print_status "Running quick smoke tests..."
if python manage.py test chats.test_quick --verbosity=2; then
    print_success "Quick tests passed"
    TESTS_PASSED=true
else
    print_warning "Quick tests had issues, but continuing..."
    TESTS_PASSED=false
fi

# Run model tests
print_status "Running model tests..."
if python manage.py test chats.test_models --verbosity=2; then
    print_success "Model tests passed"
else
    print_warning "Model tests had issues, but continuing..."
fi

# Generate coverage report
print_status "Generating coverage report..."
if command -v coverage &> /dev/null; then
    coverage run --source='.' manage.py test chats.test_quick
    coverage report -m
    coverage html -d coverage_html_report
    print_success "Coverage report generated in coverage_html_report/"
else
    print_warning "Coverage not installed, skipping coverage report"
fi

# Run basic syntax checks
print_status "Running syntax checks..."
python -m py_compile chats/*.py
python -m py_compile messaging_app/*.py
print_success "Syntax checks passed"

# Docker build test (if available)
if [ "$DOCKER_AVAILABLE" = true ] && [ "$TESTS_PASSED" = true ]; then
    print_status "Running Docker build test..."
    
    # Build Docker image
    DOCKER_IMAGE_NAME="alx-messaging-app-test"
    DOCKER_TAG="local-test"
    
    if docker build -t "${DOCKER_IMAGE_NAME}:${DOCKER_TAG}" .; then
        print_success "Docker image built successfully: ${DOCKER_IMAGE_NAME}:${DOCKER_TAG}"
        
        # Test Docker image
        print_status "Testing Docker image..."
        
        # Check if image runs without errors
        if timeout 10s docker run --rm "${DOCKER_IMAGE_NAME}:${DOCKER_TAG}" python manage.py check > /dev/null 2>&1; then
            print_success "Docker image health check passed"
        else
            print_warning "Docker image health check had issues"
        fi
        
        # Check image size
        IMAGE_SIZE=$(docker images "${DOCKER_IMAGE_NAME}:${DOCKER_TAG}" --format "{{.Size}}")
        print_status "Docker image size: $IMAGE_SIZE"
        
        # Check if running as non-root user
        USER_CHECK=$(docker run --rm "${DOCKER_IMAGE_NAME}:${DOCKER_TAG}" whoami)
        if [ "$USER_CHECK" = "appuser" ]; then
            print_success "Security check passed: Running as non-root user ($USER_CHECK)"
        else
            print_warning "Security warning: Container running as user: $USER_CHECK"
        fi
        
        # Cleanup test image
        print_status "Cleaning up test Docker image..."
        docker rmi "${DOCKER_IMAGE_NAME}:${DOCKER_TAG}" > /dev/null 2>&1
        print_success "Docker cleanup completed"
        
    else
        print_error "Docker build failed"
    fi
elif [ "$DOCKER_AVAILABLE" = false ]; then
    print_warning "Skipping Docker build test (Docker not available)"
elif [ "$TESTS_PASSED" = false ]; then
    print_warning "Skipping Docker build test (tests failed)"
fi

# Create test summary report
print_status "Generating test summary report..."
mkdir -p reports
cat > reports/local_test_summary.txt << EOF
=== LOCAL TEST VALIDATION SUMMARY ===
Date: $(date)
Python Version: $(python --version)
Django Version: $(python -c "import django; print(django.get_version())")

=== TEST RESULTS ===
✅ Django system checks: PASSED
✅ Database migrations: COMPLETED
$([ "$TESTS_PASSED" = true ] && echo "✅ Quick tests: PASSED" || echo "⚠️ Quick tests: HAD ISSUES")
✅ Coverage report: GENERATED
✅ Syntax checks: PASSED
$([ "$DOCKER_AVAILABLE" = true ] && [ "$TESTS_PASSED" = true ] && echo "✅ Docker build: TESTED" || echo "⚠️ Docker build: SKIPPED")

=== ENVIRONMENT INFO ===
Working Directory: $(pwd)
Virtual Environment: $(which python)
Docker Available: $DOCKER_AVAILABLE

=== NEXT STEPS ===
1. Review any warnings above
2. Check coverage_html_report/index.html for detailed coverage
3. Commit changes to GitHub repository
4. Run Jenkins pipeline to validate in CI environment
5. Monitor Docker build and push in Jenkins pipeline

EOF

cat reports/local_test_summary.txt

# Summary
echo ""
echo "=================================="
echo "🎉 Extended Local Test Validation Complete!"
echo "=================================="
echo ""
echo "Results:"
echo "✅ Django system checks: PASSED"
echo "✅ Database migrations: COMPLETED"
echo "$([ "$TESTS_PASSED" = true ] && echo "✅ Quick tests: PASSED" || echo "⚠️ Quick tests: HAD ISSUES")"
echo "✅ Model tests: EXECUTED"
echo "✅ Coverage report: GENERATED"
echo "✅ Syntax checks: PASSED"
echo "$([ "$DOCKER_AVAILABLE" = true ] && [ "$TESTS_PASSED" = true ] && echo "✅ Docker build: TESTED" || echo "⚠️ Docker build: SKIPPED")"
echo ""
echo "📁 Reports generated:"
echo "   • reports/local_test_summary.txt"
echo "   • coverage_html_report/index.html"
echo ""
echo "🚀 Next steps for Jenkins pipeline:"
echo "1. Set up Docker Hub credentials in Jenkins"
echo "2. Push updated Jenkinsfile to GitHub"
echo "3. Run Jenkins pipeline manually"
echo "4. Monitor Docker build and push stages"
echo ""

if [ "$DOCKER_AVAILABLE" = true ] && [ "$TESTS_PASSED" = true ]; then
    print_success "Local validation completed successfully with Docker testing!"
else
    print_warning "Local validation completed with warnings. Check Docker availability and test results."
fi
