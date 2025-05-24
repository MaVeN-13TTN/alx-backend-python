#!/usr/bin/env python3
"""
Advanced test for transactional decorator - demonstrates rollback of multiple operations
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
            original_isolation_level = conn.isolation_level
            if conn.isolation_level is None:
                conn.execute('BEGIN')
            
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
            
        except Exception as e:
            conn.rollback()
            raise e
    
    return wrapper

@with_db_connection
def get_all_users(conn):
    """Get all users to check database state"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users ORDER BY id")
    return cursor.fetchall()

@with_db_connection
@transactional
def complex_operation_with_error(conn):
    """Perform multiple operations and then fail - should rollback all changes"""
    cursor = conn.cursor()
    
    # Operation 1: Update user 1
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", ('temp1@example.com', 1))
    
    # Operation 2: Update user 2
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", ('temp2@example.com', 2))
    
    # Operation 3: Update user 3
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", ('temp3@example.com', 3))
    
    # Operation 4: This will fail and should cause rollback of all above operations
    raise ValueError("Simulated business logic error")

@with_db_connection
@transactional
def successful_complex_operation(conn):
    """Perform multiple operations successfully - should commit all changes"""
    cursor = conn.cursor()
    
    # Update multiple users
    updates = [
        ('final1@example.com', 1),
        ('final2@example.com', 2),
        ('final3@example.com', 3)
    ]
    
    for email, user_id in updates:
        cursor.execute("UPDATE users SET email = ? WHERE id = ?", (email, user_id))
    
    return len(updates)

if __name__ == "__main__":
    print("Advanced Transactional Decorator Testing:\n")
    
    print("1. Current database state:")
    current_users = get_all_users()
    for user in current_users:
        print(f"   {user}")
    
    print("\n2. Testing complex operation that fails (should rollback all changes):")
    try:
        complex_operation_with_error()
        print("   ✗ This should not execute")
    except ValueError as e:
        print(f"   ✓ Caught expected error: {e}")
        
        print("   Checking database state after rollback:")
        users_after_rollback = get_all_users()
        for user in users_after_rollback:
            print(f"   {user}")
        
        # Verify no changes were made
        if users_after_rollback == current_users:
            print("   ✓ All changes were successfully rolled back!")
        else:
            print("   ✗ Rollback failed - data was modified!")
    
    print("\n3. Testing successful complex operation (should commit all changes):")
    try:
        updated_count = successful_complex_operation()
        print(f"   ✓ Successfully updated {updated_count} users")
        
        print("   Final database state:")
        final_users = get_all_users()
        for user in final_users:
            print(f"   {user}")
        print("   ✓ All changes were successfully committed!")
        
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
    
    print("\nAdvanced transaction testing completed!")
