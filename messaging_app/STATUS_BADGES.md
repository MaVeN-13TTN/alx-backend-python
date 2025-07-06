# Status Badges for README.md

Add these badges to your README.md file to show the current status of your CI/CD pipeline:

## GitHub Actions Workflow Badge

```markdown
![Django CI/CD Pipeline](https://github.com/MaVeN-13TTN/alx-backend-python/workflows/Django%20CI/CD%20Pipeline/badge.svg)
```

## Alternative Badge (if workflow name has spaces)

```markdown
![CI](https://github.com/MaVeN-13TTN/alx-backend-python/actions/workflows/ci.yml/badge.svg)
```

## Coverage Badge (if using Codecov)

```markdown
[![codecov](https://codecov.io/gh/MaVeN-13TTN/alx-backend-python/branch/main/graph/badge.svg)](https://codecov.io/gh/MaVeN-13TTN/alx-backend-python)
```

## License Badge

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

## Python Version Badge

```markdown
![Python Version](https://img.shields.io/badge/python-3.10-blue.svg)
```

## Django Version Badge

```markdown
![Django Version](https://img.shields.io/badge/django-5.2.1-green.svg)
```

## Complete Badge Section for README.md

Copy this complete section to your README.md:

````markdown
# ALX Backend Python - Messaging App

![Django CI/CD Pipeline](https://github.com/MaVeN-13TTN/alx-backend-python/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/MaVeN-13TTN/alx-backend-python/branch/main/graph/badge.svg)](https://codecov.io/gh/MaVeN-13TTN/alx-backend-python)
![Python Version](https://img.shields.io/badge/python-3.10-blue.svg)
![Django Version](https://img.shields.io/badge/django-5.2.1-green.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Django REST API messaging application with comprehensive CI/CD pipeline including GitHub Actions, Jenkins, and Docker integration.

## Features

- JWT Authentication
- Real-time messaging
- User management
- Conversation management
- RESTful API design
- Comprehensive test coverage
- Automated CI/CD pipeline

## CI/CD Pipeline

This project includes multiple CI/CD solutions:

### GitHub Actions

- Automated testing on push/PR
- MySQL database integration
- Code quality checks (Black, isort, flake8, pylint)
- Security scanning (Bandit, Safety, Trivy)
- Docker image building and testing
- Coverage reporting

### Jenkins Pipeline

- Docker-based Jenkins setup
- Python environment management
- Django testing with pytest
- Docker image building and pushing to Docker Hub
- Manual trigger capability

## Quick Start

### Local Development

```bash
cd messaging_app
./run_tests_local.sh
```
````

### GitHub Actions Testing

```bash
cd messaging_app
./test_github_actions.sh
```

### Jenkins Setup

```bash
cd messaging_app
./setup_jenkins.sh
```

## Documentation

- [GitHub Actions Guide](messaging_app/GITHUB_ACTIONS_GUIDE.md)
- [Jenkins Implementation Guide](messaging_app/JENKINS_IMPLEMENTATION_GUIDE.md)
- [Docker Integration Guide](messaging_app/DOCKER_INTEGRATION_GUIDE.md)
- [API Documentation](messaging_app/README.md)

````

## Badge Styles

You can customize badge styles by adding parameters:

### Flat Style
```markdown
![CI](https://github.com/MaVeN-13TTN/alx-backend-python/actions/workflows/ci.yml/badge.svg?style=flat)
````

### Flat Square Style

```markdown
![CI](https://github.com/MaVeN-13TTN/alx-backend-python/actions/workflows/ci.yml/badge.svg?style=flat-square)
```

### For the Badge Style

```markdown
![CI](https://github.com/MaVeN-13TTN/alx-backend-python/actions/workflows/ci.yml/badge.svg?style=for-the-badge)
```

## Dynamic Badges

### Latest Release

```markdown
![GitHub release (latest by date)](https://img.shields.io/github/v/release/MaVeN-13TTN/alx-backend-python)
```

### Commit Activity

```markdown
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/MaVeN-13TTN/alx-backend-python)
```

### Issues

```markdown
![GitHub issues](https://img.shields.io/github/issues/MaVeN-13TTN/alx-backend-python)
```

### Pull Requests

```markdown
![GitHub pull requests](https://img.shields.io/github/issues-pr/MaVeN-13TTN/alx-backend-python)
```

## Usage Instructions

1. **Copy the badges you want** from the sections above
2. **Add them to your README.md** in the repository root or messaging_app directory
3. **Update the repository URLs** if your repository name or owner is different
4. **Test the badges** by pushing the changes and verifying they display correctly

The badges will automatically update based on your repository status, workflow runs, and other metrics.
