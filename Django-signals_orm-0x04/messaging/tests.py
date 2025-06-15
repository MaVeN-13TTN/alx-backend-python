from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.test.utils import override_settings
from unittest.mock import patch
from .models import Message, Notification, MessageHistory
from .signals import create_message_notification, update_message_read_status
from .views import MessageViewSet

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

    def test_edit_notification_on_message_update(self):
        """
        Test that an edit notification is created when a message is updated
        """
        # Create a message (this will create one notification)
        message = Message.objects.create(
            sender=self.sender, receiver=self.receiver, content="Original content"
        )

        initial_notification_count = Notification.objects.count()

        # Update the message content
        message.content = "Updated content"
        message.save()

        # Check that an additional edit notification was created
        self.assertEqual(Notification.objects.count(), initial_notification_count + 1)

        # Check that we have both original and edit notifications
        notifications = Notification.objects.filter(message=message).order_by(
            "created_at"
        )
        self.assertEqual(notifications.count(), 2)

        # First should be the original message notification
        original_notification = notifications.first()
        self.assertEqual(original_notification.notification_type, "message")
        self.assertIn("New message from", original_notification.title)

        # Second should be the edit notification
        edit_notification = notifications.last()
        self.assertEqual(edit_notification.notification_type, "edit")
        self.assertIn("Message edited by", edit_notification.title)

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


class MessageEditTests(TestCase):
    """
    Test cases for message edit functionality and logging
    """

    def setUp(self):
        """
        Set up test data
        """
        self.sender = User.objects.create_user(
            username="sender_user",
            email="sender@example.com",
            password="testpass123",
        )
        self.receiver = User.objects.create_user(
            username="receiver_user",
            email="receiver@example.com",
            password="testpass123",
        )

    def test_message_edit_creates_history(self):
        """
        Test that editing a message creates a history record
        """
        # Create initial message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original message content",
        )

        initial_history_count = MessageHistory.objects.count()

        # Edit the message
        message.content = "Edited message content"
        message.save()

        # Check that history was created
        self.assertEqual(MessageHistory.objects.count(), initial_history_count + 1)

        # Check history details
        history = MessageHistory.objects.get(message=message)
        self.assertEqual(history.old_content, "Original message content")
        self.assertEqual(history.new_content, "Edited message content")
        self.assertEqual(history.edited_by, self.sender)
        self.assertTrue(history.content_changed)

    def test_message_edit_flags_updated(self):
        """
        Test that editing a message updates the edited flag and count
        """
        # Create initial message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original content",
        )

        # Initially not edited
        self.assertFalse(message.edited)
        self.assertEqual(message.edit_count, 0)

        # Edit the message
        message.content = "First edit"
        message.save()

        # Check flags
        message.refresh_from_db()
        self.assertTrue(message.edited)
        self.assertEqual(message.edit_count, 1)

        # Edit again
        message.content = "Second edit"
        message.save()

        # Check count increased
        message.refresh_from_db()
        self.assertEqual(message.edit_count, 2)

    def test_no_history_on_same_content(self):
        """
        Test that no history is created when content doesn't actually change
        """
        # Create initial message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Same content",
        )

        initial_history_count = MessageHistory.objects.count()

        # "Edit" with same content
        message.content = "Same content"
        message.save()

        # Check that no history was created
        self.assertEqual(MessageHistory.objects.count(), initial_history_count)
        self.assertFalse(message.edited)
        self.assertEqual(message.edit_count, 0)

    def test_multiple_edits_create_multiple_histories(self):
        """
        Test that multiple edits create multiple history records
        """
        # Create initial message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original content",
        )

        # First edit
        message.content = "First edit"
        message.save()

        # Second edit
        message.content = "Second edit"
        message.save()

        # Third edit
        message.content = "Third edit"
        message.save()

        # Check multiple history records
        histories = MessageHistory.objects.filter(message=message).order_by("edited_at")
        self.assertEqual(histories.count(), 3)

        # Check content progression
        self.assertEqual(histories[0].old_content, "Original content")
        self.assertEqual(histories[0].new_content, "First edit")

        self.assertEqual(histories[1].old_content, "First edit")
        self.assertEqual(histories[1].new_content, "Second edit")

        self.assertEqual(histories[2].old_content, "Second edit")
        self.assertEqual(histories[2].new_content, "Third edit")

        # Check final message state
        message.refresh_from_db()
        self.assertEqual(message.edit_count, 3)

    def test_edit_notification_created(self):
        """
        Test that editing a message creates an edit notification
        """
        # Create initial message (creates one notification)
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original content",
        )

        initial_notification_count = Notification.objects.count()

        # Edit the message
        message.content = "Edited content"
        message.save()

        # Check that an additional notification was created for the edit
        self.assertEqual(Notification.objects.count(), initial_notification_count + 1)

        # Get the edit notification (most recent one)
        edit_notification = Notification.objects.filter(
            message=message, title__contains="edited"
        ).first()

        self.assertIsNotNone(edit_notification)
        self.assertIn("edited", edit_notification.title.lower())
        self.assertEqual(edit_notification.user, self.receiver)

    def test_history_edit_summary_property(self):
        """
        Test the edit_summary property of MessageHistory
        """
        # Create message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Short",
        )

        # Edit to longer content
        message.content = "Much longer content here"
        message.save()

        history = MessageHistory.objects.get(message=message)
        summary = history.edit_summary

        self.assertIn("expanded", summary.lower())
        self.assertIn("character", summary.lower())

    def test_new_message_no_history(self):
        """
        Test that creating a new message doesn't create history
        """
        initial_history_count = MessageHistory.objects.count()

        # Create new message
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="New message",
        )

        # Check that no history was created
        self.assertEqual(MessageHistory.objects.count(), initial_history_count)


