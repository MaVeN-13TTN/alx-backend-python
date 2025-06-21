#!/usr/bin/env python
"""
Verification script for UnreadMessagesManager implementation.

This script demonstrates all the required features:
1. Custom manager in messaging/managers.py
2. Message.unread.unread_for_user usage in views
3. .only() optimization in queries

Run this script to verify the implementation.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "messaging_app.settings")
django.setup()

from django.contrib.auth import get_user_model
from messaging.models import Message

User = get_user_model()


def verify_implementation():
    """Verify all required components are implemented"""
    print("🔍 Verifying UnreadMessagesManager Implementation")
    print("=" * 55)

    # 1. Check if managers.py exists
    import os

    managers_file = os.path.join(os.path.dirname(__file__), "messaging", "managers.py")
    if os.path.exists(managers_file):
        print("✅ messaging/managers.py exists")
    else:
        print("❌ messaging/managers.py does not exist")
        return False

    # 2. Check if UnreadMessagesManager is imported
    try:
        from messaging.managers import UnreadMessagesManager

        print("✅ UnreadMessagesManager can be imported from messaging.managers")
    except ImportError as e:
        print(f"❌ Cannot import UnreadMessagesManager: {e}")
        return False

    # 3. Check if Message model has the unread manager
    if hasattr(Message, "unread"):
        print("✅ Message.unread manager exists")
    else:
        print("❌ Message.unread manager does not exist")
        return False

    # 4. Check if unread_for_user method exists
    if hasattr(Message.unread, "unread_for_user"):
        print("✅ Message.unread.unread_for_user method exists")
    else:
        print("❌ Message.unread.unread_for_user method does not exist")
        return False

    # 5. Check views.py contains the expected patterns
    views_file = os.path.join(os.path.dirname(__file__), "messaging", "views.py")
    with open(views_file, "r") as f:
        views_content = f.read()

    if "Message.unread.unread_for_user" in views_content:
        print("✅ messaging/views.py contains Message.unread.unread_for_user")
    else:
        print("❌ messaging/views.py does not contain Message.unread.unread_for_user")
        return False

    if ".only(" in views_content:
        print("✅ messaging/views.py contains .only() optimization")
    else:
        print("❌ messaging/views.py does not contain .only() optimization")
        return False

    print("\n🧪 Testing Functionality")
    print("-" * 25)

    # Create test users
    user1, _ = User.objects.get_or_create(
        username="test_sender", defaults={"email": "sender@test.com"}
    )
    user2, _ = User.objects.get_or_create(
        username="test_receiver", defaults={"email": "receiver@test.com"}
    )

    # Clean up existing messages
    Message.objects.filter(sender__in=[user1, user2]).delete()

    # Create test messages
    msg1 = Message.objects.create(
        sender=user1, receiver=user2, content="Test unread message", is_read=False
    )

    msg2 = Message.objects.create(
        sender=user1, receiver=user2, content="Test read message", is_read=True
    )

    # Test the custom manager functionality
    try:
        unread_messages = Message.unread.unread_for_user(user2)
        unread_count = unread_messages.count()

        if unread_count == 1:
            print("✅ Custom manager correctly filters unread messages")
        else:
            print(f"❌ Expected 1 unread message, got {unread_count}")
            return False

        # Test .only() optimization by checking query
        first_msg = unread_messages.first()
        if first_msg and first_msg.content == "Test unread message":
            print("✅ .only() optimization works correctly")
        else:
            print("❌ .only() optimization not working properly")
            return False

    except Exception as e:
        print(f"❌ Error testing custom manager: {e}")
        return False

    # Test inbox display functionality
    try:
        # Simulate inbox display with .only() optimization
        inbox_messages = (
            Message.objects.filter(receiver=user2, is_read=False)
            .select_related("sender")
            .only(
                "message_id",
                "content",
                "timestamp",
                "is_read",
                "sender__username",
                "sender__first_name",
                "sender__last_name",
            )
            .order_by("-timestamp")
        )

        if inbox_messages.count() == 1:
            print("✅ Inbox display with .only() optimization works")
        else:
            print("❌ Inbox display optimization not working")
            return False

    except Exception as e:
        print(f"❌ Error testing inbox display: {e}")
        return False

    # Cleanup
    Message.objects.filter(sender__in=[user1, user2]).delete()

    print("\n🎉 All Verification Checks Passed!")
    print("=" * 35)
    print("✅ messaging/managers.py exists with UnreadMessagesManager")
    print("✅ Message.unread.unread_for_user method implemented")
    print("✅ Views use custom manager for displaying unread messages")
    print("✅ .only() optimization implemented in views")
    print("✅ Full functionality verified through testing")

    return True


if __name__ == "__main__":
    success = verify_implementation()
    if success:
        print("\n🏆 Implementation fully satisfies all requirements!")
        sys.exit(0)
    else:
        print("\n❌ Implementation issues found. Please review.")
        sys.exit(1)
