# Messaging App API Documentation

## Overview

This document provides a comprehensive overview of the Messaging App API, including its architecture, available endpoints, data models, and usage instructions. The API is built using Django and Django REST Framework with JWT (JSON Web Token) authentication for secure access control.

## Project Structure

-   `messaging_app/`: Main Django project directory.
    -   `settings.py`: Project settings including JWT configuration.
    -   `urls.py`: Project-level URL routing.
-   `chats/`: Django app for messaging functionalities.
    -   `models.py`: Defines the database models (User, Conversation, Message).
    -   `views.py`: Contains the ViewSets for API endpoints with permissions.
    -   `serializers.py`: Defines how model instances are converted to JSON and vice-versa.
    -   `urls.py`: App-level URL routing.
    -   `auth.py`: JWT authentication views and custom authentication endpoints.
    -   `auth_urls.py`: Authentication-specific URL routing.
    -   `permissions.py`: Custom permission classes for access control.
-   `manage.py`: Django's command-line utility.
-   `requirements.txt`: Lists project dependencies including djangorestframework-simplejwt.
-   `db.sqlite3`: SQLite database file (for development).

## Core Models

1.  **User**: Extends Django's `AbstractUser` with fields like `user_id` (UUID), `phone_number`, `profile_picture`, `is_online`, `last_seen`.
    -   Table name: `users`
2.  **Conversation**: Represents a conversation between users.
    -   Fields: `conversation_id` (UUID), `participants` (ManyToManyField to User), `created_at`, `updated_at`.
    -   Table name: `conversations`
    -   Includes a `last_message` property.
3.  **Message**: Represents an individual message within a conversation.
    -   Fields: `message_id` (UUID), `sender` (ForeignKey to User), `conversation` (ForeignKey to Conversation), `message_body` (TextField), `sent_at`.
    -   Table name: `messages`

## Serializers

The API uses various serializers to handle data representation:

-   **UserSerializers**:
    -   `UserSerializer`: For full user details, including password handling.
    -   `UserSummarySerializer`: For lightweight user representation in nested structures.
-   **MessageSerializers**:
    -   `MessageSerializer`: For full message details, including the sender.
    -   `MessageSummarySerializer`: For concise message representation.
-   **ConversationSerializers**:
    -   `ConversationSerializer`: For general conversation details.
    -   `ConversationListSerializer`: For listing conversations with summary information (participants, last message, message count).
    -   `ConversationDetailSerializer`: For detailed view of a conversation, including paginated messages.

Nested relationships (e.g., participants in a conversation, messages in a conversation, sender of a message) are handled appropriately by these serializers.

## API Endpoints

All API endpoints are prefixed with `/api/`. JWT authentication is required for all protected endpoints. Django REST Framework's browsable API is available at `/api-auth/login/`.

### Base URL: `http://<your-domain>/api/`

## Authentication

