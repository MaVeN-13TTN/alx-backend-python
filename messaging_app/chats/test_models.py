"""
Test cases for the messaging app models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from chats.models import Conversation, Message
import uuid

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for the User model."""

    def setUp(self):
        """Set up test data."""
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+1234567890",
        }

    def test_create_user(self):
        """Test user creation."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertIsInstance(user.user_id, uuid.UUID)
        self.assertFalse(user.is_online)

    def test_user_string_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), "testuser")

    def test_unique_username(self):
        """Test username uniqueness."""
        User.objects.create_user(**self.user_data)

        # Try to create another user with same username
        duplicate_data = self.user_data.copy()
        duplicate_data["email"] = "different@example.com"

        with self.assertRaises(IntegrityError):
            User.objects.create_user(**duplicate_data)

    def test_user_online_status(self):
        """Test user online status functionality."""
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_online)

        # Set user online
        user.is_online = True
        user.save()
        self.assertTrue(user.is_online)


class ConversationModelTest(TestCase):
    """Test cases for the Conversation model."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass123"
        )
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

    def test_create_conversation(self):
        """Test conversation creation."""
        self.assertIsInstance(self.conversation.conversation_id, uuid.UUID)
        self.assertEqual(self.conversation.participants.count(), 2)
        self.assertIn(self.user1, self.conversation.participants.all())
        self.assertIn(self.user2, self.conversation.participants.all())

    def test_conversation_string_representation(self):
        """Test conversation string representation."""
        expected = f"Conversation {self.conversation.conversation_id}"
        self.assertEqual(str(self.conversation), expected)

    def test_last_message_property(self):
        """Test last_message property."""
        # No messages yet
        self.assertIsNone(self.conversation.last_message)

        # Create a message
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Test message",
        )

        # Refresh conversation from database
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.last_message, message)


class MessageModelTest(TestCase):
    """Test cases for the Message model."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username="sender", email="sender@example.com", password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="receiver", email="receiver@example.com", password="pass123"
        )
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

    def test_create_message(self):
        """Test message creation."""
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Hello, this is a test message!",
        )

        self.assertIsInstance(message.message_id, uuid.UUID)
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.conversation, self.conversation)
        self.assertEqual(message.message_body, "Hello, this is a test message!")
        self.assertIsNotNone(message.sent_at)

    def test_message_string_representation(self):
        """Test message string representation."""
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Test message",
        )

        expected = f"Message from {self.user1.username}: Test message"
        self.assertEqual(str(message), expected)

    def test_message_ordering(self):
        """Test message ordering by sent_at."""
        message1 = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="First message",
        )
        message2 = Message.objects.create(
            sender=self.user2,
            conversation=self.conversation,
            message_body="Second message",
        )

        messages = Message.objects.all()
        # Should be ordered by sent_at descending (newest first)
        self.assertEqual(messages[0], message2)
        self.assertEqual(messages[1], message1)

    def test_empty_message_body(self):
        """Test that empty message body is not allowed."""
        with self.assertRaises(ValidationError):
            message = Message(
                sender=self.user1, conversation=self.conversation, message_body=""
            )
            message.full_clean()
