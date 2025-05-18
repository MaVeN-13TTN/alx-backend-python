#!/home/ndungu-kinyanjui/Desktop/ProDev-Backend/alx-backend-python/venv/bin/python
"""
Module for lazy loading paginated data from a database using generators.
"""

import mysql.connector
import os
from typing import Dict, Any, Generator, List
from dotenv import load_dotenv
seed = __import__('seed')

# Load environment variables from .env file
load_dotenv()


def paginate_users(page_size, offset):
    """
    Fetches a page of users from the database.
    
    Args:
        page_size: The number of rows to fetch in each page.
        offset: The offset from which to start fetching rows.
        
    Returns:
        List[Dict]: A list of dictionaries, each representing a row from the user_data table.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_pagination(page_size: int) -> Generator[List[Dict[str, Any]], None, None]:
    """
    Generator function that implements lazy pagination, fetching pages only when needed.
    
    Args:
        page_size: The number of rows to fetch in each page.
        
    Yields:
        List[Dict]: A list of dictionaries, each representing a page of rows from the user_data table.
    """
    # Initialize offset to 0
    offset = 0
    
    # Use a single loop to fetch pages as needed
    while True:
        # Fetch the current page
        page = paginate_users(page_size, offset)
        
        # If the page is empty, we've reached the end of the data
        if not page:
            break
            
        # Yield the current page
        yield page
        
        # Update the offset for the next page
        offset += page_size
