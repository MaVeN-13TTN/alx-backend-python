from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for user information in nested relationships
    """

    class Meta:
        model = User
        fields = [
            "pk",
            "username",
            "email",
            "first_name",
            "last_name",
        ]
        read_only_fields = fields


class MessageHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for MessageHistory model
    """

    edited_by = UserSummarySerializer(read_only=True)
    edit_summary = serializers.ReadOnlyField()
    content_changed = serializers.ReadOnlyField()

    class Meta:
        model = MessageHistory
        fields = [
            "history_id",
            "old_content",
            "new_content",
            "edit_reason",
            "edited_by",
            "edited_at",
            "edit_summary",
            "content_changed",
        ]
        read_only_fields = fields


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model with threading support
    """

    sender = UserSummarySerializer(read_only=True)
    receiver = UserSummarySerializer(read_only=True)
    parent_message = serializers.SerializerMethodField()
    edit_history = MessageHistorySerializer(many=True, read_only=True)

    # Threading properties
    is_reply = serializers.ReadOnlyField()
    is_thread_starter = serializers.ReadOnlyField()
    thread_depth = serializers.ReadOnlyField()
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "message_id",
            "sender",
            "receiver",
            "content",
            "parent_message",
            "timestamp",
            "is_read",
            "edited",
            "edit_count",
            "created_at",
            "updated_at",
            "edit_history",
            "is_reply",
            "is_thread_starter",
            "thread_depth",
            "reply_count",
        ]
        read_only_fields = [
            "message_id",
            "timestamp",
            "edited",
            "edit_count",
            "created_at",
            "updated_at",
        ]

    def get_parent_message(self, obj):
        """
        Get parent message details for threading
        """
        if obj.parent_message:
            return {
                "message_id": obj.parent_message.message_id,
                "content": (
                    obj.parent_message.content[:100] + "..."
                    if len(obj.parent_message.content) > 100
                    else obj.parent_message.content
                ),
                "sender": obj.parent_message.sender.username,
                "timestamp": obj.parent_message.timestamp,
            }
        return None

    def get_reply_count(self, obj):
        """
        Get the total number of replies to this message
        """
        return obj.get_reply_count()


class MessageThreadSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying a complete message thread
    """

    sender = UserSummarySerializer(read_only=True)
    receiver = UserSummarySerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    # Threading properties
    is_reply = serializers.ReadOnlyField()
    is_thread_starter = serializers.ReadOnlyField()
    thread_depth = serializers.ReadOnlyField()
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "message_id",
            "sender",
            "receiver",
            "content",
            "timestamp",
            "is_read",
            "edited",
            "edit_count",
            "is_reply",
            "is_thread_starter",
            "thread_depth",
            "reply_count",
            "replies",
        ]
        read_only_fields = fields

    def get_replies(self, obj):
        """
        Get direct replies to this message (not nested)
        """
        direct_replies = obj.get_direct_replies()
        return MessageThreadSerializer(
            direct_replies, many=True, context=self.context
        ).data

    def get_reply_count(self, obj):
        """
        Get the total number of replies to this message
        """
        return obj.get_reply_count()


class MessageListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for message listings
    """

    sender = UserSummarySerializer(read_only=True)
    receiver = UserSummarySerializer(read_only=True)
    parent_message_id = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()

    # Threading properties
    is_reply = serializers.ReadOnlyField()
    is_thread_starter = serializers.ReadOnlyField()
    thread_depth = serializers.ReadOnlyField()

    class Meta:
        model = Message
        fields = [
            "message_id",
            "sender",
            "receiver",
            "content",
            "parent_message_id",
            "timestamp",
            "is_read",
            "edited",
            "edit_count",
            "is_reply",
            "is_thread_starter",
            "thread_depth",
            "reply_count",
        ]
        read_only_fields = fields

    def get_parent_message_id(self, obj):
        """
        Get parent message ID for threading
        """
        return obj.parent_message.message_id if obj.parent_message else None

    def get_reply_count(self, obj):
        """
        Get the total number of replies to this message
        """
        return obj.get_reply_count()


class CreateMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new messages with threading support
    """

    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())
    parent_message_id = serializers.UUIDField(
        required=False, allow_null=True, write_only=True
    )

    class Meta:
        model = Message
        fields = [
            "sender",
            "receiver",
            "content",
            "parent_message_id",
        ]

    def validate_parent_message_id(self, value):
        """
        Validate that the parent message exists and the user can reply to it
        """
        if value is not None:
            try:
                parent_message = Message.objects.get(message_id=value)
                user = self.context["request"].user

                if not parent_message.can_reply_to(user):
                    raise serializers.ValidationError(
                        "You don't have permission to reply to this message."
                    )

                return parent_message
            except Message.DoesNotExist:
                raise serializers.ValidationError("Parent message does not exist.")
        return None

    def create(self, validated_data):
        """
        Create a message with proper parent message handling
        """
        parent_message = validated_data.pop("parent_message_id", None)
        if parent_message:
            validated_data["parent_message"] = parent_message

        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model
    """

    user = UserSummarySerializer(read_only=True)
    message = MessageListSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "notification_id",
            "user",
            "message",
            "notification_type",
            "title",
            "content",
            "is_read",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class NotificationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for notification listings
    """

    message_id = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "notification_id",
            "notification_type",
            "title",
            "content",
            "is_read",
            "created_at",
            "message_id",
            "sender",
        ]
        read_only_fields = fields

    def get_message_id(self, obj):
        """
        Get associated message ID
        """
        return obj.message.message_id if obj.message else None

    def get_sender(self, obj):
        """
        Get message sender username
        """
        return (
            obj.message.sender.username if obj.message and obj.message.sender else None
        )
