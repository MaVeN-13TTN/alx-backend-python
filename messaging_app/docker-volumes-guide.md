# Docker Volumes for Data Persistence Guide

This document explains how Docker volumes are implemented in the messaging app to ensure data persistence across container restarts and rebuilds.

## 📊 Overview

Docker volumes provide persistent storage that survives container lifecycle events including:

- Container stops and starts
- Container removal and recreation
- Image rebuilds
- System reboots

## 🏗️ Current Volume Configuration

### Volume Declaration in docker-compose.yml

```yaml
# Services configuration
services:
  db:
    image: mysql:8.0
    # ... other configurations
    volumes:
      - mysql_data:/var/lib/mysql # MySQL data persistence
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql # Initialization script

  web:
    build: .
    # ... other configurations
    volumes:
      - .:/app # Development code mounting
      - static_volume:/app/staticfiles # Static files persistence

# Volume declarations
volumes:
  mysql_data: # Named volume for MySQL data
  static_volume: # Named volume for Django static files

networks:
  messaging_network:
    driver: bridge
```

## 📁 Volume Types Implemented

### 1. Named Volume (mysql_data)

- **Purpose**: Persist MySQL database files
- **Mount Point**: `/var/lib/mysql` (inside container)
- **Host Location**: `/var/lib/docker/volumes/messaging_app_mysql_data/_data`
- **Persistence**: Survives container removal and recreation

### 2. Named Volume (static_volume)

- **Purpose**: Persist Django static files
- **Mount Point**: `/app/staticfiles` (inside container)
- **Host Location**: `/var/lib/docker/volumes/messaging_app_static_volume/_data`
- **Persistence**: Survives container removal and recreation

### 3. Bind Mount (Development)

- **Purpose**: Live code editing during development
- **Mount Point**: `.:/app` (current directory to container /app)
- **Host Location**: Current project directory
- **Persistence**: Files exist on host filesystem

### 4. Bind Mount (Initialization)

- **Purpose**: MySQL initialization script
- **Mount Point**: `./init.sql:/docker-entrypoint-initdb.d/init.sql`
- **Host Location**: Local init.sql file
- **Persistence**: Read-only initialization script

## ✅ Data Persistence Verification

### Test Results

I performed a complete data persistence test with the following steps:

#### 1. Initial State Check

```bash
# Check running containers
docker-compose ps
# Result: Both containers running healthy

# Check existing user count
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/users/
# Result: 1 user (testuser) in database
```

#### 2. Container Removal

```bash
# Stop and remove all containers
docker-compose down
# Result: Containers removed, network removed, volumes retained
```

#### 3. Volume Persistence Verification

```bash
# Check if volumes still exist
docker volume ls | grep messaging
# Result: messaging_app_mysql_data and messaging_app_static_volume still exist
```

#### 4. Service Restart

```bash
# Restart services with existing volumes
docker-compose up -d
# Result: New containers created, existing volumes mounted
```

#### 5. Data Integrity Test

```bash
# Login with previously created user
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "securepassword123"}'
# Result: ✅ SUCCESS - User login successful, JWT token issued

# Verify user data still exists
curl -H "Authorization: Bearer NEW_TOKEN" http://localhost:8000/api/users/
# Result: ✅ SUCCESS - Same user data retrieved, data persisted
```

## 🔧 Volume Management Commands

### Inspection Commands

```bash
# List all volumes
docker volume ls

# Inspect specific volume
docker volume inspect messaging_app_mysql_data

# Check volume usage
docker system df

# Show volume mount points
docker-compose exec db df -h /var/lib/mysql
```

### Backup Commands

```bash
# Backup MySQL data volume
docker run --rm \
  -v messaging_app_mysql_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/mysql_backup.tar.gz /data

# Restore MySQL data volume
docker run --rm \
  -v messaging_app_mysql_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/mysql_backup.tar.gz -C /
```

### Cleanup Commands

```bash
# Remove containers but keep volumes
docker-compose down

# Remove containers and volumes (DESTRUCTIVE)
docker-compose down -v

# Remove unused volumes
docker volume prune

# Remove specific volume (DESTRUCTIVE)
docker volume rm messaging_app_mysql_data

# Complete cleanup (removes everything)
docker system prune -f

# Nuclear option - remove everything including images
docker system prune -af --volumes
```

