import time
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


def retry_on_failure(retries=3, delay=2):
    """
    Decorator that retries database operations if they fail due to transient errors.

    This decorator:
    1. Attempts to execute the function up to 'retries' times
    2. Waits 'delay' seconds between retry attempts
    3. Re-raises the last exception if all retries fail
    4. Returns the result immediately if the function succeeds

    Args:
        retries (int): Maximum number of retry attempts (default: 3)
        delay (int/float): Delay in seconds between retries (default: 2)

    Returns:
        The decorator function that manages retries
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(
                retries + 1
            ):  # +1 because we include the initial attempt
                try:
                    # Attempt to execute the function
                    result = func(*args, **kwargs)
                    # If successful, return immediately
                    return result

                except Exception as e:
                    last_exception = e

                    # If this was the last attempt, don't wait
                    if attempt == retries:
                        break

                    # Log the retry attempt (optional, for debugging)
                    print(
                        f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds..."
                    )

                    # Wait before retrying
                    time.sleep(delay)

            # If we get here, all retries failed - raise the last exception
            raise last_exception

        return wrapper

    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


#### attempt to fetch users with automatic retry on failure
users = fetch_users_with_retry()
print(users)
