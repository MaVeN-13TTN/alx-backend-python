from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.test.utils import override_settings
from unittest.mock import patch
from .models import Message, Notification
from .signals import create_message_notification, update_message_read_status

User = get_user_model()


class MessageModelTests(TestCase):
    """
    Test cases for the Message model
    """

    def setUp(self):
        """
        Set up test data
        """
        self.sender = User.objects.create_user(
            username="sender_user", email="sender@example.com", password="testpass123"
        )
        self.receiver = User.objects.create_user(
            username="receiver_user",
            email="receiver@example.com",
            password="testpass123",
        )

    def test_message_creation(self):
        """
        Test that a message can be created successfully
        """
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, this is a test message!",
        )

        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.receiver, self.receiver)
        self.assertEqual(message.content, "Hello, this is a test message!")
        self.assertFalse(message.is_read)
        self.assertIsNotNone(message.message_id)
        self.assertIsNotNone(message.timestamp)

    def test_message_string_representation(self):
        """
        Test the string representation of a message
        """
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, this is a test message!",
        )

        expected_str = f"Message from {self.sender.username} to {self.receiver.username}: Hello, this is a test message!..."
        self.assertEqual(str(message), expected_str)

    def test_message_ordering(self):
        """
        Test that messages are ordered by timestamp (newest first)
        """
        message1 = Message.objects.create(
            sender=self.sender, receiver=self.receiver, content="First message"
        )
        message2 = Message.objects.create(
            sender=self.sender, receiver=self.receiver, content="Second message"
        )

        messages = Message.objects.all()
        self.assertEqual(messages[0], message2)  # Newest first
        self.assertEqual(messages[1], message1)


class NotificationModelTests(TestCase):
    """
    Test cases for the Notification model
    """

    def setUp(self):
        """
        Set up test data
        """
        self.user = User.objects.create_user(
            username="test_user", email="test@example.com", password="testpass123"
        )
        self.sender = User.objects.create_user(
            username="sender_user", email="sender@example.com", password="testpass123"
        )
        self.message = Message.objects.create(
            sender=self.sender, receiver=self.user, content="Test message content"
        )

    def test_notification_creation(self):
        """
        Test that a notification can be created successfully
        """
        notification = Notification.objects.create(
            user=self.user,
            message=self.message,
            title="New Message",
            content="You have received a new message",
        )

        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.message, self.message)
        self.assertEqual(notification.title, "New Message")
        self.assertEqual(notification.content, "You have received a new message")
        self.assertEqual(notification.notification_type, "message")
        self.assertFalse(notification.is_read)
        self.assertIsNotNone(notification.notification_id)

    def test_notification_string_representation(self):
        """
        Test the string representation of a notification
        """
        notification = Notification.objects.create(
            user=self.user,
            message=self.message,
            title="New Message",
            content="You have received a new message",
        )

        expected_str = f"Notification for {self.user.username}: New Message"
        self.assertEqual(str(notification), expected_str)


class MessageSignalTests(TestCase):
    """
    Test cases for message-related signals
    """

    def setUp(self):
        """
        Set up test data
        """
        self.sender = User.objects.create_user(
            username="sender_user", email="sender@example.com", password="testpass123"
        )
        self.receiver = User.objects.create_user(
            username="receiver_user",
            email="receiver@example.com",
            password="testpass123",
        )

    def test_notification_created_on_message_save(self):
        """
        Test that a notification is automatically created when a new message is saved
        """
        # Ensure no notifications exist initially
        self.assertEqual(Notification.objects.count(), 0)

        # Create a new message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, this is a test message!",
        )

        # Check that a notification was created
        self.assertEqual(Notification.objects.count(), 1)

        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertEqual(notification.notification_type, "message")
        self.assertIn(self.sender.username, notification.title)
        self.assertIn(message.content, notification.content)

    def test_no_notification_on_message_update(self):
        """
        Test that no additional notification is created when a message is updated
        """
        # Create a message (this will create one notification)
        message = Message.objects.create(
            sender=self.sender, receiver=self.receiver, content="Original content"
        )

        initial_notification_count = Notification.objects.count()

        # Update the message
        message.content = "Updated content"
        message.save()

        # Check that no additional notification was created
        self.assertEqual(Notification.objects.count(), initial_notification_count)

    def test_notification_marked_read_on_message_read(self):
        """
        Test that notifications are marked as read when the related message is marked as read
        """
        # Create a message (this will create a notification)
        message = Message.objects.create(
            sender=self.sender, receiver=self.receiver, content="Test message"
        )

        notification = Notification.objects.get(message=message)
        self.assertFalse(notification.is_read)

        # Mark the message as read
        message.is_read = True
        message.save()

        # Check that the notification is also marked as read
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    @patch("builtins.print")
    def test_signal_handlers_called(self, mock_print):
        """
        Test that signal handlers are called and produce expected output
        """
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message for signal",
        )

        # Check that the notification creation signal was called
        mock_print.assert_any_call(
            f"Notification created: New message from {self.sender.username} for user {self.receiver.username}"
        )

        # Mark message as read
        message.is_read = True
        message.save()

        # Check that the message read signal was called
        mock_print.assert_any_call(
            f"Notifications marked as read for message: {message.message_id}"
        )

    def test_signal_with_long_message_content(self):
        """
        Test that notifications handle long message content correctly
        """
        long_content = "A" * 150  # Content longer than 100 characters

        message = Message.objects.create(
            sender=self.sender, receiver=self.receiver, content=long_content
        )

        notification = Notification.objects.get(message=message)

        # Check that the notification content is truncated
        self.assertIn("A" * 100, notification.content)
        self.assertIn("...", notification.content)
        self.assertLess(
            len(notification.content.split('"')[1]), 105
        )  # Content part should be truncated


class SignalDisconnectionTests(TestCase):
    """
    Test cases for signal disconnection during testing
    """

    def setUp(self):
        """
        Set up test data
        """
        self.sender = User.objects.create_user(
            username="sender_user", email="sender@example.com", password="testpass123"
        )
        self.receiver = User.objects.create_user(
            username="receiver_user",
            email="receiver@example.com",
            password="testpass123",
        )

    def test_signal_disconnection(self):
        """
        Test that signals can be temporarily disconnected for testing
        """
        # Disconnect the signal
        post_save.disconnect(create_message_notification, sender=Message)

        try:
            # Create a message
            Message.objects.create(
                sender=self.sender,
                receiver=self.receiver,
                content="Test message without notification",
            )

            # Check that no notification was created
            self.assertEqual(Notification.objects.count(), 0)

        finally:
            # Reconnect the signal
            post_save.connect(create_message_notification, sender=Message)

    def test_multiple_signal_handlers(self):
        """
        Test that multiple signal handlers can be connected to the same signal
        """
        message = Message.objects.create(
            sender=self.sender, receiver=self.receiver, content="Test message"
        )

        # Should have created a notification (from create_message_notification)
        self.assertEqual(Notification.objects.count(), 1)

        # Mark as read to trigger the second signal handler
        message.is_read = True
        message.save()

        # Check that the notification was marked as read (from update_message_read_status)
        notification = Notification.objects.get(message=message)
        self.assertTrue(notification.is_read)
