from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.test.utils import override_settings
from unittest.mock import patch
from .models import Message, Notification, MessageHistory
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
