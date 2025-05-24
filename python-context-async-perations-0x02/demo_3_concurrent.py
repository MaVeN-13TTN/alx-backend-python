#!/usr/bin/env python3
"""
Minimal demonstration of the exact requirements for 3-concurrent.py

This script demonstrates:
1. async_fetch_users() - fetches all users
2. async_fetch_older_users() - fetches users older than 40
3. Using asyncio.gather() to run both functions concurrently
4. Using asyncio.run(fetch_concurrently()) to execute
"""

import asyncio
import aiosqlite
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the required functions from concurrent_queries module
from concurrent_queries import fetch_concurrently


async def simple_demonstration():
    """
    Simple demonstration showing just the core functionality.
    """
    print("MINIMAL DEMONSTRATION OF CONCURRENT ASYNC QUERIES")
    print("=" * 55)
    print()
    
    print("📋 Requirements being demonstrated:")
    print("   1. async_fetch_users() function")
    print("   2. async_fetch_older_users() function") 
    print("   3. asyncio.gather() for concurrent execution")
    print("   4. asyncio.run() to execute fetch_concurrently()")
    print()
    
    # Execute the concurrent fetch as required
    print("🚀 Executing fetch_concurrently() with asyncio.gather()...")
    all_users, older_users = await fetch_concurrently()
    
    print()
    print("📊 RESULTS:")
    print(f"   Total users fetched: {len(all_users)}")
    print(f"   Users older than 40: {len(older_users)}")
    print()
    print("✅ Requirements successfully demonstrated!")


if __name__ == "__main__":
    # Use asyncio.run() as specified in the requirements
    asyncio.run(simple_demonstration())
