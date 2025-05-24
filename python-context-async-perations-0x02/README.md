# Python Context Managers and Async Operations

This project demonstrates the implementation and usage of both synchronous and asynchronous context managers in Python, focusing on database connection management with SQLite. The project showcases proper resource management, error handling, and the performance benefits of asynchronous programming.

## 📁 Project Structure

```
python-context-async-perations-0x02/
├── README.md                          # This documentation file
├── 0-databaseconnection.py           # Synchronous context manager implementation
├── 1-async_database_connection.py    # Asynchronous context manager implementation
├── 1-execute.py                       # Original reusable query context manager
├── execute.py                         # Importable module version of ExecuteQuery
├── 3-concurrent.py                    # Concurrent async database queries with asyncio.gather()
├── test_context_manager.py           # Comprehensive tests for sync context manager
├── test_async_context_manager.py     # Comprehensive tests for async context manager
├── test_execute_requirements.py      # Tests for ExecuteQuery context manager
├── test_3_concurrent.py              # Tests for concurrent queries implementation
├── demo_exact_requirements.py        # Minimal demo of ExecuteQuery requirements
├── demo_3_concurrent.py              # Minimal demo of concurrent queries
└── users.db                          # SQLite database with sample data
```

## 🎯 Learning Objectives

By working with this project, you will understand:

- **Context Managers**: How to implement `__enter__` and `__exit__` methods
- **Async Context Managers**: How to implement `__aenter__` and `__aexit__` methods
- **Reusable Query Managers**: Creating flexible context managers for any SQL query
- **Resource Management**: Automatic cleanup of database connections
- **Error Handling**: Proper exception handling and transaction rollback
- **Async Programming**: Benefits of concurrent operations with `asyncio`
- **Performance Comparison**: Sync vs Async execution time differences

## 🚀 Features

### Synchronous Context Manager (`0-databaseconnection.py`)
- ✅ Automatic connection opening and closing
- ✅ Transaction management with commit/rollback
- ✅ Comprehensive error handling
- ✅ Support for nested context managers
- ✅ Detailed logging of database operations

### Asynchronous Context Manager (`1-async_database_connection.py`)
- ✅ Async/await pattern implementation
- ✅ Concurrent database operations support
- ✅ Non-blocking I/O operations
- ✅ Automatic async resource management
- ✅ Performance optimization for multiple operations
- ✅ Demonstration of concurrent execution benefits

### Reusable Query Context Manager (`1-execute.py` & `execute.py`)
- ✅ Flexible query execution with any SQL statement
- ✅ Parameterized query support for safety
- ✅ Automatic connection and transaction management
- ✅ Built-in error handling and rollback
- ✅ Result formatting and display utilities
- ✅ Works with SELECT, INSERT, UPDATE, DELETE operations

### Concurrent Asynchronous Database Queries (`3-concurrent.py`)
- ✅ `async_fetch_users()` - Fetches all users asynchronously
- ✅ `async_fetch_older_users()` - Fetches users older than 40 asynchronously
- ✅ `asyncio.gather()` for concurrent execution of multiple queries
- ✅ Performance comparison between concurrent and sequential execution
- ✅ Advanced multi-query concurrent operations
- ✅ Real-time performance metrics and analysis
- ✅ Comprehensive error handling for concurrent operations

## 📋 Prerequisites

### Required Dependencies
```bash
pip install aiosqlite
```

### Python Version
- Python 3.7+ (for async/await support)
- Recommended: Python 3.12+

## 🛠️ Installation & Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd python-context-async-perations-0x02
   ```

2. **Set up virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/macOS
   # venv\Scripts\activate   # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install aiosqlite
   ```

4. **Run the demonstrations:**
   ```bash
   # Test synchronous context manager
   python 0-databaseconnection.py
   
   # Test asynchronous context manager
   python 1-async_database_connection.py
   
   # Test reusable query context manager
   python 1-execute.py
   ```

## 📖 Usage Examples

### Synchronous Context Manager

```python
from 0-databaseconnection import DatabaseConnection

# Basic usage
with DatabaseConnection("users.db") as cursor:
    cursor.execute("SELECT * FROM users WHERE age > ?", (25,))
    users = cursor.fetchall()
    for user in users:
        print(f"{user[1]} - {user[3]} years old")
```

### Reusable Query Context Manager

```python
from 1-execute import ExecuteQuery

# Execute the exact query from requirements
with ExecuteQuery("users.db", "SELECT * FROM users WHERE age > ?", (25,)) as query_manager:
    results = query_manager.get_results()
    for user in results:
        print(f"{user[1]} - {user[3]} years old")

# Insert new data
with ExecuteQuery("users.db", "INSERT INTO users (name, email, age) VALUES (?, ?, ?)", 
                 ("John Doe", "john@example.com", 30)) as query_manager:
    pass  # Automatically committed

# Count users
with ExecuteQuery("users.db", "SELECT COUNT(*) FROM users") as query_manager:
    count = query_manager.get_results()[0][0]
    print(f"Total users: {count}")
```

