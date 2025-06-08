# 🧪 API Testing Guide with Postman

## 📁 Postman Collection: `post_man-Collections`

This comprehensive guide will walk you through testing all API endpoints using the Postman collection.

## 🚀 Getting Started

### 1. Import the Collection
1. Open Postman
2. Click "Import" 
3. Select the file: `post_man-Collections`
4. The collection "Messaging App API" will be imported

### 2. Set Up Environment
Create a new environment in Postman with these variables:
- `base_url`: `http://localhost:8000`
- `access_token`: (will be set automatically after login)
- `refresh_token`: (will be set automatically after login)

## 🔐 Authentication Testing

### Step 1: Register a New User
**Endpoint:** `POST /api/auth/register/`
```json
{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User"
}
```
**Expected:** 201 Created with user details

### Step 2: Login to Get JWT Token
**Endpoint:** `POST /api/auth/token/`
```json
{
    "username": "testuser",
    "password": "testpass123"
}
```
**Expected:** 200 OK with access and refresh tokens
**Note:** The collection automatically saves tokens to environment variables

### Step 3: Test Token Refresh
**Endpoint:** `POST /api/auth/token/refresh/`
```json
{
    "refresh": "{{refresh_token}}"
}
```
**Expected:** 200 OK with new access token

### Step 4: Get User Profile
**Endpoint:** `GET /api/auth/profile/`
**Headers:** `Authorization: Bearer {{access_token}}`
**Expected:** 200 OK with user profile data

## 👥 User Management Testing

### List Users
**Endpoint:** `GET /api/users/`
**Headers:** `Authorization: Bearer {{access_token}}`
**Test Pagination:** `GET /api/users/?page=1&page_size=10`
**Test Filtering:** `GET /api/users/?username=test&is_online=true`

### Get Specific User
**Endpoint:** `GET /api/users/{user_id}/`
**Expected:** 200 OK with user details

## 💬 Conversation Testing

### Step 1: Create a Conversation
**Endpoint:** `POST /api/conversations/`
**Headers:** `Authorization: Bearer {{access_token}}`
```json
{
    "participant_ids": ["fd52863a-9f0a-4678-b674-025b308a7471"]
}
```
**Expected:** 201 Created with conversation details
**Note:** Current user is automatically added as participant

### Step 2: List Conversations
**Endpoint:** `GET /api/conversations/`
**Headers:** `Authorization: Bearer {{access_token}}`
**Test Pagination:** `GET /api/conversations/?page=1&page_size=5`
**Test Filtering:** `GET /api/conversations/?participant_username=testuser`

### Step 3: Get Conversation Details
**Endpoint:** `GET /api/conversations/{conversation_id}/`
**Headers:** `Authorization: Bearer {{access_token}}`
**Expected:** 200 OK with conversation and participants

### Step 4: Add Participant to Conversation
**Endpoint:** `POST /api/conversations/{conversation_id}/add_participant/`
**Headers:** `Authorization: Bearer {{access_token}}`
```json
{
    "user_id": "new-user-id"
}
```

### Step 5: Remove Participant from Conversation
**Endpoint:** `POST /api/conversations/{conversation_id}/remove_participant/`
**Headers:** `Authorization: Bearer {{access_token}}`
```json
{
    "user_id": "user-id-to-remove"
}
```

## 📨 Message Testing

### Step 1: Send a Message
**Endpoint:** `POST /api/messages/`
**Headers:** `Authorization: Bearer {{access_token}}`
```json
{
    "conversation_id": "conversation-uuid",
    "message_body": "Hello! This is a test message."
}
```
**Expected:** 201 Created with message details
**Note:** Sender is automatically set to current user

### Step 2: List All Messages
**Endpoint:** `GET /api/messages/`
**Headers:** `Authorization: Bearer {{access_token}}`
**Expected:** 200 OK with paginated messages (20 per page)

### Step 3: Test Message Pagination
```bash
# Default pagination (20 per page)
GET /api/messages/

# Custom page size
GET /api/messages/?page_size=10

# Navigate pages
GET /api/messages/?page=2
```

