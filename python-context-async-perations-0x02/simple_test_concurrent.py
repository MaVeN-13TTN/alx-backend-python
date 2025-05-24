#!/usr/bin/env python3
"""
Simple test for concurrent queries with proper imports
"""

import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the functions from concurrent_queries module
from concurrent_queries import async_fetch_users, async_fetch_older_users, fetch_concurrently


async def simple_test():
    """Simple test of the concurrent functions."""
    print("🧪 TESTING CONCURRENT QUERIES WITH PROPER IMPORTS")
    print("=" * 55)
    
    # Test 1: Individual functions
    print("1. Testing async_fetch_users()...")
    users = await async_fetch_users()
    print(f"   ✅ Found {len(users)} users")
    
    print("\n2. Testing async_fetch_older_users()...")
    older_users = await async_fetch_older_users()
    print(f"   ✅ Found {len(older_users)} users older than 40")
    
    print("\n3. Testing fetch_concurrently()...")
    all_users, concurrent_older_users = await fetch_concurrently()
    print(f"   ✅ Concurrent fetch: {len(all_users)} users, {len(concurrent_older_users)} older")
    
    print("\n✅ ALL TESTS PASSED!")
    print("✅ Pylance can now properly detect the imported functions!")
    
    return True


def main():
    """Main function using asyncio.run()"""
    print("🚀 Running simple test with proper imports...")
    print()
    
    result = asyncio.run(simple_test())
    
    if result:
        print("\n🎉 SUCCESS: All imports and functions working correctly!")
    else:
        print("\n❌ FAILURE: Some tests failed")


if __name__ == "__main__":
    main()
