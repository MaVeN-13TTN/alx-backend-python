# GitHub Actions Quick Reference

## 🚀 Quick Setup Checklist

### Prerequisites

- [ ] GitHub repository with messaging_app code
- [ ] `.github/workflows/ci.yml` file created
- [ ] `requirements-test.txt` file present
- [ ] All test files in `chats/` directory

### Workflow Triggers

```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
```

## 📋 Workflow Jobs

### 1. Test Job 🧪

```
✅ MySQL 8.0 Service
✅ Python 3.10 Setup
✅ Dependencies Installation
✅ Django System Checks
✅ Database Migrations
✅ Django Test Execution
✅ Coverage Analysis
✅ Security Scanning
```

### 2. Lint Job 🔍

```
✅ Black Code Formatting
✅ isort Import Sorting
✅ flake8 Linting
✅ pylint Static Analysis
```

### 3. Docker Job 🐳

```
✅ Docker Image Build
✅ Security Testing
✅ Trivy Vulnerability Scan
✅ Non-root User Verification
```

### 4. Deploy Job 🚀

```
✅ Staging Deployment
✅ Health Checks
✅ Smoke Tests
```

### 5. Notify Job 📢

```
✅ Success Notifications
✅ Failure Alerts
✅ Build Metadata
```

## 🗄️ Database Configuration

### MySQL Service

```yaml
mysql:
  image: mysql:8.0
  env:
    MYSQL_DATABASE: messaging_app_test
    MYSQL_USER: messaging_user
    MYSQL_PASSWORD: messaging_password
  ports:
    - 3306:3306
```

### Django Environment

```yaml
DB_ENGINE: "django.db.backends.mysql"
DB_NAME: "messaging_app_test"
DB_USER: "messaging_user"
DB_PASSWORD: "messaging_password"
DB_HOST: "127.0.0.1"
DB_PORT: "3306"
```

## 🔧 Key Commands

### Local Testing

```bash
./test_github_actions.sh  # Full simulation
./run_tests_local.sh     # Quick tests
```

### Manual Trigger

1. Push to `main` or `develop` branch
2. Create pull request to `main` or `develop`
3. Use GitHub UI "Run workflow" button

## 📁 Files Structure

```
messaging_app/
├── .github/
│   └── workflows/
│       └── ci.yml ⬅️ MAIN WORKFLOW
├── requirements.txt ✅
├── requirements-test.txt ✅
├── pytest.ini ✅
├── pytest-github.ini ⬅️ NEW
├── test_github_actions.sh ⬅️ NEW
├── Dockerfile ✅
├── .dockerignore ✅
└── chats/
    ├── test_models.py ✅
    ├── test_api.py ✅
    └── test_quick.py ✅
```

## 📊 Expected Workflow Output

### Successful Run

```
✅ test (5-8 minutes)
  ├── MySQL service ready
  ├── Dependencies installed
  ├── Django checks passed
  ├── Migrations applied
  ├── Tests executed (quick, models, api)
  ├── Coverage: >80%
  └── Security scans completed

✅ lint (2-3 minutes)
  ├── Black formatting: PASSED
  ├── isort imports: PASSED
  ├── flake8 linting: PASSED
  └── pylint analysis: PASSED

✅ docker (3-4 minutes)
  ├── Image built successfully
  ├── Security check: non-root user
  ├── Trivy scan: completed
  └── Functionality test: PASSED

✅ deploy-staging (1-2 minutes)
  ├── Deployment simulation
  └── Health checks: PASSED

✅ notify (30 seconds)
  └── Success notification sent
```

## 🔍 Monitoring and Verification

### GitHub UI

1. **Actions Tab** → View workflow runs
2. **Pull Requests** → Check status badges
3. **Security Tab** → Review Trivy scans
4. **Code Tab** → Download artifacts

### Verification Steps

```bash
# 1. Check workflow status
git push origin main  # Triggers workflow

# 2. Monitor progress
# Visit: https://github.com/MaVeN-13TTN/alx-backend-python/actions

# 3. Review artifacts
# Download: coverage reports, security scans
```

## 🚨 Common Issues & Solutions

### MySQL Connection Failed

```yaml
# Increase health check retries
options: >-
  --health-retries=5
  --health-timeout=10s
```

### Test Dependencies Missing

```bash
# Ensure requirements-test.txt includes:
pytest==8.3.2
pytest-django==4.8.0
coverage==7.6.1
```

### Docker Build Failed

```bash
# Check Dockerfile and .dockerignore
# Verify build context is correct
```

### Coverage Upload Failed

```bash
# Codecov token may be required for private repos
# Check coverage.xml file generation
```

## ⚡ Quick Commands

### Local Development

```bash
# Test everything locally
./test_github_actions.sh

# Format code
black .
isort .

# Run linting
flake8 .
```

### Repository Commands

```bash
# Add workflow file
git add .github/workflows/ci.yml

# Commit changes
git commit -m "Add GitHub Actions CI/CD workflow"

# Push to trigger workflow
git push origin main
```

## 🎯 Success Indicators

### Workflow Completion

✅ All jobs complete successfully  
✅ No failed test cases  
✅ Coverage above threshold (>80%)  
✅ No security vulnerabilities found  
✅ Code quality checks passed  
✅ Docker image builds successfully

### Repository Status

✅ Green status badges on README  
✅ Pull requests require passing checks  
✅ Main branch protected from direct pushes  
✅ Artifacts available for download

## 📞 Support Resources

- **Detailed Guide**: `GITHUB_ACTIONS_GUIDE.md`
- **Test Script**: `./test_github_actions.sh`
- **Django Tests**: `chats/test_*.py`
- **Workflow File**: `.github/workflows/ci.yml`

## 🔗 Useful Links

- **GitHub Actions**: https://github.com/features/actions
- **Workflow Syntax**: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
- **MySQL Service**: https://docs.github.com/en/actions/guides/creating-mysql-service-containers
- **Codecov**: https://codecov.io/

---

**Ready for automated testing! 🎉**