### Step 4: Test Message Filtering
```bash
# Filter by sender username
GET /api/messages/?sender_username=testuser

# Filter by content
GET /api/messages/?message_body=hello

# Filter by date
GET /api/messages/?sent_date=2025-06-08

# Filter by time range
GET /api/messages/?sent_at_after=2025-06-08T10:00:00Z&sent_at_before=2025-06-08T18:00:00Z

# Filter by conversation participant
GET /api/messages/?conversation_participant=user-id
```

### Step 5: Get Messages in Conversation
**Endpoint:** `GET /api/conversations/{conversation_id}/messages/`
**Headers:** `Authorization: Bearer {{access_token}}`
**Expected:** 200 OK with paginated messages from that conversation

### Step 6: Get My Messages
**Endpoint:** `GET /api/messages/my_messages/`
**Headers:** `Authorization: Bearer {{access_token}}`
**Expected:** 200 OK with messages sent by current user

### Step 7: Update a Message
**Endpoint:** `PUT /api/messages/{message_id}/`
**Headers:** `Authorization: Bearer {{access_token}}`
```json
{
    "message_body": "Updated message content"
}
```
**Note:** Only message sender can update their own messages

### Step 8: Delete a Message
**Endpoint:** `DELETE /api/messages/{message_id}/`
**Headers:** `Authorization: Bearer {{access_token}}`
**Expected:** 204 No Content
**Note:** Only message sender can delete their own messages

## 🔒 Security Testing

### Test 1: Unauthorized Access
Try accessing endpoints without authentication:
```bash
GET /api/messages/
# Expected: 401 Unauthorized
```

### Test 2: Access Other User's Data
Try accessing conversations/messages you're not part of:
```bash
GET /api/conversations/other-user-conversation-id/
# Expected: 403 Forbidden or 404 Not Found
```

### Test 3: Token Expiration
Wait for token to expire or use invalid token:
```bash
Authorization: Bearer invalid_token
# Expected: 401 Unauthorized
```

## 📊 Test Scenarios

### Scenario 1: Complete Message Flow
1. Register two users
2. Login as User A
3. Create conversation with User B
4. Send messages as User A
5. Login as User B
6. View conversation and messages
7. Reply as User B
8. Test pagination and filtering

### Scenario 2: Permission Testing
1. Login as User A
2. Create conversation
3. Login as User B (not in conversation)
4. Try to access User A's conversation
5. Verify 403 Forbidden response

### Scenario 3: Pagination and Filtering
1. Create multiple messages
2. Test pagination with different page sizes
3. Test various filters (date, user, content)
4. Combine filtering with pagination

## 🎯 Expected Results Summary

| Test Case | Expected Status | Expected Response |
|-----------|----------------|-------------------|
| Register User | 201 Created | User details |
| Login | 200 OK | JWT tokens |
| Create Conversation | 201 Created | Conversation details |
| Send Message | 201 Created | Message details |
| List Messages | 200 OK | Paginated messages |
| Unauthorized Access | 401 Unauthorized | Error message |
| Forbidden Access | 403 Forbidden | Error message |
| Filter Messages | 200 OK | Filtered results |
| Pagination | 200 OK | Paginated results |

## 🚨 Troubleshooting

**Server Not Running:**
```bash
cd messaging_app
python manage.py runserver
```

**Token Issues:**
- Ensure you're using the latest access token
- Refresh token if needed
- Re-login if refresh token expired

**404 Errors:**
- Check URL paths match API routes
- Verify conversation/message IDs exist
- Ensure you have access to the resource

## ✅ Test Completion Checklist

- [ ] User registration and authentication
- [ ] JWT token management (login, refresh, logout)
- [ ] Conversation creation and management
- [ ] Message sending and retrieval
- [ ] Pagination (20 messages per page)
- [ ] Filtering (by user, time range, content)
- [ ] Security (unauthorized access prevention)
- [ ] Permission enforcement
- [ ] Error handling

**All tests passing = API implementation complete! 🎉**
