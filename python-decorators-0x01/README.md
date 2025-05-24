# Python Decorators for Database Operations

## Task 0: Logging Database Queries

### Objective
Create a decorator that logs database queries executed by any function.

### Implementation
The `log_queries` decorator intercepts function calls and logs SQL queries before execution.

### Key Features
- **Query Detection**: Automatically detects SQL queries from function arguments
- **Flexible Parameter Handling**: Works with both positional and keyword arguments
- **SQL Pattern Recognition**: Identifies common SQL operations (SELECT, INSERT, UPDATE, DELETE)
- **Function Preservation**: Uses `functools.wraps` to preserve original function metadata

### Usage Example
```python
@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# This will log: "Executing SQL Query: SELECT * FROM users"
users = fetch_all_users(query="SELECT * FROM users")
```

### Files
- `0-log_queries.py`: Main implementation file
- `setup_db.py`: Database setup script for testing
- `test_log_queries.py`: Comprehensive test examples

### How It Works
1. The decorator wraps the original function
2. Extracts SQL queries from function arguments
3. Logs the query using print statement
4. Executes the original function with all arguments preserved
5. Returns the original function's result

### Testing
Run the setup script first to create the test database:
```bash
python setup_db.py
```

Then run the main implementation:
```bash
python 0-log_queries.py
```

For more comprehensive testing:
```bash
python test_log_queries.py
```

## Task 1: Handle Database Connections with a Decorator

### Objective
Create a decorator that automatically handles opening and closing database connections.

### Implementation
The `with_db_connection` decorator manages database connections automatically, eliminating boilerplate code.

### Key Features
- **Automatic Connection Management**: Opens database connection before function execution
- **Guaranteed Cleanup**: Uses try/finally to ensure connections are always closed
- **Exception Safety**: Properly closes connections even when exceptions occur
- **Transparent Integration**: Functions receive the connection as their first parameter
- **Resource Efficiency**: Prevents connection leaks

### Usage Example
```python
@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# No need to manually manage connections
user = get_user_by_id(user_id=1)
```

### Files
- `1-with_db_connection.py`: Main implementation file
- `test_with_db_connection.py`: Comprehensive test examples
- `test_error_handling.py`: Error handling verification

### How It Works
1. The decorator opens a SQLite connection to 'users.db'
2. Passes the connection as the first argument to the decorated function
3. Uses try/finally to ensure the connection is always closed
4. Handles exceptions gracefully while maintaining connection cleanup
5. Returns the original function's result

### Benefits
- **Eliminates Boilerplate**: No need to repeatedly write connection open/close code
- **Prevents Resource Leaks**: Automatic cleanup ensures connections don't remain open
- **Error Resilience**: Connections are closed even when functions raise exceptions
- **Clean Code**: Functions focus on business logic, not connection management

### Testing
```bash
python 1-with_db_connection.py
python test_with_db_connection.py
python test_error_handling.py
```

## Task 2: Transaction Management Decorator

### Objective
Create a decorator that manages database transactions by automatically committing or rolling back changes.

### Implementation
The `transactional` decorator ensures database operations are wrapped in transactions with automatic commit/rollback handling.

### Key Features
- **Automatic Transaction Management**: Begins transactions before function execution
- **Smart Commit/Rollback**: Commits on success, rolls back on exceptions
- **Exception Preservation**: Re-raises exceptions after rollback for proper error handling
- **Decorator Composition**: Works seamlessly with `@with_db_connection`
- **ACID Compliance**: Ensures atomicity, consistency, isolation, and durability

### Usage Example
```python
@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))

# Automatically commits if successful, rolls back if error occurs
update_user_email(user_id=1, new_email='new@example.com')
```

### Files
- `2-transactional.py`: Main implementation file
- `test_transactional.py`: Basic transaction testing
- `test_advanced_transactional.py`: Complex rollback scenarios

### How It Works
1. The decorator begins a database transaction before function execution
2. Executes the decorated function with the database connection
3. If the function completes successfully, commits the transaction
4. If an exception occurs, rolls back all changes and re-raises the exception
5. Ensures data consistency regardless of operation outcome

### Benefits
- **Data Integrity**: Ensures all-or-nothing execution for database operations
- **Error Recovery**: Automatic rollback prevents partial updates
- **Simplified Code**: Eliminates manual transaction management
- **Composability**: Works with other decorators like `@with_db_connection`
- **Reliability**: Handles complex multi-operation transactions safely

### Transaction Scenarios
✅ **Success Case**: Multiple operations → All committed
✅ **Failure Case**: Error during operations → All rolled back
✅ **Complex Operations**: Batch updates handled atomically
✅ **Exception Safety**: Proper cleanup even with unexpected errors

### Testing
```bash
python 2-transactional.py
python test_transactional.py
python test_advanced_transactional.py
```