This API uses JWT (JSON Web Token) authentication. To access protected endpoints, you must include a valid JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-access-token>
```

### Authentication Endpoints (`/api/auth/`)

#### 1. JWT Token Management
-   **`POST /auth/token/`**: Obtain JWT token pair (access + refresh tokens).
    -   Body: `{"username": "your-username", "password": "your-password"}`
    -   Response: `{"access": "access-token", "refresh": "refresh-token", "user": {...}}`

-   **`POST /auth/token/refresh/`**: Refresh access token using refresh token.
    -   Body: `{"refresh": "your-refresh-token"}`
    -   Response: `{"access": "new-access-token"}`

-   **`POST /auth/token/verify/`**: Verify token validity.
    -   Body: `{"token": "your-token"}`
    -   Response: `{}` (200 OK if valid, 401 if invalid)

#### 2. User Authentication
-   **`POST /auth/register/`**: Register a new user and get JWT tokens.
    -   Body: `{"username": "username", "email": "email@example.com", "password": "password", "confirm_password": "password", "first_name": "First", "last_name": "Last"}`
    -   Response: `{"user": {...}, "tokens": {"access": "...", "refresh": "..."}}`

-   **`POST /auth/login/`**: Login user and get JWT tokens.
    -   Body: `{"username": "username", "password": "password"}`
    -   Response: `{"user": {...}, "tokens": {"access": "...", "refresh": "..."}}`

-   **`POST /auth/logout/`**: Logout user (set offline status).
    -   Headers: `Authorization: Bearer <access-token>`
    -   Response: `{"message": "Successfully logged out"}`

-   **`GET /auth/profile/`**: Get current user profile.
    -   Headers: `Authorization: Bearer <access-token>`
    -   Response: User profile data

### 1. User Endpoints

-   **`GET /users/`**: List all users (paginated).
-   **`POST /users/`**: Create a new user.
    -   Required fields: `username`, `email`, `password`, `confirm_password`.
    -   Optional: `first_name`, `last_name`, `phone_number`.
-   **`GET /users/{user_id}/`**: Retrieve details of a specific user.
-   **`PUT /users/{user_id}/`**: Update a user's details.
-   **`PATCH /users/{user_id}/`**: Partially update a user's details.
-   **`DELETE /users/{user_id}/`**: Delete a user.
-   **`POST /users/{user_id}/set_online_status/`**: Set a user's online status.
    -   Body: `{"is_online": true/false}`

### 2. Conversation Endpoints

-   **`GET /conversations/`**: List conversations for the authenticated user (paginated).
    -   Includes message count and last message time.
-   **`POST /conversations/`**: Create a new conversation.
    -   Body: `{"participant_ids": ["user-uuid-1", "user-uuid-2"]}`
    -   The authenticated user is automatically added as a participant.
-   **`GET /conversations/{conversation_id}/`**: Retrieve details of a specific conversation.
    -   Includes participants and recent messages.
-   **`PUT /conversations/{conversation_id}/`**: Update a conversation (e.g., manage participants).
-   **`PATCH /conversations/{conversation_id}/`**: Partially update a conversation.
-   **`DELETE /conversations/{conversation_id}/`**: Delete a conversation.

#### Custom Conversation Actions:

-   **`POST /conversations/{conversation_id}/add_participant/`**: Add a user to a conversation.
    -   Body: `{"user_id": "user-uuid-to-add"}`
-   **`POST /conversations/{conversation_id}/remove_participant/`**: Remove a user from a conversation.
    -   Body: `{"user_id": "user-uuid-to-remove"}`
-   **`GET /conversations/{conversation_id}/messages/`**: List all messages within a specific conversation (paginated, newest first). This uses `NestedDefaultRouter`.
-   **`POST /conversations/{conversation_id}/messages/`**: Create a new message within a specific conversation.
    -   Body: `{"message_body": "Your message content"}`
-   **`GET /conversations/{conversation_id}/messages/{message_id}/`**: Retrieve a specific message within a conversation.
-   **`PUT /conversations/{conversation_id}/messages/{message_id}/`**: Update a specific message within a conversation.
-   **`PATCH /conversations/{conversation_id}/messages/{message_id}/`**: Partially update a specific message.
-   **`DELETE /conversations/{conversation_id}/messages/{message_id}/`**: Delete a specific message.

### 3. Message Endpoints (Standalone)

-   **`GET /messages/`**: List messages from conversations the authenticated user participates in (paginated, newest first).
-   **`POST /messages/`**: Send a new message.
    -   Body: `{"conversation": "conversation-uuid", "message_body": "Your message content"}`
    -   The sender is automatically set to the authenticated user.
-   **`GET /messages/{message_id}/`**: Retrieve details of a specific message.
-   **`PUT /messages/{message_id}/`**: Update a message. (Only sender can update)
-   **`PATCH /messages/{message_id}/`**: Partially update a message. (Only sender can update)
-   **`DELETE /messages/{message_id}/`**: Delete a message. (Only sender can delete)

#### Custom Message Actions:

-   **`GET /messages/my_messages/`**: Get all messages sent by the authenticated user (paginated).
-   **`GET /messages/{message_id}/conversation_messages/`**: Get all messages from the same conversation as the specified message.

## URL Routing

-   The main project URLs (`messaging_app/urls.py`) include the app-specific URLs from `chats.urls` under the `/api/` prefix.
-   `chats/urls.py` uses `routers.DefaultRouter()` for standard viewsets (User, Conversation, Message).
-   `rest_framework_nested.routers.NestedDefaultRouter` is used to create nested routes for messages within conversations (e.g., `/api/conversations/{conversation_id}/messages/`).
-   Authentication URLs are provided by Django REST Framework at `/api-auth/`.

## Key Features & Security

-   **JWT Authentication**: All API endpoints require JWT authentication using Bearer tokens.
-   **Token Security**:
    -   Access tokens expire after 60 minutes
    -   Refresh tokens expire after 7 days
    -   Token rotation and blacklisting enabled for enhanced security
-   **Permissions**:
    -   Users can only access conversations they participate in.
    -   Users can only edit/delete their own messages.
    -   Custom permission classes ensure proper access control:
        - `UserPermission`: Users can read all users but modify only their own profile
        - `ConversationPermission`: Users can only access conversations they participate in
        - `MessagePermission`: Users can only access messages in their conversations
-   **Data Validation**: Input data is validated by serializers. User participation is validated before message creation or conversation updates.
-   **Filtering and Searching**:
    -   `ConversationViewSet` supports filtering by `created_at`, `updated_at`, and searching by `participants__username`, `participants__email`.
    -   `MessageViewSet` supports filtering by `conversation`, `sender`, `sent_at`, `created_at`, and searching by `message_body`, `sender__username`.
    -   Ordering is available on various fields.
-   **Pagination**: List endpoints are paginated (default 20 items per page, max 100). Use `?page=<num>&page_size=<num>` to control pagination.
-   **Error Handling**: Standard HTTP error responses are used (e.g., 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found).

## Dependencies

-   Django
-   djangorestframework
-   djangorestframework-simplejwt (for JWT authentication)
-   django-filter
-   drf-nested-routers

Refer to `requirements.txt` for specific versions.

## JWT Configuration

The application is configured with the following JWT settings:

-   **Access Token Lifetime**: 60 minutes
-   **Refresh Token Lifetime**: 7 days
-   **Token Rotation**: Enabled (new refresh token issued on refresh)
-   **Blacklist After Rotation**: Enabled (old tokens are blacklisted)
-   **Algorithm**: HS256
-   **Auth Header Type**: Bearer
-   **Custom Claims**: username, email, user_id, is_staff

The JWT configuration can be found in `messaging_app/settings.py` under the `SIMPLE_JWT` section.

## Setup and Running the Project

1.  **Clone the repository.**
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Apply database migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
5.  **Create a superuser (optional, for admin panel access):**
    ```bash
    python manage.py createsuperuser
    ```
6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The API will typically be available at `http://127.0.0.1:8000/api/`.

