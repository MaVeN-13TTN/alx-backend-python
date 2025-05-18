# Python Generators Project

## Overview
This project demonstrates the use of Python generators to stream rows from a MySQL database one by one. It includes functionality to set up a MySQL database, create tables, and populate them with data from a CSV file.

## Requirements
- Python 3.x
- MySQL server
- Required Python packages (install using `pip install -r requirements.txt`):
  - mysql-connector-python
  - pandas
  - python-dotenv

## Project Structure
- `seed.py`: Main script that contains functions to connect to MySQL, create database and tables, and insert data
- `user_data.csv`: Sample data file containing user information
- `.env`: Configuration file for database connection parameters (not tracked in git)
- `env.example`: Template for the .env file showing required environment variables
- `.gitignore`: Specifies files that should not be tracked by git

## Features
- Connect to MySQL database server
- Create a database named `ALX_prodev`
- Create a table `user_data` with the following fields:
  - `user_id` (Primary Key, UUID, Indexed)
  - `name` (VARCHAR, NOT NULL)
  - `email` (VARCHAR, NOT NULL)
  - `age` (DECIMAL, NOT NULL)
- Populate the database with sample data from a CSV file
- Stream rows from the database using Python generators

## Functions
- `connect_db()`: Connects to the MySQL database server
- `create_database(connection)`: Creates the database ALX_prodev if it does not exist
- `connect_to_prodev()`: Connects to the ALX_prodev database in MySQL
- `create_table(connection)`: Creates a table user_data if it does not exist with the required fields
- `insert_data(connection, data)`: Inserts data in the database if it does not exist
- `get_rows(connection)`: Generator function that streams rows from the database one by one

## Usage
1. Ensure MySQL server is running
2. Create a `.env` file based on the `env.example` template and configure your database connection parameters
3. Create a dedicated MySQL user for the application (recommended):
```sql
CREATE USER 'alx_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON ALX_prodev.* TO 'alx_user'@'localhost';
FLUSH PRIVILEGES;
```
4. Run the script:
```
python3 seed.py
```

## Example
```python
#!/usr/bin/python3

seed = __import__('seed')

connection = seed.connect_db()
if connection:
    seed.create_database(connection)
    connection.close()
    print(f"connection successful")

    connection = seed.connect_to_prodev()

    if connection:
        seed.create_table(connection)
        seed.insert_data(connection, 'user_data.csv')

        # Using the generator to stream rows
        row_generator = seed.get_rows(connection)
        for i, row in enumerate(row_generator):
            if i >= 5:  # Print only first 5 rows
                break
            print(row)

        connection.close()
```
