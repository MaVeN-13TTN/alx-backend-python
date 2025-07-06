"""
Test configuration and fixtures for the messaging app.
"""

import pytest
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from chats.models import Conversation, Message

User = get_user_model()


@override_settings(
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
)
class BaseTestCase(APITestCase):
    """Base test case with common setup."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create test users
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="user1@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User1",
        )

        self.user2 = User.objects.create_user(
            username="testuser2",
            email="user2@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User2",
        )

        # Get authentication tokens
        self.refresh_token = RefreshToken.for_user(self.user1)
        self.access_token = self.refresh_token.access_token

        # Set up authenticated client
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def authenticate_as(self, user):
        """Authenticate as a specific user."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return refresh.access_token

    def create_conversation(self, participants=None):
        """Helper method to create a conversation."""
        if participants is None:
            participants = [self.user1, self.user2]

        conversation = Conversation.objects.create()
        conversation.participants.add(*participants)
        return conversation

    def create_message(self, sender=None, conversation=None, body="Test message"):
        """Helper method to create a message."""
        if sender is None:
            sender = self.user1
        if conversation is None:
            conversation = self.create_conversation()

        return Message.objects.create(
            sender=sender, conversation=conversation, message_body=body
        )


class QuickTestCase(BaseTestCase):
    """Quick smoke tests for basic functionality."""

    def test_models_creation(self):
        """Test that models can be created successfully."""
        # Test user creation
        user = User.objects.create_user(
            username="quicktest", email="quick@test.com", password="pass123"
        )
        self.assertEqual(user.username, "quicktest")
        self.assertIsNotNone(user.pk)

        # Test conversation creation
        conversation = Conversation.objects.create()
        conversation.participants.add(user, self.user1)
        self.assertEqual(conversation.participants.count(), 2)

        # Test message creation
        message = Message.objects.create(
            sender=user, conversation=conversation, message_body="Quick test message"
        )
        self.assertEqual(message.message_body, "Quick test message")

    def test_api_authentication(self):
        """Test that API requires authentication."""
        # Remove authentication
        self.client.credentials()

        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, 401)

        # Add authentication back
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, 200)

    def test_basic_api_endpoints(self):
        """Test that basic API endpoints are accessible."""
        # Test users endpoint
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, 200)

        # Test conversations endpoint
        response = self.client.get("/api/conversations/")
        self.assertEqual(response.status_code, 200)

        # Test messages endpoint
        response = self.client.get("/api/messages/")
        self.assertEqual(response.status_code, 200)

    def test_message_creation_flow(self):
        """Test complete message creation flow."""
        # Create conversation
        conversation_data = {"participant_ids": [str(self.user2.pk)]}
        response = self.client.post(
            "/api/conversations/", conversation_data, format="json"
        )
        self.assertEqual(response.status_code, 201)

        conversation_id = response.data["conversation_id"]

        # Send message
        message_data = {
            "conversation": conversation_id,
            "message_body": "Hello from test!",
        }
        response = self.client.post("/api/messages/", message_data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["message_body"], "Hello from test!")

    def test_pagination_works(self):
        """Test that pagination is working."""
        # Create multiple messages
        conversation = self.create_conversation()
        for i in range(25):
            self.create_message(conversation=conversation, body=f"Message {i}")

        # Test pagination
        response = self.client.get("/api/messages/?page_size=10")
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertEqual(len(response.data["results"]), 10)

    def test_filtering_works(self):
        """Test that filtering is working."""
        # Create conversation and messages
        conversation = self.create_conversation()
        message = self.create_message(
            conversation=conversation, body="Searchable message"
        )

        # Test filtering by conversation
        response = self.client.get(f"/api/messages/?conversation={conversation.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["results"]) >= 1)


# Pytest configuration for test discovery
def pytest_collection_modifyitems(config, items):
    """Configure pytest to find Django tests."""
    for item in items:
        # Add Django marker to all tests
        item.add_marker(pytest.mark.django_db)
