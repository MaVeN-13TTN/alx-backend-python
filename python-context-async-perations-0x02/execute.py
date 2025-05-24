#!/usr/bin/env python3
"""
Reusable Query Context Manager Module

This module provides the ExecuteQuery class, a reusable context manager
for executing SQL queries with proper connection and error handling.
"""

import sqlite3
from typing import List, Tuple, Any, Optional


class ExecuteQuery:
    """
    A reusable context manager for executing SQL queries with proper
    connection management and error handling.

    This class implements the context manager protocol with __enter__ and __exit__
    methods to ensure proper resource cleanup and transaction management.
    """

    def __init__(self, db_name: str, query: str, parameters: Optional[Tuple] = None):
        """
        Initialize the ExecuteQuery context manager.

        Args:
            db_name (str): Path to the SQLite database file
            query (str): SQL query to execute
            parameters (Optional[Tuple]): Parameters for parameterized queries
        """
        self.db_name = db_name
        self.query = query
        self.parameters = parameters or ()
        self.connection = None
        self.cursor = None
        self.results = None
        self.rowcount = 0

    def __enter__(self):
        """
        Enter the context manager - establish database connection and execute query.

        Returns:
            self: The ExecuteQuery instance for method chaining
        """
        try:
            print(f"Opening database connection to {self.db_name}")
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()

            # Execute the query with parameters if provided
            if self.parameters:
                print(f"Executing query: {self.query}")
                print(f"With parameters: {self.parameters}")
                self.cursor.execute(self.query, self.parameters)
            else:
                print(f"Executing query: {self.query}")
                self.cursor.execute(self.query)

            # Handle different types of queries
            if self.query.strip().upper().startswith(("SELECT", "PRAGMA")):
                # For SELECT queries, fetch results
                self.results = self.cursor.fetchall()
                self.rowcount = len(self.results) if self.results else 0
                print(f"Query executed successfully, fetched {self.rowcount} rows")
            else:
                # For INSERT, UPDATE, DELETE queries
                self.rowcount = self.cursor.rowcount
                print(f"Query executed successfully, {self.rowcount} rows affected")

            return self

        except Exception as e:
            print(f"Error executing query: {e}")
            if self.connection:
                self.connection.rollback()
                print("Transaction rolled back due to error")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager - commit transaction and close connection.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        try:
            if exc_type is not None:
                # An exception occurred, rollback the transaction
                if self.connection:
                    self.connection.rollback()
                    print("Transaction rolled back due to exception")
            else:
                # No exception, commit the transaction
                if self.connection:
                    self.connection.commit()
                    print("Database transaction committed successfully")
        finally:
            # Always close the connection
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
                print("Database connection closed")

    def get_results(self) -> List[Tuple[Any, ...]]:
        """
        Get the results of the executed query.

        Returns:
            List[Tuple[Any, ...]]: List of result tuples
        """
        return self.results if self.results is not None else []

    def print_results(self, max_rows: int = 10) -> None:
        """
        Print the results in a formatted way.

        Args:
            max_rows (int): Maximum number of rows to print
        """
        if not self.results:
            print("No results to display")
            return

        print("\nQuery Results:")
        print("-" * 50)
        for i, row in enumerate(self.results[:max_rows], 1):
            if len(row) == 4:  # Assuming user table structure (id, name, email, age)
                print(
                    f"{i:2d}. ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Age: {row[3]}"
                )
            else:
                print(f"{i:2d}. {row}")

        if len(self.results) > max_rows:
            print(f"... and {len(self.results) - max_rows} more rows")

        print(f"\nTotal rows: {len(self.results)}")


# Example usage and testing
if __name__ == "__main__":
    # Create a simple test database and table
    with sqlite3.connect("test_execute.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS test_users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER
            )
        """
        )
        cursor.execute("DELETE FROM test_users")  # Clean slate
        cursor.execute(
            "INSERT INTO test_users (name, age) VALUES (?, ?)", ("Alice", 30)
        )
        cursor.execute("INSERT INTO test_users (name, age) VALUES (?, ?)", ("Bob", 25))
        cursor.execute(
            "INSERT INTO test_users (name, age) VALUES (?, ?)", ("Charlie", 35)
        )
        conn.commit()

    print("Testing ExecuteQuery Context Manager")
    print("=" * 50)

    # Test 1: SELECT query with parameters
    print("\n1. Testing SELECT query with parameters:")
    with ExecuteQuery(
        "test_execute.db", "SELECT * FROM test_users WHERE age > ?", (27,)
    ) as query:
        results = query.get_results()
        print(f"Found {len(results)} users over 27")
        query.print_results()

    # Test 2: INSERT query
    print("\n2. Testing INSERT query:")
    with ExecuteQuery(
        "test_execute.db",
        "INSERT INTO test_users (name, age) VALUES (?, ?)",
        ("David", 28),
    ) as query:
        print("Insert operation completed")

    # Test 3: Error handling
    print("\n3. Testing error handling:")
    try:
        with ExecuteQuery(
            "test_execute.db", "SELECT * FROM non_existent_table"
        ) as query:
            pass
    except Exception as e:
        print(f"Caught expected error: {e}")

    print("\nExecuteQuery testing completed!")
