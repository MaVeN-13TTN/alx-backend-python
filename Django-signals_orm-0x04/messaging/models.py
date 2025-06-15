from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

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

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}: {self.content[:50]}..."

    class Meta:
        db_table = "messaging_messages"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["receiver", "-timestamp"]),
            models.Index(fields=["sender", "-timestamp"]),
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
