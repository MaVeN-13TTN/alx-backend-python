#!/usr/bin/env python
"""
Demonstration script for the Threaded Messaging System

This script demonstrates the key features of the threaded messaging system:
1. Creating messages and replies
2. Retrieving threaded conversations
3. Using ORM optimizations
4. Working with notifications and edit history

Run this script with: python manage.py shell < demo_threading.py
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "messaging_app.settings")
django.setup()

from django.contrib.auth import get_user_model
from messaging.models import Message, Notification, MessageHistory

User = get_user_model()


def create_demo_users():
    """Create demo users for the demonstration"""
    print("🔧 Setting up demo users...")

    # Create users
    alice, _ = User.objects.get_or_create(
        username="alice",
        defaults={
            "email": "alice@example.com",
            "first_name": "Alice",
            "last_name": "Smith",
        },
    )

    bob, _ = User.objects.get_or_create(
        username="bob",
        defaults={
            "email": "bob@example.com",
            "first_name": "Bob",
            "last_name": "Johnson",
        },
    )

    charlie, _ = User.objects.get_or_create(
        username="charlie",
        defaults={
            "email": "charlie@example.com",
            "first_name": "Charlie",
            "last_name": "Brown",
        },
    )

    print(f"✅ Created users: {alice.username}, {bob.username}, {charlie.username}")
    return alice, bob, charlie


def demonstrate_basic_messaging(alice, bob):
    """Demonstrate basic message creation"""
    print("\n📨 Creating basic messages...")

    # Create a root message
    message1 = Message.objects.create(
        sender=alice, receiver=bob, content="Hey Bob! How's the project going?"
    )

    print(f"✅ Created message: {message1.content[:30]}...")
    print(f"   └─ ID: {message1.message_id}")
    print(f"   └─ Is thread starter: {message1.is_thread_starter}")
    print(f"   └─ Thread depth: {message1.thread_depth}")

    return message1


def demonstrate_threaded_replies(alice, bob, charlie, root_message):
    """Demonstrate threaded conversation creation"""
    print("\n🧵 Creating threaded conversation...")

    # Bob replies to Alice
    reply1 = Message.objects.create(
        sender=bob,
        receiver=alice,
        content="It's going well! We're ahead of schedule.",
        parent_message=root_message,
    )

    # Alice replies to Bob's reply
    reply2 = Message.objects.create(
        sender=alice,
        receiver=bob,
        content="That's great to hear! What about the testing phase?",
        parent_message=reply1,
    )

    # Charlie joins the conversation
    reply3 = Message.objects.create(
        sender=charlie,
        receiver=alice,
        content="I can help with testing if needed!",
        parent_message=root_message,
    )

    # Bob responds to Charlie
    reply4 = Message.objects.create(
        sender=bob,
        receiver=charlie,
        content="That would be awesome, Charlie! Let's coordinate.",
        parent_message=reply3,
    )

    print(f"✅ Created {4} replies in the thread")

    # Display thread structure
    print("\n📊 Thread structure:")
    all_messages = [root_message, reply1, reply2, reply3, reply4]

    for msg in all_messages:
        indent = "   " * msg.thread_depth
        print(
            f"{indent}├─ {msg.sender.username} → {msg.receiver.username}: {msg.content[:40]}..."
        )
        print(f"{indent}   └─ Depth: {msg.thread_depth}, Is reply: {msg.is_reply}")

    return reply1, reply2, reply3, reply4


def demonstrate_thread_retrieval(root_message):
    """Demonstrate efficient thread retrieval"""
    print("\n🔍 Retrieving thread data...")

    # Get all messages in the thread
    thread_messages = root_message.get_thread_messages()
    print(f"✅ Thread contains {thread_messages.count()} messages")

    # Get all replies to root message
    all_replies = root_message.get_all_replies()
    print(f"✅ Root message has {all_replies.count()} total replies")

    # Get only direct replies to root message
    direct_replies = root_message.get_direct_replies()
    print(f"✅ Root message has {direct_replies.count()} direct replies")

    # Show reply count
    print(f"✅ Reply count: {root_message.get_reply_count()}")

    return thread_messages


def demonstrate_permissions(alice, bob, charlie, root_message):
    """Demonstrate permission checking"""
    print("\n🔐 Testing permissions...")

    print(f"Can Alice reply to root message? {root_message.can_reply_to(alice)}")
    print(f"Can Bob reply to root message? {root_message.can_reply_to(bob)}")
    print(f"Can Charlie reply to root message? {root_message.can_reply_to(charlie)}")


def demonstrate_notifications(alice, bob):
    """Demonstrate notification system"""
    print("\n🔔 Checking notifications...")

    # Get notifications for Bob (he should have received notification for Alice's message)
    bob_notifications = Notification.objects.filter(user=bob)
    print(f"✅ Bob has {bob_notifications.count()} notifications")

    for notification in bob_notifications:
        print(f"   └─ {notification.title}: {notification.content[:40]}...")

    # Get notifications for Alice
    alice_notifications = Notification.objects.filter(user=alice)
    print(f"✅ Alice has {alice_notifications.count()} notifications")


def demonstrate_edit_history(root_message):
    """Demonstrate message editing and history"""
    print("\n📝 Demonstrating message editing...")

    original_content = root_message.content
    print(f"Original content: {original_content}")

    # Edit the message
    root_message.content = "Hey Bob! How's the project going? Any updates?"
    root_message.save()

    print(f"Updated content: {root_message.content}")
    print(f"Message is edited: {root_message.edited}")
    print(f"Edit count: {root_message.edit_count}")

    # Check edit history
    edit_history = root_message.edit_history.all()
    print(f"✅ Message has {edit_history.count()} edit history entries")

    for history in edit_history:
        print(f"   └─ Edit by {history.edited_by.username} at {history.edited_at}")
        print(f"      └─ {history.edit_summary}")


def demonstrate_orm_optimization(root_message):
    """Demonstrate ORM query optimization"""
    print("\n⚡ Demonstrating ORM optimizations...")

    from django.db import connection
    from django.test.utils import override_settings

    # Reset query count
    connection.queries_log.clear()

    # Get thread messages with optimization
    thread_messages = list(root_message.get_thread_messages())

    # Access related fields (this should not cause additional queries due to select_related)
    for msg in thread_messages:
        _ = msg.sender.username
        _ = msg.receiver.username
        if msg.parent_message:
            _ = msg.parent_message.content

    query_count = len(connection.queries)
    print(
        f"✅ Retrieved {len(thread_messages)} messages with {query_count} database queries"
    )
    print("   └─ Optimized with select_related and prefetch_related")


def demonstrate_cleanup():
    """Demonstrate data cleanup"""
    print("\n🧹 Data cleanup demonstration...")

    # Count current data
    message_count = Message.objects.count()
    notification_count = Notification.objects.count()
    history_count = MessageHistory.objects.count()

    print(
        f"Current data: {message_count} messages, {notification_count} notifications, {history_count} histories"
    )
    print(
        "Note: User deletion would automatically clean up all related data via signals"
    )


def main():
    """Main demonstration function"""
    print("=" * 60)
    print("🚀 THREADED MESSAGING SYSTEM DEMONSTRATION")
    print("=" * 60)

    try:
        # Setup
        alice, bob, charlie = create_demo_users()

        # Basic messaging
        root_message = demonstrate_basic_messaging(alice, bob)

        # Threaded replies
        replies = demonstrate_threaded_replies(alice, bob, charlie, root_message)

        # Thread retrieval
        thread_messages = demonstrate_thread_retrieval(root_message)

        # Permissions
        demonstrate_permissions(alice, bob, charlie, root_message)

        # Notifications
        demonstrate_notifications(alice, bob)

        # Edit history
        demonstrate_edit_history(root_message)

        # ORM optimization
        demonstrate_orm_optimization(root_message)

        # Cleanup info
        demonstrate_cleanup()

        print("\n" + "=" * 60)
        print("✅ DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)

        print("\n📚 Key Features Demonstrated:")
        print("   ✓ Threaded conversation creation")
        print("   ✓ Efficient thread retrieval with ORM optimization")
        print("   ✓ Permission-based reply system")
        print("   ✓ Automatic notification generation")
        print("   ✓ Message edit history tracking")
        print("   ✓ Database query optimization")
        print("   ✓ Comprehensive data relationships")

    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