### Asynchronous Context Manager

```python
import asyncio
from 1-async_database_connection import AsyncDatabaseConnection

async def fetch_users():
    async with AsyncDatabaseConnection("users.db") as cursor:
        await cursor.execute("SELECT * FROM users WHERE age > ?", (25,))
        users = await cursor.fetchall()
        return users

# Run async function
users = asyncio.run(fetch_users())
```

### Concurrent Operations Example

```python
import asyncio
from 1-async_database_connection import AsyncDatabaseConnection

async def concurrent_operations():
    # Multiple database operations running concurrently
    tasks = []
    
    for i in range(5):
        task = asyncio.create_task(fetch_user_data(i))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

async def fetch_user_data(operation_id):
    async with AsyncDatabaseConnection("users.db") as cursor:
        await cursor.execute("SELECT COUNT(*) FROM users")
        count = await cursor.fetchone()
        return f"Op{operation_id}: {count[0]} users"

# Run concurrent operations
results = asyncio.run(concurrent_operations())
```

## 🚀 Usage Examples

### Concurrent Asynchronous Database Queries

#### Basic Usage
```python
import asyncio
from concurrent_queries import async_fetch_users, async_fetch_older_users, fetch_concurrently

# Run individual async functions
async def example_individual():
    users = await async_fetch_users()
    older_users = await async_fetch_older_users()
    print(f"Total users: {len(users)}")
    print(f"Users older than 40: {len(older_users)}")

# Run functions concurrently
async def example_concurrent():
    all_users, older_users = await fetch_concurrently()
    print(f"Concurrent fetch: {len(all_users)} users, {len(older_users)} older")

# Execute with asyncio.run()
asyncio.run(example_concurrent())
```

#### Advanced Concurrent Operations
```python
import asyncio
import aiosqlite

async def multiple_concurrent_queries():
    """Demonstrate multiple different queries running concurrently."""
    
    async def count_users():
        async with aiosqlite.connect("users.db") as db:
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            result = await cursor.fetchone()
            return result[0]
    
    async def get_average_age():
        async with aiosqlite.connect("users.db") as db:
            cursor = await db.execute("SELECT AVG(age) FROM users")
            result = await cursor.fetchone()
            return round(result[0], 2)
    
    async def get_age_stats():
        async with aiosqlite.connect("users.db") as db:
            cursor = await db.execute("SELECT MIN(age), MAX(age) FROM users")
            result = await cursor.fetchone()
            return result
    
    # Execute all queries concurrently
    count, avg_age, (min_age, max_age) = await asyncio.gather(
        count_users(),
        get_average_age(),
        get_age_stats()
    )
    
    print(f"Users: {count}, Avg Age: {avg_age}, Age Range: {min_age}-{max_age}")

# Run advanced example
asyncio.run(multiple_concurrent_queries())
```

#### Testing Concurrent Performance
```python
# Run the performance demonstration
python 3-concurrent.py

# Run minimal demonstration
python demo_3_concurrent.py

# Run comprehensive tests
python test_3_concurrent.py
```

### Sample Output for Concurrent Queries
```
🚀 CONCURRENT EXECUTION TEST
============================================================
🔍 Starting async_fetch_users()...
🔍 Starting async_fetch_older_users()...
  📁 Connected to database for fetching all users
  📁 Connected to database for fetching older users
  ✅ Fetched 18 total users
  ✅ Fetched 5 users older than 40
============================================================
⚡ Concurrent execution completed in 0.0008 seconds

📊 PERFORMANCE ANALYSIS
⚡ Concurrent execution time:  0.0008 seconds
🐌 Sequential execution time:  0.0013 seconds
🏆 Performance improvement:    1.63x faster with concurrent execution
```

## 🧪 Testing

### Run Synchronous Tests
```bash
python test_context_manager.py
```

**Test Coverage:**
- ✅ Basic database operations
- ✅ Error handling and SQL exceptions
- ✅ Transaction rollback scenarios
- ✅ Multiple context manager instances
- ✅ Nested context managers

### Run Reusable Query Tests
```bash
python test_execute_requirements.py
# or
python demo_exact_requirements.py
```

**Test Coverage:**
- ✅ ExecuteQuery context manager functionality
- ✅ Query execution with parameters
- ✅ Context manager protocol verification
- ✅ Error handling and rollback
- ✅ Multiple query types (SELECT, INSERT, UPDATE, DELETE)
- ✅ Result formatting and display

### Run Asynchronous Tests
```bash
python test_async_context_manager.py
```

**Test Coverage:**
- ✅ Basic async operations
- ✅ Async error handling
- ✅ Async transaction rollback
- ✅ Concurrent operations (4-5x performance improvement)
- ✅ Batch operations
- ✅ Nested async context managers
- ✅ Performance benchmarking

