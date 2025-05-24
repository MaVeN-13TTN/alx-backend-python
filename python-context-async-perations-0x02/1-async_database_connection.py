#!/usr/bin/env python3
"""
Task 1: Asynchronous Database Context Manager

This module implements an asynchronous context manager for database connections,
demonstrating async/await patterns with database operations.
"""

import asyncio
import aiosqlite
from typing import Optional


class AsyncDatabaseConnection:
    """
    An asynchronous context manager for handling database connections.

    This async context manager automatically handles opening and closing database connections
    using async/await syntax, ensuring proper resource management in asynchronous environments.
    """

    def __init__(self, database_name: str = "users.db"):
        """
        Initialize the AsyncDatabaseConnection context manager.

        Args:
            database_name (str): Name of the SQLite database file. Defaults to 'users.db'
        """
        self.database_name = database_name
        self.connection: Optional[aiosqlite.Connection] = None

    async def __aenter__(self) -> aiosqlite.Connection:
        """
        Enter the async context manager - open database connection.

        This method is called when entering the 'async with' statement.
        It opens an asynchronous connection to the database and returns the connection object.

        Returns:
            aiosqlite.Connection: The asynchronous database connection object
        """
        print(f"Opening async database connection to {self.database_name}")
        self.connection = await aiosqlite.connect(self.database_name)
        return self.connection

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
        Exit the async context manager - close database connection.

        This method is called when exiting the 'async with' statement, even if an exception occurs.
        It ensures the database connection is properly closed.

        Args:
            exc_type: Exception type (if any exception occurred)
            exc_value: Exception value (if any exception occurred)
            traceback: Exception traceback (if any exception occurred)

        Returns:
            None: Returning None means exceptions will propagate normally
        """
        if self.connection:
            if exc_type is None:
                # No exception occurred, commit any pending transactions
                await self.connection.commit()
                print("Async database transaction committed successfully")
            else:
                # An exception occurred, rollback any pending transactions
                await self.connection.rollback()
                print(f"Exception occurred: {exc_value}")
                print("Async database transaction rolled back")

            # Always close the connection
            await self.connection.close()
            print("Async database connection closed")

        # Return None to propagate any exceptions that occurred
        return None


# Async utility functions for database operations
async def setup_async_database():
    """Setup the database with sample data for async operations."""
    async with AsyncDatabaseConnection() as conn:
        # Create table if it doesn't exist
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER
            )
        """
        )

        # Check if table is empty and populate it
        cursor = await conn.execute("SELECT COUNT(*) FROM users")
        count = await cursor.fetchone()

        if count[0] == 0:
            print("Populating database with sample data...")
            sample_users = [
                ("Alice Johnson", "alice@example.com", 28),
                ("Bob Smith", "bob@example.com", 34),
                ("Charlie Brown", "charlie@example.com", 22),
                ("Diana Prince", "diana@example.com", 30),
            ]

            await conn.executemany(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)", sample_users
            )
            print("Sample data inserted successfully")


async def fetch_all_users():
    """Fetch all users using the async context manager."""
    async with AsyncDatabaseConnection() as conn:
        cursor = await conn.execute("SELECT * FROM users")
        results = await cursor.fetchall()
        return results


async def fetch_users_by_age(min_age: int):
    """Fetch users above a certain age using the async context manager."""
    async with AsyncDatabaseConnection() as conn:
        cursor = await conn.execute(
            "SELECT name, email, age FROM users WHERE age >= ?", (min_age,)
        )
        results = await cursor.fetchall()
        return results


async def add_user_async(name: str, email: str, age: int):
    """Add a new user using the async context manager."""
    async with AsyncDatabaseConnection() as conn:
        cursor = await conn.execute(
            "INSERT INTO users (name, email, age) VALUES (?, ?, ?)", (name, email, age)
        )
        user_id = cursor.lastrowid
        return user_id


async def concurrent_database_operations():
    """Demonstrate concurrent database operations using asyncio."""
    print("\nDemonstrating concurrent database operations:")
    print("-" * 50)

    # Create multiple concurrent tasks
    tasks = [
        fetch_users_by_age(25),
        fetch_users_by_age(30),
        add_user_async("Frank Wilson", "frank@example.com", 35),
        add_user_async("Grace Lee", "grace@example.com", 27),
    ]

    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks)

    print(f"Users 25+: {len(results[0])} found")
    print(f"Users 30+: {len(results[1])} found")
    print(f"New user Frank added with ID: {results[2]}")
    print(f"New user Grace added with ID: {results[3]}")


# Demonstration of async context manager usage
async def main():
    """Main async function demonstrating the async context manager."""
    try:
        # Setup database
        await setup_async_database()

        print("\n" + "=" * 60)
        print("DEMONSTRATING ASYNC CONTEXT MANAGER USAGE")
        print("=" * 60)

        # Fetch all users
        print("\n1. Fetching all users:")
        users = await fetch_all_users()

        if users:
            print(f"{'ID':<5} {'Name':<15} {'Email':<25} {'Age':<5}")
            print("-" * 50)

            for user in users:
                user_id, name, email, age = user
                print(f"{user_id:<5} {name:<15} {email:<25} {age:<5}")
        else:
            print("No users found in the database")

        print(f"\nTotal users found: {len(users)}")

        # Fetch users by age
        print("\n2. Fetching users aged 25 and above:")
        older_users = await fetch_users_by_age(25)
        for user in older_users:
            name, email, age = user
            print(f"  - {name} ({email}) - {age} years old")

        # Add a new user
        print("\n3. Adding a new user:")
        new_user_id = await add_user_async("Eve Wilson", "eve@example.com", 26)
        print(f"New user added with ID: {new_user_id}")

        # Demonstrate concurrent operations
        await concurrent_database_operations()

        # Final count
        print("\n4. Final user count:")
        final_users = await fetch_all_users()
        print(f"Total users now: {len(final_users)}")

    except Exception as e:
        print(f"Error in async operations: {e}")

    print("\nAsync context manager demonstration completed!")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
