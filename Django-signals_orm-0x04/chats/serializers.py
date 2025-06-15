from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with password handling
    """

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    confirm_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "user_id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "profile_picture",
            "is_online",
            "last_seen",
            "password",
            "confirm_password",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user_id", "last_seen", "created_at", "updated_at"]
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": True},
        }

    def validate(self, attrs):
        """
        Validate that password and confirm_password match
        """
        if "password" in attrs and "confirm_password" in attrs:
            if attrs["password"] != attrs["confirm_password"]:
                raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        """
        Create user with hashed password
        """
        validated_data.pop("confirm_password", None)
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update user, handling password separately
        """
        validated_data.pop("confirm_password", None)
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
        return super().update(instance, validated_data)


class UserSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for user information in nested relationships
    """

    class Meta:
        model = User
        fields = [
            "user_id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_online",
            "profile_picture",
        ]
        read_only_fields = fields


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model with sender details
    """

    sender = UserSummarySerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True, source="sender.user_id")

    class Meta:
        model = Message
        fields = [
            "message_id",
            "sender",
            "sender_id",
            "conversation",
            "message_body",
            "sent_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["message_id", "sent_at", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Create message with sender from validated data
        """
        sender_data = validated_data.pop("sender", {})
        if "user_id" in sender_data:
            try:
                sender = User.objects.get(user_id=sender_data["user_id"])
                validated_data["sender"] = sender
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid sender")
        return super().create(validated_data)


class MessageSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for messages in conversation listings
    """

    sender = UserSummarySerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["message_id", "sender", "message_body", "sent_at"]
        read_only_fields = fields


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model with participants and messages
    """

    participants = UserSummarySerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    messages = MessageSummarySerializer(many=True, read_only=True)
    last_message = MessageSummarySerializer(read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "participant_ids",
            "messages",
            "last_message",
            "message_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["conversation_id", "created_at", "updated_at"]

    def get_message_count(self, obj):
        """
        Get the total number of messages in the conversation
        """
        return obj.messages.count()

    def create(self, validated_data):
        """
        Create conversation with participants
        """
        participant_ids = validated_data.pop("participant_ids", [])
        conversation = super().create(validated_data)

        # Add participants
        if participant_ids:
            participants = User.objects.filter(user_id__in=participant_ids)
            conversation.participants.set(participants)

        return conversation

    def update(self, instance, validated_data):
        """
        Update conversation and participants
        """
        participant_ids = validated_data.pop("participant_ids", None)
        instance = super().update(instance, validated_data)

        # Update participants if provided
        if participant_ids is not None:
            participants = User.objects.filter(user_id__in=participant_ids)
            instance.participants.set(participants)

        return instance


class ConversationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for conversation listings
    """

    participants = UserSummarySerializer(many=True, read_only=True)
    last_message = MessageSummarySerializer(read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "last_message",
            "message_count",
            "updated_at",
        ]
        read_only_fields = fields

    def get_message_count(self, obj):
        """
        Get the total number of messages in the conversation
        """
        return obj.messages.count()


class ConversationDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for single conversation view with all messages
    """

    participants = UserSummarySerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "messages",
            "message_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_messages(self, obj):
        """
        Get messages with pagination support
        """
        # Get messages ordered by sent_at (most recent first)
        messages = obj.messages.all().order_by("-sent_at")

        # Support for pagination through context
        request = self.context.get("request")
        if request and hasattr(request, "query_params"):
            limit = request.query_params.get("limit", 50)
            try:
                limit = int(limit)
                messages = messages[:limit]
            except (ValueError, TypeError):
                messages = messages[:50]

        return MessageSummarySerializer(messages, many=True).data

    def get_message_count(self, obj):
        """
        Get the total number of messages in the conversation
        """
        return obj.messages.count()
