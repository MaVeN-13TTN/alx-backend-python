# GitHub Actions CI/CD Workflow Guide

## Overview

This guide explains the GitHub Actions workflow setup for the ALX Backend Python messaging app, providing automated testing, code quality checks, and deployment capabilities.

## Workflow Features

### 🧪 **Automated Testing**

- Runs on every push and pull request
- Multi-job parallel execution for efficiency
- MySQL database integration for realistic testing
- Comprehensive test coverage reporting

### 🔍 **Code Quality Assurance**

- Black code formatting validation
- isort import sorting checks
- flake8 linting with complexity analysis
- pylint static code analysis

### 🐳 **Docker Integration**

- Automated Docker image building
- Container security scanning with Trivy
- Non-root user verification
- Vulnerability assessment

### 🚀 **Deployment Pipeline**

- Staging environment deployment
- Health checks and smoke tests
- Artifact management and reporting

## Workflow Structure

### Jobs Overview

```yaml
Jobs:
├── test (Ubuntu) ──────── MySQL Service
├── lint (Ubuntu) ──────── Code Quality
├── docker (Ubuntu) ────── Docker Build & Scan
├── deploy-staging ─────── Staging Deployment
└── notify ─────────────── Results Notification
```

### Trigger Conditions

**Push Events:**

- `main` branch
- `develop` branch

**Pull Request Events:**

- Target: `main` branch
- Target: `develop` branch

## Database Configuration

### MySQL Service Setup

The workflow uses MySQL 8.0 as a service container:

```yaml
services:
  mysql:
    image: mysql:8.0
    env:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: messaging_app_test
      MYSQL_USER: messaging_user
      MYSQL_PASSWORD: messaging_password
    ports:
      - 3306:3306
    options: >-
      --health-cmd="mysqladmin ping"
      --health-interval=10s
      --health-timeout=5s
      --health-retries=3
```

### Django Database Configuration

Environment variables configure Django to use MySQL:

```yaml
env:
  DB_ENGINE: "django.db.backends.mysql"
  DB_NAME: "messaging_app_test"
  DB_USER: "messaging_user"
  DB_PASSWORD: "messaging_password"
  DB_HOST: "127.0.0.1"
  DB_PORT: "3306"
```

## Job Details

### Job 1: Test

**Purpose:** Run comprehensive Django tests with MySQL

**Steps:**

1. **Environment Setup**

   - Ubuntu latest runner
   - Python 3.10 with pip caching
   - System dependencies (MySQL client libraries)

2. **Dependencies Installation**

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

3. **Database Preparation**

   - Wait for MySQL service readiness
   - Verify database connection
   - Run Django migrations

4. **Testing Execution**

   ```bash
   python manage.py test chats.test_quick --verbosity=2 --keepdb
   python manage.py test chats.test_models --verbosity=2 --keepdb
   python manage.py test chats.test_api --verbosity=2 --keepdb
   ```

5. **Coverage Analysis**

   ```bash
   coverage run --source='.' manage.py test chats.test_quick
   coverage report -m
   coverage xml -o coverage.xml
   coverage html -d coverage_html_report
   ```

6. **Security Scanning**

   - Django deployment checks
   - Safety vulnerability scanning
   - Bandit security analysis

7. **Artifact Upload**
   - Coverage reports to Codecov
   - HTML coverage reports
   - Security scan results

### Job 2: Lint

**Purpose:** Ensure code quality and consistency

**Tools Used:**

- **Black:** Code formatting validation
- **isort:** Import sorting verification
- **flake8:** PEP 8 compliance and complexity analysis
- **pylint:** Static code analysis with Django plugin

**Configuration:**

```bash
# Black formatting
black --check --diff .

# Import sorting
isort --check-only --diff .

# Flake8 linting
flake8 . --max-complexity=10 --max-line-length=127

# Pylint analysis
pylint --load-plugins=pylint_django --django-settings-module=messaging_app.settings **/*.py
```

### Job 3: Docker

**Purpose:** Build and test Docker images

**Requirements:**

- Depends on successful test and lint jobs
- Only runs on main branch pushes

**Process:**

1. **Image Building**

   ```bash
   docker build -t messaging-app:${{ github.sha }} .
   docker build -t messaging-app:latest .
   ```

2. **Security Testing**

   ```bash
   # Test non-root user execution
   docker run --rm messaging-app:${{ github.sha }} whoami

   # Basic functionality test
   docker run --rm messaging-app:${{ github.sha }} python manage.py check
   ```

3. **Vulnerability Scanning**
   - Trivy security scanner
   - SARIF report generation
   - GitHub Security tab integration

### Job 4: Deploy Staging

**Purpose:** Deploy to staging environment

**Conditions:**

- All previous jobs successful
- Push to main branch only
- Uses GitHub Environments for approval

**Features:**

- Deployment simulation
- Health check validation
- Team notification capability

### Job 5: Notify

**Purpose:** Provide workflow result notifications

**Conditions:**

- Always runs (regardless of job outcomes)
- Provides success/failure status
- Includes build metadata

## Environment Variables

### Django Configuration

```yaml
DJANGO_SETTINGS_MODULE: messaging_app.settings
DJANGO_SECRET_KEY: "test-secret-key-for-github-actions"
DJANGO_DEBUG: "False"
```

### Database Configuration

```yaml
DB_ENGINE: "django.db.backends.mysql"
DB_NAME: "messaging_app_test"
DB_USER: "messaging_user"
DB_PASSWORD: "messaging_password"
DB_HOST: "127.0.0.1"
DB_PORT: "3306"
```

## Artifacts and Reporting

### Coverage Reports

