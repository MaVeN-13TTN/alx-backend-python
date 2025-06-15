from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
from .managers import UnreadMessagesManager

User = get_user_model()


class Message(models.Model):
    """
    Model representing a message sent between users
    """

    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="messaging_sent_messages",
        help_text="User who sent the message",
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="messaging_received_messages",
        help_text="User who receives the message",
    )
    content = models.TextField(help_text="Message content")

    # Threading support - self-referential foreign key for replies
    parent_message = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        help_text="Parent message if this is a reply",
    )

    timestamp = models.DateTimeField(
        default=timezone.now, help_text="When the message was sent"
    )
    is_read = models.BooleanField(
        default=False, help_text="Whether the message has been read"
    )
    edited = models.BooleanField(
        default=False, help_text="Whether the message has been edited"
    )
    edit_count = models.PositiveIntegerField(
        default=0, help_text="Number of times the message has been edited"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()  # The default manager.
    unread = UnreadMessagesManager()  # Our custom manager for unread messages.
    unread_messages = UnreadMessagesManager()  # Alternative access to the same manager.

    def __str__(self):
        reply_indicator = " (Reply)" if self.parent_message else ""
        return f"Message from {self.sender.username} to {self.receiver.username}: {self.content[:50]}...{reply_indicator}"

    @property
    def is_reply(self):
        """Check if this message is a reply to another message"""
        return self.parent_message is not None

    @property
    def is_thread_starter(self):
        """Check if this message starts a new thread (has no parent)"""
        return self.parent_message is None

    @property
    def thread_depth(self):
        """Calculate the depth of this message in the thread"""
        depth = 0
        current = self.parent_message
        while current is not None:
            depth += 1
            current = current.parent_message
        return depth

    @property
    def root_message(self):
        """Get the root message of this thread"""
        current = self
        while current.parent_message is not None:
            current = current.parent_message
        return current

    def get_thread_messages(self):
        """
        Get all messages in this thread, including the root and all replies.
        Returns a queryset with optimized loading.
        """
        root = self.root_message

        # Use a single query with a subquery to get all descendants
        # This is more efficient than the recursive approach
        from django.db.models import Q

        # First, get all messages that are direct or indirect descendants
        all_descendants = []
        current_level = [root.pk]

        while current_level:
            # Get direct children of current level
            children = Message.objects.filter(
                parent_message_id__in=current_level
            ).values_list("pk", flat=True)

            if children:
                all_descendants.extend(children)
                current_level = list(children)
            else:
                break

        # Include root message and all descendants
        all_message_ids = [root.pk] + all_descendants

        return (
            Message.objects.filter(pk__in=all_message_ids)
            .select_related("sender", "receiver", "parent_message")
            .prefetch_related("replies")
        )

    def get_all_replies(self):
        """
        Get all direct and nested replies to this message using recursive query.
        Returns a queryset with optimized loading.
        """
        return (
            Message.objects.filter(pk__in=self._get_all_descendants(self))
            .select_related("sender", "receiver", "parent_message")
            .prefetch_related("replies")
        )

    def _get_all_descendants(self, message):
        """
        Recursively get all descendant message IDs.
        This is a helper method for building recursive queries.
        """
        descendants = []

        def collect_descendants(msg_id):
            # Get direct children
            children = Message.objects.filter(parent_message_id=msg_id).values_list(
                "pk", flat=True
            )
            for child_id in children:
                descendants.append(child_id)
                collect_descendants(child_id)  # Recursively get grandchildren

        collect_descendants(message.pk)
        return descendants

    def get_reply_count(self):
        """Get the total number of replies (direct and nested) to this message"""
        return len(self._get_all_descendants(self))

    def get_direct_replies(self):
        """
        Get only direct replies to this message (not nested replies).
        Returns a queryset with optimized loading.
        """
        return self.replies.select_related("sender", "receiver").prefetch_related(
            "replies"
        )

    def can_reply_to(self, user):
        """
        Check if a user can reply to this message.
        Business logic: users can reply if they are the sender or receiver of the original message.
        """
        root = self.root_message
        return (
            user == root.sender
            or user == root.receiver
            or user == self.sender
            or user == self.receiver
        )

    class Meta:
        db_table = "messaging_messages"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["receiver", "-timestamp"]),
            models.Index(fields=["sender", "-timestamp"]),
            models.Index(fields=["parent_message"]),  # Index for threading optimization
            models.Index(
                fields=["receiver", "is_read", "-timestamp"]
            ),  # Index for unread messages optimization
            models.Index(fields=["is_read"]),  # General index for read status
        ]


class Notification(models.Model):
    """
    Model representing notifications for users
    """

    NOTIFICATION_TYPES = (
        ("message", "New Message"),
        ("edit", "Message Edit"),
        ("system", "System Notification"),
    )

    notification_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="messaging_notifications",
        help_text="User who receives the notification",
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="messaging_notifications",
        help_text="Message that triggered this notification",
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default="message",
        help_text="Type of notification",
    )
    title = models.CharField(max_length=255, help_text="Notification title")
    content = models.TextField(help_text="Notification content")
    is_read = models.BooleanField(
        default=False, help_text="Whether the notification has been read"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"

    class Meta:
        db_table = "messaging_notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "is_read"]),
        ]


class MessageHistory(models.Model):
    """
    Model to track message edit history
    """

    history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="edit_history",
        help_text="Message this history entry belongs to",
    )
    old_content = models.TextField(help_text="Previous content before edit")
    new_content = models.TextField(help_text="New content after edit")
    edit_reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional reason for the edit",
    )
    edited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="message_edits",
        help_text="User who made the edit",
    )
    edited_at = models.DateTimeField(
        auto_now_add=True, help_text="When the edit was made"
    )

    def __str__(self):
        return f"Edit history for message {self.message.message_id} at {self.edited_at}"

    @property
    def content_changed(self):
        """Check if content actually changed"""
        return self.old_content != self.new_content

    @property
    def edit_summary(self):
        """Provide a summary of the edit"""
        old_length = len(self.old_content)
        new_length = len(self.new_content)

        if new_length > old_length:
            return f"Content expanded by {new_length - old_length} characters"
        elif new_length < old_length:
            return f"Content shortened by {old_length - new_length} characters"
        else:
            return "Content modified (same length)"

    class Meta:
        db_table = "messaging_message_history"
        ordering = ["-edited_at"]
        indexes = [
            models.Index(fields=["message", "-edited_at"]),
            models.Index(fields=["edited_by", "-edited_at"]),
        ]
        verbose_name = "Message Edit History"
        verbose_name_plural = "Message Edit Histories"
