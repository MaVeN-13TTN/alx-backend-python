#!/usr/bin/env python3
"""
Test file for the retry_on_failure decorator
Demonstrates retry functionality with various scenarios
"""

import time
import sqlite3
import functools
import random


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


def retry_on_failure(retries=3, delay=2):
    """Decorator that retries database operations if they fail due to transient errors."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(retries + 1):
                try:
                    result = func(*args, **kwargs)
                    # If we had previous failures, log success
                    if attempt > 0:
                        print(f"   ✓ Success on attempt {attempt + 1}")
                    return result

                except Exception as e:
                    last_exception = e

                    if attempt == retries:
                        break

                    print(
                        f"   Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds..."
                    )
                    time.sleep(delay)

            raise last_exception

        return wrapper

    return decorator


# Counter to simulate intermittent failures
failure_counter = 0


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """Fetch users - always succeeds"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def intermittent_failure_query(conn):
    """Simulates a query that fails a few times then succeeds"""
    global failure_counter
    failure_counter += 1

    cursor = conn.cursor()

    # Fail on first 2 attempts, succeed on 3rd
    if failure_counter <= 2:
        # Simulate database lock or connection issue
        raise sqlite3.OperationalError("database is locked")

    # Success case
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]


@with_db_connection
@retry_on_failure(retries=2, delay=0.5)
def always_failing_query(conn):
    """Simulates a query that always fails"""
    cursor = conn.cursor()
    # This will always fail
    raise sqlite3.DatabaseError("Persistent database error")


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def random_failure_query(conn):
    """Simulates random transient failures"""
    cursor = conn.cursor()

    # 70% chance of failure to demonstrate retry behavior
    if random.random() < 0.7:
        raise sqlite3.OperationalError("Random transient error")

    cursor.execute("SELECT name FROM users LIMIT 3")
    return cursor.fetchall()


if __name__ == "__main__":
    print("Testing retry_on_failure decorator:\n")

    print("1. Test successful query (no retries needed):")
    try:
        users = fetch_users_with_retry()
        print(f"   ✓ Retrieved {len(users)} users successfully")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n2. Test intermittent failure (should succeed after retries):")
    try:
        failure_counter = 0  # Reset counter
        count = intermittent_failure_query()
        print(f"   ✓ User count: {count}")
    except Exception as e:
        print(f"   ✗ Failed after retries: {e}")

    print("\n3. Test persistent failure (should exhaust retries):")
    try:
        always_failing_query()
        print("   ✗ This should not execute")
    except sqlite3.DatabaseError as e:
        print(f"   ✓ Failed as expected after retries: {e}")

    print("\n4. Test random failures (may succeed or fail):")
    for i in range(3):
        print(f"\n   Attempt {i+1}:")
        try:
            # Set random seed for reproducible results in some runs
            random.seed(i)
            result = random_failure_query()
            print(f"   ✓ Query succeeded: {result}")
        except Exception as e:
            print(f"   ✗ Query failed after retries: {e}")

    print("\nRetry testing completed!")
