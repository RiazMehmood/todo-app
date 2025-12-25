# WebSocket Protocol Specification

## Connection

### Endpoint

```
ws://localhost:8000/api/{user_id}/ws?token={jwt_token}
wss://todo-app-production-be56.up.railway.app/api/{user_id}/ws?token={jwt_token}
```

### Authentication

- JWT token passed as query parameter: `?token={jwt_token}`
- Connection rejected if token is invalid or expired
- Token validated on connection establishment

### Connection Lifecycle

1. **Client initiates connection** with JWT token
2. **Server validates token** and establishes WebSocket
3. **Server sends welcome message** with session_id
4. **Client sends heartbeat** every 10 seconds
5. **Server broadcasts events** to all connected clients
6. **Server times out** connection after 30 seconds of no heartbeat

---

## Message Format

All messages use JSON format with a `type` field to identify the message type.

### Message Structure

```json
{
  "type": "message_type",
  "payload": { ... }
}
```

---

## Client → Server Messages

### 1. Heartbeat

Sent every 10 seconds to maintain connection and update presence.

```json
{
  "type": "heartbeat",
  "task_id": "uuid-or-null",
  "status": "viewing"
}
```

**Fields:**
- `task_id` (string|null): Currently viewing this task ID, or null if on task list
- `status` (string): One of: `viewing`, `editing`, `idle`

**Response:** Server updates presence tracking (no response message sent)

---

### 2. Task Edit Start

Notify other users that you're editing a task.

