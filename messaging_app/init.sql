-- Initialize the messaging app database
-- This script runs automatically when the MySQL container starts for the first time

-- Create database if it doesn't exist (redundant as docker-compose does this)
CREATE DATABASE IF NOT EXISTS messaging_app_db;

-- Grant privileges to the user (redundant as docker-compose does this)
GRANT ALL PRIVILEGES ON messaging_app_db.* TO 'messaging_user'@'%';

-- Flush privileges
FLUSH PRIVILEGES;
