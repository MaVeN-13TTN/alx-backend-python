from django.db.models.signals import post_save, pre_save, post_delete
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


# ============================================================================
# USER DELETION CLEANUP SIGNALS
# ============================================================================


@receiver(post_delete, sender=User)
def cleanup_user_messages(sender, instance, **kwargs):
    """
    Signal handler that cleans up messages when a user is deleted.

    This signal removes all messages sent by or received by the deleted user.
    Note: The CASCADE foreign key relationships should handle this automatically,
    but we include explicit cleanup for logging and custom business logic.

    Args:
        sender: The model class (User)
        instance: The deleted User instance
        **kwargs: Additional keyword arguments
    """
    try:
        user_id = instance.pk
        username = getattr(instance, "username", "Unknown")

        # Count messages before deletion for logging
        sent_messages_count = Message.objects.filter(sender=instance).count()
        received_messages_count = Message.objects.filter(receiver=instance).count()

        # Delete messages sent by this user
        deleted_sent = Message.objects.filter(sender=instance).delete()

        # Delete messages received by this user
        deleted_received = Message.objects.filter(receiver=instance).delete()

        print(f"User cleanup - Messages: {username} (ID: {user_id})")
        print(f"  ├─ Sent messages deleted: {sent_messages_count}")
        print(f"  └─ Received messages deleted: {received_messages_count}")

        # Optional: Add custom cleanup logic here
        # - Archive important messages before deletion
        # - Send notifications to other users about deleted conversations
        # - Log deletion for audit purposes

    except Exception as e:
        print(f"Error cleaning up messages for deleted user: {str(e)}")


@receiver(post_delete, sender=User)
def cleanup_user_notifications(sender, instance, **kwargs):
    """
    Signal handler that cleans up notifications when a user is deleted.

    This removes all notifications associated with the deleted user.

    Args:
        sender: The model class (User)
        instance: The deleted User instance
        **kwargs: Additional keyword arguments
    """
    try:
        user_id = instance.pk
        username = getattr(instance, "username", "Unknown")

        # Count notifications before deletion
        notifications_count = Notification.objects.filter(user=instance).count()

        # Delete notifications for this user
        deleted_notifications = Notification.objects.filter(user=instance).delete()

        print(f"User cleanup - Notifications: {username} (ID: {user_id})")
        print(f"  └─ Notifications deleted: {notifications_count}")

        # Optional: Send final notifications to related users
        # - Notify contacts that user has left
        # - Clean up notification preferences

    except Exception as e:
        print(f"Error cleaning up notifications for deleted user: {str(e)}")


@receiver(post_delete, sender=User)
def cleanup_user_message_histories(sender, instance, **kwargs):
    """
    Signal handler that cleans up message edit histories when a user is deleted.

    This removes all message histories edited by the deleted user and also
    histories related to messages the user was involved in.

    Args:
        sender: The model class (User)
        instance: The deleted User instance
        **kwargs: Additional keyword arguments
    """
    try:
        user_id = instance.pk
        username = getattr(instance, "username", "Unknown")

        # Count histories before deletion
        edited_by_user_count = MessageHistory.objects.filter(edited_by=instance).count()

        # Count histories for messages where user was sender or receiver
        # Note: These will be deleted automatically when messages are deleted due to CASCADE
        related_histories_count = (
            MessageHistory.objects.filter(message__sender=instance).count()
            + MessageHistory.objects.filter(message__receiver=instance).count()
        )

        # Delete histories edited by this user
        deleted_histories = MessageHistory.objects.filter(edited_by=instance).delete()

        print(f"User cleanup - Message Histories: {username} (ID: {user_id})")
        print(f"  ├─ Histories edited by user: {edited_by_user_count}")
        print(
            f"  └─ Related message histories: {related_histories_count} (deleted via CASCADE)"
        )

        # Optional: Archive edit histories for compliance
        # - Export edit logs before deletion
        # - Maintain anonymized editing statistics

    except Exception as e:
        print(f"Error cleaning up message histories for deleted user: {str(e)}")


@receiver(post_delete, sender=User)
def log_user_deletion_summary(sender, instance, **kwargs):
    """
    Signal handler that logs a comprehensive summary of user deletion.

    This provides a final audit log of what was cleaned up when the user
    was deleted.

    Args:
        sender: The model class (User)
        instance: The deleted User instance
        **kwargs: Additional keyword arguments
    """
    try:
        user_id = instance.pk
        username = getattr(instance, "username", "Unknown")
        email = getattr(instance, "email", "Unknown")
        date_joined = getattr(instance, "date_joined", "Unknown")

        print(f"📋 USER DELETION SUMMARY")
        print(f"{'='*50}")
        print(f"👤 User: {username} ({email})")
        print(f"🆔 ID: {user_id}")
        print(f"📅 Joined: {date_joined}")
        print(f"🗑️  Deletion completed successfully")
        print(f"✅ All related data cleaned up via signals and CASCADE relationships")
        print(f"{'='*50}")

        # Optional: Send to external logging service
        # - Audit logs
        # - Analytics
        # - Compliance reporting

    except Exception as e:
        print(f"Error logging user deletion summary: {str(e)}")


# ============================================================================
# MESSAGE DELETION CLEANUP SIGNALS
# ============================================================================


@receiver(post_delete, sender=Message)
def cleanup_message_related_data(sender, instance, **kwargs):
    """
    Signal handler that cleans up data when a message is deleted.

    This removes notifications and histories related to the deleted message.
    Note: This should happen automatically due to CASCADE relationships,
    but we include it for explicit logging and custom logic.

    Args:
        sender: The model class (Message)
        instance: The deleted Message instance
        **kwargs: Additional keyword arguments
    """
    try:
        message_id = instance.pk
        sender_username = getattr(instance.sender, "username", "Unknown")
        receiver_username = getattr(instance.receiver, "username", "Unknown")

        print(f"Message cleanup: {message_id}")
        print(f"  ├─ From: {sender_username}")
        print(f"  ├─ To: {receiver_username}")
        print(f"  └─ Related notifications and histories cleaned up via CASCADE")

        # Optional: Custom cleanup logic
        # - Archive message content before deletion
        # - Update conversation statistics
        # - Notify participants about message deletion

    except Exception as e:
        print(f"Error cleaning up data for deleted message: {str(e)}")
