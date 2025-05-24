#!/usr/bin/env python3
"""
Test error handling for the with_db_connection decorator
"""

import sqlite3
import functools


def with_db_connection(func):
    """Decorator that automatically handles opening and closing database connections."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")
        print(f"Connection opened for {func.__name__}")

        try:
            result = func(conn, *args, **kwargs)
            return result
        except Exception as e:
            print(f"Exception occurred: {e}")
            raise
        finally:
            conn.close()
            print(f"Connection closed for {func.__name__}")

    return wrapper


@with_db_connection
def faulty_query(conn):
    """Function that will cause an error to test exception handling"""
    cursor = conn.cursor()
    # This will cause an error - table doesn't exist
    cursor.execute("SELECT * FROM non_existent_table")
    return cursor.fetchall()


@with_db_connection
def successful_query(conn):
    """Function that works correctly"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]


if __name__ == "__main__":
    print("Testing error handling with with_db_connection decorator:\n")

    print("1. Testing successful operation:")
    try:
        count = successful_query()
        print(f"   Users count: {count}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n2. Testing operation that causes an error:")
    try:
        result = faulty_query()
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Caught error: {e}")

    print("\n3. Testing another successful operation after error:")
    try:
        count = successful_query()
        print(f"   Users count: {count}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\nAll tests completed - connections were properly managed!")
