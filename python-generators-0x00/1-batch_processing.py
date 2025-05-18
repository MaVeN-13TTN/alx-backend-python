#!/home/ndungu-kinyanjui/Desktop/ProDev-Backend/alx-backend-python/venv/bin/python
"""
Module for batch processing of user data from a database using generators.
"""

import mysql.connector
import os
from dotenv import load_dotenv
from typing import Dict, Any, Generator, List

# Load environment variables from .env file
load_dotenv()


def stream_users_in_batches(batch_size: int) -> Generator[List[Dict[str, Any]], None, None]:
    """
    Generator function that fetches rows from the user_data table in batches.
    
    Args:
        batch_size: The number of rows to fetch in each batch.
        
    Yields:
        List[Dict]: A list of dictionaries, each representing a row from the user_data table.
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
        
        # Get the total number of rows
        cursor.execute("SELECT COUNT(*) as count FROM user_data")
        total_rows = cursor.fetchone()['count']
        
        # Process data in batches
        offset = 0
        while offset < total_rows:
            # Execute the query to select a batch of rows
            cursor.execute(
                "SELECT * FROM user_data LIMIT %s OFFSET %s",
                (batch_size, offset)
            )
            
            # Fetch all rows in the current batch
            batch = cursor.fetchall()
            
            # If the batch is empty, break the loop
            if not batch:
                break
                
            # Yield the batch
            yield batch
            
            # Update the offset for the next batch
            offset += batch_size
            
        # Clean up resources
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        yield []
    except Exception as e:
        print(f"Error: {e}")
        yield []


def batch_processing(batch_size: int) -> None:
    """
    Processes each batch to filter users over the age of 25.
    
    Args:
        batch_size: The number of rows to fetch in each batch.
    """
    # Get batches of users
    for batch in stream_users_in_batches(batch_size):
        # Filter users over the age of 25
        for user in batch:
            if int(user['age']) > 25:
                # Print the filtered user with a blank line after each user
                print(user)
                print()