### Complete Environment Cleanup

For a complete reset of the Docker environment:

```bash
# Step 1: Stop and remove all containers and volumes
docker-compose down -v

# Step 2: Verify volumes are removed
docker volume ls | grep messaging
# Should return no results

# Step 3: Clean up unused Docker resources
docker system prune -f

# Step 4: Verify cleanup
docker ps -a | grep messaging  # Should return no containers
docker images | grep messaging  # Should return no images
docker volume ls | grep messaging  # Should return no volumes

# Step 5: Optional - Remove all unused Docker resources including images
docker system prune -af --volumes
```

### Cleanup Verification

After cleanup, verify the environment is clean:

```bash
# Check containers
echo "=== Containers ==="
docker ps -a | grep messaging || echo "No messaging containers found ✅"

# Check volumes
echo "=== Volumes ==="
docker volume ls | grep messaging || echo "No messaging volumes found ✅"

# Check networks
echo "=== Networks ==="
docker network ls | grep messaging || echo "No messaging networks found ✅"

# Check images
echo "=== Images ==="
docker images | grep messaging || echo "No messaging images found ✅"

# Check disk space reclaimed
echo "=== Disk Usage ==="
docker system df
```

## 📈 Volume Benefits

### 1. Data Persistence

- ✅ Database survives container restarts
- ✅ User data preserved across deployments
- ✅ Application state maintained

### 2. Development Workflow

- ✅ Live code reloading with bind mounts
- ✅ Static files persist across rebuilds
- ✅ Database data retained during development

### 3. Production Readiness

- ✅ Scalable storage solution
- ✅ Backup and restore capabilities
- ✅ Independent of container lifecycle

### 4. Performance

- ✅ Native filesystem performance
- ✅ Efficient I/O operations
- ✅ Optimized for database workloads

## 🚨 Volume Security Considerations

### ⚠️ Data Loss Prevention

**CRITICAL WARNING**: The following commands will permanently delete data:

```bash
# DESTRUCTIVE COMMANDS - USE WITH CAUTION
docker-compose down -v          # Removes all volumes and data
docker volume prune             # Removes unused volumes
docker system prune -af --volumes  # Nuclear option - removes everything
```

**Before running destructive commands:**

1. **Backup your data** using the backup procedures below
2. **Verify you want to lose all data**
3. **Consider using `docker-compose down` instead** (keeps volumes)
4. **Document what you're doing** for team members

### 🔄 Data Recovery Procedures

If you accidentally removed volumes, recovery depends on your backup strategy:

#### 1. From Database Backup

```bash
# If you have a SQL backup
docker-compose up -d db
docker-compose exec db mysql -u root -p messaging_app_db < backup/mysql_backup.sql
```

#### 2. From Volume Backup

```bash
# If you have a volume backup
docker volume create messaging_app_mysql_data
docker run --rm \
  -v messaging_app_mysql_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/mysql_backup.tar.gz -C /
```

#### 3. Fresh Start (if no backups)

```bash
# Complete fresh installation
docker-compose up --build
# Note: All previous data will be lost
```

### 1. File Permissions

```bash
# Check volume ownership
docker-compose exec db ls -la /var/lib/mysql
# MySQL files owned by mysql:mysql (999:999)

# Check static files ownership
docker-compose exec web ls -la /app/staticfiles
# Static files owned by appuser:appuser (1000:1000)
```

### 2. Access Control

- Named volumes are isolated to Docker daemon
- Only containers can access volume data
- Host access requires root privileges

### 3. Backup Security

- Regular backups to secure locations
- Encrypted backup storage
- Access control on backup files

## 📊 Volume Monitoring

### Storage Usage

```bash
# Check volume disk usage
docker system df -v

# Monitor MySQL data growth
docker-compose exec db du -sh /var/lib/mysql

# Check static files size
docker-compose exec web du -sh /app/staticfiles
```

### Performance Monitoring

```bash
# MySQL performance stats
docker-compose exec db mysqladmin status

# Container resource usage
docker stats messaging_db messaging_web

# Volume I/O statistics
docker-compose exec db iostat 1
```

## 🔄 Volume Migration Strategies

### 1. Development to Production

