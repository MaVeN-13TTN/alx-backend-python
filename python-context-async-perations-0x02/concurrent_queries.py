#!/usr/bin/env python3
"""
Concurrent Database Queries Module

This module provides functions for concurrent asynchronous database operations
that can be properly imported by other modules.
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


# For backward compatibility and testing
if __name__ == "__main__":
    async def main():
        """Main function for testing the module."""
        print("🧪 Testing concurrent database queries module...")
        
        # Test the concurrent fetch
        all_users, older_users = await fetch_concurrently()
        display_results(all_users, older_users)
        
        print("\n✅ Module test completed successfully!")
    
    asyncio.run(main())