## Testing the API

### JWT Authentication Flow

1. **Register a new user:**
   ```bash
   curl -X POST http://127.0.0.1:8000/api/auth/register/ \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "testpass123",
       "confirm_password": "testpass123",
       "first_name": "Test",
       "last_name": "User"
     }'
   ```

2. **Login to get JWT tokens:**
   ```bash
   curl -X POST http://127.0.0.1:8000/api/auth/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "testpass123"}'
   ```

3. **Use the access token for authenticated requests:**
   ```bash
   curl -X GET http://127.0.0.1:8000/api/conversations/ \
     -H "Authorization: Bearer <your-access-token>"
   ```

4. **Refresh token when needed:**
   ```bash
   curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
     -H "Content-Type: application/json" \
     -d '{"refresh": "<your-refresh-token>"}'
   ```

### Other Testing Methods

-   Use Django REST Framework's browsable API by navigating to `/api/` or specific endpoints in your browser (after authenticating).
-   Use tools like Postman, Insomnia, or Thunder Client for VS Code.
-   The `/api-auth/login/` endpoint is available for session-based authentication in the browsable API.

### Example API Usage

```bash
# Create a conversation
curl -X POST http://127.0.0.1:8000/api/conversations/ \
  -H "Authorization: Bearer <access-token>" \
  -H "Content-Type: application/json" \
  -d '{"participant_ids": ["user-uuid-1", "user-uuid-2"]}'

# Send a message
curl -X POST http://127.0.0.1:8000/api/messages/ \
  -H "Authorization: Bearer <access-token>" \
  -H "Content-Type: application/json" \
  -d '{"conversation": "conversation-uuid", "message_body": "Hello!"}'

# Get user profile
curl -X GET http://127.0.0.1:8000/api/auth/profile/ \
  -H "Authorization: Bearer <access-token>"
```

This `README.md` provides a consolidated summary of the project's documentation.
