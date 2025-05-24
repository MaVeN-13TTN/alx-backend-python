#!/usr/bin/env python3
"""
Test file for the with_db_connection decorator
Demonstrates various database operations with automatic connection handling
"""

import sqlite3
import functools


# Copy the decorator definition for testing
def with_db_connection(func):
    """
    Decorator that automatically handles opening and closing database connections.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect("users.db")

        try:
            # Call the original function with connection as first argument
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Always close the connection, even if an exception occurs
            conn.close()

    return wrapper


@with_db_connection
def get_user_by_id(conn, user_id):
    """Get a specific user by ID"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


@with_db_connection
def get_all_users(conn):
    """Get all users from the database"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


@with_db_connection
def get_users_by_age_range(conn, min_age, max_age):
    """Get users within a specific age range"""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, email, age FROM users WHERE age BETWEEN ? AND ?",
        (min_age, max_age),
    )
    return cursor.fetchall()


@with_db_connection
def count_users(conn):
    """Count total number of users"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]


@with_db_connection
def add_user(conn, name, email, age):
    """Add a new user to the database"""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, age) VALUES (?, ?, ?)", (name, email, age)
    )
    conn.commit()
    return cursor.lastrowid


if __name__ == "__main__":
    print("Testing with_db_connection decorator with various database operations:\n")

    print("1. Get user by ID (1):")
    user = get_user_by_id(user_id=1)
    print(f"   {user}\n")

    print("2. Get all users:")
    all_users = get_all_users()
    for user in all_users:
        print(f"   {user}")
    print()

    print("3. Get users aged between 25 and 35:")
    age_range_users = get_users_by_age_range(min_age=25, max_age=35)
    for user in age_range_users:
        print(f"   {user}")
    print()

    print("4. Count total users:")
    total_users = count_users()
    print(f"   Total users: {total_users}\n")

    print("5. Add a new user:")
    new_user_id = add_user(name="Eve Wilson", email="eve@example.com", age=26)
    print(f"   New user added with ID: {new_user_id}")

    print("\n6. Verify new user was added:")
    new_user = get_user_by_id(user_id=new_user_id)
    print(f"   {new_user}")

    print(f"\n7. Updated total count:")
    updated_total = count_users()
    print(f"   Total users now: {updated_total}")
