import sqlite3
import functools

#### decorator to log SQL queries


def log_queries(func):
    """
    Decorator that logs SQL queries executed by a function.

    Args:
        func: The function to be decorated

    Returns:
        The wrapper function that logs queries before execution
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from function arguments
        # Assuming the query is passed as a keyword argument or the first positional argument
        query = None

        # Check if query is in kwargs
        if "query" in kwargs:
            query = kwargs["query"]
        # Check if query is the first positional argument
        elif args and isinstance(args[0], str):
            query = args[0]
        # Check for other common parameter names
        elif len(args) > 0:
            for arg in args:
                if isinstance(arg, str) and (
                    "SELECT" in arg.upper()
                    or "INSERT" in arg.upper()
                    or "UPDATE" in arg.upper()
                    or "DELETE" in arg.upper()
                ):
                    query = arg
                    break

        # Log the query if found
        if query:
            print(f"Executing SQL Query: {query}")

        # Execute the original function
        return func(*args, **kwargs)

    return wrapper


@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")