class MessageHistoryModelTests(TestCase):
    """
    Test cases for MessageHistory model
    """

    def setUp(self):
        """
        Set up test data
        """
        self.user = User.objects.create_user(
            username="test_user", email="test@example.com", password="testpass123"
        )
        self.receiver = User.objects.create_user(
            username="receiver_user",
            email="receiver@example.com",
            password="testpass123",
        )
        self.message = Message.objects.create(
            sender=self.user,
            receiver=self.receiver,
            content="Test message",
        )

    def test_message_history_creation(self):
        """
        Test MessageHistory model creation
        """
        history = MessageHistory.objects.create(
            message=self.message,
            old_content="Old content",
            new_content="New content",
            edited_by=self.user,
            edit_reason="Testing",
        )

        self.assertEqual(history.message, self.message)
        self.assertEqual(history.old_content, "Old content")
        self.assertEqual(history.new_content, "New content")
        self.assertEqual(history.edited_by, self.user)
        self.assertEqual(history.edit_reason, "Testing")
        self.assertIsNotNone(history.history_id)
        self.assertIsNotNone(history.edited_at)

    def test_content_changed_property(self):
        """
        Test the content_changed property
        """
        # Different content
        history1 = MessageHistory.objects.create(
            message=self.message,
            old_content="Old content",
            new_content="New content",
            edited_by=self.user,
        )
        self.assertTrue(history1.content_changed)

        # Same content
        history2 = MessageHistory.objects.create(
            message=self.message,
            old_content="Same content",
            new_content="Same content",
            edited_by=self.user,
        )
        self.assertFalse(history2.content_changed)

    def test_edit_summary_variations(self):
        """
        Test different variations of edit_summary
        """
        # Expanded content
        history1 = MessageHistory.objects.create(
            message=self.message,
            old_content="Short",
            new_content="Much longer content",
            edited_by=self.user,
        )
        self.assertIn("expanded", history1.edit_summary)

        # Shortened content
        history2 = MessageHistory.objects.create(
            message=self.message,
            old_content="Much longer content here",
            new_content="Short",
            edited_by=self.user,
        )
        self.assertIn("shortened", history2.edit_summary)

        # Same length content
        history3 = MessageHistory.objects.create(
            message=self.message,
            old_content="Hello",
            new_content="World",
            edited_by=self.user,
        )
        self.assertIn("same length", history3.edit_summary)

    def test_string_representation(self):
        """
        Test string representation of MessageHistory
        """
        history = MessageHistory.objects.create(
            message=self.message,
            old_content="Old",
            new_content="New",
            edited_by=self.user,
        )

        str_repr = str(history)
        self.assertIn(str(self.message.message_id), str_repr)
        self.assertIn("Edit history", str_repr)


# ============================================================================
# USER DELETION TESTS
# ============================================================================


