#!/usr/bin/env python3
"""
Test file for the log_queries decorator
"""

import sqlite3
import functools


# Copy the decorator definition here for testing
def log_queries(func):
    """
    Decorator that logs SQL queries executed by a function.

    Args:
        func: The function to be decorated

    Returns:
        The wrapper function that logs queries before execution
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from function arguments
        # Assuming the query is passed as a keyword argument or the first positional argument
        query = None

        # Check if query is in kwargs
        if "query" in kwargs:
            query = kwargs["query"]
        # Check if query is the first positional argument
        elif args and isinstance(args[0], str):
            query = args[0]
        # Check for other common parameter names
        elif len(args) > 0:
            for arg in args:
                if isinstance(arg, str) and (
                    "SELECT" in arg.upper()
                    or "INSERT" in arg.upper()
                    or "UPDATE" in arg.upper()
                    or "DELETE" in arg.upper()
                ):
                    query = arg
                    break

        # Log the query if found
        if query:
            print(f"Executing SQL Query: {query}")

        # Execute the original function
        return func(*args, **kwargs)

    return wrapper


@log_queries
def fetch_user_by_id(user_id):
    """Fetch a specific user by ID"""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result


@log_queries
def fetch_users_by_age(min_age):
    """Fetch users above a certain age"""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT name, email FROM users WHERE age > {min_age}"
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


@log_queries
def count_users():
    """Count total number of users"""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM users"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result[0]


if __name__ == "__main__":
    print("Testing log_queries decorator with various database operations:\n")

    print("1. Fetching all users:")

    @log_queries
    def fetch_all_users(query):
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results

    users = fetch_all_users(query="SELECT * FROM users")
    print(f"Found {len(users)} users\n")

    print("2. Fetching user by ID:")
    user = fetch_user_by_id(1)
    print(f"User found: {user}\n")

    print("3. Fetching users above age 25:")
    older_users = fetch_users_by_age(25)
    print(f"Found {len(older_users)} users above age 25\n")

    print("4. Counting total users:")
    total = count_users()
    print(f"Total users: {total}")
