from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Message, Notification

User = get_user_model()


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal handler that creates a notification when a new message is sent.

    This signal is triggered after a Message instance is saved.
    It automatically creates a notification for the receiving user.

    Args:
        sender: The model class (Message)
        instance: The actual Message instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:  # Only create notification for new messages
        # Create notification for the receiver
        notification = Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type="message",
            title=f"New message from {instance.sender.username}",
            content=f'{instance.sender.get_full_name() or instance.sender.username} sent you a message: "{instance.content[:100]}{"..." if len(instance.content) > 100 else ""}"',
        )

        # Optional: You can add additional logic here such as:
        # - Sending push notifications
        # - Sending email notifications
        # - Logging the notification creation
        # - Triggering real-time updates via WebSocket

        print(
            f"Notification created: {notification.title} for user {instance.receiver.username}"
        )


@receiver(post_save, sender=Message)
def update_message_read_status(sender, instance, created, **kwargs):
    """
    Signal handler to handle message read status updates.

    This demonstrates how multiple signal handlers can listen to the same signal
    and perform different actions.

    Args:
        sender: The model class (Message)
        instance: The actual Message instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if not created and instance.is_read:
        # When a message is marked as read, mark related notifications as read too
        Notification.objects.filter(
            message=instance, user=instance.receiver, is_read=False
        ).update(is_read=True)

        print(f"Notifications marked as read for message: {instance.message_id}")


# Optional: Signal for when notifications are marked as read
@receiver(post_save, sender=Notification)
def notification_read_handler(sender, instance, created, **kwargs):
    """
    Signal handler for notification updates.

    This can be used to trigger additional actions when notifications
    are marked as read or updated.

    Args:
        sender: The model class (Notification)
        instance: The actual Notification instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if not created and instance.is_read:
        # Optional: Log when notifications are read
        print(
            f"Notification {instance.notification_id} marked as read by {instance.user.username}"
        )

        # You could add logic here for:
        # - Analytics tracking
        # - User engagement metrics
        # - Clean up old read notifications
