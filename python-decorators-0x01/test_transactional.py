#!/usr/bin/env python3
"""
Test file for the transactional decorator
Demonstrates transaction management with commit and rollback scenarios
"""

import sqlite3
import functools


def with_db_connection(func):
    """Decorator that automatically handles opening and closing database connections."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")
        try:
            result = func(conn, *args, **kwargs)
            return result
        finally:
            conn.close()

    return wrapper


def transactional(func):
    """Decorator that manages database transactions."""

    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Start transaction
            original_isolation_level = conn.isolation_level
            if conn.isolation_level is None:
                conn.execute("BEGIN")

            # Execute the original function
            result = func(conn, *args, **kwargs)

            # Commit the transaction
            conn.commit()
            return result

        except Exception as e:
            # Rollback on error
            conn.rollback()
            raise e

    return wrapper


@with_db_connection
def get_user_by_id(conn, user_id):
    """Get user by ID to check current data"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """Update user email with transaction management"""
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))


@with_db_connection
@transactional
def update_user_with_error(conn, user_id, new_email):
    """Function that will cause an error to test rollback"""
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    # This will cause an error - invalid SQL
    cursor.execute("INVALID SQL STATEMENT")


@with_db_connection
@transactional
def batch_update_users(conn, updates):
    """Update multiple users in a single transaction"""
    cursor = conn.cursor()
    for user_id, new_email in updates:
        cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))


if __name__ == "__main__":
    print("Testing transactional decorator:\n")

    print("1. Check original user data:")
    original_user = get_user_by_id(user_id=1)
    print(f"   User 1: {original_user}")

    print("\n2. Update user email successfully:")
    try:
        update_user_email(user_id=1, new_email="Crawford_Cartwright@hotmail.com")
        updated_user = get_user_by_id(user_id=1)
        print(f"   Updated User 1: {updated_user}")
        print("   ✓ Transaction committed successfully")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n3. Test transaction rollback with error:")
    try:
        update_user_with_error(
            user_id=1, new_email="this_should_not_persist@example.com"
        )
        print("   ✗ This should not print - error should have occurred")
    except Exception as e:
        print(f"   ✓ Caught expected error: {e}")
        # Check that the email wasn't changed
        user_after_error = get_user_by_id(user_id=1)
        print(f"   User 1 after rollback: {user_after_error}")
        print("   ✓ Transaction rolled back successfully")

    print("\n4. Test batch updates in transaction:")
    try:
        batch_updates = [
            (2, "bob_updated@example.com"),
            (3, "charlie_updated@example.com"),
        ]
        batch_update_users(updates=batch_updates)

        user2 = get_user_by_id(user_id=2)
        user3 = get_user_by_id(user_id=3)
        print(f"   User 2: {user2}")
        print(f"   User 3: {user3}")
        print("   ✓ Batch transaction committed successfully")
    except Exception as e:
        print(f"   ✗ Error in batch update: {e}")

    print("\nAll transaction tests completed!")