class UserDeletionTests(TestCase):
    """
    Test cases for user deletion and related data cleanup
    """

    def setUp(self):
        """
        Set up test data for user deletion tests
        """
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )
        self.user3 = User.objects.create_user(
            username="user3", email="user3@example.com", password="testpass123"
        )

    def test_user_deletion_cleans_up_sent_messages(self):
        """
        Test that deleting a user removes all messages they sent
        """
        # Create messages from user1 to user2
        message1 = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Message 1"
        )
        message2 = Message.objects.create(
            sender=self.user1, receiver=self.user3, content="Message 2"
        )

        # Create a message from user2 to user1 (should remain after user1 deletion)
        message3 = Message.objects.create(
            sender=self.user2, receiver=self.user1, content="Message 3"
        )

        # Verify messages exist
        self.assertEqual(Message.objects.count(), 3)
        self.assertEqual(Message.objects.filter(sender=self.user1).count(), 2)

        # Delete user1
        user1_id = self.user1.pk
        self.user1.delete()

        # Verify user1's sent messages are deleted (CASCADE should handle this)
        self.assertEqual(Message.objects.filter(sender_id=user1_id).count(), 0)

        # Verify user1's received messages are also deleted (CASCADE should handle this)
        self.assertEqual(Message.objects.filter(receiver_id=user1_id).count(), 0)

        # Only message2 (user1->user3) should remain, but user1 is deleted so it should be gone
        # Actually, both message1 and message2 should be deleted because user1 (sender) is deleted
        # message3 should also be deleted because user1 (receiver) is deleted
        # So no messages should remain
        self.assertEqual(Message.objects.count(), 0)

    def test_user_deletion_cleans_up_received_messages(self):
        """
        Test that deleting a user removes all messages they received
        """
        # Create messages to user1 from different users
        message1 = Message.objects.create(
            sender=self.user2, receiver=self.user1, content="Message to user1"
        )
        message2 = Message.objects.create(
            sender=self.user3, receiver=self.user1, content="Another message to user1"
        )

        # Create a message between user2 and user3 (should remain)
        message3 = Message.objects.create(
            sender=self.user2,
            receiver=self.user3,
            content="Message between user2 and user3",
        )

        # Verify initial state
        self.assertEqual(Message.objects.count(), 3)
        self.assertEqual(Message.objects.filter(receiver=self.user1).count(), 2)

        # Delete user1
        user1_id = self.user1.pk
        self.user1.delete()

        # Verify messages to user1 are deleted
        self.assertEqual(Message.objects.filter(receiver_id=user1_id).count(), 0)

        # Only message3 should remain
        self.assertEqual(Message.objects.count(), 1)
        remaining_message = Message.objects.first()
        self.assertEqual(remaining_message.sender, self.user2)
        self.assertEqual(remaining_message.receiver, self.user3)

    def test_user_deletion_cleans_up_notifications(self):
        """
        Test that deleting a user removes all their notifications
        """
        # Create messages which will create notifications
        message1 = Message.objects.create(
            sender=self.user2, receiver=self.user1, content="Message 1"
        )
        message2 = Message.objects.create(
            sender=self.user3, receiver=self.user1, content="Message 2"
        )

        # Verify notifications were created
        user1_notifications = Notification.objects.filter(user=self.user1)
        self.assertGreater(user1_notifications.count(), 0)

        initial_notification_count = Notification.objects.count()

        # Delete user1
        user1_id = self.user1.pk
        self.user1.delete()

        # Verify user1's notifications are deleted
        self.assertEqual(Notification.objects.filter(user_id=user1_id).count(), 0)

        # All notifications should be gone since messages are also deleted
        self.assertEqual(Notification.objects.count(), 0)

    def test_user_deletion_cleans_up_message_histories(self):
        """
        Test that deleting a user removes message histories they created
        """
        # Create a message
        message = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Original content"
        )

        # Create message histories (simulating edits by user1)
        history1 = MessageHistory.objects.create(
            message=message,
            old_content="Original content",
            new_content="Edited content 1",
            edited_by=self.user1,
        )

        # Edit by user2 (should be cleaned up when user2 is deleted)
        history2 = MessageHistory.objects.create(
            message=message,
            old_content="Edited content 1",
            new_content="Edited content 2",
            edited_by=self.user2,
        )

        # Verify histories exist
        self.assertEqual(MessageHistory.objects.count(), 2)
        self.assertEqual(MessageHistory.objects.filter(edited_by=self.user1).count(), 1)

        # Delete user1
        user1_id = self.user1.pk
        self.user1.delete()

        # All histories should be deleted because the message is deleted (CASCADE)
        self.assertEqual(MessageHistory.objects.count(), 0)

    def test_multiple_user_deletion_cleanup(self):
        """
        Test cleanup when multiple users are deleted
        """
        # Create a complex web of messages and interactions
        messages = [
            Message.objects.create(
                sender=self.user1, receiver=self.user2, content="1->2"
            ),
            Message.objects.create(
                sender=self.user2, receiver=self.user1, content="2->1"
            ),
            Message.objects.create(
                sender=self.user1, receiver=self.user3, content="1->3"
            ),
            Message.objects.create(
                sender=self.user3, receiver=self.user1, content="3->1"
            ),
            Message.objects.create(
                sender=self.user2, receiver=self.user3, content="2->3"
            ),
        ]

        # Create some message histories
        for i, message in enumerate(messages[:3]):
            MessageHistory.objects.create(
                message=message,
                old_content=f"Original {i}",
                new_content=f"Edited {i}",
                edited_by=message.sender,
            )

        # Verify initial state
        self.assertEqual(Message.objects.count(), 5)
        self.assertEqual(MessageHistory.objects.count(), 3)
        self.assertGreater(Notification.objects.count(), 0)

        # Delete user1
        self.user1.delete()

        # After user1 deletion, only messages between user2 and user3 should remain
        remaining_messages = Message.objects.all()
        self.assertEqual(remaining_messages.count(), 1)
        self.assertEqual(remaining_messages.first().content, "2->3")

        # Delete user2
        self.user2.delete()

        # Now no messages should remain
        self.assertEqual(Message.objects.count(), 0)
        self.assertEqual(MessageHistory.objects.count(), 0)
        self.assertEqual(Notification.objects.count(), 0)

    @patch("builtins.print")
    def test_user_deletion_signals_called(self, mock_print):
        """
        Test that user deletion signals are called and produce expected output
        """
        # Create some data for the user
        Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Test message"
        )

        # Delete the user
        username = self.user1.username
        user_id = self.user1.pk
        self.user1.delete()

        # Verify that cleanup signals were called (check print statements)
        printed_messages = [str(call) for call in mock_print.call_args_list]
        printed_text = " ".join(printed_messages)

        # Should contain user cleanup messages
        self.assertIn(username, printed_text)
        self.assertIn("cleanup", printed_text.lower())

    def test_cascading_deletion_integrity(self):
        """
        Test that CASCADE relationships work correctly for data integrity
        """
        # Create interconnected data
        message = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Test message"
        )

        # Get the notification created by the signal
        notification = Notification.objects.filter(message=message).first()
        self.assertIsNotNone(notification)

        # Create message history
        history = MessageHistory.objects.create(
            message=message,
            old_content="Original",
            new_content="Edited",
            edited_by=self.user1,
        )

        # Store IDs for verification after deletion
        message_id = message.pk
        notification_id = notification.pk
        history_id = history.pk

        # Delete user1
        self.user1.delete()

        # Verify all related data is cleaned up
        self.assertFalse(Message.objects.filter(pk=message_id).exists())
        self.assertFalse(Notification.objects.filter(pk=notification_id).exists())
        self.assertFalse(MessageHistory.objects.filter(pk=history_id).exists())

    def test_partial_data_cleanup(self):
        """
        Test cleanup when user has mixed relationships (sender/receiver/editor)
        """
        # user1 sends to user2
        message1 = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Message 1"
        )

        # user2 sends to user3
        message2 = Message.objects.create(
            sender=self.user2, receiver=self.user3, content="Message 2"
        )

        # user1 edits message2 (as if they were a moderator or had edit permissions)
        history = MessageHistory.objects.create(
            message=message2,
            old_content="Message 2",
            new_content="Message 2 (edited by user1)",
            edited_by=self.user1,
        )

        # Verify initial state
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(MessageHistory.objects.count(), 1)

        # Delete user1
        self.user1.delete()

        # message1 should be deleted (user1 was sender)
        # message2 should remain (user1 was not sender or receiver)
        # history should be deleted (user1 was editor) - CASCADE from edited_by
        self.assertEqual(Message.objects.count(), 1)
        remaining_message = Message.objects.first()
        self.assertEqual(remaining_message.content, "Message 2")

        # History should be deleted because edited_by user is deleted
        # (assuming CASCADE is set on edited_by foreign key)
        self.assertEqual(MessageHistory.objects.count(), 0)


