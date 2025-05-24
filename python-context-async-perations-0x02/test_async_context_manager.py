#!/usr/bin/env python3
"""
Comprehensive test file for the AsyncDatabaseConnection context manager
Demonstrates various asynchronous scenarios including error handling and concurrency
"""

import asyncio
import aiosqlite
import time
from typing import List, Tuple

# Import our async context manager
import sys
import importlib.util

spec = importlib.util.spec_from_file_location(
    "async_db_module", "1-async_database_connection.py"
)
async_db_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(async_db_module)
AsyncDatabaseConnection = async_db_module.AsyncDatabaseConnection


async def test_basic_async_operations():
    """Test basic asynchronous database operations."""
    print("1. Testing basic async operations:")
    print("-" * 40)

    try:
        async with AsyncDatabaseConnection() as conn:
            # Test SELECT operation
            cursor = await conn.execute("SELECT name, email FROM users WHERE age > 25")
            older_users = await cursor.fetchall()

            print(f"Users over 25 years old:")
            for name, email in older_users:
                print(f"  - {name} ({email})")

            print(f"Total: {len(older_users)} users")

    except Exception as e:
        print(f"Error in basic async operations test: {e}")


async def test_async_error_handling():
    """Test error handling with the async context manager."""
    print("\n2. Testing async error handling (invalid SQL):")
    print("-" * 40)

    try:
        async with AsyncDatabaseConnection() as conn:
            # This will cause an error - invalid table name
            cursor = await conn.execute("SELECT * FROM non_existent_table")
            results = await cursor.fetchall()
            print(f"This shouldn't print: {results}")

    except aiosqlite.OperationalError as e:
        print(f"✓ Caught expected SQL error: {e}")
        print("✓ Async context manager handled the error properly")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


async def test_async_transaction_rollback():
    """Test transaction rollback on error in async context."""
    print("\n3. Testing async transaction rollback:")
    print("-" * 40)

    try:
        async with AsyncDatabaseConnection() as conn:
            # Start a transaction that will fail
            await conn.execute(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                ("Test User", "test@example.com", 25),
            )

            print("Inserted test user (not committed yet)")

            # This will cause an error and trigger rollback
            await conn.execute("INSERT INTO invalid_table VALUES (1, 2, 3)")

    except aiosqlite.OperationalError as e:
        print(f"✓ Expected error occurred: {e}")
        print("✓ Transaction should have been rolled back")

        # Verify the test user was not actually inserted
        try:
            async with AsyncDatabaseConnection() as conn:
                cursor = await conn.execute(
                    "SELECT COUNT(*) FROM users WHERE email = 'test@example.com'"
                )
                count = await cursor.fetchone()
                if count[0] == 0:
                    print("✓ Rollback successful - test user was not persisted")
                else:
                    print("✗ Rollback failed - test user was persisted")
        except Exception as verify_error:
            print(f"✗ Error verifying rollback: {verify_error}")


async def test_concurrent_context_managers():
    """Test using multiple concurrent async context managers."""
    print("\n4. Testing concurrent async context managers:")
    print("-" * 40)

    async def query_task(task_id: int, min_age: int) -> Tuple[int, List]:
        async with AsyncDatabaseConnection() as conn:
            cursor = await conn.execute(
                "SELECT name, age FROM users WHERE age >= ?", (min_age,)
            )
            results = await cursor.fetchall()
            return task_id, results

    try:
        # Create multiple concurrent database tasks
        tasks = [
            query_task(1, 25),
            query_task(2, 30),
            query_task(3, 35),
            query_task(4, 20),
        ]

        # Execute all tasks concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        for task_id, users in results:
            print(f"Task {task_id}: Found {len(users)} users")

        print(f"✓ All {len(tasks)} concurrent operations completed")
        print(f"✓ Total time: {end_time - start_time:.3f} seconds")

    except Exception as e:
        print(f"✗ Error with concurrent context managers: {e}")


async def test_async_performance_comparison():
    """Compare sync vs async performance with multiple operations."""
    print("\n5. Testing async performance benefits:")
    print("-" * 40)

    async def async_operation(operation_id: int):
        async with AsyncDatabaseConnection() as conn:
            cursor = await conn.execute("SELECT COUNT(*) FROM users")
            result = await cursor.fetchone()
            # Simulate some processing time
            await asyncio.sleep(0.1)
            return operation_id, result[0]

    try:
        # Test async operations
        print("Running 5 concurrent async operations...")
        start_time = time.time()

        tasks = [async_operation(i) for i in range(5)]
        results = await asyncio.gather(*tasks)

        async_time = time.time() - start_time

        print(f"Async operations completed in: {async_time:.3f} seconds")
        print(
            f"Operations: {[f'Op{op_id}: {count} users' for op_id, count in results]}"
        )

        # Estimate sync time (would be ~0.5 seconds sequentially)
        estimated_sync_time = 0.1 * 5  # 5 operations × 0.1s each
        improvement = estimated_sync_time / async_time

        print(f"Estimated sync time: {estimated_sync_time:.3f} seconds")
        print(f"Performance improvement: ~{improvement:.1f}x faster with async")

    except Exception as e:
        print(f"✗ Error in performance test: {e}")


async def test_async_batch_operations():
    """Test batch operations with async context manager."""
    print("\n6. Testing async batch operations:")
    print("-" * 40)

    try:
        # Batch insert operation
        async with AsyncDatabaseConnection() as conn:
            users_to_add = [
                ("John Async", "john.async@example.com", 32),
                ("Jane Await", "jane.await@example.com", 29),
                ("Bob Concurrent", "bob.concurrent@example.com", 31),
            ]

            await conn.executemany(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)", users_to_add
            )

            print(f"✓ Batch inserted {len(users_to_add)} users")

            # Verify insertion
            cursor = await conn.execute("SELECT COUNT(*) FROM users")
            total_count = await cursor.fetchone()
            print(f"✓ Total users in database: {total_count[0]}")

    except Exception as e:
        print(f"✗ Error in batch operations: {e}")


async def test_nested_async_context_managers():
    """Test nested async context managers (not recommended but should work)."""
    print("\n7. Testing nested async context managers:")
    print("-" * 40)

    try:
        async with AsyncDatabaseConnection() as outer_conn:
            outer_cursor = await outer_conn.execute("SELECT COUNT(*) FROM users")
            outer_count = await outer_cursor.fetchone()

            async with AsyncDatabaseConnection() as inner_conn:
                inner_cursor = await inner_conn.execute(
                    "SELECT name FROM users LIMIT 1"
                )
                first_user = await inner_cursor.fetchone()

                print(f"Outer connection - Total users: {outer_count[0]}")
                print(
                    f"Inner connection - First user: {first_user[0] if first_user else 'None'}"
                )

        print("✓ Nested async context managers worked (though not recommended)")

    except Exception as e:
        print(f"✗ Error with nested async context managers: {e}")


async def main():
    """Run all async context manager tests."""
    print("Comprehensive Testing of AsyncDatabaseConnection Context Manager")
    print("=" * 70)

    # Ensure database is set up
    await async_db_module.setup_async_database()

    # Run all tests
    await test_basic_async_operations()
    await test_async_error_handling()
    await test_async_transaction_rollback()
    await test_concurrent_context_managers()
    await test_async_performance_comparison()
    await test_async_batch_operations()
    await test_nested_async_context_managers()

    print("\n" + "=" * 70)
    print("All async tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    # Run the async test suite
    asyncio.run(main())
