#!/usr/bin/env python3
"""
Test different retry configurations for the retry_on_failure decorator
"""

import time
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


def retry_on_failure(retries=3, delay=2):
    """Decorator that retries database operations if they fail due to transient errors."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(retries + 1):
                try:
                    result = func(*args, **kwargs)
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


# Test functions with different retry configurations


@with_db_connection
@retry_on_failure(retries=1, delay=0.5)
def quick_retry_query(conn, fail_times=1):
    """Query with minimal retries"""
    # Simulate failure based on global state
    if hasattr(quick_retry_query, "call_count"):
        quick_retry_query.call_count += 1
    else:
        quick_retry_query.call_count = 1

    if quick_retry_query.call_count <= fail_times:
        raise sqlite3.OperationalError("Quick retry test failure")

    cursor = conn.cursor()
    cursor.execute("SELECT 'quick_retry' as test, COUNT(*) as count FROM users")
    return cursor.fetchone()


@with_db_connection
@retry_on_failure(retries=5, delay=0.2)
def patient_retry_query(conn, fail_times=3):
    """Query with many retries but short delays"""
    if hasattr(patient_retry_query, "call_count"):
        patient_retry_query.call_count += 1
    else:
        patient_retry_query.call_count = 1

    if patient_retry_query.call_count <= fail_times:
        raise sqlite3.OperationalError("Patient retry test failure")

    cursor = conn.cursor()
    cursor.execute("SELECT 'patient_retry' as test, COUNT(*) as count FROM users")
    return cursor.fetchone()


@with_db_connection
@retry_on_failure(retries=0, delay=1)
def no_retry_query(conn):
    """Query with no retries (fails immediately)"""
    raise sqlite3.OperationalError("No retry test - immediate failure")


if __name__ == "__main__":
    print("Testing different retry configurations:\n")

    print("1. Quick retry (1 retry, 0.5s delay) - should succeed:")
    try:
        quick_retry_query.call_count = 0  # Reset counter
        result = quick_retry_query(fail_times=1)
        print(f"   ✓ Result: {result}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print(
        "\n2. Patient retry (5 retries, 0.2s delay) - should succeed after 3 failures:"
    )
    try:
        patient_retry_query.call_count = 0  # Reset counter
        start_time = time.time()
        result = patient_retry_query(fail_times=3)
        duration = time.time() - start_time
        print(f"   ✓ Result: {result}")
        print(f"   ✓ Total time: {duration:.1f} seconds")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n3. No retry (0 retries) - should fail immediately:")
    try:
        start_time = time.time()
        no_retry_query()
        print("   ✗ This should not execute")
    except Exception as e:
        duration = time.time() - start_time
        print(f"   ✓ Failed immediately as expected: {e}")
        print(f"   ✓ Time taken: {duration:.2f} seconds (should be ~0)")

    print("\n4. Quick retry with too many failures - should exhaust retries:")
    try:
        quick_retry_query.call_count = 0  # Reset counter
        result = quick_retry_query(fail_times=5)  # More failures than retries
        print(f"   ✗ This should not execute: {result}")
    except Exception as e:
        print(f"   ✓ Exhausted retries as expected: {e}")

    print("\nRetry configuration testing completed!")