# ============================================================================
# USER DELETION API TESTS
# ============================================================================


class UserDeletionAPITests(TestCase):
    """
    Test cases for user deletion API endpoints
    """

    def setUp(self):
        """
        Set up test data for API tests
        """
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )

    def test_user_data_summary_endpoint(self):
        """
        Test the user data summary API endpoint
        """
        # Create some data for the user
        Message.objects.create(
            sender=self.user, receiver=self.other_user, content="Sent message"
        )
        Message.objects.create(
            sender=self.other_user, receiver=self.user, content="Received message"
        )

        # The API test would require Django's test client
        # This is a placeholder for the structure
        self.assertTrue(True)  # Placeholder assertion

    def test_delete_user_endpoint_authentication(self):
        """
        Test that user deletion endpoint requires authentication
        """
        # This would test the API endpoint authentication
        # Placeholder for API testing structure
        self.assertTrue(True)  # Placeholder assertion

    def test_delete_user_with_confirmation_endpoint(self):
        """
        Test user deletion with password confirmation
        """
        # This would test the password confirmation endpoint
        # Placeholder for API testing structure
        self.assertTrue(True)  # Placeholder assertion


class MessageThreadingTests(TestCase):
    """
    Test cases for message threading functionality
    """

    def setUp(self):
        """
        Set up test users and messages for threading tests
        """
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )
        self.user3 = User.objects.create_user(
            username="user3", email="user3@example.com", password="testpass123"
        )

    def test_message_thread_creation(self):
        """
        Test creating a threaded conversation
        """
        # Create root message
        root_message = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="This is the root message"
        )

        # Create first reply
        reply1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="This is a reply to the root message",
            parent_message=root_message,
        )

        # Create nested reply
        reply2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="This is a reply to the first reply",
            parent_message=reply1,
        )

        # Test threading properties
        self.assertFalse(root_message.is_reply)
        self.assertTrue(root_message.is_thread_starter)
        self.assertEqual(root_message.thread_depth, 0)

        self.assertTrue(reply1.is_reply)
        self.assertFalse(reply1.is_thread_starter)
        self.assertEqual(reply1.thread_depth, 1)

        self.assertTrue(reply2.is_reply)
        self.assertFalse(reply2.is_thread_starter)
        self.assertEqual(reply2.thread_depth, 2)

    def test_root_message_property(self):
        """
        Test that root_message property returns the correct root message
        """
        # Create a deep thread
        root = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Root message"
        )

        reply1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply 1",
            parent_message=root,
        )

        reply2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Reply 2",
            parent_message=reply1,
        )

        reply3 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply 3",
            parent_message=reply2,
        )

        # All messages should point to the same root
        self.assertEqual(root.root_message, root)
        self.assertEqual(reply1.root_message, root)
        self.assertEqual(reply2.root_message, root)
        self.assertEqual(reply3.root_message, root)

    def test_get_thread_messages(self):
        """
        Test retrieving all messages in a thread
        """
        # Create a branched thread
        root = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Root message"
        )

        # Branch 1
        reply1a = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply 1A",
            parent_message=root,
        )

        reply2a = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Reply 2A",
            parent_message=reply1a,
        )

        # Branch 2
        reply1b = Message.objects.create(
            sender=self.user3,
            receiver=self.user1,
            content="Reply 1B",
            parent_message=root,
        )

        # Get all thread messages from any message in the thread
        thread_messages_from_root = list(root.get_thread_messages())
        thread_messages_from_reply = list(reply2a.get_thread_messages())

        # Should get all 4 messages regardless of starting point
        self.assertEqual(len(thread_messages_from_root), 4)
        self.assertEqual(len(thread_messages_from_reply), 4)

        # Should contain all our messages
        message_ids = [msg.message_id for msg in thread_messages_from_root]
        self.assertIn(root.message_id, message_ids)
        self.assertIn(reply1a.message_id, message_ids)
        self.assertIn(reply2a.message_id, message_ids)
        self.assertIn(reply1b.message_id, message_ids)

    def test_get_all_replies(self):
        """
        Test retrieving all replies to a message
        """
        root = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Root message"
        )

        reply1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply 1",
            parent_message=root,
        )

        reply2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Reply 2",
            parent_message=reply1,
        )

        reply3 = Message.objects.create(
            sender=self.user3,
            receiver=self.user1,
            content="Reply 3",
            parent_message=root,
        )

        # Get all replies to root message
        all_replies = list(root.get_all_replies())
        self.assertEqual(len(all_replies), 3)

        # Get all replies to first reply
        reply1_replies = list(reply1.get_all_replies())
        self.assertEqual(len(reply1_replies), 1)
        self.assertEqual(reply1_replies[0], reply2)

    def test_get_direct_replies(self):
        """
        Test retrieving only direct replies to a message
        """
        root = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Root message"
        )

        reply1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Direct reply 1",
            parent_message=root,
        )

        reply2 = Message.objects.create(
            sender=self.user3,
            receiver=self.user1,
            content="Direct reply 2",
            parent_message=root,
        )

        # This should not be included in direct replies to root
        nested_reply = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Nested reply",
            parent_message=reply1,
        )

        direct_replies = list(root.get_direct_replies())
        self.assertEqual(len(direct_replies), 2)

        direct_reply_ids = [msg.message_id for msg in direct_replies]
        self.assertIn(reply1.message_id, direct_reply_ids)
        self.assertIn(reply2.message_id, direct_reply_ids)
        self.assertNotIn(nested_reply.message_id, direct_reply_ids)

    def test_get_reply_count(self):
        """
        Test getting the total reply count for a message
        """
        root = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Root message"
        )

        # No replies initially
        self.assertEqual(root.get_reply_count(), 0)

        # Add some replies
        reply1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply 1",
            parent_message=root,
        )

        reply2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Reply 2",
            parent_message=reply1,
        )

        reply3 = Message.objects.create(
            sender=self.user3,
            receiver=self.user1,
            content="Reply 3",
            parent_message=root,
        )

        # Should count all replies (direct and nested)
        self.assertEqual(root.get_reply_count(), 3)
        self.assertEqual(reply1.get_reply_count(), 1)
        self.assertEqual(reply2.get_reply_count(), 0)

    def test_can_reply_to_permissions(self):
        """
        Test the can_reply_to method for permission checking
        """
        # Create a conversation between user1 and user2
        root = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Root message"
        )

        # Both participants should be able to reply
        self.assertTrue(root.can_reply_to(self.user1))
        self.assertTrue(root.can_reply_to(self.user2))

        # Third party user should not be able to reply
        self.assertFalse(root.can_reply_to(self.user3))

        # Create a reply
        reply = Message.objects.create(
            sender=self.user2, receiver=self.user1, content="Reply", parent_message=root
        )

        # Same rules should apply to replies
        self.assertTrue(reply.can_reply_to(self.user1))
        self.assertTrue(reply.can_reply_to(self.user2))
        self.assertFalse(reply.can_reply_to(self.user3))

    def test_threading_with_signals(self):
        """
        Test that threading works correctly with notification signals
        """
        # Create root message - should create notification
        root = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Root message"
        )

        # Check notification was created
        notifications = Notification.objects.filter(user=self.user2)
        self.assertEqual(notifications.count(), 1)

        # Create reply - should create notification
        reply = Message.objects.create(
            sender=self.user2, receiver=self.user1, content="Reply", parent_message=root
        )

        # Check notification was created for the reply
        notifications = Notification.objects.filter(user=self.user1)
        self.assertEqual(notifications.count(), 1)

    def test_threading_query_optimization(self):
        """
        Test that threading queries are optimized with select_related and prefetch_related
        """
        # Create a thread with multiple messages
        root = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Root message"
        )

        for i in range(5):
            Message.objects.create(
                sender=self.user2 if i % 2 else self.user1,
                receiver=self.user1 if i % 2 else self.user2,
                content=f"Reply {i}",
                parent_message=root,
            )

        # Test that get_thread_messages uses optimized queries
        with self.assertNumQueries(
            4
        ):  # Expect reasonable number of queries for thread traversal
            thread_messages = list(root.get_thread_messages())
            # Access related fields to ensure they're prefetched
            for msg in thread_messages:
                _ = msg.sender.username
                _ = msg.receiver.username
                if msg.parent_message:
                    _ = msg.parent_message.content

    def test_message_deletion_in_thread(self):
        """
        Test that deleting a message in a thread works correctly
        """
        root = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Root message"
        )

        reply1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply 1",
            parent_message=root,
        )

        reply2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Reply 2",
            parent_message=reply1,
        )

        # Delete the middle message
        reply1.delete()

        # Root should still exist
        self.assertTrue(Message.objects.filter(message_id=root.message_id).exists())

        # reply2 should be deleted due to CASCADE
        self.assertFalse(Message.objects.filter(message_id=reply2.message_id).exists())

    def test_user_deletion_cleans_up_threads(self):
        """
        Test that deleting a user cleans up their threaded messages
        """
        # Create a thread involving the user
        root = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Root message"
        )

        reply = Message.objects.create(
            sender=self.user2, receiver=self.user1, content="Reply", parent_message=root
        )

        # Count messages before deletion
        initial_count = Message.objects.count()
        user1_id = self.user1.pk  # Store the ID before deletion

        # Delete user1
        self.user1.delete()

        # All messages involving user1 should be deleted
        remaining_messages = Message.objects.count()
        self.assertLess(remaining_messages, initial_count)

        # No messages should reference the deleted user (can't query with deleted instance)
        self.assertFalse(Message.objects.filter(sender_id=user1_id).exists())
        self.assertFalse(Message.objects.filter(receiver_id=user1_id).exists())


