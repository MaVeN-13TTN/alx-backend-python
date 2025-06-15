from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UnreadMessagesManager(models.Manager):
    """
    Custom manager for filtering unread messages with query optimization
    """

    def unread_for_user(self, user):
        """
        Get unread messages for a specific user (as receiver)
        Optimized with select_related and only() for necessary fields
        """
        return (
            self.get_queryset()
            .filter(receiver=user, is_read=False)
            .select_related("sender", "parent_message")
            .only(
                "message_id",
                "content",
                "timestamp",
                "is_read",
                "sender__username",
                "sender__email",
                "sender__first_name",
                "sender__last_name",
                "parent_message__message_id",
                "parent_message__content",
            )
            .order_by("-timestamp")
        )

    def for_user(self, user):
        """
        Get unread messages for a specific user (as receiver)
        Optimized with select_related and only() for necessary fields
        """
        return self.unread_for_user(user)

    def inbox_for_user(self, user):
        """
        Get unread messages in user's inbox with threading info
        Includes parent message details for threaded conversations
        """
        return (
            self.get_queryset()
            .filter(receiver=user, is_read=False)
            .select_related("sender", "parent_message", "parent_message__sender")
            .only(
                "message_id",
                "content",
                "timestamp",
                "is_read",
                "edited",
                "edit_count",
                "sender__username",
                "sender__email",
                "sender__first_name",
                "sender__last_name",
                "parent_message__message_id",
                "parent_message__content",
                "parent_message__timestamp",
                "parent_message__sender__username",
            )
            .order_by("-timestamp")
        )

    def unread_count_for_user(self, user):
        """
        Get count of unread messages for a user
        """
        return self.get_queryset().filter(receiver=user, is_read=False).count()

    def unread_threads_for_user(self, user):
        """
        Get unread thread starter messages for a user
        Only returns root messages (no parent) that are unread
        """
        return (
            self.get_queryset()
            .filter(receiver=user, is_read=False, parent_message__isnull=True)
            .select_related("sender")
            .only(
                "message_id",
                "content",
                "timestamp",
                "is_read",
                "sender__username",
                "sender__email",
                "sender__first_name",
                "sender__last_name",
            )
            .order_by("-timestamp")
        )
