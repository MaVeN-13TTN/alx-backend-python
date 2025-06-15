from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.db.models import Q
from .models import User, Conversation, Message


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user_id == request.user.user_id


class IsParticipantInConversation(BasePermission):
    """
    Custom permission to ensure users can only access conversations they participate in.
    """

    def has_permission(self, request, view):
        # Allow access if user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # For Conversation objects
        if hasattr(obj, "participants"):
            return obj.participants.filter(user_id=request.user.user_id).exists()

        # For Message objects - check if user is participant in the conversation
        if hasattr(obj, "conversation"):
            return obj.conversation.participants.filter(
                user_id=request.user.user_id
            ).exists()

        return False


class IsMessageSenderOrParticipant(BasePermission):
    """
    Custom permission for messages:
    - Senders can read, update, and delete their own messages
    - Other conversation participants can only read messages
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        if not obj.conversation.participants.filter(
            user_id=request.user.user_id
        ).exists():
            return False

        # If it's a safe method (GET, HEAD, OPTIONS), allow if user is participant
        if request.method in SAFE_METHODS:
            return True

        # For write operations (PUT, PATCH, DELETE), only allow sender
        return obj.sender.user_id == request.user.user_id


class IsUserProfileOwner(BasePermission):
    """
    Custom permission to ensure users can only access and modify their own profile.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the requested user profile belongs to the authenticated user
        return obj.user_id == request.user.user_id


class CanManageConversationParticipants(BasePermission):
    """
    Custom permission for managing conversation participants.
    Only conversation participants can add/remove other participants.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # User must be a participant in the conversation to manage participants
        return obj.participants.filter(user_id=request.user.user_id).exists()


class ConversationPermission(BasePermission):
    """
    Comprehensive permission class for conversations:
    - Users can only see conversations they participate in
    - Users can create new conversations
    - Users can update conversations they participate in
    - Users can delete conversations they participate in
    """

    def has_permission(self, request, view):
        # Must be authenticated
        if not (request.user and request.user.is_authenticated):
            return False

        # Allow POST (create) for authenticated users
        if request.method == "POST":
            return True

        return True

    def has_object_permission(self, request, view, obj):
        # User must be a participant in the conversation
        return obj.participants.filter(user_id=request.user.user_id).exists()


class MessagePermission(BasePermission):
    """
    Comprehensive permission class for messages:
    - Users can only see messages from conversations they participate in
    - Users can create messages in conversations they participate in
    - Users can only update/delete their own messages
    """

    def has_permission(self, request, view):
        # Must be authenticated
        if not (request.user and request.user.is_authenticated):
            return False

        # For POST (create), check if user is participant in the specified conversation
        if request.method == "POST":
            conversation_id = request.data.get("conversation")
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(
                        conversation_id=conversation_id
                    )
                    return conversation.participants.filter(
                        user_id=request.user.user_id
                    ).exists()
                except Conversation.DoesNotExist:
                    return False

        return True

    def has_object_permission(self, request, view, obj):
        # User must be a participant in the conversation
        if not obj.conversation.participants.filter(
            user_id=request.user.user_id
        ).exists():
            return False

        # For safe methods, allow if user is participant
        if request.method in SAFE_METHODS:
            return True

        # For write operations, only allow message sender
        return obj.sender.user_id == request.user.user_id


class UserPermission(BasePermission):
    """
    Permission class for user operations:
    - Users can view their own profile and other users' basic info
    - Users can only update their own profile
    - Staff users have additional permissions
    """

    def has_permission(self, request, view):
        # Must be authenticated
        if not (request.user and request.user.is_authenticated):
            return False

        # Staff users can perform all operations
        if request.user.is_staff:
            return True

        # Regular users can view (GET) and create (POST) accounts
        if request.method in ["GET", "POST"]:
            return True

        return True

    def has_object_permission(self, request, view, obj):
        # Staff users can access any user object
        if request.user.is_staff:
            return True

        # For safe methods, allow access to any user (for basic info)
        if request.method in SAFE_METHODS:
            return True

        # For write operations, only allow access to own profile
        return obj.user_id == request.user.user_id
