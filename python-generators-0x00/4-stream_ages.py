#!/home/ndungu-kinyanjui/Desktop/ProDev-Backend/alx-backend-python/venv/bin/python
"""
Module for memory-efficient aggregation with generators.
"""

import mysql.connector
import os
from typing import Generator, Union
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def stream_user_ages() -> Generator[int, None, None]:
    """
    Generator function that yields user ages one by one.
    
    Yields:
        int: The age of a user.
    """
    try:
        # Connect to the database using environment variables
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "root"),
            database=os.getenv("MYSQL_DATABASE", "ALX_prodev")
        )
        
        # Create a cursor
        cursor = connection.cursor()
        
        # Execute the query to select only the age column
        cursor.execute("SELECT age FROM user_data")
        
        # Yield each age one by one
        for (age,) in cursor:
            yield int(age)
            
        # Clean up resources
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except Exception as e:
        print(f"Error: {e}")


def calculate_average_age() -> Union[float, None]:
    """
    Calculates the average age of users without loading the entire dataset into memory.
    
    Returns:
        float: The average age of users, or None if there are no users.
    """
    total_age = 0
    count = 0
    
    # Use the generator to process ages one by one
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    # Calculate the average
    if count > 0:
        return total_age / count
    else:
        return None


if __name__ == "__main__":
    # Calculate and print the average age
    average_age = calculate_average_age()
    
    if average_age is not None:
        print(f"Average age of users: {average_age:.2f}")
    else:
        print("No users found in the database.")
