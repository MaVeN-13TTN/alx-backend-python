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


query_cache = {}


def cache_query(func):
    """
    Decorator that caches the results of database queries to avoid redundant calls.

    This decorator:
    1. Uses the SQL query string as the cache key
    2. Returns cached results if the query has been executed before
    3. Executes and caches the query result if not previously cached
    4. Stores results in the global query_cache dictionary

    Args:
        func: The function to be decorated (should accept query parameter)

    Returns:
        The wrapper function that manages query caching
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from function arguments
        query = None

        # Check if query is in kwargs
        if "query" in kwargs:
            query = kwargs["query"]
        # Check if query is the second positional argument (after connection)
        elif len(args) >= 2 and isinstance(args[1], str):
            query = args[1]
        # Look for query in all string arguments
        else:
            for arg in args[1:]:  # Skip the connection argument
                if isinstance(arg, str) and (
                    "SELECT" in arg.upper()
                    or "INSERT" in arg.upper()
                    or "UPDATE" in arg.upper()
                    or "DELETE" in arg.upper()
                ):
                    query = arg
                    break

        # If no query found, execute without caching
        if not query:
            return func(*args, **kwargs)

        # Create a cache key from the query (normalize whitespace)
        cache_key = " ".join(query.split()).upper()

        # Check if result is already cached
        if cache_key in query_cache:
            print(f"Cache hit for query: {query}")
            return query_cache[cache_key]

        # Execute the function and cache the result
        print(f"Cache miss for query: {query}")
        result = func(*args, **kwargs)

        # Store the result in cache
        query_cache[cache_key] = result
        print(f"Result cached for query: {query}")

        return result

    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
