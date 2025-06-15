from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
import json

User = get_user_model()


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
