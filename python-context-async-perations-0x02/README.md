# Python Context Managers and Async Operations

This project demonstrates the implementation and usage of both synchronous and asynchronous context managers in Python, focusing on database connection management with SQLite. The project showcases proper resource management, error handling, and the performance benefits of asynchronous programming.

## 📁 Project Structure

```
python-context-async-perations-0x02/
├── README.md                          # This documentation file
├── 0-databaseconnection.py           # Synchronous context manager implementation
├── 1-async_database_connection.py    # Asynchronous context manager implementation
├── test_context_manager.py           # Comprehensive tests for sync context manager
├── test_async_context_manager.py     # Comprehensive tests for async context manager
└── users.db                          # SQLite database with sample data
```

## 🎯 Learning Objectives

By working with this project, you will understand:

- **Context Managers**: How to implement `__enter__` and `__exit__` methods
- **Async Context Managers**: How to implement `__aenter__` and `__aexit__` methods
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

## 🛡️ Error Handling

Both implementations provide robust error handling:

- **SQL Exceptions**: Automatic rollback on database errors
- **Connection Failures**: Proper cleanup even if connection fails
- **Transaction Management**: Ensures data consistency
- **Resource Cleanup**: Guaranteed connection closure

## 🎓 Educational Value

This project teaches:

1. **Context Manager Patterns**: The `with` statement and resource management
2. **Async Programming**: Modern Python concurrency patterns
3. **Database Best Practices**: Transaction management and error handling
4. **Performance Optimization**: When and how to use async operations
5. **Testing Strategies**: Comprehensive test coverage for both sync and async code

## 📚 Key Concepts Demonstrated

### Context Managers
- Automatic resource management
- Exception-safe cleanup
- The `with` statement protocol

### Async Programming
- `async`/`await` keywords
- Concurrent execution with `asyncio`
- Non-blocking I/O operations
- Performance benefits of asynchronous code

### Database Management
- SQLite integration
- Transaction handling
- Error recovery
- Connection pooling concepts

## 🚦 Running the Project

### Quick Start
```bash
# Run sync demo
python 0-databaseconnection.py

# Run async demo  
python 1-async_database_connection.py

# Run all tests
python test_context_manager.py
python test_async_context_manager.py
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

## 📝 License

This project is part of the ALX Backend Python curriculum and is intended for educational purposes.

---

**Author**: ALX Backend Python Student  
**Date**: May 24, 2025  
**Project**: Python Context Managers and Async Operations
