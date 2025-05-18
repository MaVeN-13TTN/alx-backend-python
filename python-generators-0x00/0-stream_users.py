#!/home/ndungu-kinyanjui/Desktop/ProDev-Backend/alx-backend-python/venv/bin/python
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
            database=os.getenv("MYSQL_DATABASE", "ALX_prodev"),
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