### Sample Test Output
```
Comprehensive Testing of AsyncDatabaseConnection Context Manager
======================================================================
1. Testing basic async operations: ✓
2. Testing async error handling: ✓ 
3. Testing async transaction rollback: ✓
4. Testing concurrent async context managers: ✓
5. Testing async performance benefits: ✓ (~4.9x faster)
6. Testing async batch operations: ✓
7. Testing nested async context managers: ✓
======================================================================
All async tests completed!
```

## 📊 Performance Comparison

### Sync vs Async Performance
The async implementation demonstrates significant performance benefits:

- **Concurrent Operations**: ~4.9x faster execution
- **Resource Efficiency**: Better CPU utilization
- **Scalability**: Handles multiple operations simultaneously
- **Non-blocking**: Doesn't freeze the application during I/O

### Benchmark Results
```
Async operations completed in: 0.102 seconds
Estimated sync time: 0.500 seconds
Performance improvement: ~4.9x faster with async
```

## 🔧 Technical Implementation Details

### Context Manager Protocol (Sync)
```python
class DatabaseConnection:
    def __enter__(self):
        # Open database connection
        # Begin transaction
        return cursor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Handle exceptions
        # Commit or rollback transaction
        # Close connection
```

### Async Context Manager Protocol
```python
class AsyncDatabaseConnection:
    async def __aenter__(self):
        # Async open database connection
        # Begin async transaction
        return cursor
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Handle async exceptions
        # Async commit or rollback
        # Async close connection
```

### Reusable Query Context Manager Protocol
```python
class ExecuteQuery:
    def __init__(self, db_name, query, parameters=None):
        # Store query details
        
    def __enter__(self):
        # Open connection
        # Execute query with parameters
        # Fetch results for SELECT queries
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Handle exceptions and rollback if needed
        # Commit transactions for non-SELECT queries
        # Close connection
        # Async close connection
```

## 🛡️ Error Handling

Both implementations provide robust error handling:

- **SQL Exceptions**: Automatic rollback on database errors
- **Connection Failures**: Proper cleanup even if connection fails
- **Transaction Management**: Ensures data consistency
- **Resource Cleanup**: Guaranteed connection closure

## 🎓 Educational Value

This project teaches:

1. **Context Manager Patterns**: The `with` statement and resource management
2. **Reusable Query Execution**: Creating flexible, parameterized query managers
3. **Async Programming**: Modern Python concurrency patterns
4. **Database Best Practices**: Transaction management and error handling
5. **Performance Optimization**: When and how to use async operations
6. **Testing Strategies**: Comprehensive test coverage for both sync and async code

## 📚 Key Concepts Demonstrated

### Context Managers
- Automatic resource management
- Exception-safe cleanup
- The `with` statement protocol
- Reusable query execution patterns

### Async Programming
- `async`/`await` keywords
- Concurrent execution with `asyncio`
- Non-blocking I/O operations
- Performance benefits of asynchronous code

### Database Management
- SQLite integration
- Transaction handling
- Error recovery
- Parameterized queries for security
- Connection pooling concepts

## 🚦 Running the Project

### Quick Start
```bash
# Run sync demo
python 0-databaseconnection.py

# Run async demo  
python 1-async_database_connection.py

# Run reusable query demo
python 1-execute.py

# Run all tests
python test_context_manager.py
python test_async_context_manager.py
python test_execute_requirements.py
```

### Sample Database Schema
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    age INTEGER
);
```

## 🤝 Contributing

To extend this project:

1. Add more async patterns (connection pooling, async generators)
2. Implement additional database operations
3. Add more comprehensive error scenarios
4. Create performance benchmarking tools
5. Add support for other database types
6. Implement async version of ExecuteQuery
7. Add query caching and optimization features

## 🎯 Task Implementations

### Task 1: Reusable Query Context Manager (`1-execute.py`)
**Objective**: Create a reusable context manager that takes a query as input and executes it, managing both connection and query execution.

**Key Features**:
- **Class**: `ExecuteQuery` with `__enter__` and `__exit__` methods
- **Required Query**: `"SELECT * FROM users WHERE age > ?"` with parameter `25`
- **Flexible Design**: Works with any SQL query and parameters
- **Automatic Management**: Handles connection, transaction, and cleanup
- **Error Handling**: Comprehensive exception management and rollback
- **Result Access**: `get_results()` method and formatted display options

**Usage Example**:
```python
# Exact requirements implementation
with ExecuteQuery("users.db", "SELECT * FROM users WHERE age > ?", (25,)) as query_manager:
    results = query_manager.get_results()
    query_manager.print_results()
```

## 📝 License

This project is part of the ALX Backend Python curriculum and is intended for educational purposes.

---

**Author**: ALX Backend Python Student  
**Date**: May 24, 2025  
**Project**: Python Context Managers and Async Operations
