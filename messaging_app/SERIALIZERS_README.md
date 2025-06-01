# Django REST Framework Serializers Documentation

## Overview
This file contains comprehensive serializers for the messaging app with proper handling of nested relationships and many-to-many fields.

## Serializers

### 1. UserSerializer
**Purpose**: Full user serialization with password handling
**Features**:
- Password validation and hashing
- Confirm password validation
- Read-only fields for security

**Usage**:
```python
# Creating a user
data = {
    'username': 'john_doe',
    'email': 'john@example.com',
    'password': 'secure_password123',
    'confirm_password': 'secure_password123',
    'first_name': 'John',
    'last_name': 'Doe'
}
serializer = UserSerializer(data=data)
if serializer.is_valid():
    user = serializer.save()
```

### 2. UserSummarySerializer
**Purpose**: Lightweight user info for nested relationships
**Fields**: user_id, username, email, first_name, last_name, is_online, profile_picture

### 3. MessageSerializer
**Purpose**: Full message serialization with sender details
**Features**:
- Nested sender information (read-only)
- sender_id for creating messages (write-only)
- Automatic timestamp handling

**Usage**:
```python
# Creating a message
data = {
    'sender_id': user.user_id,
    'conversation': conversation.conversation_id,
    'message_body': 'Hello, world!'
}
serializer = MessageSerializer(data=data)
if serializer.is_valid():
    message = serializer.save()
```

### 4. MessageSummarySerializer
**Purpose**: Lightweight message info for conversation listings
**Fields**: message_id, sender, message_body, sent_at

### 5. ConversationSerializer
**Purpose**: Full conversation serialization with participants and messages
**Features**:
- Many-to-many participants handling
- participant_ids for adding/removing participants
- Nested messages and last_message
- Message count calculation

**Usage**:
```python
# Creating a conversation
data = {
    'participant_ids': [user1.user_id, user2.user_id]
}
serializer = ConversationSerializer(data=data)
if serializer.is_valid():
    conversation = serializer.save()
```

### 6. ConversationListSerializer
**Purpose**: Lightweight conversation listing
**Features**:
- Participants summary
- Last message preview
- Message count

### 7. ConversationDetailSerializer
**Purpose**: Detailed conversation view with all messages
**Features**:
- Paginated messages support
- Complete participant details
- Message count

**Usage**:
```python
# Get conversation with messages (limited)
serializer = ConversationDetailSerializer(
    conversation, 
    context={'request': request}  # For pagination support
)
data = serializer.data
```

## Nested Relationships Handled

### Many-to-Many: Conversation ↔ Users (participants)
- **Read**: `participants` field shows full user details
- **Write**: `participant_ids` field accepts list of user UUIDs
- **Update**: Can add/remove participants by updating `participant_ids`

### One-to-Many: Conversation → Messages
- **Read**: `messages` field shows all messages in conversation
- **Summary**: `last_message` shows most recent message
- **Count**: `message_count` shows total number of messages

### Foreign Key: Message → User (sender)
- **Read**: `sender` field shows full user details
- **Write**: `sender_id` field accepts user UUID

### Foreign Key: Message → Conversation
- **Read/Write**: `conversation` field handles conversation UUID

## API Response Examples

### User Response
```json
{
    "user_id": "uuid-here",
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "profile_picture": "https://example.com/avatar.jpg",
    "is_online": true,
    "last_seen": "2025-06-01T10:30:00Z",
    "created_at": "2025-06-01T09:00:00Z",
    "updated_at": "2025-06-01T10:30:00Z"
}
```

### Conversation Response
```json
{
    "conversation_id": "uuid-here",
    "participants": [
        {
            "user_id": "uuid-1",
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "is_online": true,
            "profile_picture": "https://example.com/avatar1.jpg"
        },
        {
            "user_id": "uuid-2",
            "username": "jane_smith",
            "email": "jane@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "is_online": false,
            "profile_picture": "https://example.com/avatar2.jpg"
        }
    ],
    "last_message": {
        "message_id": "uuid-here",
        "sender": {
            "user_id": "uuid-1",
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
    "created_at": "2025-06-01T09:00:00Z",
    "updated_at": "2025-06-01T10:25:00Z"
}
```

### Message Response
```json
{
    "message_id": "uuid-here",
    "sender": {
        "user_id": "uuid-1",
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

## Best Practices

1. **Use appropriate serializers for different contexts**:
   - List views: Use lightweight serializers (Summary/List versions)
   - Detail views: Use full serializers with nested data
   - Create/Update: Use main serializers with validation

2. **Handle many-to-many relationships**:
   - Use separate write fields (`participant_ids`) for cleaner API
   - Provide nested read fields for complete data

3. **Performance considerations**:
   - Summary serializers reduce data transfer
   - Pagination support in detail serializers
   - Selective field exposure based on use case

4. **Security**:
   - Password fields are write-only
   - Sensitive fields marked as read-only
   - Proper validation on all inputs