```json
{
  "type": "task_edit_start",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Fields:**
- `task_id` (string): UUID of task being edited

**Response:** Server broadcasts `presence_update` to other users

---

### 3. Task Edit End

Notify that you've finished editing a task.

```json
{
  "type": "task_edit_end",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Fields:**
- `task_id` (string): UUID of task no longer being edited

**Response:** Server broadcasts `presence_update` to other users

---

## Server → Client Messages

### 1. Welcome

Sent immediately after connection is established.

```json
{
  "type": "welcome",
  "session_id": "abc123def456",
  "user_id": "660e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2025-12-23T12:00:00Z"
}
```

**Fields:**
- `session_id` (string): Unique identifier for this WebSocket session
- `user_id` (string): Authenticated user ID
- `timestamp` (string): Server timestamp (ISO 8601)

---

### 2. Task Created

Broadcast when a new task is created by any user.

```json
{
  "type": "task_created",
  "task": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "user_id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "New task",
    "description": "Task description",
    "status": "pending",
    "priority": "medium",
    "tags": ["work"],
    "created_at": "2025-12-23T12:05:00Z",
    "updated_at": "2025-12-23T12:05:00Z",
    "due_date": null
  },
  "created_by": "660e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2025-12-23T12:05:00Z"
}
```

**Fields:**
- `task` (object): Full task object
- `created_by` (string): User ID who created the task
- `timestamp` (string): When task was created

---

### 3. Task Updated

Broadcast when a task is updated.

```json
{
  "type": "task_updated",
  "task": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "user_id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Updated task title",
    "status": "in_progress",
    "priority": "high",
    ...
  },
  "updated_by": "660e8400-e29b-41d4-a716-446655440001",
  "updated_at": "2025-12-23T12:10:00Z",
  "changes": ["title", "priority", "status"]
}
```

**Fields:**
- `task` (object): Full updated task object
- `updated_by` (string): User ID who made the update
- `updated_at` (string): When update occurred
- `changes` (array): List of fields that changed

---

### 4. Task Deleted

Broadcast when a task is deleted.

```json
{
  "type": "task_deleted",
  "task_id": "770e8400-e29b-41d4-a716-446655440002",
  "deleted_by": "660e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2025-12-23T12:15:00Z"
}
```

**Fields:**
- `task_id` (string): UUID of deleted task
- `deleted_by` (string): User ID who deleted the task
- `timestamp` (string): When deletion occurred

---

### 5. Presence Update

Broadcast when user presence changes (someone starts/stops viewing/editing).

```json
{
  "type": "presence_update",
  "users": [
    {
      "user_id": "660e8400-e29b-41d4-a716-446655440001",
      "username": "Alice",
      "task_id": "770e8400-e29b-41d4-a716-446655440002",
      "status": "editing",
      "last_seen": "2025-12-23T12:20:00Z"
    },
    {
      "user_id": "880e8400-e29b-41d4-a716-446655440003",
      "username": "Bob",
      "task_id": null,
      "status": "viewing",
      "last_seen": "2025-12-23T12:19:50Z"
    }
  ]
}
```

**Fields:**
- `users` (array): List of currently active users
- Each user object contains:
  - `user_id` (string): User UUID
  - `username` (string): Display name
  - `task_id` (string|null): Currently viewing/editing task, or null
  - `status` (string): One of: `viewing`, `editing`, `idle`
  - `last_seen` (string): Timestamp of last heartbeat

---

### 6. Notification

Broadcast for various event notifications.

```json
{
  "type": "notification",
  "title": "Task Completed",
  "message": "Bob completed 'Design Homepage'",
  "task_id": "770e8400-e29b-41d4-a716-446655440002",
  "action": "task_completed",
  "timestamp": "2025-12-23T12:25:00Z"
}
```

**Fields:**
- `title` (string): Notification title
- `message` (string): Human-readable notification message
- `task_id` (string): Related task ID
- `action` (string): Notification type (task_completed, task_assigned, comment_added, etc.)
- `timestamp` (string): When notification was generated

---

### 7. Error

Sent when a client message causes an error.

```json
{
  "type": "error",
  "code": "INVALID_MESSAGE",
  "message": "Invalid message format: missing 'type' field",
  "timestamp": "2025-12-23T12:30:00Z"
}
```

**Fields:**
- `code` (string): Error code (INVALID_MESSAGE, UNAUTHORIZED, RATE_LIMIT, etc.)
- `message` (string): Human-readable error description
- `timestamp` (string): When error occurred

---

## Disconnection Handling

### Server-Initiated Disconnection

Server closes connection if:
- No heartbeat received for 30 seconds
- Invalid JWT token detected
- Rate limit exceeded (>100 messages/minute)

**Close Codes:**
- `1000`: Normal closure (client disconnected)
- `1001`: Server going away (maintenance)
- `1008`: Policy violation (invalid auth, rate limit)
- `1011`: Internal server error

### Client-Initiated Disconnection

Client should:
1. Send final heartbeat with `status: "idle"`
2. Close WebSocket connection gracefully
3. Implement reconnection with exponential backoff (1s, 2s, 4s, 8s, max 30s)

---

## Reconnection Strategy

### Client Behavior

When connection drops:
1. **Wait** 1 second
2. **Attempt reconnection** with same JWT token
3. If failed, **double wait time** (max 30 seconds)
4. **Reset backoff** on successful connection
5. **Request missed events** using `sync` message (future enhancement)

### Optimistic UI Updates

Client should:
- Apply local updates immediately (optimistic)
- Mark as "pending sync" until server confirms via WebSocket
- Rollback on error response from HTTP API
- Show "Offline" indicator when WebSocket disconnected

---

## Rate Limiting

- **Heartbeats**: 1 per 10 seconds (enforced on client)
- **Messages**: Max 100 per minute (enforced on server)
- **Connections**: Max 10 per user (prevents DOS)

Exceeding limits results in connection termination with close code `1008`.

---

## Security

### Authentication
- JWT token validated on connection
- Token expiry checked every 5 minutes
- Connection closed if token expires

### Authorization
- Users only receive events for their own tasks
- Presence updates only for users viewing same task list
- No cross-user data leakage

### Data Validation
- All client messages validated against schema
- Invalid messages logged and rejected (error sent to client)
- Malformed JSON closes connection

---

## Example Flow

### Task Creation Flow

1. **Client A** creates task via HTTP POST `/api/{user_id}/tasks`
2. **Server** creates task in database
3. **Server** publishes `task_created` event to Redis pub/sub
4. **Redis** broadcasts to all WebSocket servers
5. **WebSocket servers** send `task_created` message to all connected clients (including Client A)
6. **Client B** receives message within 2 seconds and updates UI

### Presence Update Flow

1. **Client A** opens task for editing
2. **Client A** sends `task_edit_start` message via WebSocket
3. **Server** updates Redis presence key: `presence:alice:session123 = {task_id: "...", status: "editing"}`
4. **Server** broadcasts `presence_update` to all clients viewing same task
5. **Client B** shows "Alice is editing" indicator
6. **Client A** closes task, sends `task_edit_end`
7. **Server** updates Redis presence, broadcasts update
8. **Client B** removes "Alice is editing" indicator

---

## Implementation Notes

### Backend (FastAPI)

- WebSocket endpoint: `@app.websocket("/api/{user_id}/ws")`
- Connection manager tracks all active connections
- Redis pub/sub for multi-instance broadcasting
- Asyncio tasks for heartbeat timeout monitoring

### Frontend (Next.js/TypeScript)

- WebSocket client wrapper with auto-reconnect
- Event listeners for each message type
- Optimistic UI updates + rollback logic
- Presence indicator components

---

## Future Enhancements

- **Sync Message**: Request missed events after reconnection
- **Typing Indicators**: Show when user is typing in task description
- **Cursor Positions**: Collaborative editing with cursor tracking
- **Binary Messages**: Support for efficient binary protocol (MessagePack)
- **Compression**: Per-message compression for large payloads
