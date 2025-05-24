#!/usr/bin/env python3
"""
Test script for the ExecuteQuery context manager demonstrating the exact requirements.
"""

from typing import List, Tuple, Any
import sys
import os

# Add the current directory to the Python path to import our module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our ExecuteQuery class
from execute import ExecuteQuery


def test_exact_requirements():
    """
    Test the exact requirements: ExecuteQuery that takes the query
    "SELECT * FROM users WHERE age > ?" and parameter 25
    """
    print("Testing ExecuteQuery with exact requirements:")
    print("Query: 'SELECT * FROM users WHERE age > ?'")
    print("Parameter: 25")
    print("-" * 50)

    # Use the ExecuteQuery context manager with the exact requirements
    with ExecuteQuery(
        "users.db", "SELECT * FROM users WHERE age > ?", (25,)
    ) as query_context:
        # Get the results
        results = query_context.get_results()

        # Print results
        if results:
            print(f"Found {len(results)} users with age > 25:")
            for user in results:
                print(f"  - {user[1]} ({user[2]}) - {user[3]} years old")
        else:
            print("No users found with age > 25")

        return results


def test_context_manager_methods():
    """
    Verify that the ExecuteQuery class uses __enter__ and __exit__ methods
    """
    print("\nVerifying context manager methods:")
    print("-" * 40)

    # Check if the class has the required methods
    has_enter = hasattr(ExecuteQuery, "__enter__")
    has_exit = hasattr(ExecuteQuery, "__exit__")

    print(f"✓ Has __enter__ method: {has_enter}")
    print(f"✓ Has __exit__ method: {has_exit}")

    if has_enter and has_exit:
        print("✓ ExecuteQuery is a proper context manager!")
    else:
        print("✗ ExecuteQuery is missing required context manager methods!")

    return has_enter and has_exit


def main():
    """
    Main test function demonstrating the exact requirements
    """
    print("=" * 60)
    print("TESTING EXECUTEQUERY CONTEXT MANAGER - EXACT REQUIREMENTS")
    print("=" * 60)

    # Test 1: Exact requirements
    results = test_exact_requirements()

    # Test 2: Verify context manager implementation
    is_valid_context_manager = test_context_manager_methods()

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"✓ Query executed successfully: {results is not None}")
    print(f"✓ Results returned: {len(results) if results else 0} rows")
    print(f"✓ Context manager properly implemented: {is_valid_context_manager}")
    print("=" * 60)

    # Show that it works with the 'with' statement
    print("\nDemonstrating 'with' statement usage:")
    print("-" * 40)
    with ExecuteQuery("users.db", "SELECT * FROM users WHERE age > ?", (25,)) as eq:
        count = len(eq.get_results()) if eq.get_results() else 0
        print(f"Context manager successfully executed query and found {count} users")


if __name__ == "__main__":
    main()
