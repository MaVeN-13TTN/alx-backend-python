from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

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


@receiver(pre_save, sender=Message)
def log_message_edit_history(sender, instance, **kwargs):
    """
    Signal handler that logs message edits before they are saved.

    This signal is triggered before a Message instance is saved.
    It captures the old content and creates a history record if the message
    is being edited (not created for the first time).

    Args:
        sender: The model class (Message)
        instance: The actual Message instance that will be saved
        **kwargs: Additional keyword arguments
    """
    # Only process if this is an update (message already exists in database)
    if instance.pk:
        try:
            # Get the original message from database
            original_message = Message.objects.get(pk=instance.pk)

            # Check if content has actually changed
            if original_message.content != instance.content:
                # Create history record with old content
                MessageHistory.objects.create(
                    message=original_message,
                    old_content=original_message.content,
                    new_content=instance.content,
                    edited_by=instance.sender,  # Assuming sender is the editor
                    edit_reason="Content modified",  # Could be enhanced to accept custom reasons
                )

                # Update message metadata
                instance.edited = True
                instance.edit_count = original_message.edit_count + 1

                print(
                    f"Message edit logged: {instance.message_id} (Edit #{instance.edit_count})"
                )

        except Message.DoesNotExist:
            # This shouldn't happen, but handle gracefully
            print(
                f"Warning: Could not find original message {instance.pk} for edit logging"
            )
            pass


@receiver(post_save, sender=Message)
def handle_message_edit_notification(sender, instance, created, **kwargs):
    """
    Signal handler that creates notifications for message edits.

    This runs after a message is saved and creates additional notifications
    if the message was edited (separate from new message notifications).

    Args:
        sender: The model class (Message)
        instance: The actual Message instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    # Only create edit notification if this is an update and message was edited
    if not created and instance.edited and instance.edit_count > 0:
        # Create notification for the receiver about the edit
        edit_notification = Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type="edit",
            title=f"Message edited by {instance.sender.username}",
            content=f'{instance.sender.get_full_name() or instance.sender.username} edited their message: "{instance.content[:100]}{"..." if len(instance.content) > 100 else ""}"',
        )

        print(
            f"Edit notification created: {edit_notification.title} for user {instance.receiver.username}"
        )


@receiver(post_save, sender=MessageHistory)
def log_message_history_creation(sender, instance, created, **kwargs):
    """
    Signal handler for when message history records are created.

    This can be used for analytics, monitoring, or additional processing
    when message edits are logged.

    Args:
        sender: The model class (MessageHistory)
        instance: The actual MessageHistory instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        print(
            f"Message history recorded: Message {instance.message.message_id} edited by {instance.edited_by.username}"
        )

        # Optional: Add additional logic here such as:
        # - Audit logging for compliance
        # - Analytics tracking for user behavior
        # - Real-time notifications to moderators
        # - Automatic content moderation checks
