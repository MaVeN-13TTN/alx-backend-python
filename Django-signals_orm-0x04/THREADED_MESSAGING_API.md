# Threaded Messaging API Documentation

This document provides comprehensive information about the threaded messaging system implemented in the Django messaging app.

## Overview

The messaging system supports threaded conversations where users can reply to specific messages, creating hierarchical discussions. The system uses advanced ORM techniques for efficient data retrieval and includes comprehensive notification and audit trail features.

## Features

- **Threaded Conversations**: Messages can be replies to other messages, creating conversation threads
- **Advanced ORM Optimization**: Uses `select_related` and `prefetch_related` for efficient database queries
- **Real-time Notifications**: Automatic notifications for new messages and edits
- **Message Edit History**: Complete audit trail of message modifications
- **User Data Cleanup**: Automatic cleanup of related data when users are deleted
- **Permission Control**: Built-in permission checks for message threading

## API Endpoints

### Messages

#### List Messages

```
GET /messaging/api/messages/
```

Returns paginated list of messages for the authenticated user.

**Response:**

```json
{
  "count": 25,
  "next": "http://localhost:8000/messaging/api/messages/?page=2",
  "previous": null,
  "results": [
    {
      "message_id": "123e4567-e89b-12d3-a456-426614174000",
      "sender": {
        "pk": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
      },
      "receiver": {
        "pk": 2,
        "username": "jane_doe",
        "email": "jane@example.com",
        "first_name": "Jane",
        "last_name": "Doe"
      },
      "content": "Hello, how are you?",
      "parent_message_id": null,
      "timestamp": "2025-06-15T10:30:00Z",
      "is_read": false,
      "edited": false,
      "edit_count": 0,
      "is_reply": false,
      "is_thread_starter": true,
      "thread_depth": 0,
      "reply_count": 3
    }
  ]
}
```

#### Create Message

```
POST /messaging/api/messages/
```

Creates a new message or reply.

**Request Body:**

```json
{
  "receiver": 2,
  "content": "This is my message",
  "parent_message_id": "123e4567-e89b-12d3-a456-426614174000" // Optional for replies
}
```

#### Get Message Thread

```
GET /messaging/api/messages/{message_id}/thread/
```

Returns the complete thread containing the specified message.

**Response:**

```json
{
  "root_message": {
    "message_id": "123e4567-e89b-12d3-a456-426614174000",
    "sender": {...},
    "receiver": {...},
    "content": "Original message",
    "timestamp": "2025-06-15T10:30:00Z",
    "is_reply": false,
    "is_thread_starter": true,
    "thread_depth": 0,
    "reply_count": 2,
    "replies": [
      {
        "message_id": "223e4567-e89b-12d3-a456-426614174001",
        "sender": {...},
        "receiver": {...},
        "content": "First reply",
        "timestamp": "2025-06-15T10:35:00Z",
        "is_reply": true,
        "is_thread_starter": false,
        "thread_depth": 1,
        "reply_count": 1,
        "replies": [...]
      }
    ]
  },
  "thread_stats": {
    "total_messages": 5,
    "max_depth": 3,
    "participants": ["john_doe", "jane_doe", "bob_smith"]
  }
}
```

#### Get Message Replies

```
GET /messaging/api/messages/{message_id}/replies/
```

Returns all replies (direct and nested) to a specific message.

#### Get Direct Replies Only

```
GET /messaging/api/messages/{message_id}/direct_replies/
```

Returns only direct replies to a specific message (not nested replies).

#### Get Thread Starters

```
GET /messaging/api/messages/threads/
```

Returns all messages that start threads (have no parent message).

#### Reply to Message

```
POST /messaging/api/messages/{message_id}/reply/
```

Creates a reply to a specific message.

**Request Body:**

```json
{
  "receiver": 2,
  "content": "This is my reply"
}
```

### Notifications

#### List Notifications

```
GET /messaging/api/notifications/
```

Returns paginated list of notifications for the authenticated user.

#### Mark Notification as Read

```
PATCH /messaging/api/notifications/{notification_id}/mark_read/
```

Marks a specific notification as read.

#### Mark All Notifications as Read

```
PATCH /messaging/api/notifications/mark_all_read/
```

Marks all notifications for the user as read.

### User Management

#### Get User Data Summary

```
GET /messaging/user/data-summary/
```

Returns a summary of user's data before deletion.

#### Delete User Account

```
DELETE /messaging/user/delete/
```

Deletes the user's account and all related data.

#### Delete User with Confirmation

```
POST /messaging/user/delete-with-confirmation/
```

Deletes the user's account with password confirmation.

**Request Body:**

```json
{
  "password": "user_password"
}
```

## Threading Model

### Message Model Fields

- `parent_message`: ForeignKey to self for threading support
- `is_reply`: Property indicating if message is a reply
- `is_thread_starter`: Property indicating if message starts a thread
- `thread_depth`: Property showing nesting level (0 for root messages)
- `reply_count`: Property showing total number of replies

### Threading Methods

#### `root_message`

Returns the root message of the thread.

#### `get_thread_messages()`

Returns all messages in the thread with optimized queries.

