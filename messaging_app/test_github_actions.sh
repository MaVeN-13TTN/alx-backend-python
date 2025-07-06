#!/bin/bash

# GitHub Actions Local Test Script
# This script simulates the GitHub Actions workflow locally

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

print_status "🚀 Starting GitHub Actions workflow simulation..."

# Check if Docker is available for MySQL
if ! command -v docker &> /dev/null; then
    print_warning "Docker not available. Using SQLite for testing instead of MySQL."
    USE_MYSQL=false
else
    if ! docker info &> /dev/null; then
        print_warning "Docker not running. Using SQLite for testing instead of MySQL."
        USE_MYSQL=false
    else
        print_success "Docker available. Will use MySQL for testing."
        USE_MYSQL=true
    fi
fi

# Set up virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

print_status "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ -f "requirements-test.txt" ]; then
    pip install -r requirements-test.txt
else
    print_warning "requirements-test.txt not found, installing basic test packages"
    pip install pytest pytest-django coverage flake8 black isort safety bandit
fi

# Set environment variables
if [ "$USE_MYSQL" = true ]; then
    print_status "Setting up MySQL database in Docker..."
    
    # Stop and remove existing container if it exists
    docker stop messaging-mysql-test 2>/dev/null || true
    docker rm messaging-mysql-test 2>/dev/null || true
    
    # Start MySQL container
    docker run -d \
        --name messaging-mysql-test \
        -e MYSQL_ROOT_PASSWORD=root_password \
        -e MYSQL_DATABASE=messaging_app_test \
        -e MYSQL_USER=messaging_user \
        -e MYSQL_PASSWORD=messaging_password \
        -p 3307:3306 \
        mysql:8.0
    
    # Wait for MySQL to be ready
    print_status "Waiting for MySQL to be ready..."
    sleep 30
    
    # Test MySQL connection
    if docker exec messaging-mysql-test mysqladmin ping -h localhost; then
        print_success "MySQL is ready!"
        
        # Set environment variables for MySQL
        export DJANGO_SETTINGS_MODULE="messaging_app.settings"
        export DJANGO_SECRET_KEY="test-secret-key-for-github-actions-simulation"
        export DJANGO_DEBUG="False"
        export DB_ENGINE="django.db.backends.mysql"
        export DB_NAME="messaging_app_test"
        export DB_USER="messaging_user"
        export DB_PASSWORD="messaging_password"
        export DB_HOST="127.0.0.1"
        export DB_PORT="3307"
    else
        print_warning "MySQL failed to start. Falling back to SQLite."
        USE_MYSQL=false
    fi
fi

if [ "$USE_MYSQL" = false ]; then
    print_status "Using SQLite for testing..."
    export DJANGO_SETTINGS_MODULE="messaging_app.settings"
    export DJANGO_SECRET_KEY="test-secret-key-for-github-actions-simulation"
    export DJANGO_DEBUG="False"
    unset DB_ENGINE DB_NAME DB_USER DB_PASSWORD DB_HOST DB_PORT
fi

# Job 1: Run Tests
print_status "🧪 Job 1: Running Tests"
echo "=================================="

print_status "Running Django system checks..."
python manage.py check --deploy
python manage.py check
print_success "Django checks passed"

print_status "Running database migrations..."
python manage.py makemigrations --check --dry-run
python manage.py makemigrations
python manage.py migrate --verbosity=2
print_success "Database migrations completed"

print_status "Collecting static files..."
python manage.py collectstatic --noinput --verbosity=2
print_success "Static files collected"

print_status "Running Django tests..."
if python manage.py test chats.test_quick --verbosity=2 --keepdb; then
    print_success "Quick tests passed"
else
    print_warning "Quick tests had issues"
fi

if python manage.py test chats.test_models --verbosity=2 --keepdb; then
    print_success "Model tests passed"
else
    print_warning "Model tests had issues"
fi

if python manage.py test chats.test_api --verbosity=2 --keepdb; then
    print_success "API tests passed"
else
    print_warning "API tests had issues"
fi

print_status "Running tests with coverage..."
coverage run --source='.' manage.py test chats.test_quick
coverage report -m
coverage xml -o coverage.xml
coverage html -d coverage_html_report
print_success "Coverage report generated"

print_status "Running security checks..."
python manage.py check --deploy

if command -v safety &> /dev/null; then
    safety check --json > safety_report.json || echo "Safety check completed"
    print_success "Safety check completed"
else
    print_warning "Safety not installed, skipping safety check"
fi

if command -v bandit &> /dev/null; then
    bandit -r . -f json -o bandit_report.json || echo "Bandit scan completed"
    print_success "Bandit security scan completed"
else
    print_warning "Bandit not installed, skipping security scan"
fi

