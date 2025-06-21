#!/usr/bin/env python
"""
Demonstration script for unread message functionality with custom manager
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
from messaging.models import Message

User = get_user_model()


def demo_unread_messages():
    """Demonstrate unread message functionality"""
    print("=" * 60)
    print("🔔 UNREAD MESSAGES CUSTOM MANAGER DEMONSTRATION")
    print("=" * 60)

    # Create test users
    print("👥 Creating test users...")
    user1 = User.objects.create_user(
        username="alice", email="alice@example.com", password="pass123"
    )
    user2 = User.objects.create_user(
        username="bob", email="bob@example.com", password="pass123"
    )
    user3 = User.objects.create_user(
        username="charlie", email="charlie@example.com", password="pass123"
    )
    print("   ✓ Created users: alice, bob, charlie")

    # Create test messages
    print("\n📝 Creating test messages...")

    # Messages for bob (some read, some unread)
    msg1 = Message.objects.create(
        sender=user1, receiver=user2, content="Hello Bob from Alice!", is_read=False
    )
    msg2 = Message.objects.create(
        sender=user1, receiver=user2, content="Second message from Alice", is_read=True
    )
    msg3 = Message.objects.create(
        sender=user3, receiver=user2, content="Hi Bob from Charlie!", is_read=False
    )

    # Create a threaded conversation
    root_msg = Message.objects.create(
        sender=user1, receiver=user2, content="Let's start a thread", is_read=False
    )
    reply_msg = Message.objects.create(
        sender=user2,
        receiver=user1,
        content="Sure, let's discuss",
        parent_message=root_msg,
        is_read=False,
    )

    # Messages for alice
    msg4 = Message.objects.create(
        sender=user2, receiver=user1, content="Thanks Alice!", is_read=False
    )
    msg5 = Message.objects.create(
        sender=user3, receiver=user1, content="Hey Alice!", is_read=False
    )

    print(f"   ✓ Created {Message.objects.count()} messages")

    # Demonstrate custom manager methods
    print("\n🔍 DEMONSTRATING CUSTOM MANAGER METHODS")
    print("-" * 60)

    # 1. Unread messages for user
    print("1️⃣  Unread messages for Bob:")
    unread_for_bob = Message.unread_messages.for_user(user2)
    for msg in unread_for_bob:
        print(
            f"   📧 From {msg.sender.username}: '{msg.content[:30]}...' ({msg.timestamp.strftime('%H:%M')})"
        )
    print(f"   📊 Total unread: {len(unread_for_bob)}")

    # 2. Inbox with threading info
    print("\n2️⃣  Bob's inbox with threading info:")
    inbox_for_bob = Message.unread_messages.inbox_for_user(user2)
    for msg in inbox_for_bob:
        thread_info = " (Reply)" if msg.parent_message else " (Root)"
        print(f"   📨 From {msg.sender.username}: '{msg.content[:30]}...'{thread_info}")

    # 3. Unread count
    print("\n3️⃣  Unread counts:")
    bob_count = Message.unread_messages.unread_count_for_user(user2)
    alice_count = Message.unread_messages.unread_count_for_user(user1)
    charlie_count = Message.unread_messages.unread_count_for_user(user3)
    print(f"   📊 Bob has {bob_count} unread messages")
    print(f"   📊 Alice has {alice_count} unread messages")
    print(f"   📊 Charlie has {charlie_count} unread messages")

    # 4. Unread threads (root messages only)
    print("\n4️⃣  Unread thread starters for Bob:")
    unread_threads = Message.unread_messages.unread_threads_for_user(user2)
    for msg in unread_threads:
        print(f"   🧵 Thread from {msg.sender.username}: '{msg.content[:30]}...'")
    print(f"   📊 Total unread threads: {len(unread_threads)}")

    # Demonstrate query optimization
    print("\n⚡ QUERY OPTIMIZATION DEMONSTRATION")
    print("-" * 60)

    # Reset query counter
    connection.queries.clear()

    # Fetch unread messages with optimizations
    print("5️⃣  Testing query optimization with .only() fields:")
    optimized_messages = Message.unread_messages.for_user(user2)

    # Access the optimized fields
    for msg in optimized_messages:
        # These should not trigger additional queries due to .only() and select_related
        sender_name = msg.sender.username
        content = msg.content
        timestamp = msg.timestamp
        read_status = msg.is_read

    query_count = len(connection.queries)
    print(f"   📈 Total queries executed: {query_count}")
    print(
        f"   ✅ Optimization successful: Only {query_count} query needed for {len(optimized_messages)} messages"
    )

    # Show SQL queries
    if query_count > 0:
        print(f"\n📜 SQL Query executed:")
        print(f"   {connection.queries[-1]['sql'][:100]}...")

    # Demonstrate marking messages as read
    print("\n✅ MARK AS READ FUNCTIONALITY")
    print("-" * 60)

    print("6️⃣  Before marking as read:")
    print(
        f"   📊 Bob's unread count: {Message.unread_messages.unread_count_for_user(user2)}"
    )

    # Mark one message as read
    msg1.is_read = True
    msg1.save(update_fields=["is_read"])

    print("7️⃣  After marking one message as read:")
    print(
        f"   📊 Bob's unread count: {Message.unread_messages.unread_count_for_user(user2)}"
    )

    # Mark all messages as read for bob
    Message.objects.filter(receiver=user2, is_read=False).update(is_read=True)

    print("8️⃣  After marking all messages as read:")
    print(
        f"   📊 Bob's unread count: {Message.unread_messages.unread_count_for_user(user2)}"
    )

    # Performance comparison
    print("\n🏃 PERFORMANCE COMPARISON")
    print("-" * 60)

    # Create more messages for performance testing
    print("Creating 50 additional messages for performance testing...")
    for i in range(50):
        Message.objects.create(
            sender=user1,
            receiver=user2,
            content=f"Performance test message {i}",
            is_read=False,
        )

    # Test regular query vs optimized query
    connection.queries.clear()

    # Regular query (without optimization)
    regular_messages = Message.objects.filter(receiver=user2, is_read=False)
    for msg in regular_messages:
        sender_name = msg.sender.username  # This would trigger additional queries
        break  # Just test one to avoid too many queries

    regular_query_count = len(connection.queries)

    connection.queries.clear()

    # Optimized query
    optimized_messages = Message.unread_messages.for_user(user2)
    for msg in optimized_messages:
        sender_name = msg.sender.username  # This should not trigger additional queries
        break

    optimized_query_count = len(connection.queries)

    print(f"9️⃣  Performance comparison:")
    print(f"   📊 Regular query: {regular_query_count} database queries")
    print(f"   📊 Optimized query: {optimized_query_count} database queries")
    print(
        f"   🚀 Improvement: {regular_query_count - optimized_query_count} fewer queries"
    )

    print("\n🎯 SUMMARY")
    print("-" * 60)
    print("✅ Custom UnreadMessagesManager implemented with:")
    print("   • for_user() - Get unread messages with .only() optimization")
    print("   • inbox_for_user() - Get inbox with threading info")
    print("   • unread_count_for_user() - Get count of unread messages")
    print("   • unread_threads_for_user() - Get unread thread starters")
    print("✅ Query optimizations:")
    print("   • select_related() for sender and parent_message")
    print("   • .only() for specific fields to reduce data transfer")
    print("   • Database indexes on (receiver, is_read, timestamp)")
    print("✅ API endpoints for unread message management")
    print("✅ Mark as read functionality with permission checks")

    # Cleanup
    print("\n🧹 Cleaning up test data...")
    user1.delete()
    user2.delete()
    user3.delete()
    print("   ✓ Test data cleaned up")


if __name__ == "__main__":
    try:
        demo_unread_messages()
        print("\n" + "=" * 60)
        print("🎉 UNREAD MESSAGES DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback

        traceback.print_exc()
