#!/usr/bin/env python3
"""
Test file for the cache_query decorator
Demonstrates query result caching with various scenarios
"""

import time
import sqlite3
import functools


def with_db_connection(func):
    """Decorator that automatically handles opening and closing database connections."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")
        try:
            result = func(conn, *args, **kwargs)
            return result
        finally:
            conn.close()

    return wrapper


# Global cache dictionary
query_cache = {}


def cache_query(func):
    """Decorator that caches the results of database queries."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from function arguments
        query = None

        if "query" in kwargs:
            query = kwargs["query"]
        elif len(args) >= 2 and isinstance(args[1], str):
            query = args[1]
        else:
            for arg in args[1:]:
                if isinstance(arg, str) and (
                    "SELECT" in arg.upper()
                    or "INSERT" in arg.upper()
                    or "UPDATE" in arg.upper()
                    or "DELETE" in arg.upper()
                ):
                    query = arg
                    break

        if not query:
            return func(*args, **kwargs)

        # Create cache key
        cache_key = " ".join(query.split()).upper()

        # Check cache
        if cache_key in query_cache:
            print(f"   ✓ Cache HIT for: {query}")
            return query_cache[cache_key]

        # Execute and cache
        print(f"   ✗ Cache MISS for: {query}")
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time

        query_cache[cache_key] = result
        print(f"   ✓ Cached result (execution time: {execution_time:.3f}s)")

        return result

    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """Fetch users with caching enabled"""
    cursor = conn.cursor()
    cursor.execute(query)
    # Simulate some processing time
    time.sleep(0.1)
    return cursor.fetchall()


@with_db_connection
@cache_query
def fetch_user_by_id_with_cache(conn, user_id):
    """Fetch specific user by ID with caching"""
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor = conn.cursor()
    cursor.execute(query)
    time.sleep(0.05)  # Simulate processing
    return cursor.fetchone()


@with_db_connection
@cache_query
def count_users_with_cache(conn):
    """Count users with caching"""
    query = "SELECT COUNT(*) FROM users"
    cursor = conn.cursor()
    cursor.execute(query)
    time.sleep(0.02)  # Simulate processing
    return cursor.fetchone()[0]


def clear_cache():
    """Helper function to clear the cache"""
    global query_cache
    query_cache.clear()
    print("   Cache cleared")


if __name__ == "__main__":
    print("Testing cache_query decorator:\n")

    print("1. Test basic caching - same query multiple times:")
    print("   First call (should cache):")
    start = time.time()
    users1 = fetch_users_with_cache(query="SELECT * FROM users")
    time1 = time.time() - start
    print(f"   Retrieved {len(users1)} users in {time1:.3f}s")

    print("\n   Second call (should use cache):")
    start = time.time()
    users2 = fetch_users_with_cache(query="SELECT * FROM users")
    time2 = time.time() - start
    print(f"   Retrieved {len(users2)} users in {time2:.3f}s")

    print(f"\n   Speed improvement: {time1/time2:.1f}x faster!")
    print(f"   Results identical: {users1 == users2}")

    print("\n2. Test different queries (should not use cache):")
    users_limited = fetch_users_with_cache(query="SELECT * FROM users LIMIT 3")
    print(f"   Limited query retrieved {len(users_limited)} users")

    print("\n3. Test query normalization (whitespace differences):")
    print("   Query with extra spaces:")
    users3 = fetch_users_with_cache(query="SELECT  *   FROM   users")
    print("   Query with tabs and newlines:")
    users4 = fetch_users_with_cache(query="SELECT\t*\nFROM\tusers")
    print(f"   Both should use cache: {len(users3) == len(users4) == len(users1)}")

    print("\n4. Test parameterized queries:")
    user1 = fetch_user_by_id_with_cache(user_id=1)
    print(f"   User 1: {user1[1] if user1 else 'Not found'}")

    user1_again = fetch_user_by_id_with_cache(user_id=1)
    print(f"   User 1 again: {user1_again[1] if user1_again else 'Not found'}")

    user2 = fetch_user_by_id_with_cache(user_id=2)
    print(f"   User 2: {user2[1] if user2 else 'Not found'}")

    print("\n5. Test multiple function calls:")
    count1 = count_users_with_cache()
    print(f"   User count: {count1}")

    count2 = count_users_with_cache()
    print(f"   User count again: {count2}")

    print("\n6. Test cache state:")
    print(f"   Cache contains {len(query_cache)} entries:")
    for i, key in enumerate(query_cache.keys(), 1):
        # Show shortened version of cache keys
        short_key = key[:50] + "..." if len(key) > 50 else key
        print(f"   {i}. {short_key}")

    print("\n7. Test cache clearing:")
    clear_cache()
    print("   After clearing, same query should miss cache:")
    users_after_clear = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"   Retrieved {len(users_after_clear)} users")

    print("\nCache testing completed!")
