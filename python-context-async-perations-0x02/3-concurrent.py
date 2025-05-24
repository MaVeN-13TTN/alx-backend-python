#!/usr/bin/env python3
"""
Concurrent Asynchronous Database Queries

This module demonstrates running multiple database queries concurrently using
asyncio.gather() with the aiosqlite library for asynchronous SQLite operations.

Objective: Run multiple database queries concurrently using asyncio.gather.

Features:
- async_fetch_users(): Fetches all users from the database
- async_fetch_older_users(): Fetches users older than 40
- fetch_concurrently(): Runs both queries concurrently using asyncio.gather()
- Performance comparison between sequential and concurrent execution
"""

import asyncio
import aiosqlite
import time
from typing import List, Tuple, Any


async def async_fetch_users() -> List[Tuple[Any, ...]]:
    """
    Asynchronously fetch all users from the database.
    
    Returns:
        List[Tuple[Any, ...]]: List of all user records (id, name, email, age)
    """
    print("🔍 Starting async_fetch_users()...")
    
    async with aiosqlite.connect("users.db") as db:
        print("  📁 Connected to database for fetching all users")
        cursor = await db.execute("SELECT * FROM users")
        users = await cursor.fetchall()
        await cursor.close()
        
        print(f"  ✅ Fetched {len(users)} total users")
        return users


async def async_fetch_older_users() -> List[Tuple[Any, ...]]:
    """
    Asynchronously fetch users older than 40 from the database.
    
    Returns:
        List[Tuple[Any, ...]]: List of user records where age > 40
    """
    print("🔍 Starting async_fetch_older_users()...")
    
    async with aiosqlite.connect("users.db") as db:
        print("  📁 Connected to database for fetching older users")
        cursor = await db.execute("SELECT * FROM users WHERE age > ?", (40,))
        older_users = await cursor.fetchall()
        await cursor.close()
        
        print(f"  ✅ Fetched {len(older_users)} users older than 40")
        return older_users


async def fetch_concurrently() -> Tuple[List[Tuple[Any, ...]], List[Tuple[Any, ...]]]:
    """
    Execute both async_fetch_users() and async_fetch_older_users() concurrently
    using asyncio.gather().
    
    Returns:
        Tuple[List[Tuple[Any, ...]], List[Tuple[Any, ...]]]: 
        A tuple containing (all_users, older_users)
    """
    print("🚀 Starting concurrent database queries using asyncio.gather()...")
    print("=" * 60)
    
    # Record start time for performance measurement
    start_time = time.time()
    
    # Execute both queries concurrently using asyncio.gather()
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    # Calculate execution time
    end_time = time.time()
    execution_time = end_time - start_time
    
    print("=" * 60)
    print(f"⚡ Concurrent execution completed in {execution_time:.4f} seconds")
    print()
    
    return all_users, older_users


async def fetch_sequentially() -> Tuple[List[Tuple[Any, ...]], List[Tuple[Any, ...]]]:
    """
    Execute the same queries sequentially for performance comparison.
    
    Returns:
        Tuple[List[Tuple[Any, ...]], List[Tuple[Any, ...]]]: 
        A tuple containing (all_users, older_users)
    """
    print("🐌 Starting sequential database queries for comparison...")
    print("=" * 60)
    
    # Record start time for performance measurement
    start_time = time.time()
    
    # Execute queries sequentially (one after the other)
    all_users = await async_fetch_users()
    older_users = await async_fetch_older_users()
    
    # Calculate execution time
    end_time = time.time()
    execution_time = end_time - start_time
    
    print("=" * 60)
    print(f"🐌 Sequential execution completed in {execution_time:.4f} seconds")
    print()
    
    return all_users, older_users


def display_results(all_users: List[Tuple[Any, ...]], older_users: List[Tuple[Any, ...]]) -> None:
    """
    Display the results of the database queries in a formatted way.
    
    Args:
        all_users: List of all user records
        older_users: List of older user records
    """
    print("📊 QUERY RESULTS")
    print("=" * 60)
    
    print(f"📈 Total Users: {len(all_users)}")
    print("👥 All Users:")
    for i, (user_id, name, email, age) in enumerate(all_users[:10], 1):  # Show first 10
        print(f"  {i:2d}. {name} ({email}) - {age} years old")
    
    if len(all_users) > 10:
        print(f"     ... and {len(all_users) - 10} more users")
    
    print()
    print(f"👴 Users Older Than 40: {len(older_users)}")
    if older_users:
        print("🎯 Older Users:")
        for i, (user_id, name, email, age) in enumerate(older_users, 1):
            print(f"  {i:2d}. {name} ({email}) - {age} years old")
    else:
        print("  No users older than 40 found")
    
    print("=" * 60)


