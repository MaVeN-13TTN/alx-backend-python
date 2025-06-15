from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework import status, permissions, generics, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.db.models import Q, Prefetch
import json

from .models import Message, Notification, MessageHistory
from .serializers import (
    MessageSerializer,
    MessageListSerializer,
    MessageThreadSerializer,
    CreateMessageSerializer,
    NotificationSerializer,
    NotificationListSerializer,
)

User = get_user_model()


class MessagePagination(PageNumberPagination):
    """Custom pagination for messages"""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages with threading support
    """

    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessagePagination

    def get_queryset(self):
        """
        Get messages for the authenticated user with optimized queries
        """
        user = self.request.user
        return (
            Message.objects.filter(Q(sender=user) | Q(receiver=user))
            .select_related("sender", "receiver", "parent_message")
            .prefetch_related("replies", "edit_history")
            .order_by("-timestamp")
        )

    def get_serializer_class(self):
        """
        Use different serializers for different actions
        """
        if self.action == "list":
            return MessageListSerializer
        elif self.action == "create":
            return CreateMessageSerializer
        elif self.action == "thread":
            return MessageThreadSerializer
        return MessageSerializer

    @action(detail=True, methods=["get"])
    def thread(self, request, pk=None):
        """
        Get the complete thread for a message
        """
        message = self.get_object()
        root_message = message.root_message

        # Get all messages in the thread with optimized loading
        thread_messages = root_message.get_thread_messages()

        serializer = MessageThreadSerializer(root_message, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def replies(self, request, pk=None):
        """
        Get all replies to a message
        """
        message = self.get_object()
        replies = message.get_all_replies()

        page = self.paginate_queryset(replies)
        if page is not None:
            serializer = MessageListSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = MessageListSerializer(
            replies, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def direct_replies(self, request, pk=None):
        """
        Get only direct replies to a message
        """
        message = self.get_object()
        direct_replies = message.get_direct_replies()

        page = self.paginate_queryset(direct_replies)
        if page is not None:
            serializer = MessageListSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = MessageListSerializer(
            direct_replies, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def threads(self, request):
        """
        Get all thread starter messages (messages with no parent)
        """
        user = request.user
        thread_starters = (
            Message.objects.filter(
                Q(sender=user) | Q(receiver=user), parent_message__isnull=True
            )
            .select_related("sender", "receiver")
            .prefetch_related("replies")
            .order_by("-timestamp")
        )

        page = self.paginate_queryset(thread_starters)
        if page is not None:
            serializer = MessageListSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = MessageListSerializer(
            thread_starters, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def unread(self, request):
        """
        Get unread messages for the authenticated user using custom manager
        """
        user = request.user
        # Using the custom manager with .only() optimization
        unread_messages = Message.unread.unread_for_user(user)

        page = self.paginate_queryset(unread_messages)
        if page is not None:
            serializer = MessageListSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = MessageListSerializer(
            unread_messages, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def inbox(self, request):
        """
        Get user's inbox with unread messages and threading info
        """
        user = request.user
        inbox_messages = Message.unread_messages.inbox_for_user(user)

        page = self.paginate_queryset(inbox_messages)
        if page is not None:
            serializer = MessageListSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = MessageListSerializer(
            inbox_messages, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """
        Get count of unread messages for the authenticated user
        """
        user = request.user
        count = Message.unread_messages.unread_count_for_user(user)

        return Response({"unread_count": count, "user": user.username})

    @action(detail=False, methods=["get"])
    def unread_threads(self, request):
        """
        Get unread thread starter messages for the authenticated user
        """
        user = request.user
        unread_threads = Message.unread_messages.unread_threads_for_user(user)

        page = self.paginate_queryset(unread_threads)
        if page is not None:
            serializer = MessageListSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = MessageListSerializer(
            unread_threads, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["patch"])
    def mark_read(self, request, pk=None):
        """
        Mark a message as read
        """
        message = self.get_object()

        # Only allow receiver to mark message as read
        if request.user != message.receiver:
            return Response(
                {"error": "You can only mark your own received messages as read"},
                status=status.HTTP_403_FORBIDDEN,
            )

        message.is_read = True
        message.save(update_fields=["is_read"])

        serializer = self.get_serializer(message)
        return Response(serializer.data)

    @action(detail=False, methods=["patch"])
    def mark_all_read(self, request):
        """
        Mark all unread messages as read for the authenticated user
        """
        user = request.user
        updated_count = Message.objects.filter(receiver=user, is_read=False).update(
            is_read=True
        )

        return Response(
            {
                "message": f"Marked {updated_count} messages as read",
                "count": updated_count,
                "user": user.username,
            }
        )

    def perform_create(self, serializer):
        """
        Set the sender to the current authenticated user when creating a message
        """
        serializer.save(sender=self.request.user)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing notifications
    """

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessagePagination

    def get_queryset(self):
        """
        Get notifications for the authenticated user
        """
        return (
            Notification.objects.filter(user=self.request.user)
            .select_related("user", "message", "message__sender", "message__receiver")
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        """
        Use different serializers for different actions
        """
        if self.action == "list":
            return NotificationListSerializer
        return NotificationSerializer

    @action(detail=True, methods=["patch"])
    def mark_read(self, request, pk=None):
        """
        Mark a notification as read
        """
        notification = self.get_object()
        notification.is_read = True
        notification.save()

        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=["patch"])
    def mark_all_read(self, request):
        """
        Mark all notifications as read for the user
        """
        count = Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True
        )

        return Response(
            {"message": f"Marked {count} notifications as read", "count": count}
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_message_thread(request, message_id):
    """
    Get the complete thread for a specific message
    """
    try:
        # Optimize the initial message query
        message = get_object_or_404(
            Message.objects.select_related("sender", "receiver", "parent_message"),
            message_id=message_id,
        )

        # Check if user has permission to view this message
        if request.user not in [message.sender, message.receiver]:
            return Response(
                {"error": "You do not have permission to view this message"},
                status=status.HTTP_403_FORBIDDEN,
            )

        root_message = message.root_message
        thread_messages = root_message.get_thread_messages()

        # Serialize the thread data
        serializer = MessageThreadSerializer(root_message, context={"request": request})

        return Response(
            {
                "root_message": serializer.data,
                "thread_stats": {
                    "total_messages": thread_messages.count(),
                    "max_depth": max(
                        [msg.thread_depth for msg in thread_messages] + [0]
                    ),
                    "participants": list(
                        set(
                            [msg.sender.username for msg in thread_messages]
                            + [msg.receiver.username for msg in thread_messages]
                        )
                    ),
                },
            }
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def reply_to_message(request, message_id):
    """
    Reply to a specific message
    """
    try:
        # Optimize the parent message query
        parent_message = get_object_or_404(
            Message.objects.select_related("sender", "receiver", "parent_message"),
            message_id=message_id,
        )

        # Check if user can reply to this message
        if not parent_message.can_reply_to(request.user):
            return Response(
                {"error": "You do not have permission to reply to this message"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Create the reply with sender automatically set
        serializer = CreateMessageSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            reply = serializer.save(sender=request.user, parent_message=parent_message)

            # Return the created reply
            response_serializer = MessageSerializer(reply, context={"request": request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_user_account(request):
    """
    API view to delete a user's account and all associated data.

    This view handles user account deletion with proper cleanup of related data.
    The actual cleanup is handled by post_delete signals.

    Args:
        request: The HTTP request object

    Returns:
        Response: JSON response indicating success or failure
    """
    try:
        user = request.user
        user_id = user.pk
        username = user.username

        # Log the deletion attempt
        print(f"User deletion initiated: {username} (ID: {user_id})")

        # Use transaction to ensure atomicity
        with transaction.atomic():
            # Delete the user (signals will handle cleanup of related data)
            user.delete()

        # Log successful deletion
        print(f"User successfully deleted: {username} (ID: {user_id})")

        return Response(
            {
                "success": True,
                "message": f"User account {username} has been successfully deleted.",
                "deleted_user_id": str(user_id),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        print(f"Error deleting user {request.user.username}: {str(e)}")
        return Response(
            {
                "success": False,
                "message": "An error occurred while deleting the user account.",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def delete_user_with_confirmation(request):
    """
    API view to delete a user's account with password confirmation.

    This provides an additional security layer by requiring password confirmation
    before allowing account deletion.

    Args:
        request: The HTTP request object with password in body

    Returns:
        Response: JSON response indicating success or failure
    """
    try:
        # Get password from request data
        password = request.data.get("password")

        if not password:
            return Response(
                {
                    "success": False,
                    "message": "Password confirmation is required for account deletion.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user

        # Verify password
        if not user.check_password(password):
            return Response(
                {
                    "success": False,
                    "message": "Invalid password. Account deletion cancelled.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = user.pk
        username = user.username

        # Log the deletion attempt
        print(f"Confirmed user deletion initiated: {username} (ID: {user_id})")

        # Use transaction to ensure atomicity
        with transaction.atomic():
            # Delete the user (signals will handle cleanup of related data)
            user.delete()

        # Log successful deletion
        print(
            f"User successfully deleted with confirmation: {username} (ID: {user_id})"
        )

        return Response(
            {
                "success": True,
                "message": f"User account {username} has been successfully deleted with confirmation.",
                "deleted_user_id": str(user_id),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        print(
            f"Error deleting user with confirmation {request.user.username}: {str(e)}"
        )
        return Response(
            {
                "success": False,
                "message": "An error occurred while deleting the user account.",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_user_data_summary(request):
    """
    API view to get a summary of user's data before deletion.

    This helps users understand what data will be deleted when they
    delete their account.

    Args:
        request: The HTTP request object

    Returns:
        Response: JSON response with user data summary
    """
    try:
        user = request.user

        # Import models here to avoid circular imports
        from .models import Message, Notification, MessageHistory

        # Count user's data
        sent_messages = Message.objects.filter(sender=user).count()
        received_messages = Message.objects.filter(receiver=user).count()
        notifications = Notification.objects.filter(user=user).count()
        message_histories = MessageHistory.objects.filter(edited_by=user).count()

        # Also count data from messages the user received (history from other users editing)
        received_message_histories = MessageHistory.objects.filter(
            message__receiver=user
        ).count()

        return Response(
            {
                "user_info": {
                    "username": user.username,
                    "email": user.email,
                    "date_joined": user.date_joined,
                    "last_login": user.last_login,
                },
                "data_summary": {
                    "sent_messages": sent_messages,
                    "received_messages": received_messages,
                    "total_messages": sent_messages + received_messages,
                    "notifications": notifications,
                    "message_edit_histories": message_histories,
                    "received_message_histories": received_message_histories,
                    "total_histories": message_histories + received_message_histories,
                },
                "deletion_impact": {
                    "messages_to_delete": sent_messages + received_messages,
                    "notifications_to_delete": notifications,
                    "histories_to_delete": message_histories
                    + received_message_histories,
                },
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        print(f"Error getting user data summary for {request.user.username}: {str(e)}")
        return Response(
            {
                "success": False,
                "message": "An error occurred while retrieving user data summary.",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_message(request):
    """
    Create a new message or reply with proper optimization
    """
    try:
        serializer = CreateMessageSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            # Save with sender automatically set
            message = serializer.save(sender=request.user)

            # Return the created message with optimized loading
            response_serializer = MessageSerializer(
                Message.objects.select_related("sender", "receiver", "parent_message")
                .prefetch_related("replies", "edit_history")
                .get(pk=message.pk),
                context={"request": request},
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_unread_messages(request):
    """
    Get unread messages for the authenticated user using custom manager
    This view uses the custom manager to display only unread messages in a user's inbox
    """
    try:
        user = request.user
        # Using the custom manager with .only() optimization for unread messages
        unread_messages = Message.unread.unread_for_user(user)

        # Apply pagination
        paginator = MessagePagination()
        page = paginator.paginate_queryset(unread_messages, request)

        if page is not None:
            serializer = MessageListSerializer(
                page, many=True, context={"request": request}
            )
            return paginator.get_paginated_response(serializer.data)

        serializer = MessageListSerializer(
            unread_messages, many=True, context={"request": request}
        )
        return Response(serializer.data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_user_inbox(request):
    """
    Get user's inbox with unread messages and threading information
    """
    try:
        user = request.user
        inbox_messages = Message.unread_messages.inbox_for_user(user)

        # Apply pagination
        paginator = MessagePagination()
        page = paginator.paginate_queryset(inbox_messages, request)

        if page is not None:
            serializer = MessageListSerializer(
                page, many=True, context={"request": request}
            )
            return paginator.get_paginated_response(serializer.data)

        serializer = MessageListSerializer(
            inbox_messages, many=True, context={"request": request}
        )
        return Response(
            {
                "inbox": serializer.data,
                "unread_count": Message.unread_messages.unread_count_for_user(user),
                "user": user.username,
            }
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def mark_message_read(request, message_id):
    """
    Mark a specific message as read
    """
    try:
        message = get_object_or_404(
            Message.objects.select_related("sender", "receiver"), message_id=message_id
        )

        # Only allow receiver to mark message as read
        if request.user != message.receiver:
            return Response(
                {"error": "You can only mark your own received messages as read"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if message.is_read:
            return Response(
                {"message": "Message is already marked as read"},
                status=status.HTTP_200_OK,
            )

        message.is_read = True
        message.save(update_fields=["is_read"])

        serializer = MessageSerializer(message, context={"request": request})
        return Response({"message": "Message marked as read", "data": serializer.data})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def mark_all_messages_read(request):
    """
    Mark all unread messages as read for the authenticated user
    """
    try:
        user = request.user
        updated_count = Message.objects.filter(receiver=user, is_read=False).update(
            is_read=True
        )

        return Response(
            {
                "message": f"Marked {updated_count} messages as read",
                "count": updated_count,
                "user": user.username,
            }
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_unread_count(request):
    """
    Get count of unread messages for the authenticated user
    """
    try:
        user = request.user
        count = Message.unread_messages.unread_count_for_user(user)

        return Response({"unread_count": count, "user": user.username})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@action(detail=False, methods=["get"])
def inbox_unread(self, request):
    """
    Display only unread messages in a user's inbox with .only() optimization
    This method demonstrates explicit use of .only() to retrieve only necessary fields
    """
    user = request.user

    # Using .only() to retrieve only necessary fields for inbox display
    unread_inbox_messages = (
        Message.objects.filter(receiver=user, is_read=False)
        .select_related("sender", "parent_message")
        .only(
            "message_id",
            "content",
            "timestamp",
            "is_read",
            "sender__username",
            "sender__first_name",
            "sender__last_name",
            "parent_message__content",
        )
        .order_by("-timestamp")
    )

    page = self.paginate_queryset(unread_inbox_messages)
    if page is not None:
        serializer = MessageListSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    serializer = MessageListSerializer(
        unread_inbox_messages, many=True, context={"request": request}
    )
    return Response(serializer.data)