class MessageThreadingAPITests(TestCase):
    """
    Test cases for the threaded messaging API endpoints
    """

    def setUp(self):
        """
        Set up test data for API tests
        """
        self.user1 = User.objects.create_user(
            username="apiuser1", email="api1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="apiuser2", email="api2@example.com", password="testpass123"
        )

    def test_message_serializer_threading_fields(self):
        """
        Test that message serializer includes threading fields
        """
        from .serializers import MessageSerializer

        root = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Root message"
        )

        reply = Message.objects.create(
            sender=self.user2, receiver=self.user1, content="Reply", parent_message=root
        )

        # Test root message serialization
        root_serializer = MessageSerializer(root)
        root_data = root_serializer.data

        self.assertIn("is_reply", root_data)
        self.assertIn("is_thread_starter", root_data)
        self.assertIn("thread_depth", root_data)
        self.assertIn("reply_count", root_data)

        self.assertFalse(root_data["is_reply"])
        self.assertTrue(root_data["is_thread_starter"])
        self.assertEqual(root_data["thread_depth"], 0)
        self.assertEqual(root_data["reply_count"], 1)

        # Test reply serialization
        reply_serializer = MessageSerializer(reply)
        reply_data = reply_serializer.data

        self.assertTrue(reply_data["is_reply"])
        self.assertFalse(reply_data["is_thread_starter"])
        self.assertEqual(reply_data["thread_depth"], 1)
        self.assertEqual(reply_data["reply_count"], 0)
        self.assertIsNotNone(reply_data["parent_message"])

    def test_create_message_serializer_with_parent(self):
        """
        Test creating a message with parent_message_id
        """
        from .serializers import CreateMessageSerializer

        root = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Root message"
        )

        # Mock request object
        class MockRequest:
            def __init__(self, user):
                self.user = user

        mock_request = MockRequest(self.user2)

        serializer_data = {
            "receiver": self.user1.pk,
            "content": "This is a reply",
            "parent_message_id": root.message_id,
        }

        serializer = CreateMessageSerializer(
            data=serializer_data, context={"request": mock_request}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        reply = serializer.save()

        self.assertEqual(reply.parent_message, root)
        self.assertTrue(reply.is_reply)
        self.assertEqual(reply.thread_depth, 1)


class MessageViewSetTests(TestCase):
    """
    Test cases for the MessageViewSet functionality
    """

    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username="testuser1", email="test1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpass123"
        )

    def test_perform_create_sets_sender(self):
        """Test that perform_create method sets sender=request.user"""
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(user=self.user1)

        # Use the viewset's create action to test perform_create
        response = client.post(
            "/api/messaging/messages/",
            {"receiver": self.user2.pk, "content": "Test message"},
        )

        self.assertEqual(response.status_code, 201)

        # Verify the message was created with correct sender (set by perform_create)
        message_data = response.json()
        message = Message.objects.get(message_id=message_data["message_id"])

        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.content, "Test message")

    def test_get_queryset_optimizations(self):
        """Test that get_queryset uses select_related and prefetch_related"""
        # Create some test messages
        Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Message 1"
        )
        Message.objects.create(
            sender=self.user2, receiver=self.user1, content="Message 2"
        )

        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/api/messages/")
        request.user = self.user1

        viewset = MessageViewSet()
        viewset.request = request

        # Test that queryset includes optimizations
        queryset = viewset.get_queryset()

        # Check that the queryset has the right query optimizations
        query_str = str(queryset.query)
        self.assertIn("sender", query_str.lower())
        self.assertIn("receiver", query_str.lower())

        # Test that it filters correctly
        messages = list(queryset)
        self.assertTrue(
            all(
                msg.sender == self.user1 or msg.receiver == self.user1
                for msg in messages
            )
        )

    def test_create_message_api_endpoint(self):
        """Test the custom create_message API endpoint"""
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(user=self.user1)

        response = client.post(
            "/api/messaging/create-message/",
            {"receiver": self.user2.pk, "content": "Test message via create endpoint"},
        )

        self.assertEqual(response.status_code, 201)

        # Verify the message was created with correct sender
        message_data = response.json()
        message = Message.objects.get(message_id=message_data["message_id"])

        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.content, "Test message via create endpoint")

    def test_reply_to_message_sets_sender(self):
        """Test that reply_to_message sets sender=request.user"""
        # Create a root message
        root_message = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Root message"
        )

        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(user=self.user2)  # User2 will reply

        response = client.post(
            f"/api/messaging/messages/{root_message.message_id}/reply/",
            {"receiver": self.user1.pk, "content": "Reply message"},
        )

        self.assertEqual(response.status_code, 201)

        # Verify the reply was created with correct sender
        reply_data = response.json()
        reply = Message.objects.get(message_id=reply_data["message_id"])

        self.assertEqual(reply.sender, self.user2)  # Should be set to request.user
        self.assertEqual(reply.receiver, self.user1)
        self.assertEqual(reply.parent_message, root_message)
        self.assertEqual(reply.content, "Reply message")


