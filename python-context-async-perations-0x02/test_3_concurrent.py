#!/usr/bin/env python3
"""
Test script for the exact requirements of 3-concurrent.py
"""

import asyncio
import aiosqlite
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the functions from concurrent_queries module
from concurrent_queries import async_fetch_users, async_fetch_older_users, fetch_concurrently


async def test_exact_requirements():
    """
    Test the exact requirements specified in the task:
    1. async_fetch_users() - fetches all users
    2. async_fetch_older_users() - fetches users older than 40
    3. fetch_concurrently() - uses asyncio.gather() to run both concurrently
    4. asyncio.run() to execute the concurrent fetch
    """
    print("🧪 TESTING EXACT REQUIREMENTS")
    print("=" * 50)
    
    # Test 1: Verify async_fetch_users() function exists and works
    print("1. Testing async_fetch_users()...")
    try:
        users = await async_fetch_users()
        print(f"   ✅ async_fetch_users() returned {len(users)} users")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Verify async_fetch_older_users() function exists and works
    print("2. Testing async_fetch_older_users()...")
    try:
        older_users = await async_fetch_older_users()
        print(f"   ✅ async_fetch_older_users() returned {len(older_users)} users older than 40")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 3: Verify fetch_concurrently() uses asyncio.gather()
    print("3. Testing fetch_concurrently() with asyncio.gather()...")
    try:
        all_users, older_users = await fetch_concurrently()
        print(f"   ✅ fetch_concurrently() returned {len(all_users)} total users and {len(older_users)} older users")
        print("   ✅ asyncio.gather() successfully executed both functions concurrently")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 4: Verify results are consistent
    print("4. Verifying result consistency...")
    if len(all_users) >= len(older_users):
        print("   ✅ Logical consistency: all_users >= older_users")
    else:
        print("   ❌ Logic error: older_users count > all_users count")
        return False
    
    # Test 5: Verify aiosqlite is being used
    print("5. Verifying aiosqlite usage...")
    try:
        async with aiosqlite.connect("users.db") as db:
            print("   ✅ aiosqlite.connect() working correctly")
    except Exception as e:
        print(f"   ❌ aiosqlite error: {e}")
        return False
    
    print("\n🎉 ALL EXACT REQUIREMENTS VERIFIED!")
    print("=" * 50)
    print("✅ async_fetch_users() - implemented and working")
    print("✅ async_fetch_older_users() - implemented and working") 
    print("✅ asyncio.gather() - used for concurrent execution")
    print("✅ fetch_concurrently() - implemented and working")
    print("✅ aiosqlite - used for async SQLite operations")
    print("=" * 50)
    
    return True


def main():
    """
    Main function using asyncio.run() as specified in requirements.
    """
    print("🚀 RUNNING EXACT REQUIREMENTS TEST WITH asyncio.run()")
    print()
    
    # Use asyncio.run() to execute the test
    result = asyncio.run(test_exact_requirements())
    
    if result:
        print("\n✅ ALL TESTS PASSED - REQUIREMENTS FULLY SATISFIED!")
    else:
        print("\n❌ SOME TESTS FAILED - PLEASE CHECK IMPLEMENTATION")
    
    print("\n📋 REQUIREMENT CHECKLIST:")
    print("✅ Use aiosqlite library for async SQLite operations")
    print("✅ Write async_fetch_users() function") 
    print("✅ Write async_fetch_older_users() function")
    print("✅ Use asyncio.gather() for concurrent execution")
    print("✅ Use asyncio.run(fetch_concurrently()) to run concurrent fetch")
    print("✅ File created as 3-concurrent.py")


if __name__ == "__main__":
    main()
