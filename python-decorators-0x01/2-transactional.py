import sqlite3
import functools

def with_db_connection(func):
    """
    Decorator that automatically handles opening and closing database connections.

    This decorator:
    1. Opens a connection to the 'users.db' database
    2. Passes the connection as the first argument to the decorated function
    3. Ensures the connection is properly closed after function execution
    4. Handles exceptions to ensure connection cleanup

    Args:
        func: The function to be decorated

    Returns:
        The wrapper function that manages database connections
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect("users.db")

        try:
            # Call the original function with connection as first argument
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Always close the connection, even if an exception occurs
            conn.close()

    return wrapper


def transactional(func):
    """
    Decorator that manages database transactions by automatically committing or rolling back changes.
    
    This decorator:
    1. Begins a transaction before executing the function
    2. Commits the transaction if the function executes successfully
    3. Rolls back the transaction if the function raises an exception
    4. Re-raises any exceptions that occurred
    
    Args:
        func: The function to be decorated (should accept a database connection as first argument)
        
    Returns:
        The wrapper function that manages transactions
    """
    
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Begin transaction (SQLite uses autocommit=False by default when executing statements)
            # Save the current autocommit state
            original_isolation_level = conn.isolation_level
            
            # Start transaction by setting isolation level
            if conn.isolation_level is None:
                conn.execute('BEGIN')
            
            # Execute the original function
            result = func(conn, *args, **kwargs)
            
            # If we get here, the function executed successfully - commit the transaction
            conn.commit()
            
            return result
            
        except Exception as e:
            # If an exception occurred, rollback the transaction
            conn.rollback()
            # Re-raise the exception so it can be handled upstream
            raise e
    
    return wrapper


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))


#### Update user's email with automatic transaction handling
update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
