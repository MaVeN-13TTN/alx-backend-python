# Jenkins CI/CD Pipeline for ALX Backend Python - Messaging App

## Quick Start

### 1. Setup Jenkins (Automated)

```bash
cd messaging_app
./setup_jenkins.sh
```

### 2. Access Jenkins

- URL: http://localhost:8080
- Use the password displayed by the setup script

### 3. Install Required Plugins

- Git Plugin
- Pipeline Plugin
- ShiningPanda Plugin
- HTML Publisher Plugin
- JUnit Plugin

### 4. Add GitHub Credentials

1. Go to **Manage Jenkins** → **Manage Credentials**
2. Add new **Username with password** credential
3. ID: `github-credentials`
4. Username: Your GitHub username
5. Password: Your GitHub Personal Access Token

### 5. Create Pipeline Job

1. **New Item** → **Pipeline**
2. Name: `ALX-Messaging-App-Pipeline`
3. **Pipeline** → **Pipeline script from SCM**
4. **SCM**: Git
5. **Repository URL**: `https://github.com/MaVeN-13TTN/alx-backend-python.git`
6. **Credentials**: `github-credentials`
7. **Script Path**: `messaging_app/Jenkinsfile`

### 6. Run Pipeline

Click **Build Now** to trigger the pipeline manually.

## Local Testing

Before running the Jenkins pipeline, test locally:

```bash
cd messaging_app
./run_tests_local.sh
```

## Pipeline Features

✅ **Automated Testing**: Django unit tests and API tests  
✅ **Code Coverage**: HTML reports with detailed coverage metrics  
✅ **Parallel Execution**: Multiple test stages run simultaneously  
✅ **Quality Checks**: Django system checks and syntax validation  
✅ **Security Validation**: Django deployment checks  
✅ **Comprehensive Reporting**: Test results, coverage, and build artifacts

## Project Structure

```
messaging_app/
├── Jenkinsfile                 # Pipeline configuration
├── setup_jenkins.sh           # Jenkins setup script
├── run_tests_local.sh         # Local test runner
├── requirements-test.txt       # Test dependencies
├── pytest.ini                 # Test configuration
├── chats/
│   ├── test_models.py         # Model tests
│   ├── test_api.py            # API tests
│   └── test_quick.py          # Quick tests
└── JENKINS_IMPLEMENTATION_GUIDE.md  # Detailed guide
```

## Test Types

### Quick Tests (`chats/test_quick.py`)

- Fast smoke tests for immediate feedback
- Basic functionality validation
- API accessibility checks
- Model creation verification

### Model Tests (`chats/test_models.py`)

- User model functionality
- Conversation model operations
- Message model behavior
- Database relationship validation

### API Tests (`chats/test_api.py`)

- Authentication endpoints
- User management APIs
- Conversation operations
- Message functionality
- Permission validation

## Pipeline Stages

1. **Checkout** - Pull code from GitHub
2. **Setup Python Environment** - Create venv and install deps
3. **Environment Validation** - Django configuration checks
4. **Database Setup** - Run migrations
5. **Run Tests** - Execute test suites (parallel)
6. **Test Coverage** - Generate coverage reports
7. **Code Quality** - Syntax and system checks
8. **Security Checks** - Django security validation
9. **Integration Tests** - Full API testing
10. **Generate Reports** - Comprehensive reporting

## Troubleshooting

### Jenkins Container Issues

```bash
# Check status
docker ps | grep jenkins

# View logs
docker logs jenkins

# Restart
docker restart jenkins
```

### Test Failures

```bash
# Run tests manually
cd messaging_app
python manage.py test chats.test_quick --verbosity=2

# Check Django configuration
python manage.py check
```

### Permission Issues

```bash
# Fix Jenkins permissions
docker exec jenkins chown -R jenkins:jenkins /var/jenkins_home
```

## Repository Information

- **Repository**: alx-backend-python
- **Owner**: MaVeN-13TTN
- **Directory**: messaging_app
- **Main Branch**: main
- **Jenkinsfile**: messaging_app/Jenkinsfile

## Manual Trigger

The pipeline is designed for manual triggering as specified in the requirements:

1. Access Jenkins dashboard
2. Navigate to the pipeline job
3. Click **Build Now**
4. Monitor build progress and view reports

## Reports and Artifacts

After each build:

- **Test Results**: Available in Jenkins build page
- **Coverage Report**: Published as HTML report
- **Build Artifacts**: Downloadable logs and reports
- **Console Output**: Detailed build logs

## Dependencies

### Main Dependencies (requirements.txt)

- Django==5.2.1
- djangorestframework==3.15.2
- django-filter==24.3
- drf-nested-routers==0.94.1
- djangorestframework-simplejwt==5.5.0

### Test Dependencies (requirements-test.txt)

- pytest==8.3.2
- pytest-django==4.8.0
- coverage==7.6.1
- And other testing utilities

## Support

For detailed implementation guidance, see:

- `JENKINS_IMPLEMENTATION_GUIDE.md` - Complete setup guide
- `Jenkinsfile` - Pipeline configuration
- Test files in `chats/` directory

## Security Notes

- Use Personal Access Tokens for GitHub integration
- Store credentials securely in Jenkins
- Never commit secrets to the repository
- Regularly update Jenkins and plugins
