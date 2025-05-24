#!/usr/bin/env python3
"""
Test file for the DatabaseConnection context manager
Demonstrates various scenarios including error handling
"""

import sqlite3
from contextlib import contextmanager

# Import our custom context manager
import sys

sys.path.append(".")
import importlib.util

spec = importlib.util.spec_from_file_location("db_module", "0-databaseconnection.py")
db_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(db_module)
DatabaseConnection = db_module.DatabaseConnection


def test_successful_operations():
    """Test normal database operations using the context manager"""
    print("1. Testing successful database operations:")
    print("-" * 40)

    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            # Test SELECT operation
            cursor.execute("SELECT name, email FROM users WHERE age > 25")
            older_users = cursor.fetchall()

            print(f"Users over 25 years old:")
            for name, email in older_users:
                print(f"  - {name} ({email})")

            print(f"Total: {len(older_users)} users")

    except Exception as e:
        print(f"Error in successful operations test: {e}")


def test_error_handling():
    """Test error handling with the context manager"""
    print("\n2. Testing error handling (invalid SQL):")
    print("-" * 40)

    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            # This will cause an error - invalid table name
            cursor.execute("SELECT * FROM non_existent_table")
            results = cursor.fetchall()
            print(f"This shouldn't print: {results}")

    except sqlite3.OperationalError as e:
        print(f"✓ Caught expected SQL error: {e}")
        print("✓ Context manager handled the error properly")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def test_transaction_rollback():
    """Test transaction rollback on error"""
    print("\n3. Testing transaction rollback:")
    print("-" * 40)

    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            # Start a transaction that will fail
            cursor.execute(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                ("Test User", "test@example.com", 25),
            )

            print("Inserted test user (not committed yet)")

            # This will cause an error and trigger rollback
            cursor.execute("INSERT INTO invalid_table VALUES (1, 2, 3)")

    except sqlite3.OperationalError as e:
        print(f"✓ Expected error occurred: {e}")
        print("✓ Transaction should have been rolled back")

        # Verify the test user was not actually inserted
        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE email = 'test@example.com'"
                )
                count = cursor.fetchone()[0]
                if count == 0:
                    print("✓ Rollback successful - test user was not persisted")
                else:
                    print("✗ Rollback failed - test user was persisted")
        except Exception as verify_error:
            print(f"✗ Error verifying rollback: {verify_error}")


def test_multiple_context_managers():
    """Test using multiple context managers"""
    print("\n4. Testing multiple context manager instances:")
    print("-" * 40)

    try:
        # First context manager
        with DatabaseConnection() as conn1:
            cursor1 = conn1.cursor()
            cursor1.execute("SELECT COUNT(*) FROM users")
            count1 = cursor1.fetchone()[0]
            print(f"Connection 1 - User count: {count1}")

        # Second context manager (separate connection)
        with DatabaseConnection() as conn2:
            cursor2 = conn2.cursor()
            cursor2.execute("SELECT name FROM users LIMIT 2")
            names = cursor2.fetchall()
            print(f"Connection 2 - First 2 users: {[name[0] for name in names]}")

        print("✓ Multiple context managers worked independently")

    except Exception as e:
        print(f"✗ Error with multiple context managers: {e}")


def test_nested_context_managers():
    """Test nested context managers (not recommended but should work)"""
    print("\n5. Testing nested context managers:")
    print("-" * 40)

    try:
        with DatabaseConnection() as outer_conn:
            outer_cursor = outer_conn.cursor()
            outer_cursor.execute("SELECT COUNT(*) FROM users")
            outer_count = outer_cursor.fetchone()[0]

            with DatabaseConnection() as inner_conn:
                inner_cursor = inner_conn.cursor()
                inner_cursor.execute("SELECT name FROM users LIMIT 1")
                first_user = inner_cursor.fetchone()[0]

                print(f"Outer connection - Total users: {outer_count}")
                print(f"Inner connection - First user: {first_user}")

        print("✓ Nested context managers worked (though not recommended)")

    except Exception as e:
        print(f"✗ Error with nested context managers: {e}")


if __name__ == "__main__":
    print("Comprehensive Testing of DatabaseConnection Context Manager")
    print("=" * 60)

    test_successful_operations()
    test_error_handling()
    test_transaction_rollback()
    test_multiple_context_managers()
    test_nested_context_managers()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
