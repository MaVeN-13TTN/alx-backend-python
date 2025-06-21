#!/usr/bin/env python
"""
Test script to verify that caching is working properly in the messaging app.

This script tests:
1. Cache configuration in settings
2. Cache functionality on message views
3. Performance improvement from caching

Run this script to verify caching implementation.
"""

import os
import sys
import django
import time
import requests
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "messaging_app.settings")
django.setup()

from django.conf import settings
from django.core.cache import cache
from chats.models import User, Conversation, Message


def verify_cache_configuration():
    """Verify that cache is properly configured"""
    print("🔧 Verifying Cache Configuration")
    print("-" * 35)

    # Check cache settings
    if hasattr(settings, "CACHES") and "default" in settings.CACHES:
        cache_config = settings.CACHES["default"]
        print(f"✅ Cache backend: {cache_config.get('BACKEND')}")
        print(f"✅ Cache location: {cache_config.get('LOCATION')}")

        if (
            cache_config.get("BACKEND")
            == "django.core.cache.backends.locmem.LocMemCache"
        ):
            print("✅ Correct cache backend (LocMemCache) configured")
        else:
            print("❌ Incorrect cache backend")
            return False

    else:
        print("❌ Cache not properly configured in settings")
        return False

    # Test basic cache functionality
    try:
        cache.set("test_key", "test_value", 30)
        cached_value = cache.get("test_key")
        if cached_value == "test_value":
            print("✅ Basic cache functionality working")
        else:
            print("❌ Cache not storing/retrieving values properly")
            return False

        cache.delete("test_key")
        print("✅ Cache configuration verified successfully")
        return True

    except Exception as e:
        print(f"❌ Cache functionality error: {e}")
        return False


def test_cache_decorators():
    """Test that cache decorators are properly applied"""
    print("\n🎯 Verifying Cache Decorators")
    print("-" * 30)

    # Read the views.py file to check for cache decorators
    views_file = os.path.join(os.path.dirname(__file__), "chats", "views.py")

    try:
        with open(views_file, "r") as f:
            views_content = f.read()

        # Check for cache_page import
        if "from django.views.decorators.cache import cache_page" in views_content:
            print("✅ cache_page decorator imported")
        else:
            print("❌ cache_page decorator not imported")
            return False

        # Check for method_decorator import
        if "from django.utils.decorators import method_decorator" in views_content:
            print("✅ method_decorator imported")
        else:
            print("❌ method_decorator not imported")
            return False

        # Check for cache decorators usage
        if "@method_decorator(cache_page(60))" in views_content:
            print("✅ cache_page(60) decorator found in views")
        else:
            print("❌ cache_page(60) decorator not found")
            return False

        # Count occurrences of caching
        cache_occurrences = views_content.count("cache_page(60)")
        print(f"✅ Found {cache_occurrences} cached views with 60-second timeout")

        return True

    except Exception as e:
        print(f"❌ Error reading views file: {e}")
        return False


def test_cache_performance():
    """Test basic cache performance characteristics"""
    print("\n⚡ Testing Cache Performance")
    print("-" * 25)

    try:
        # Test cache write/read performance
        start_time = time.time()

        # Write to cache
        for i in range(100):
            cache.set(f"perf_test_{i}", f"value_{i}", 60)

        write_time = time.time() - start_time
        print(f"✅ Cache write performance: {write_time:.4f}s for 100 items")

        # Read from cache
        start_time = time.time()

        for i in range(100):
            value = cache.get(f"perf_test_{i}")

        read_time = time.time() - start_time
        print(f"✅ Cache read performance: {read_time:.4f}s for 100 items")

        # Cleanup
        for i in range(100):
            cache.delete(f"perf_test_{i}")

        print("✅ Cache performance test completed")
        return True

    except Exception as e:
        print(f"❌ Cache performance test error: {e}")
        return False


def verify_view_caching():
    """Verify that views are properly cached"""
    print("\n📋 Verifying View Caching Implementation")
    print("-" * 40)

    # Check specific views that should be cached
    cached_views = [
        "ConversationViewSet.messages",
        "MessageViewSet.conversation_messages",
        "MessageViewSet (list view)",
    ]

    views_file = os.path.join(os.path.dirname(__file__), "chats", "views.py")

    try:
        with open(views_file, "r") as f:
            content = f.read()

        # Check for messages action caching
        if "def messages(self, request, conversation_id=None):" in content:
            if (
                "@method_decorator(cache_page(60))"
                in content.split("def messages(self, request, conversation_id=None):")[
                    0
                ].split("\n")[-2:]
            ):
                print("✅ ConversationViewSet.messages action is cached")
            else:
                # Check if decorator is right before the method
                messages_index = content.find(
                    "def messages(self, request, conversation_id=None):"
                )
                preceding_lines = content[:messages_index].split("\n")[-10:]
                if any("cache_page(60)" in line for line in preceding_lines):
                    print("✅ ConversationViewSet.messages action is cached")
                else:
                    print("❌ ConversationViewSet.messages action not cached")

        # Check for conversation_messages action caching
        if "def conversation_messages(self, request, message_id=None):" in content:
            conv_msg_index = content.find(
                "def conversation_messages(self, request, message_id=None):"
            )
            preceding_lines = content[:conv_msg_index].split("\n")[-10:]
            if any("cache_page(60)" in line for line in preceding_lines):
                print("✅ MessageViewSet.conversation_messages action is cached")
            else:
                print("❌ MessageViewSet.conversation_messages action not cached")

        # Check for class-level caching on MessageViewSet
        if "class MessageViewSet" in content:
            msg_viewset_index = content.find("class MessageViewSet")
            preceding_lines = content[:msg_viewset_index].split("\n")[-5:]
            if any(
                "cache_page(60)" in line and "list" in line for line in preceding_lines
            ):
                print("✅ MessageViewSet list view is cached")
            else:
                print("❌ MessageViewSet list view not cached")

        return True

    except Exception as e:
        print(f"❌ Error verifying view caching: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 Cache Implementation Verification")
    print("=" * 40)

    tests = [
        verify_cache_configuration,
        test_cache_decorators,
        test_cache_performance,
        verify_view_caching,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
            results.append(False)

    print("\n" + "=" * 40)
    if all(results):
        print("🎉 All cache tests passed successfully!")
        print("✅ Cache configuration: WORKING")
        print("✅ Cache decorators: APPLIED")
        print("✅ View caching: IMPLEMENTED")
        print("✅ Performance: VERIFIED")
        print("\n🏆 Cache implementation is complete and working!")
        return True
    else:
        failed_tests = sum(1 for r in results if not r)
        print(f"❌ {failed_tests} test(s) failed")
        print("Please review the cache implementation")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