```bash
# Export development data
docker run --rm \
  -v messaging_app_mysql_data:/data \
  -v $(pwd):/backup \
  mysql:8.0 mysqldump -u root -p --all-databases > backup/dev_data.sql

# Import to production volume
docker run --rm \
  -v production_mysql_data:/var/lib/mysql \
  -v $(pwd):/backup \
  mysql:8.0 mysql -u root -p < backup/dev_data.sql
```

### 2. Volume Upgrade

```bash
# Create new volume
docker volume create messaging_app_mysql_data_v2

# Copy data between volumes
docker run --rm \
  -v messaging_app_mysql_data:/source \
  -v messaging_app_mysql_data_v2:/target \
  alpine cp -av /source/. /target/
```

## 📋 Volume Best Practices

### 1. Naming Convention

- ✅ Use descriptive volume names
- ✅ Include project prefix
- ✅ Specify data type in name

### 2. Backup Strategy

- ✅ Automated daily backups
- ✅ Test restore procedures
- ✅ Offsite backup storage

### 3. Monitoring

- ✅ Track volume growth
- ✅ Monitor I/O performance
- ✅ Set up storage alerts

### 4. Documentation

- ✅ Document volume purposes
- ✅ Maintain backup procedures
- ✅ Record restoration steps

## 🎯 Production Recommendations

### 1. External Volume Drivers

```yaml
volumes:
  mysql_data:
    driver: local
    driver_opts:
      type: nfs
      o: addr=nfs-server,rw
      device: ":/path/to/mysql/data"
```

### 2. Volume Constraints

```yaml
volumes:
  mysql_data:
    driver: local
    driver_opts:
      type: ext4
      device: /dev/sdb1
```

### 3. Backup Automation

```yaml
services:
  backup:
    image: mysql:8.0
    volumes:
      - mysql_data:/var/lib/mysql:ro
    command: |
      sh -c "
        mysqldump -h db -u root -p$$MYSQL_ROOT_PASSWORD --all-databases | 
        gzip > /backup/mysql_backup_$(date +%Y%m%d_%H%M%S).sql.gz
      "
    depends_on:
      - db
```

## 📚 Summary

The messaging app implements comprehensive data persistence using Docker volumes:

- ✅ **MySQL Data Volume**: Ensures database persistence across container lifecycle
- ✅ **Static Files Volume**: Maintains Django static assets
- ✅ **Development Bind Mounts**: Enables live code editing
- ✅ **Initialization Scripts**: Consistent database setup

**Verification Results**: Data persistence tested and confirmed working - user data survives complete container removal and recreation.

## 🧹 Environment Cleanup Results

### Cleanup Operation Performed

The following cleanup was performed to demonstrate complete environment reset:

#### Commands Executed:

```bash
# Step 1: Stop containers and remove volumes
docker-compose down -v
# Result: All messaging containers and volumes removed

# Step 2: Verify volume removal
docker volume ls | grep messaging
# Result: No messaging volumes found ✅

# Step 3: System cleanup
docker system prune -f
# Result: Reclaimed 558.7MB of disk space
```

#### Resources Removed:

- ✅ **Containers**: All messaging app containers removed
- ✅ **Volumes**: `messaging_app_mysql_data` and `messaging_app_static_volume` deleted
- ✅ **Networks**: `messaging_app_messaging_network` removed
- ✅ **Unused Images**: Build cache and unused images cleaned
- ✅ **Disk Space**: 558.7MB reclaimed

#### Impact:

- ❌ **Database Data**: All user data lost (testuser and any other data)
- ❌ **Static Files**: All collected static files removed
- ❌ **Development State**: Container state reset to initial
- ✅ **Clean Environment**: Ready for fresh deployment

#### Post-Cleanup Verification:

```bash
Containers: ✅ No messaging containers found
Volumes: ✅ No messaging volumes found
Networks: ✅ No messaging networks found
Disk Usage: 288MB reclaimable in unused volumes
```

### Recovery Steps

To restore the environment after cleanup:

```bash
# 1. Rebuild and start services
docker-compose up --build

# 2. Verify services are healthy
docker-compose ps

# 3. Test API endpoints
curl -I http://localhost:8000/api/auth/register/

# 4. Create new test data as needed
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "email": "new@example.com", ...}'
```

The volume configuration provides a robust foundation for both development and production deployments! 🚀
