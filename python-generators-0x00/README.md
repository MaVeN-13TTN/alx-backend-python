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
- `0-stream_users.py`: Contains the generator function that streams rows from the database one by one
- `0-main.py`: Script to set up the database and table, and insert data from the CSV file
- `1-main.py`: Script to test the generator function
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
4. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
5. Install the required packages:
```bash
pip install -r requirements.txt
```
6. Run the scripts:
```bash
# To set up the database and insert data
./0-main.py

# To test the generator function
./1-main.py
```

**Note:** The scripts use a shebang line that points to the Python interpreter in the virtual environment. If you're using a different path for your virtual environment, you may need to update the shebang lines in the scripts.

Example shebang line:
```bash
#!/path/to/your/venv/bin/python
```

For instance, if your virtual environment is in `/home/username/projects/myproject/venv`, the shebang would be:
```bash
#!/home/username/projects/myproject/venv/bin/python
```

You can update the shebang lines in all scripts using the following command:
```bash
sed -i '1s|^#!.*$|#!/path/to/your/venv/bin/python|' *.py
```

## Examples

### Generator Implementation

```python
#!/path/to/your/venv/bin/python
"""
Module for streaming user data from a database using generators.
"""

import mysql.connector
import os
from dotenv import load_dotenv
from typing import Dict, Any, Generator

# Load environment variables from .env file
load_dotenv()


def stream_users() -> Generator[Dict[str, Any], None, None]:
    """
    Generator function that streams rows from the user_data table one by one.

    Yields:
        Dict: A dictionary representing a row from the user_data table.
    """
    try:
        # Connect to the database using environment variables
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "root"),
            database=os.getenv("MYSQL_DATABASE", "ALX_prodev")
        )

        # Create a cursor with dictionary=True to return rows as dictionaries
        cursor = connection.cursor(dictionary=True)

        # Execute the query to select all rows from user_data
        cursor.execute("SELECT * FROM user_data")

        # Yield each row one by one
        for row in cursor:
            yield row

        # Clean up resources
        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        yield None
    except Exception as e:
        print(f"Error: {e}")
        yield None
```

### Using the Generator Function

```python
#!/path/to/your/venv/bin/python
from itertools import islice
stream_users = __import__('0-stream_users').stream_users

# iterate over the generator function and print only the first 6 rows
for user in islice(stream_users(), 6):
    print(user)
```

Output:
```
{'user_id': '02cd053c-5cb9-4dce-9147-0fa28d4d4b7e', 'name': 'Vanessa Kihn-Durgan', 'email': 'Lorena.Schuppe@hotmail.com', 'age': Decimal('49')}
{'user_id': '08908687-c99b-444f-9cea-ff390ebe423e', 'name': 'Annie Rogahn', 'email': 'June.Kuhn24@hotmail.com', 'age': Decimal('92')}
{'user_id': '09845c36-cfa4-479c-a67b-0145fa665f30', 'name': 'Seth Mraz', 'email': 'Cecilia_Blanda89@gmail.com', 'age': Decimal('24')}
{'user_id': '09a7803c-74a7-4fac-a38c-513f9595b34a', 'name': 'Spencer Larson', 'email': 'Rickey65@gmail.com', 'age': Decimal('110')}
{'user_id': '0ae4ecc8-637e-424e-9b47-9ef7d78fe689', 'name': 'Myrtle Waters', 'email': 'Edmund_Funk@gmail.com', 'age': Decimal('99')}
{'user_id': '110a63ec-4741-46f9-9299-d5453506ea0d', 'name': 'Clark Willms', 'email': 'Leo25@gmail.com', 'age': Decimal('45')}
```

### Setting Up the Database

```python
#!/path/to/your/venv/bin/python
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
        cursor = connection.cursor()
        cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'ALX_prodev';")
        result = cursor.fetchone()
        if result:
            print(f"Database ALX_prodev is present ")
        cursor.execute(f"SELECT * FROM user_data LIMIT 5;")
        rows = cursor.fetchall()
        print(rows)
        cursor.close()
```
