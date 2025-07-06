"""
API test cases for the messaging app.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from chats.models import Conversation, Message
import json

User = get_user_model()


class AuthenticationTestCase(TestCase):
    """Test cases for authentication endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "confirm_password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_user_registration(self):
        """Test user registration endpoint."""
        url = reverse("auth:register")
        response = self.client.post(url, self.user_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])

        # Verify user was created
        user = User.objects.get(username="testuser")
        self.assertEqual(user.email, "test@example.com")

    def test_user_login(self):
        """Test user login endpoint."""
        # Create user first
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        url = reverse("auth:login")
        login_data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, login_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertIn("tokens", response.data)

    def test_jwt_token_obtain(self):
        """Test JWT token obtain endpoint."""
        # Create user first
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        url = reverse("auth:token_obtain_pair")
        token_data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, token_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_jwt_token_refresh(self):
        """Test JWT token refresh endpoint."""
        # Create user and get refresh token
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        refresh = RefreshToken.for_user(user)

        url = reverse("auth:token_refresh")
        refresh_data = {"refresh": str(refresh)}
        response = self.client.post(url, refresh_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_authentication_required(self):
        """Test that protected endpoints require authentication."""
        url = reverse("user-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserAPITestCase(TestCase):
    """Test cases for User API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        # Authenticate user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_get_user_list(self):
        """Test getting list of users."""
        url = reverse("user-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertTrue(len(response.data["results"]) >= 1)

    def test_get_user_detail(self):
        """Test getting user details."""
        url = reverse("user-detail", kwargs={"pk": self.user.user_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")

    def test_update_user_profile(self):
        """Test updating user profile."""
        url = reverse("user-detail", kwargs={"pk": self.user.user_id})
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone_number": "+1234567890",
        }
        response = self.client.patch(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Updated")
        self.assertEqual(response.data["phone_number"], "+1234567890")

    def test_set_online_status(self):
        """Test setting user online status."""
        url = reverse("user-set-online-status", kwargs={"pk": self.user.user_id})
        status_data = {"is_online": True}
        response = self.client.post(url, status_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_online)


class ConversationAPITestCase(TestCase):
    """Test cases for Conversation API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass123"
        )

        # Authenticate as user1
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_create_conversation(self):
        """Test creating a new conversation."""
        url = reverse("conversation-list")
        conversation_data = {"participant_ids": [str(self.user2.user_id)]}
        response = self.client.post(url, conversation_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("conversation_id", response.data)

        # Verify conversation was created
        conversation = Conversation.objects.get(
            conversation_id=response.data["conversation_id"]
        )
        self.assertIn(self.user1, conversation.participants.all())
        self.assertIn(self.user2, conversation.participants.all())

    def test_get_conversation_list(self):
        """Test getting list of conversations."""
        # Create a conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)

        url = reverse("conversation-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertTrue(len(response.data["results"]) >= 1)

    def test_get_conversation_detail(self):
        """Test getting conversation details."""
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)

        url = reverse(
            "conversation-detail", kwargs={"pk": conversation.conversation_id}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["conversation_id"], str(conversation.conversation_id)
        )

    def test_add_participant(self):
        """Test adding participant to conversation."""
        user3 = User.objects.create_user(
            username="user3", email="user3@example.com", password="pass123"
        )

        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)

        url = reverse(
            "conversation-add-participant", kwargs={"pk": conversation.conversation_id}
        )
        participant_data = {"user_id": str(user3.user_id)}
        response = self.client.post(url, participant_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(user3, conversation.participants.all())


class MessageAPITestCase(TestCase):
    """Test cases for Message API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username="sender", email="sender@example.com", password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="receiver", email="receiver@example.com", password="pass123"
        )

        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

        # Authenticate as user1
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_send_message(self):
        """Test sending a message."""
        url = reverse("message-list")
        message_data = {
            "conversation": str(self.conversation.conversation_id),
            "message_body": "Hello, this is a test message!",
        }
        response = self.client.post(url, message_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["message_body"], "Hello, this is a test message!"
        )
        self.assertEqual(response.data["sender"]["username"], "sender")

    def test_get_message_list(self):
        """Test getting list of messages."""
        # Create a message first
        Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Test message",
        )

        url = reverse("message-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertTrue(len(response.data["results"]) >= 1)

    def test_get_conversation_messages(self):
        """Test getting messages for a specific conversation."""
        # Create messages
        Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="First message",
        )
        Message.objects.create(
            sender=self.user2,
            conversation=self.conversation,
            message_body="Second message",
        )

        url = reverse(
            "conversation-messages-list",
            kwargs={"parent_lookup_conversation": self.conversation.conversation_id},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)

    def test_update_message(self):
        """Test updating a message."""
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Original message",
        )

        url = reverse("message-detail", kwargs={"pk": message.message_id})
        update_data = {"message_body": "Updated message"}
        response = self.client.patch(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message_body"], "Updated message")

    def test_delete_message(self):
        """Test deleting a message."""
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Message to delete",
        )

        url = reverse("message-detail", kwargs={"pk": message.message_id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Message.objects.filter(message_id=message.message_id).exists())

    def test_message_filtering(self):
        """Test message filtering by conversation."""
        # Create another conversation and message
        other_conversation = Conversation.objects.create()
        other_conversation.participants.add(self.user1)

        Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Message in main conversation",
        )
        Message.objects.create(
            sender=self.user1,
            conversation=other_conversation,
            message_body="Message in other conversation",
        )

        url = reverse("message-list")
        response = self.client.get(
            url, {"conversation": str(self.conversation.conversation_id)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["message_body"], "Message in main conversation"
        )

    def test_pagination(self):
        """Test message pagination."""
        # Create multiple messages
        for i in range(25):
            Message.objects.create(
                sender=self.user1,
                conversation=self.conversation,
                message_body=f"Message {i}",
            )

        url = reverse("message-list")
        response = self.client.get(url, {"page_size": 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIn("next", response.data)
        self.assertEqual(response.data["count"], 25)


class PermissionTestCase(TestCase):
    """Test cases for API permissions."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass123"
        )

        # Create conversation between users
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

        # Create message
        self.message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Test message",
        )

    def test_user_cannot_access_other_conversations(self):
        """Test that users cannot access conversations they're not part of."""
        # Create third user
        user3 = User.objects.create_user(
            username="user3", email="user3@example.com", password="pass123"
        )

        # Authenticate as user3
        refresh = RefreshToken.for_user(user3)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        url = reverse(
            "conversation-detail", kwargs={"pk": self.conversation.conversation_id}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_edit_other_users_messages(self):
        """Test that users cannot edit messages they didn't send."""
        # Authenticate as user2 (not the sender)
        refresh = RefreshToken.for_user(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        url = reverse("message-detail", kwargs={"pk": self.message.message_id})
        update_data = {"message_body": "Trying to edit other user message"}
        response = self.client.patch(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_only_edit_own_profile(self):
        """Test that users can only edit their own profile."""
        # Authenticate as user1
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Try to edit user2's profile
        url = reverse("user-detail", kwargs={"pk": self.user2.user_id})
        update_data = {"first_name": "Hacked"}
        response = self.client.patch(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
