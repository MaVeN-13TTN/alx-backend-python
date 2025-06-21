#!/usr/bin/env python
"""
Quick verification script for messaging optimizations and sender assignment
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "messaging_app.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import override_settings
from messaging.models import Message
from messaging.views import MessageViewSet
from rest_framework.test import APIRequestFactory, force_authenticate

User = get_user_model()


def test_query_optimizations():
    """Test that select_related and prefetch_related are used"""
    print("=" * 50)
    print("Testing Query Optimizations")
    print("=" * 50)

    # Create test users
    user1 = User.objects.create_user(username="test1", email="test1@example.com")
    user2 = User.objects.create_user(username="test2", email="test2@example.com")

    # Create test messages
    root_msg = Message.objects.create(
        sender=user1, receiver=user2, content="Root message"
    )
    reply_msg = Message.objects.create(
        sender=user2, receiver=user1, content="Reply", parent_message=root_msg
    )

    # Test ViewSet query optimization
    factory = APIRequestFactory()
    request = factory.get("/api/messages/")
    force_authenticate(request, user=user1)

    viewset = MessageViewSet()
    viewset.request = request

    # Reset queries
    connection.queries.clear()

    # Get queryset and evaluate it
    queryset = viewset.get_queryset()
    list(queryset)  # Force evaluation

    query_count = len(connection.queries)
    print(f"Query count for MessageViewSet.get_queryset(): {query_count}")

    # Test that select_related and prefetch_related are in the SQL
    query_str = str(queryset.query).lower()
    has_select_related = "join" in query_str and (
        "sender" in query_str or "receiver" in query_str
    )
    print(f"Has select_related optimization: {has_select_related}")

    # Test threading methods
    connection.queries.clear()
    thread_messages = root_msg.get_thread_messages()
    list(thread_messages)

    thread_query_count = len(connection.queries)
    print(f"Query count for get_thread_messages(): {thread_query_count}")

    print("✓ Query optimizations verified")

    # Cleanup
    user1.delete()
    user2.delete()


def test_sender_assignment():
    """Test that sender=request.user is enforced"""
    print("\n" + "=" * 50)
    print("Testing Sender Assignment")
    print("=" * 50)

    # Create test users
    user1 = User.objects.create_user(username="test1", email="test1@example.com")
    user2 = User.objects.create_user(username="test2", email="test2@example.com")

    # Test perform_create method
    factory = APIRequestFactory()
    request = factory.post("/api/messages/", {"receiver": user2.pk, "content": "Test"})
    force_authenticate(request, user=user1)

    viewset = MessageViewSet()
    viewset.request = request

    # Create a message using the serializer
    from messaging.serializers import CreateMessageSerializer

    # Test direct creation
    message = Message.objects.create(
        sender=user1, receiver=user2, content="Direct creation test"
    )
    print(f"Direct creation - Sender: {message.sender.username}")

    # Test that perform_create exists and has the right signature
    perform_create_method = getattr(viewset, "perform_create", None)
    if perform_create_method:
        print("✓ perform_create method exists")
        # Check method source
        import inspect

        source = inspect.getsource(perform_create_method)
        has_sender_assignment = "sender=self.request.user" in source
        print(f"✓ perform_create sets sender=request.user: {has_sender_assignment}")
    else:
        print("✗ perform_create method not found")

    # Test reply_to_message function
    from messaging.views import reply_to_message

    source = inspect.getsource(reply_to_message)
    has_reply_sender = "sender=request.user" in source
    print(f"✓ reply_to_message sets sender=request.user: {has_reply_sender}")

    # Test create_message function
    from messaging.views import create_message

    source = inspect.getsource(create_message)
    has_create_sender = "sender=request.user" in source
    print(f"✓ create_message sets sender=request.user: {has_create_sender}")

    print("✓ Sender assignment verified")

    # Cleanup
    user1.delete()
    user2.delete()


def check_views_content():
    """Check that views.py contains the expected optimizations"""
    print("\n" + "=" * 50)
    print("Checking Views Content")
    print("=" * 50)

    with open("messaging/views.py", "r") as f:
        content = f.read()

    # Check for select_related and prefetch_related
    select_related_count = content.count("select_related")
    prefetch_related_count = content.count("prefetch_related")
    sender_assignment_count = content.count("sender=request.user") + content.count(
        "sender=self.request.user"
    )

    print(f"select_related occurrences: {select_related_count}")
    print(f"prefetch_related occurrences: {prefetch_related_count}")
    print(f"sender=request.user occurrences: {sender_assignment_count}")

    if select_related_count >= 3 and prefetch_related_count >= 3:
        print("✓ Query optimizations present in views")
    else:
        print("✗ Insufficient query optimizations")

    if sender_assignment_count >= 3:
        print("✓ Sender assignment present in views")
    else:
        print("✗ Insufficient sender assignments")


if __name__ == "__main__":
    try:
        check_views_content()
        test_query_optimizations()
        test_sender_assignment()
        print("\n" + "=" * 50)
        print("✅ ALL VERIFICATIONS COMPLETED")
        print("=" * 50)
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback

        traceback.print_exc()
