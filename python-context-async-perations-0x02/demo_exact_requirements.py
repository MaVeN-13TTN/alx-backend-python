#!/usr/bin/env python3
"""
Minimal demonstration of the ExecuteQuery context manager
with the exact requirements specified in the task.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import ExecuteQuery from the execute module
from execute import ExecuteQuery


def main():
    """
    Demonstrate the exact requirements:
    - ExecuteQuery context manager
    - Query: "SELECT * FROM users WHERE age > ?"
    - Parameter: 25
    - Using __enter__ and __exit__ methods
    """
    print("EXACT REQUIREMENTS DEMONSTRATION")
    print("=" * 50)
    print("Context Manager: ExecuteQuery")
    print("Query: 'SELECT * FROM users WHERE age > ?'")
    print("Parameter: 25")
    print("Methods: __enter__ and __exit__")
    print("=" * 50)

    # Use the ExecuteQuery context manager exactly as specified
    with ExecuteQuery(
        "users.db", "SELECT * FROM users WHERE age > ?", (25,)
    ) as query_manager:
        results = query_manager.get_results()

        print(f"\n✓ Context manager executed successfully")
        print(f"✓ Found {len(results)} users with age > 25")
        print(f"✓ Results type: {type(results)}")

        # Display first few results
        if results:
            print("\nFirst 3 results:")
            for i, user in enumerate(results[:3]):
                print(f"  {i+1}. {user[1]} - {user[3]} years old")

    print(f"\n✓ Context manager cleanup completed")
    print("✓ __enter__ and __exit__ methods used automatically")


if __name__ == "__main__":
    main()
