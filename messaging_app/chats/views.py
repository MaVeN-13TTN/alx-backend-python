from django.shortcuts import render
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Max
from django.shortcuts import get_object_or_404
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    UserSummarySerializer,
    ConversationSerializer,
    ConversationListSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
    MessageSummarySerializer,
)
from .permissions import (
    UserPermission,
    ConversationPermission,
    MessagePermission,
    IsParticipantInConversation,
    IsMessageSenderOrParticipant,
    CanManageConversationParticipants,
)


class StandardResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class for API responses
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model
    Provides CRUD operations for users with enhanced permissions
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermission]
    pagination_class = StandardResultsSetPagination
    lookup_field = "user_id"
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_online", "created_at"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["created_at", "last_seen", "username"]

    def get_serializer_class(self):
        """
        Return different serializers based on action
        """
        if self.action in ["list", "retrieve"]:
            return UserSummarySerializer
        return UserSerializer

    def get_queryset(self):
        """
        Filter queryset based on user permissions
        """
        if self.request.user.is_staff:
            return User.objects.all()

        # Regular users can see all users but with limited information
        return User.objects.all()

    @action(detail=True, methods=["post"], permission_classes=[UserPermission])
    def set_online_status(self, request, user_id=None):
        """
        Set user online status - only user can set their own status
        """
        user = self.get_object()

        # Check if user is setting their own status
        if user.user_id != request.user.user_id:
            return Response(
                {"error": "You can only set your own online status"},
                status=status.HTTP_403_FORBIDDEN,
            )

        is_online = request.data.get("is_online", False)
        user.is_online = is_online
        user.save()
        serializer = UserSummarySerializer(user)
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversation model
    Handles listing, creating, updating, and deleting conversations with enhanced permissions
    """

    permission_classes = [ConversationPermission]
    pagination_class = StandardResultsSetPagination
    lookup_field = "conversation_id"
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["created_at", "updated_at"]
    search_fields = ["participants__username", "participants__email"]
    ordering_fields = ["created_at", "updated_at", "last_message_time"]

    def get_queryset(self):
        """
        Get conversations where the current user is a participant
        """
        return (
            Conversation.objects.filter(participants=self.request.user)
            .annotate(
                message_count=Count("messages"),
                last_message_time=Max("messages__sent_at"),
            )
            .order_by("-last_message_time")
        )

    def get_serializer_class(self):
        """
        Return different serializers based on action
        """
        if self.action == "list":
            return ConversationListSerializer
        elif self.action == "retrieve":
            return ConversationDetailSerializer
        return ConversationSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation
        Automatically adds the current user as a participant
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get participant IDs from request
        participant_ids = request.data.get("participant_ids", [])

        # Add current user to participants if not already included
        current_user_id = str(request.user.user_id)
        if current_user_id not in participant_ids:
            participant_ids.append(current_user_id)

        # Create conversation
        conversation = serializer.save()

        # Add participants
        participants = User.objects.filter(user_id__in=participant_ids)
        conversation.participants.set(participants)

        # Return detailed serializer response
        response_serializer = ConversationDetailSerializer(conversation)
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        """
        Update conversation (mainly for adding/removing participants)
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return detailed response
        response_serializer = ConversationDetailSerializer(instance)
        return Response(response_serializer.data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[CanManageConversationParticipants],
    )
    def add_participant(self, request, conversation_id=None):
        """
        Add a participant to the conversation
        """
        conversation = self.get_object()
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
            serializer = ConversationDetailSerializer(conversation)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[CanManageConversationParticipants],
    )
    def remove_participant(self, request, conversation_id=None):
        """
        Remove a participant from the conversation
        """
        conversation = self.get_object()
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.remove(user)
            serializer = ConversationDetailSerializer(conversation)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["get"])
    def messages(self, request, conversation_id=None):
        """
        Get all messages in a conversation with pagination
        """
        conversation = self.get_object()
        messages = conversation.messages.all().order_by("-sent_at")

        # Apply pagination
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSummarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MessageSummarySerializer(messages, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Message model
    Handles creating, listing, updating, and deleting messages with enhanced permissions
    """

    serializer_class = MessageSerializer
    permission_classes = [MessagePermission]
    pagination_class = StandardResultsSetPagination
    lookup_field = "message_id"
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["conversation", "sender", "sent_at", "created_at"]
    search_fields = ["message_body", "sender__username"]
    ordering_fields = ["sent_at", "created_at", "updated_at"]

    def get_queryset(self):
        """
        Get messages from conversations where the current user is a participant
        """
        user_conversations = Conversation.objects.filter(participants=self.request.user)
        return Message.objects.filter(conversation__in=user_conversations).order_by(
            "-sent_at"
        )

    def get_serializer_class(self):
        """
        Return different serializers based on action
        """
        if self.action == "list":
            return MessageSummarySerializer
        return MessageSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new message
        Automatically sets the sender to the current user
        """
        data = request.data.copy()
        data["sender_id"] = request.user.user_id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        """
        Update a message (only sender can update their own messages)
        """
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a message (only sender can delete their own messages)
        """
        self.perform_destroy(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def my_messages(self, request):
        """
        Get all messages sent by the current user
        """
        messages = Message.objects.filter(sender=request.user).order_by("-sent_at")

        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSummarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MessageSummarySerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def conversation_messages(self, request, message_id=None):
        """
        Get all messages from the same conversation as this message
        """
        message = self.get_object()
        conversation_messages = Message.objects.filter(
            conversation=message.conversation
        ).order_by("-sent_at")

        page = self.paginate_queryset(conversation_messages)
        if page is not None:
            serializer = MessageSummarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MessageSummarySerializer(conversation_messages, many=True)
        return Response(serializer.data)