async def demonstrate_concurrent_vs_sequential():
    """
    Demonstrate the performance difference between concurrent and sequential execution.
    """
    print("🏁 PERFORMANCE COMPARISON: Concurrent vs Sequential")
    print("=" * 80)
    print()
    
    # Test concurrent execution
    print("🚀 CONCURRENT EXECUTION TEST")
    concurrent_start = time.time()
    concurrent_all_users, concurrent_older_users = await fetch_concurrently()
    concurrent_time = time.time() - concurrent_start
    
    print()
    
    # Test sequential execution
    print("🐌 SEQUENTIAL EXECUTION TEST")
    sequential_start = time.time()
    sequential_all_users, sequential_older_users = await fetch_sequentially()
    sequential_time = time.time() - sequential_start
    
    print()
    
    # Performance analysis
    print("📊 PERFORMANCE ANALYSIS")
    print("=" * 80)
    print(f"⚡ Concurrent execution time:  {concurrent_time:.4f} seconds")
    print(f"🐌 Sequential execution time:  {sequential_time:.4f} seconds")
    
    if sequential_time > 0:
        speedup = sequential_time / concurrent_time
        print(f"🏆 Performance improvement:    {speedup:.2f}x faster with concurrent execution")
        print(f"⏱️  Time saved:               {(sequential_time - concurrent_time) * 1000:.2f} milliseconds")
    
    print("=" * 80)
    
    # Display results from concurrent execution
    display_results(concurrent_all_users, concurrent_older_users)


async def main():
    """
    Main function to demonstrate concurrent asynchronous database queries.
    """
    print("🌟 CONCURRENT ASYNCHRONOUS DATABASE QUERIES DEMONSTRATION")
    print("=" * 80)
    print("📖 This demonstration shows how to use asyncio.gather() to run")
    print("   multiple database queries concurrently for improved performance.")
    print("=" * 80)
    print()
    
    try:
        # Run the basic concurrent fetch demonstration
        print("🎯 BASIC CONCURRENT FETCH DEMONSTRATION")
        all_users, older_users = await fetch_concurrently()
        display_results(all_users, older_users)
        
        print()
        
        # Run performance comparison
        await demonstrate_concurrent_vs_sequential()
        
        print()
        print("✅ DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("🎉 Key takeaways:")
        print("   - asyncio.gather() enables concurrent execution of async functions")
        print("   - Concurrent database queries can significantly improve performance")
        print("   - aiosqlite provides async context manager support")
        print("   - Proper error handling ensures robust async operations")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        raise


# Additional utility functions for enhanced demonstration

async def test_multiple_concurrent_queries():
    """
    Demonstrate running multiple different queries concurrently.
    """
    print("\n🔬 ADVANCED: Multiple Different Concurrent Queries")
    print("=" * 60)
    
    async def count_users():
        async with aiosqlite.connect("users.db") as db:
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            result = await cursor.fetchone()
            await cursor.close()
            return result[0]
    
    async def get_average_age():
        async with aiosqlite.connect("users.db") as db:
            cursor = await db.execute("SELECT AVG(age) FROM users")
            result = await cursor.fetchone()
            await cursor.close()
            return round(result[0], 2) if result[0] else 0
    
    async def get_youngest_user():
        async with aiosqlite.connect("users.db") as db:
            cursor = await db.execute("SELECT name, age FROM users ORDER BY age ASC LIMIT 1")
            result = await cursor.fetchone()
            await cursor.close()
            return result
    
    async def get_oldest_user():
        async with aiosqlite.connect("users.db") as db:
            cursor = await db.execute("SELECT name, age FROM users ORDER BY age DESC LIMIT 1")
            result = await cursor.fetchone()
            await cursor.close()
            return result
    
    # Execute all queries concurrently
    start_time = time.time()
    results = await asyncio.gather(
        count_users(),
        get_average_age(),
        get_youngest_user(),
        get_oldest_user(),
        return_exceptions=True
    )
    execution_time = time.time() - start_time
    
    user_count, avg_age, youngest, oldest = results
    
    print(f"📊 Database Statistics (computed in {execution_time:.4f}s):")
    print(f"   👥 Total users: {user_count}")
    print(f"   📈 Average age: {avg_age} years")
    print(f"   👶 Youngest user: {youngest[0]} ({youngest[1]} years)")
    print(f"   👴 Oldest user: {oldest[0]} ({oldest[1]} years)")


if __name__ == "__main__":
    # Use asyncio.run() to execute the main coroutine
    print("🚀 Running concurrent database queries with asyncio.run()...")
    print()
    
    asyncio.run(main())
    
    print()
    print("🔍 Running additional advanced demonstration...")
    asyncio.run(test_multiple_concurrent_queries())
    
    print()
    print("🏁 All demonstrations completed!")
