#!/usr/bin/env python3
"""
Task 1: Reusable Query Context Manager

This module implements a reusable context manager that takes a query as input
and executes it, managing both connection and query execution automatically.
"""

import sqlite3
from typing import Any, Optional, Tuple, List


class ExecuteQuery:
    """
    A reusable context manager for executing database queries.

    This context manager automatically handles opening and closing database connections,
    executing queries with parameters, and managing transactions. It provides a clean
    interface for database operations while ensuring proper resource management.
    """

    def __init__(self, db_name: str, query: str, parameters: Optional[Tuple] = None):
        """
        Initialize the ExecuteQuery context manager.

        Args:
            db_name (str): Name of the SQLite database file
            query (str): SQL query to execute
            parameters (Optional[Tuple]): Parameters for the SQL query
        """
        self.db_name = db_name
        self.query = query
        self.parameters = parameters or ()
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.results: Optional[List[Tuple[Any, ...]]] = None

    def __enter__(self) -> "ExecuteQuery":
        """
        Enter the context manager - establish database connection and execute query.

        Returns:
            ExecuteQuery: Self instance with query results available
        """
        try:
            # Open database connection
            print(f"Opening database connection to {self.db_name}")
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()

            # Execute the query with parameters
            print(f"Executing query: {self.query}")
            if self.parameters:
                print(f"With parameters: {self.parameters}")
                self.cursor.execute(self.query, self.parameters)
            else:
                self.cursor.execute(self.query)

            # Fetch results for SELECT queries
            if self.query.strip().upper().startswith("SELECT"):
                self.results = self.cursor.fetchall()
                print(f"Query executed successfully, fetched {len(self.results)} rows")
            else:
                # For non-SELECT queries, commit the transaction
                self.connection.commit()
                print(
                    f"Query executed successfully, {self.cursor.rowcount} rows affected"
                )

            return self

        except Exception as e:
            print(f"Error executing query: {e}")
            if self.connection:
                self.connection.rollback()
                print("Transaction rolled back due to error")
            raise

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> None:
        """
        Exit the context manager - handle cleanup and error management.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        try:
            if exc_type is not None:
                # An exception occurred, rollback transaction
                if self.connection:
                    self.connection.rollback()
                    print(f"Exception occurred: {exc_val}")
                    print("Database transaction rolled back")
            else:
                # No exception, commit transaction for non-SELECT queries
                if self.connection and not self.query.strip().upper().startswith(
                    "SELECT"
                ):
                    self.connection.commit()
                    print("Database transaction committed successfully")

        finally:
            # Always close cursor and connection
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
                print("Database connection closed")

    def get_results(self) -> Optional[List[Tuple[Any, ...]]]:
        """
        Get the results of the executed query.

        Returns:
            Optional[List[Tuple]]: Query results if available, None otherwise
        """
        return self.results

    def print_results(self) -> None:
        """
        Print the query results in a formatted way.
        """
        if self.results is None:
            print("No results to display (non-SELECT query or query not executed)")
            return

        if not self.results:
            print("Query returned no rows")
            return

        print("\nQuery Results:")
        print("-" * 50)
        for i, row in enumerate(self.results, 1):
            if len(row) >= 4:  # Assuming users table structure (id, name, email, age)
                print(
                    f"{i:2d}. ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Age: {row[3]}"
                )
            else:
                print(f"{i:2d}. {row}")
        print(f"\nTotal rows: {len(self.results)}")


def setup_database():
    """
    Set up the database with sample data for testing.
    """
    print("Setting up database with sample data...")

    # Create table and insert sample data
    with ExecuteQuery(
        "users.db",
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER
        )
    """,
    ) as query_manager:
        pass

    # Insert sample users if table is empty
    with ExecuteQuery("users.db", "SELECT COUNT(*) FROM users") as query_manager:
        count = query_manager.get_results()[0][0] if query_manager.get_results() else 0

    if count == 0:
        sample_users = [
            ("Alice Johnson", "alice@example.com", 28),
            ("Bob Smith", "bob@example.com", 34),
            ("Charlie Brown", "charlie@example.com", 22),
            ("Diana Prince", "diana@example.com", 30),
            ("Eve Wilson", "eve@example.com", 19),
        ]

        for name, email, age in sample_users:
            with ExecuteQuery(
                "users.db",
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                (name, email, age),
            ) as query_manager:
                pass

        print("Sample data inserted successfully!")


def main():
    """
    Demonstrate the ExecuteQuery context manager functionality.
    """
    print("=" * 60)
    print("DEMONSTRATING REUSABLE QUERY CONTEXT MANAGER")
    print("=" * 60)

    # Setup database
    setup_database()
    print()

    # Example 1: Execute the required query - SELECT users WHERE age > 25
    print("1. Executing required query: SELECT * FROM users WHERE age > 25")
    print("-" * 60)

    with ExecuteQuery(
        "users.db", "SELECT * FROM users WHERE age > ?", (25,)
    ) as query_manager:
        query_manager.print_results()

    print("\n" + "=" * 60)

    # Example 2: Execute a different query - Count all users
    print("2. Executing count query: SELECT COUNT(*) FROM users")
    print("-" * 60)

    with ExecuteQuery(
        "users.db", "SELECT COUNT(*) as total_users FROM users"
    ) as query_manager:
        results = query_manager.get_results()
        if results:
            print(f"Total users in database: {results[0][0]}")

    print("\n" + "=" * 60)

    # Example 3: Execute an INSERT query
    print("3. Executing INSERT query: Adding a new user")
    print("-" * 60)

    with ExecuteQuery(
        "users.db",
        "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
        ("Frank Miller", "frank@example.com", 45),
    ) as query_manager:
        print("New user added successfully!")

    print("\n" + "=" * 60)

    # Example 4: Verify the insert worked
    print("4. Verifying insert: SELECT * FROM users WHERE name = 'Frank Miller'")
    print("-" * 60)

    with ExecuteQuery(
        "users.db", "SELECT * FROM users WHERE name = ?", ("Frank Miller",)
    ) as query_manager:
        query_manager.print_results()

    print("\n" + "=" * 60)

    # Example 5: Demonstrate error handling
    print("5. Demonstrating error handling with invalid query")
    print("-" * 60)

    try:
        with ExecuteQuery(
            "users.db", "SELECT * FROM non_existent_table"
        ) as query_manager:
            query_manager.print_results()
    except Exception as e:
        print(f"✓ Caught expected error: {e}")
        print("✓ Context manager handled the error properly")

    print("\n" + "=" * 60)
    print("REUSABLE QUERY CONTEXT MANAGER DEMONSTRATION COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    main()