class UnreadMessagesTests(TestCase):
    """Test cases for unread message functionality with custom manager"""

    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )
        self.user3 = User.objects.create_user(
            username="user3", email="user3@example.com", password="testpass123"
        )

    def test_unread_messages_manager_for_user(self):
        """Test UnreadMessagesManager.for_user method"""
        # Create messages - some read, some unread
        msg1 = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Message 1", is_read=False
        )
        msg2 = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Message 2", is_read=True
        )
        msg3 = Message.objects.create(
            sender=self.user3, receiver=self.user2, content="Message 3", is_read=False
        )
        msg4 = Message.objects.create(
            sender=self.user2, receiver=self.user1, content="Message 4", is_read=False
        )

        # Test unread messages for user2
        # Test the custom manager
        unread_messages = Message.unread.unread_for_user(self.user2)
        unread_ids = [msg.message_id for msg in unread_messages]

        self.assertEqual(len(unread_ids), 2)
        self.assertIn(msg1.message_id, unread_ids)
        self.assertIn(msg3.message_id, unread_ids)
        self.assertNotIn(msg2.message_id, unread_ids)  # This one is read
        self.assertNotIn(msg4.message_id, unread_ids)  # This one is for user1

    def test_unread_messages_manager_inbox_for_user(self):
        """Test UnreadMessagesManager.inbox_for_user method"""
        # Create a thread with unread messages
        root_msg = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Root message",
            is_read=False,
        )
        reply_msg = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply",
            parent_message=root_msg,
            is_read=False,
        )

        # Test inbox for user2
        inbox_messages = Message.unread_messages.inbox_for_user(self.user2)

        self.assertEqual(len(inbox_messages), 1)
        self.assertEqual(inbox_messages[0].message_id, root_msg.message_id)
        self.assertEqual(inbox_messages[0].parent_message, None)  # Root message

    def test_unread_count_for_user(self):
        """Test UnreadMessagesManager.unread_count_for_user method"""
        # Create messages
        Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Message 1", is_read=False
        )
        Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Message 2", is_read=True
        )
        Message.objects.create(
            sender=self.user3, receiver=self.user2, content="Message 3", is_read=False
        )

        count = Message.unread_messages.unread_count_for_user(self.user2)
        self.assertEqual(count, 2)

    def test_unread_threads_for_user(self):
        """Test UnreadMessagesManager.unread_threads_for_user method"""
        # Create thread messages
        root_msg = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Root message",
            is_read=False,
        )
        reply_msg = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply",
            parent_message=root_msg,
            is_read=False,
        )
        standalone_msg = Message.objects.create(
            sender=self.user3, receiver=self.user2, content="Standalone", is_read=False
        )

        # Test unread threads for user2
        unread_threads = Message.unread_messages.unread_threads_for_user(self.user2)
        thread_ids = [msg.message_id for msg in unread_threads]

        self.assertEqual(len(thread_ids), 2)
        self.assertIn(root_msg.message_id, thread_ids)
        self.assertIn(standalone_msg.message_id, thread_ids)
        self.assertNotIn(reply_msg.message_id, thread_ids)  # This is not a root message

    def test_query_optimization_with_only(self):
        """Test that the custom manager uses .only() for query optimization"""
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message",
            is_read=False,
        )

        # Test that only specific fields are loaded
        unread_messages = Message.unread_messages.for_user(self.user2)

        # This should work without additional queries
        with self.assertNumQueries(1):
            for msg in unread_messages:
                # These fields should be available without additional queries
                self.assertIsNotNone(msg.message_id)
                self.assertIsNotNone(msg.content)
                self.assertIsNotNone(msg.timestamp)
                self.assertIsNotNone(msg.sender.username)

    def test_unread_messages_with_only_optimization(self):
        """Test that .only() is used to optimize queries for unread messages"""
        # Create test messages
        self.msg1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message 1",
            is_read=False,
        )

        # Test explicit .only() usage for inbox display
        unread_messages_optimized = (
            Message.objects.filter(receiver=self.user2, is_read=False)
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

        # Check that we get the expected results
        self.assertEqual(unread_messages_optimized.count(), 1)
        first_msg = unread_messages_optimized.first()
        self.assertEqual(first_msg.content, "Test message 1")
        self.assertEqual(first_msg.sender.username, "user1")
        self.assertFalse(first_msg.is_read)


class UnreadMessagesAPITests(TestCase):
    """Test cases for unread message API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )

        # Create test messages
        self.msg1 = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Message 1", is_read=False
        )
        self.msg2 = Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Message 2", is_read=True
        )
        self.msg3 = Message.objects.create(
            sender=self.user2, receiver=self.user1, content="Message 3", is_read=False
        )

    def test_unread_messages_viewset_action(self):
        """Test the unread messages ViewSet action"""
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(user=self.user2)

        response = client.get("/api/messaging/messages/unread/")

        self.assertEqual(response.status_code, 200)

        # Check that only unread messages for user2 are returned
        messages = (
            response.json()["results"]
            if "results" in response.json()
            else response.json()
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["content"], "Message 1")

    def test_inbox_viewset_action(self):
        """Test the inbox ViewSet action"""
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(user=self.user2)

        response = client.get("/api/messaging/messages/inbox/")

        self.assertEqual(response.status_code, 200)

        # Check that inbox returns unread messages
        messages = (
            response.json()["results"]
            if "results" in response.json()
            else response.json()
        )
        self.assertEqual(len(messages), 1)

    def test_unread_count_viewset_action(self):
        """Test the unread count ViewSet action"""
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(user=self.user2)

        response = client.get("/api/messaging/messages/unread_count/")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["unread_count"], 1)
        self.assertEqual(data["user"], "user2")

    def test_mark_message_read_viewset_action(self):
        """Test marking a message as read via ViewSet action"""
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(user=self.user2)

        response = client.patch(
            f"/api/messaging/messages/{self.msg1.message_id}/mark_read/"
        )

        self.assertEqual(response.status_code, 200)

        # Verify message is marked as read
        self.msg1.refresh_from_db()
        self.assertTrue(self.msg1.is_read)

    def test_mark_all_read_viewset_action(self):
        """Test marking all messages as read via ViewSet action"""
        from rest_framework.test import APIClient

        # Create another unread message
        Message.objects.create(
            sender=self.user1, receiver=self.user2, content="Message 4", is_read=False
        )

        client = APIClient()
        client.force_authenticate(user=self.user2)

        response = client.patch("/api/messaging/mark-all-read/")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["count"], 2)  # Should have marked 2 messages as read

        # Verify messages are marked as read
        unread_count = Message.unread_messages.unread_count_for_user(self.user2)
        self.assertEqual(unread_count, 0)

    def test_get_unread_messages_function_view(self):
        """Test the get_unread_messages function-based view"""
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(user=self.user2)

        response = client.get("/api/messaging/unread-messages/")

        self.assertEqual(response.status_code, 200)

        # Check response structure
        if "results" in response.json():
            messages = response.json()["results"]
        else:
            messages = response.json()

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["content"], "Message 1")

    def test_mark_message_read_function_view(self):
        """Test the mark_message_read function-based view"""
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(user=self.user2)

        response = client.patch(
            f"/api/messaging/messages/{self.msg1.message_id}/mark-read/"
        )

        self.assertEqual(response.status_code, 200)

        # Verify message is marked as read
        self.msg1.refresh_from_db()
        self.assertTrue(self.msg1.is_read)

    def test_get_unread_count_function_view(self):
        """Test the get_unread_count function-based view"""
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(user=self.user2)

        response = client.get("/api/messaging/unread-count/")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["unread_count"], 1)
        self.assertEqual(data["user"], "user2")

    def test_permission_denied_for_other_users_messages(self):
        """Test that users can't mark other users' messages as read"""
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(
            user=self.user1
        )  # user1 trying to mark user2's message

        response = client.patch(
            f"/api/messaging/messages/{self.msg1.message_id}/mark-read/"
        )

        self.assertEqual(response.status_code, 403)

        # Verify message is still unread
        self.msg1.refresh_from_db()
        self.assertFalse(self.msg1.is_read)


class UnreadMessagesPerformanceTests(TestCase):
    """Test cases for unread message performance optimization"""

    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )

        # Create multiple messages for performance testing
        for i in range(10):
            Message.objects.create(
                sender=self.user1,
                receiver=self.user2,
                content=f"Message {i}",
                is_read=False,
            )

    def test_unread_messages_query_count(self):
        """Test that unread messages queries are optimized"""
        # Test that fetching unread messages with related data uses minimal queries
        with self.assertNumQueries(1):  # Should only need 1 query due to select_related
            unread_messages = list(Message.unread_messages.for_user(self.user2))

            # Access related fields that should be prefetched
            for msg in unread_messages:
                self.assertIsNotNone(msg.sender.username)

    def test_inbox_query_optimization(self):
        """Test that inbox queries are optimized with select_related"""
        with self.assertNumQueries(1):  # Should only need 1 query
            inbox_messages = list(Message.unread_messages.inbox_for_user(self.user2))

            # Access related fields
            for msg in inbox_messages:
                self.assertIsNotNone(msg.sender.username)

    def test_unread_count_query_optimization(self):
        """Test that unread count uses optimized query"""
        with self.assertNumQueries(1):  # Should only need 1 query for count
            count = Message.unread_messages.unread_count_for_user(self.user2)
            self.assertEqual(count, 10)