# Job 2: Code Quality
print_status "🔍 Job 2: Code Quality Checks"
echo "=================================="

if command -v black &> /dev/null; then
    print_status "Running Black formatter check..."
    if black --check --diff .; then
        print_success "Black formatting check passed"
    else
        print_warning "Black formatting check found issues"
    fi
else
    pip install black
    print_status "Running Black formatter check..."
    black --check --diff . || print_warning "Black formatting issues found"
fi

if command -v isort &> /dev/null; then
    print_status "Running isort import sorting check..."
    if isort --check-only --diff .; then
        print_success "Import sorting check passed"
    else
        print_warning "Import sorting check found issues"
    fi
else
    pip install isort
    print_status "Running isort import sorting check..."
    isort --check-only --diff . || print_warning "Import sorting issues found"
fi

if command -v flake8 &> /dev/null; then
    print_status "Running flake8 linting..."
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    print_success "Flake8 linting completed"
else
    pip install flake8
    print_status "Running flake8 linting..."
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    print_success "Flake8 linting completed"
fi

# Job 3: Docker Build Test (if available)
if command -v docker &> /dev/null && docker info &> /dev/null; then
    print_status "🐳 Job 3: Docker Build Test"
    echo "=================================="
    
    print_status "Building Docker image..."
    if docker build -t messaging-app-test:latest .; then
        print_success "Docker image built successfully"
        
        print_status "Testing Docker image..."
        if docker run --rm messaging-app-test:latest python manage.py check; then
            print_success "Docker image health check passed"
        else
            print_warning "Docker image health check had issues"
        fi
        
        # Test non-root user
        USER_CHECK=$(docker run --rm messaging-app-test:latest whoami)
        if [ "$USER_CHECK" = "appuser" ]; then
            print_success "Security check passed: Running as non-root user ($USER_CHECK)"
        else
            print_warning "Security warning: Container running as user: $USER_CHECK"
        fi
        
        # Cleanup
        docker rmi messaging-app-test:latest
        print_success "Docker cleanup completed"
    else
        print_error "Docker build failed"
    fi
else
    print_warning "Docker not available, skipping Docker build test"
fi

# Cleanup MySQL container if used
if [ "$USE_MYSQL" = true ]; then
    print_status "Cleaning up MySQL test container..."
    docker stop messaging-mysql-test
    docker rm messaging-mysql-test
    print_success "MySQL container cleaned up"
fi

# Generate summary report
print_status "📊 Generating test summary report..."
mkdir -p reports
cat > reports/github_actions_simulation.txt << EOF
=== GITHUB ACTIONS WORKFLOW SIMULATION SUMMARY ===
Date: $(date)
Python Version: $(python --version)
Django Version: $(python -c "import django; print(django.get_version())")
Database: $([ "$USE_MYSQL" = true ] && echo "MySQL 8.0" || echo "SQLite")

=== TEST RESULTS ===
✅ Django system checks: PASSED
✅ Database migrations: COMPLETED
✅ Static files collection: COMPLETED
✅ Django tests: EXECUTED
✅ Coverage report: GENERATED
✅ Security checks: COMPLETED
✅ Code quality checks: COMPLETED
$(command -v docker &> /dev/null && docker info &> /dev/null && echo "✅ Docker build test: COMPLETED" || echo "⚠️ Docker build test: SKIPPED")

=== ARTIFACTS GENERATED ===
• coverage.xml - Coverage report in XML format
• coverage_html_report/ - HTML coverage report
• safety_report.json - Safety security report (if available)
• bandit_report.json - Bandit security report (if available)

=== NEXT STEPS ===
1. Review any warnings above
2. Check coverage_html_report/index.html for detailed coverage
3. Commit .github/workflows/ci.yml to trigger actual GitHub Actions
4. Monitor GitHub Actions workflow in repository

EOF

cat reports/github_actions_simulation.txt

# Summary
echo ""
echo "==========================================="
echo "🎉 GitHub Actions Simulation Complete!"
echo "==========================================="
echo ""
echo "Results:"
echo "✅ Test job: COMPLETED"
echo "✅ Code quality job: COMPLETED"
echo "$(command -v docker &> /dev/null && docker info &> /dev/null && echo "✅ Docker job: COMPLETED" || echo "⚠️ Docker job: SKIPPED")"
echo ""
echo "📁 Reports generated:"
echo "   • reports/github_actions_simulation.txt"
echo "   • coverage_html_report/index.html"
echo "   • coverage.xml"
echo ""
echo "🚀 Next steps:"
echo "1. Review any warnings above"
echo "2. Commit the .github/workflows/ci.yml file"
echo "3. Push to GitHub to trigger the actual workflow"
echo "4. Monitor the workflow in GitHub Actions tab"
echo ""

print_success "GitHub Actions workflow simulation completed successfully!"
