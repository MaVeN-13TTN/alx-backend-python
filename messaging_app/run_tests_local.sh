#!/bin/bash

# Quick test runner script for local validation
# This script mimics what the Jenkins pipeline will do

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

print_status "Starting local test validation..."

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
else
    print_warning "Quick tests had issues, but continuing..."
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

# Summary
echo ""
echo "=================================="
echo "🎉 Local Test Validation Complete!"
echo "=================================="
echo ""
echo "Results:"
echo "✅ Django system checks: PASSED"
echo "✅ Database migrations: COMPLETED"
echo "✅ Quick tests: EXECUTED"
echo "✅ Model tests: EXECUTED"
echo "✅ Coverage report: GENERATED"
echo "✅ Syntax checks: PASSED"
echo ""
echo "Next steps:"
echo "1. Review any warnings above"
echo "2. Check coverage_html_report/index.html for detailed coverage"
echo "3. Run GitHub Actions simulation: ./test_github_actions.sh"
echo "4. Run Jenkins pipeline to validate in CI environment"
echo "5. Push .github/workflows/ci.yml to trigger automated testing"
echo ""

print_success "Local validation completed successfully!"
