# API Endpoints Test and Documentation

## Available API Endpoints

### Authentication
All endpoints require authentication. Use Django's built-in authentication or implement token authentication.

### Base URL: `/api/v1/`

## 1. Users API

### List Users
```
GET /api/v1/users/
```
Returns paginated list of users (summary view).

### Create User
```
POST /api/v1/users/
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password123",
    "confirm_password": "secure_password123",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890"
}
```

### Get User Details
```
GET /api/v1/users/{user_id}/
```

### Update User
```
PUT /api/v1/users/{user_id}/
PATCH /api/v1/users/{user_id}/
```

### Set Online Status
```
POST /api/v1/users/{user_id}/set_online_status/
Content-Type: application/json

{
    "is_online": true
}
```

## 2. Conversations API

### List Conversations
```
GET /api/v1/conversations/
```
Returns conversations where the authenticated user is a participant.

### Create Conversation
```
POST /api/v1/conversations/
Content-Type: application/json

{
    "participant_ids": ["user-uuid-1", "user-uuid-2"]
}
```
Note: Current user is automatically added as participant.

### Get Conversation Details
```
GET /api/v1/conversations/{conversation_id}/
```
Returns detailed conversation with messages.

### Update Conversation
```
PUT /api/v1/conversations/{conversation_id}/
PATCH /api/v1/conversations/{conversation_id}/
Content-Type: application/json

{
    "participant_ids": ["user-uuid-1", "user-uuid-2", "user-uuid-3"]
}
```

### Add Participant
```
POST /api/v1/conversations/{conversation_id}/add_participant/
Content-Type: application/json

{
    "user_id": "user-uuid-to-add"
}
```

### Remove Participant
```
POST /api/v1/conversations/{conversation_id}/remove_participant/
Content-Type: application/json

{
    "user_id": "user-uuid-to-remove"
}
```

### Get Conversation Messages
```
GET /api/v1/conversations/{conversation_id}/messages/
```
Returns paginated messages in the conversation.

## 3. Messages API

### List Messages
```
GET /api/v1/messages/
```
Returns messages from conversations where user is a participant.

### Send Message
```
POST /api/v1/messages/
Content-Type: application/json

{
    "conversation": "conversation-uuid",
    "message_body": "Hello, how are you doing today?"
}
```
Note: Sender is automatically set to authenticated user.

### Get Message Details
```
GET /api/v1/messages/{message_id}/
```

### Update Message
```
PUT /api/v1/messages/{message_id}/
PATCH /api/v1/messages/{message_id}/
Content-Type: application/json

{
    "message_body": "Updated message content"
}
```
Note: Only message sender can update their messages.

### Delete Message
```
DELETE /api/v1/messages/{message_id}/
```
Note: Only message sender can delete their messages.

### Get My Messages
```
GET /api/v1/messages/my_messages/
```
Returns all messages sent by the authenticated user.

### Get Conversation Messages (from message)
```
GET /api/v1/messages/{message_id}/conversation_messages/
```
Returns all messages from the same conversation as the specified message.

## API Response Examples

### Conversation List Response
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/v1/conversations/?page=2",
    "previous": null,
    "results": [
        {
            "conversation_id": "uuid-here",
            "participants": [
                {
                    "user_id": "user-uuid-1",
                    "username": "john_doe",
                    "email": "john@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "is_online": true,
                    "profile_picture": "https://example.com/avatar1.jpg"
                }
            ],
            "last_message": {
                "message_id": "message-uuid",
                "sender": {
                    "user_id": "user-uuid-1",
                    "username": "john_doe",
                    "email": "john@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "is_online": true,
                    "profile_picture": "https://example.com/avatar1.jpg"
                },
                "message_body": "Hello there!",
                "sent_at": "2025-06-01T10:25:00Z"
            },
            "message_count": 15,
            "updated_at": "2025-06-01T10:25:00Z"
        }
    ]
}
```

### Message Creation Response
```json
{
    "message_id": "message-uuid-here",
    "sender": {
        "user_id": "user-uuid-1",
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_online": true,
        "profile_picture": "https://example.com/avatar1.jpg"
    },
    "conversation": "conversation-uuid-here",
    "message_body": "Hello, how are you doing today?",
    "sent_at": "2025-06-01T10:25:00Z",
    "created_at": "2025-06-01T10:25:00Z",
    "updated_at": "2025-06-01T10:25:00Z"
}
```

## Security Features

1. **Authentication Required**: All endpoints require user authentication
2. **Participant Validation**: Users can only access conversations they participate in
3. **Message Ownership**: Users can only edit/delete their own messages
4. **Automatic User Assignment**: Current user automatically set as sender for messages
5. **Permission Checks**: Proper permission checks for all operations

## Pagination

All list endpoints support pagination with the following parameters:
- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 20, max: 100)

Example: `/api/v1/conversations/?page=2&page_size=10`

## Error Responses

### 400 Bad Request
```json
{
    "error": "Validation error message"
}
```

### 403 Forbidden
```json
{
    "error": "You are not a participant in this conversation"
}
```

### 404 Not Found
```json
{
    "error": "Conversation not found"
}
```

## Testing the API

You can test the API using:
1. Django REST Framework's browsable API at `/api/v1/`
2. Tools like Postman or curl
3. Django's test client
4. Frontend applications

Example curl command:
```bash
curl -X POST http://localhost:8000/api/v1/conversations/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Token your-auth-token" \
     -d '{"participant_ids": ["user-uuid-1", "user-uuid-2"]}'
```
