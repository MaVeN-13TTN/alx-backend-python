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