- **Codecov Integration:** Automatic upload to Codecov.io
- **HTML Reports:** Downloadable coverage visualization
- **XML Reports:** Machine-readable coverage data

### Security Reports

- **Bandit:** Python security issue detection
- **Safety:** Known vulnerability scanning
- **Trivy:** Container image vulnerability assessment

### Code Quality Reports

- **Linting Results:** Detailed code quality analysis
- **Formatting Issues:** Black and isort violations
- **Complexity Metrics:** Cyclomatic complexity analysis

## Local Testing

### GitHub Actions Simulation

Run the complete workflow locally:

```bash
cd messaging_app
./test_github_actions.sh
```

This script:

- ✅ Sets up local MySQL container (if Docker available)
- ✅ Runs all test suites
- ✅ Performs code quality checks
- ✅ Tests Docker image building
- ✅ Generates comprehensive reports

### Quick Testing

For rapid validation:

```bash
cd messaging_app
./run_tests_local.sh
```

## Repository Setup

### Required Files

Ensure these files exist in your repository:

```
messaging_app/
├── .github/
│   └── workflows/
│       └── ci.yml ⬅️ Main workflow file
├── requirements.txt ⬅️ Main dependencies
├── requirements-test.txt ⬅️ Test dependencies
├── pytest.ini ⬅️ Test configuration
├── pytest-github.ini ⬅️ GitHub Actions test config
├── Dockerfile ⬅️ Container configuration
├── .dockerignore ⬅️ Docker ignore rules
└── manage.py ⬅️ Django management script
```

### Branch Protection

Configure branch protection for `main`:

1. **GitHub Repository Settings**
2. **Branches → Add rule**
3. **Branch name pattern:** `main`
4. **Protection settings:**
   - ☑ Require status checks to pass
   - ☑ Require branches to be up to date
   - ☑ Status checks: `test`, `lint`, `docker`
   - ☑ Require pull request reviews
   - ☑ Dismiss stale reviews

### Secrets Configuration

No secrets required for basic workflow. Optional integrations:

**Codecov (Optional):**

- `CODECOV_TOKEN` - For private repositories

**Slack/Discord (Optional):**

- `SLACK_WEBHOOK` - For team notifications
- `DISCORD_WEBHOOK` - For Discord integration

## Monitoring and Maintenance

### Workflow Monitoring

**GitHub Actions Tab:**

- Monitor workflow execution times
- Review build logs and errors
- Download artifacts and reports

**Status Badges:**
Add to README.md:

```markdown
![CI](https://github.com/MaVeN-13TTN/alx-backend-python/workflows/Django%20CI%2FCD%20Pipeline/badge.svg)
```

### Performance Optimization

**Caching Strategies:**

- ✅ Python pip cache enabled
- ✅ Docker layer caching configured
- ✅ Database reuse with `--keepdb`

**Parallel Execution:**

- ✅ Test and lint jobs run in parallel
- ✅ Multiple test modules run concurrently
- ✅ Independent job execution

### Regular Maintenance

**Weekly Tasks:**

- Review workflow execution times
- Update dependencies in requirements files
- Check for new security vulnerabilities

**Monthly Tasks:**

- Update GitHub Actions versions
- Review and optimize workflow configuration
- Update Python and MySQL versions

## Troubleshooting

### Common Issues

#### 1. MySQL Connection Failures

```yaml
# Solution: Increase health check timeout
options: >-
  --health-cmd="mysqladmin ping"
  --health-interval=10s
  --health-timeout=10s  # Increased
  --health-retries=5     # Increased
```

#### 2. Test Database Creation Issues

```bash
# Check MySQL service logs
# Verify user permissions
# Ensure database name consistency
```

#### 3. Docker Build Failures

```bash
# Check Dockerfile syntax
# Verify build context
# Review .dockerignore rules
```

#### 4. Coverage Report Issues

```bash
# Ensure coverage package installed
# Check file path configurations
# Verify source code paths
```

### Debug Mode

Enable debug output in workflow:

```yaml
env:
  DJANGO_DEBUG: "True" # Temporary for debugging
  PYTHONUNBUFFERED: "1"
```

### Local Debugging

Test individual components:

```bash
# Test MySQL connection
docker run --rm mysql:8.0 mysqladmin ping -h host.docker.internal

# Test Django with MySQL
DB_ENGINE=django.db.backends.mysql python manage.py check

# Test coverage generation
coverage run manage.py test && coverage report
```

## Advanced Configuration

### Multi-Environment Testing

Test against multiple Python versions:

```yaml
strategy:
  matrix:
    python-version: [3.9, 3.10, 3.11]
    django-version: [4.2, 5.0, 5.1]
```

### Conditional Deployment

Deploy only on tagged releases:

```yaml
if: startsWith(github.ref, 'refs/tags/')
```

### Custom Test Runners

Use custom Django test runners:

```yaml
- name: Run tests with custom runner
  run: python manage.py test --testrunner=custom.test.runner
```

## Integration Examples

### Slack Notifications

```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Email Notifications

```yaml
- name: Send email notification
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: "Build Failed: ${{ github.repository }}"
    body: "Build ${{ github.run_number }} failed on ${{ github.ref }}"
```

## Summary

This GitHub Actions workflow provides:

✅ **Comprehensive Testing** with MySQL database  
✅ **Automated Code Quality** checks and formatting  
✅ **Security Scanning** for vulnerabilities  
✅ **Docker Integration** with container testing  
✅ **Parallel Execution** for faster feedback  
✅ **Artifact Management** and reporting  
✅ **Staging Deployment** automation  
✅ **Notification System** for team awareness

The workflow ensures high code quality, security, and reliability through automated testing and validation on every code change.
