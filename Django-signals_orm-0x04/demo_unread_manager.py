#!/usr/bin/env python
"""
Demonstration script for the UnreadMessagesManager custom manager.

This script shows how to use the custom manager to filter unread messages
for a user with query optimization using .only() and select_related().
"""

import os
import sys
import django
from django.db import connection

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "messaging_app.settings")
django.setup()

from django.contrib.auth import get_user_model
from messaging.models import Message

User = get_user_model()


def reset_db_queries():
    """Reset the query counter"""
    connection.queries_log.clear()


def print_query_count(action_name):
    """Print the number of database queries executed"""
    query_count = len(connection.queries)
    print(f"✓ {action_name}: {query_count} database queries")


def main():
    """Main demonstration function"""
    print("🚀 UnreadMessagesManager Demonstration")
    print("=" * 50)

    # Create test users
    user1, created = User.objects.get_or_create(
        username="demo_sender",
        defaults={
            "email": "sender@example.com",
            "first_name": "Demo",
            "last_name": "Sender",
        },
    )
    user2, created = User.objects.get_or_create(
        username="demo_receiver",
        defaults={
            "email": "receiver@example.com",
            "first_name": "Demo",
            "last_name": "Receiver",
        },
    )

    print(f"👥 Users: {user1.username} and {user2.username}")

    # Clean up any existing messages for demo
    Message.objects.filter(sender__in=[user1, user2]).delete()

    # Create some test messages
    print("\n📝 Creating test messages...")

    # Create unread messages
    msg1 = Message.objects.create(
        sender=user1,
        receiver=user2,
        content="Hello! This is an unread message #1",
        is_read=False,
    )

    msg2 = Message.objects.create(
        sender=user1,
        receiver=user2,
        content="Hello! This is an unread message #2",
        is_read=False,
    )

    # Create a read message
    msg3 = Message.objects.create(
        sender=user1, receiver=user2, content="This message has been read", is_read=True
    )

    # Create message for different user
    msg4 = Message.objects.create(
        sender=user2,
        receiver=user1,
        content="Message from user2 to user1",
        is_read=False,
    )

    print(f"✓ Created {Message.objects.count()} total messages")
    print(
        f"✓ Unread messages for {user2.username}: {Message.objects.filter(receiver=user2, is_read=False).count()}"
    )

    print("\n🔍 Testing UnreadMessagesManager Methods")
    print("-" * 40)

    # Test 1: for_user method
    reset_db_queries()
    unread_messages = Message.unread_messages.for_user(user2)
    print(f"\n1. for_user({user2.username}):")
    print(f"   Found {unread_messages.count()} unread messages")
    print_query_count("for_user query")

    # Show which fields are loaded
    if unread_messages.exists():
        first_msg = unread_messages.first()
        print(f"   First message: '{first_msg.content[:30]}...'")
        print(
            f"   Sender: {first_msg.sender.username} ({first_msg.sender.first_name} {first_msg.sender.last_name})"
        )
        print(f"   Timestamp: {first_msg.timestamp}")

    # Test 2: inbox_for_user method
    reset_db_queries()
    inbox_messages = Message.unread_messages.inbox_for_user(user2)
    print(f"\n2. inbox_for_user({user2.username}):")
    print(f"   Found {inbox_messages.count()} unread messages in inbox")
    print_query_count("inbox_for_user query")

    # Test 3: unread_count_for_user method
    reset_db_queries()
    unread_count = Message.unread_messages.unread_count_for_user(user2)
    print(f"\n3. unread_count_for_user({user2.username}):")
    print(f"   Unread count: {unread_count}")
    print_query_count("unread_count_for_user query")

    # Test 4: unread_threads_for_user method
    reset_db_queries()
    unread_threads = Message.unread_messages.unread_threads_for_user(user2)
    print(f"\n4. unread_threads_for_user({user2.username}):")
    print(f"   Found {unread_threads.count()} unread thread starters")
    print_query_count("unread_threads_for_user query")

    # Test query optimization
    print("\n⚡ Query Optimization Demonstration")
    print("-" * 40)

    # Show optimized query with .only()
    reset_db_queries()
    optimized_messages = Message.unread_messages.for_user(user2)
    list(optimized_messages)  # Force evaluation
    optimized_queries = len(connection.queries)

    # Compare with naive query (without optimization)
    reset_db_queries()
    naive_messages = Message.objects.filter(receiver=user2, is_read=False)
    list(naive_messages)  # Force evaluation
    naive_queries = len(connection.queries)

    print(
        f"Optimized query (with .only() and select_related): {optimized_queries} queries"
    )
    print(f"Naive query (without optimization): {naive_queries} queries")

    if optimized_queries <= naive_queries:
        print("✓ Query optimization is working effectively!")
    else:
        print("⚠ Query optimization might need review")

    # Show the actual SQL generated
    print("\n📊 SQL Query Analysis")
    print("-" * 30)

    reset_db_queries()
    queryset = Message.unread_messages.for_user(user2)

    print("Generated SQL:")
    print(str(queryset.query))

    # Test marking messages as read
    print("\n📨 Testing Message Read Status")
    print("-" * 35)

    print(
        f"Before marking as read: {Message.unread_messages.unread_count_for_user(user2)} unread"
    )

    # Mark first message as read
    first_unread = Message.unread_messages.for_user(user2).first()
    if first_unread:
        first_unread.is_read = True
        first_unread.save()
        print(f"Marked message '{first_unread.content[:30]}...' as read")

    print(
        f"After marking as read: {Message.unread_messages.unread_count_for_user(user2)} unread"
    )

    print("\n🎉 Demonstration completed successfully!")
    print("=" * 50)

    # Cleanup (optional)
    print("\n🧹 Cleaning up test data...")
    Message.objects.filter(sender__in=[user1, user2]).delete()
    print("✓ Test messages cleaned up")


if __name__ == "__main__":
    main()