#### `get_all_replies()`

Returns all replies (direct and nested) to the message.

#### `get_direct_replies()`

Returns only direct replies to the message.

#### `can_reply_to(user)`

Checks if a user has permission to reply to the message.

## Query Optimization

The system uses several optimization techniques:

### Select Related

```python
Message.objects.select_related('sender', 'receiver', 'parent_message')
```

Reduces database queries by fetching related objects in a single query.

### Prefetch Related

```python
Message.objects.prefetch_related('replies', 'edit_history')
```

Efficiently loads reverse foreign key relationships.

### Thread Traversal

The `get_thread_messages()` method uses an optimized iterative approach to traverse the thread hierarchy without excessive database queries.

## Signals and Notifications

### Automatic Notifications

- New message notifications are created automatically
- Message edit notifications are sent to relevant users
- Notifications are marked as read when messages are read

### Message Edit History

- Complete audit trail of message modifications
- Tracks who made edits and when
- Preserves original content for comparison

### User Deletion Cleanup

- Automatic cleanup of messages, notifications, and histories
- Maintains data integrity through CASCADE relationships
- Comprehensive logging of cleanup operations

## Usage Examples

### Creating a Threaded Conversation

1. **Start a new conversation:**

```javascript
POST /
  messaging /
  api /
  messages /
  {
    receiver: 2,
    content: "Hey, want to discuss the project?",
  };
```

2. **Reply to the message:**

```javascript
POST /messaging/api/messages/123e4567-e89b-12d3-a456-426614174000/reply/
{
  "receiver": 1,
  "content": "Sure! What aspects do you want to cover?"
}
```

3. **Continue the thread:**

```javascript
POST /
  messaging /
  api /
  messages /
  {
    receiver: 2,
    content: "Let's start with the timeline",
    parent_message_id: "223e4567-e89b-12d3-a456-426614174001",
  };
```

### Retrieving Thread Data

1. **Get complete thread:**

```javascript
GET /messaging/api/messages/123e4567-e89b-12d3-a456-426614174000/thread/
```

2. **Get thread starters only:**

```javascript
GET /messaging/api/messages/threads/
```

3. **Get replies to a specific message:**

```javascript
GET /messaging/api/messages/223e4567-e89b-12d3-a456-426614174001/replies/
```

## Database Schema

### Message Table

```sql
CREATE TABLE messaging_messages (
    message_id UUID PRIMARY KEY,
    sender_id UUID REFERENCES users(user_id),
    receiver_id UUID REFERENCES users(user_id),
    content TEXT,
    parent_message_id UUID REFERENCES messaging_messages(message_id),
    timestamp TIMESTAMP,
    is_read BOOLEAN,
    edited BOOLEAN,
    edit_count INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Indexes for optimization
CREATE INDEX idx_parent_message ON messaging_messages(parent_message_id);
CREATE INDEX idx_receiver_timestamp ON messaging_messages(receiver_id, timestamp DESC);
CREATE INDEX idx_sender_timestamp ON messaging_messages(sender_id, timestamp DESC);
```

### Notification Table

```sql
CREATE TABLE messaging_notifications (
    notification_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    message_id UUID REFERENCES messaging_messages(message_id),
    notification_type VARCHAR(20),
    title VARCHAR(255),
    content TEXT,
    is_read BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Message History Table

```sql
CREATE TABLE messaging_message_history (
    history_id UUID PRIMARY KEY,
    message_id UUID REFERENCES messaging_messages(message_id),
    old_content TEXT,
    new_content TEXT,
    edit_reason VARCHAR(255),
    edited_by_id UUID REFERENCES users(user_id),
    edited_at TIMESTAMP
);
```

## Performance Considerations

1. **Thread Depth**: Deep threads may impact performance. Consider limiting thread depth.
2. **Pagination**: Always use pagination for large result sets.
3. **Caching**: Consider implementing Redis caching for frequently accessed threads.
4. **Database Indexes**: The system includes optimized indexes for common query patterns.

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successful requests
- `201 Created`: Successful resource creation
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server errors

## Security Considerations

1. **Permission Checks**: Users can only reply to messages they're involved in
2. **Data Privacy**: Users can only see their own messages and notifications
3. **Soft Deletion**: Consider implementing soft deletion for better data recovery
4. **Rate Limiting**: Implement rate limiting for message creation endpoints

## Testing

The system includes comprehensive test coverage:

- Unit tests for model methods and properties
- Integration tests for API endpoints
- Signal and cleanup tests
- Performance and optimization tests

Run tests with:

```bash
python manage.py test messaging
```

## Future Enhancements

Potential improvements to consider:

1. **Real-time Updates**: WebSocket support for live message updates
2. **Message Reactions**: Emoji reactions to messages
3. **File Attachments**: Support for file uploads in messages
4. **Message Formatting**: Rich text support with markdown
5. **Thread Subscriptions**: Users can subscribe to thread updates
6. **Advanced Search**: Full-text search across message content
7. **Message Templates**: Predefined message templates
8. **Bulk Operations**: Bulk message operations for administrators

This threaded messaging system provides a robust foundation for building sophisticated communication features in Django applications.
