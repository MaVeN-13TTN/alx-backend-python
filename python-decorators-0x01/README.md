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
