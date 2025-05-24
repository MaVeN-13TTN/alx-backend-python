#!/usr/bin/env python3
"""
Test cache_query decorator with other decorators and advanced scenarios
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


# Cache with TTL (Time To Live) enhancement
query_cache_with_ttl = {}


def cache_query_with_ttl(ttl_seconds=60):
    """Enhanced cache decorator with TTL support"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract query
            query = None
            if "query" in kwargs:
                query = kwargs["query"]
            elif len(args) >= 2 and isinstance(args[1], str):
                query = args[1]

            if not query:
                return func(*args, **kwargs)

            cache_key = " ".join(query.split()).upper()
            current_time = time.time()

            # Check if cached and not expired
            if cache_key in query_cache_with_ttl:
                cached_result, timestamp = query_cache_with_ttl[cache_key]
                if current_time - timestamp < ttl_seconds:
                    print(f"   ✓ Cache HIT (TTL) for: {query}")
                    return cached_result
                else:
                    print(f"   ⏰ Cache EXPIRED for: {query}")
                    del query_cache_with_ttl[cache_key]

            # Execute and cache with timestamp
            print(f"   ✗ Cache MISS (TTL) for: {query}")
            result = func(*args, **kwargs)
            query_cache_with_ttl[cache_key] = (result, current_time)

            return result

        return wrapper

    return decorator


# Simple cache decorator (original)
simple_cache = {}


def cache_query_simple(func):
    """Simple cache decorator for comparison"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = None
        if "query" in kwargs:
            query = kwargs["query"]
        elif len(args) >= 2 and isinstance(args[1], str):
            query = args[1]

        if not query:
            return func(*args, **kwargs)

        cache_key = " ".join(query.split()).upper()

        if cache_key in simple_cache:
            print(f"   ✓ Simple Cache HIT: {query}")
            return simple_cache[cache_key]

        print(f"   ✗ Simple Cache MISS: {query}")
        result = func(*args, **kwargs)
        simple_cache[cache_key] = result

        return result

    return wrapper


@with_db_connection
@cache_query_simple
def fetch_with_simple_cache(conn, query):
    """Function with simple caching"""
    cursor = conn.cursor()
    cursor.execute(query)
    time.sleep(0.05)  # Simulate work
    return cursor.fetchall()


@with_db_connection
@cache_query_with_ttl(ttl_seconds=2)
def fetch_with_ttl_cache(conn, query):
    """Function with TTL caching"""
    cursor = conn.cursor()
    cursor.execute(query)
    time.sleep(0.05)  # Simulate work
    return cursor.fetchall()


def show_cache_stats():
    """Display cache statistics"""
    print(f"   Simple cache entries: {len(simple_cache)}")
    print(f"   TTL cache entries: {len(query_cache_with_ttl)}")


if __name__ == "__main__":
    print("Advanced Cache Testing:\n")

    print("1. Test simple caching:")
    users1 = fetch_with_simple_cache(query="SELECT * FROM users")
    print(f"   Retrieved {len(users1)} users")

    users2 = fetch_with_simple_cache(query="SELECT * FROM users")
    print(f"   Retrieved {len(users2)} users (cached)")

    print("\n2. Test TTL caching:")
    users3 = fetch_with_ttl_cache(query="SELECT * FROM users")
    print(f"   Retrieved {len(users3)} users")

    users4 = fetch_with_ttl_cache(query="SELECT * FROM users")
    print(f"   Retrieved {len(users4)} users (cached)")

    print("\n3. Test cache expiration:")
    print("   Waiting 3 seconds for TTL cache to expire...")
    time.sleep(3)

    users5 = fetch_with_ttl_cache(query="SELECT * FROM users")
    print(f"   Retrieved {len(users5)} users (should be cache miss due to expiration)")

    print("\n4. Test different queries:")
    limited_users1 = fetch_with_simple_cache(query="SELECT * FROM users LIMIT 2")
    print(f"   Simple cache - Limited query: {len(limited_users1)} users")

    limited_users2 = fetch_with_ttl_cache(query="SELECT * FROM users LIMIT 2")
    print(f"   TTL cache - Limited query: {len(limited_users2)} users")

    print("\n5. Cache statistics:")
    show_cache_stats()

    print("\n6. Test cache behavior with identical queries:")
    for i in range(3):
        print(f"\n   Round {i+1}:")
        fetch_with_simple_cache(query="SELECT COUNT(*) FROM users")
        fetch_with_ttl_cache(query="SELECT COUNT(*) FROM users")

    print("\n7. Final cache statistics:")
    show_cache_stats()

    print("\nAdvanced cache testing completed!")
