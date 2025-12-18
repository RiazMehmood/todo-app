# Model Context Protocol (MCP) Specification

**Feature**: AI Chatbot Integration
**Version**: 1.0.0
**Date**: 2025-12-16

## Overview

The Model Context Protocol (MCP) defines the message format and communication patterns between the Next.js frontend, FastAPI backend, and OpenAI API. It standardizes how user intent is transmitted, processed, and responded to across system boundaries.

## Architecture

```
Frontend (Next.js)
    ↓ HTTP/WebSocket
Backend API (FastAPI)
    ↓ MCP Messages
MCP Server Layer
    ↓ Agents SDK
AI Agent (OpenAI)
```

## Message Format

### Base Message Structure

All MCP messages follow this JSON structure:

```json
{
  "version": "1.0",
  "message_id": "uuid-v4",
  "timestamp": "2025-12-16T10:30:00Z",
  "user_id": "uuid-of-user",
  "session_id": "uuid-of-session",
  "type": "user_message | ai_response | system_event",
  "payload": {}
}
```

**Fields**:
- `version`: MCP protocol version (currently "1.0")
- `message_id`: Unique identifier for this message
- `timestamp`: ISO 8601 timestamp
- `user_id`: User this message belongs to
- `session_id`: Current chat session ID
- `type`: Message type (see below)
- `payload`: Type-specific payload

---

## Message Types

### 1. User Message

Sent from frontend when user submits a chat message.

**Type**: `user_message`

**Payload**:
```json
{
  "text": "Add task to buy milk tomorrow",
  "language": "en",
  "context": {
    "current_task_count": 5,
    "last_action": "created_task",
    "conversation_history_ids": [123, 124, 125]
  }
}
```

**Fields**:
- `text`: User's message (1-2000 characters)
- `language`: Message language ('en' or 'ur', optional)
- `context`: Contextual information for AI
  - `current_task_count`: Number of tasks user has
  - `last_action`: Last action performed
  - `conversation_history_ids`: Recent message IDs for context

---

### 2. AI Response

Returned from MCP server after AI processing.

**Type**: `ai_response`

**Payload**:
```json
{
  "text": "I've created a task titled 'Buy milk' for tomorrow.",
  "language": "en",
  "intent": "create_task",
  "confidence": 0.95,
  "action": {
    "type": "task_created",
    "task_id": 42,
    "requires_confirmation": false,
    "task": {
      "id": 42,
      "title": "Buy milk",
      "description": null,
      "completed": false,
      "created_via_ai": true
    }
  },
  "suggestions": [
    "Would you like to set a reminder?",
    "Should I add a description?"
  ]
}
```

**Fields**:
- `text`: AI's response message
- `language`: Response language
- `intent`: Detected intent (see Intent Types)
- `confidence`: AI confidence score (0.0-1.0)
- `action`: Optional action performed (see Action Types)
- `suggestions`: Optional follow-up suggestions

---

### 3. System Event

Internal events for session management and errors.

**Type**: `system_event`

**Payload**:
```json
{
  "event_type": "session_started | session_ended | error | rate_limit",
  "severity": "info | warning | error",
  "message": "Human-readable message",
  "details": {}
}
```

---

## Intent Types

Standardized intent classifications:

| Intent | Description | Example User Input |
|--------|-------------|-------------------|
| `create_task` | User wants to create a new task | "Add task buy groceries" |
| `query_tasks` | User wants to view/search tasks | "Show me my tasks" |
| `update_task` | User wants to modify existing task | "Change milk task to buy organic milk" |
| `delete_task` | User wants to remove a task | "Delete the milk task" |
| `mark_complete` | User wants to mark task done | "Mark groceries as done" |
| `mark_incomplete` | User wants to reopen task | "Uncheck the report task" |
| `help` | User needs assistance | "What can you do?" |
| `clarification` | AI needs more information | "Which task did you mean?" |
| `other` | Unclassified or conversational | "How are you?" |

---

## Action Types

Actions the AI can perform on tasks:

```typescript
type ActionType =
  | 'task_created'
  | 'task_updated'
  | 'task_deleted'
  | 'task_marked_complete'
  | 'task_marked_incomplete'
  | 'tasks_queried'
  | 'clarification_requested'
  | 'none';

interface Action {
  type: ActionType;
  task_id?: number;
  task?: Task;
  tasks?: Task[];
  requires_confirmation: boolean;
  clarification_question?: string;
}
```

**Confirmation Rules**:
- `task_created`: No confirmation required
- `task_updated`: Confirmation required if ambiguous
- `task_deleted`: **Always** requires confirmation
- `task_marked_complete`: No confirmation required
- `clarification_requested`: User must respond

---

## Request/Response Flows

### Flow 1: Task Creation

**1. User Message**:
```json
{
  "version": "1.0",
  "message_id": "abc123",
  "timestamp": "2025-12-16T10:30:00Z",
  "user_id": "user-uuid",
  "session_id": "session-uuid",
  "type": "user_message",
  "payload": {
    "text": "Add task to prepare presentation",
    "language": "en"
  }
}
```

**2. MCP Processing**:
- Intent detection: `create_task`
- Entity extraction: title="prepare presentation"
- Task creation via backend API
- Generate response

**3. AI Response**:
```json
{
  "version": "1.0",
  "message_id": "def456",
  "timestamp": "2025-12-16T10:30:02Z",
  "user_id": "user-uuid",
  "session_id": "session-uuid",
  "type": "ai_response",
  "payload": {
    "text": "I've created a task: 'Prepare presentation'",
    "language": "en",
    "intent": "create_task",
    "confidence": 0.98,
    "action": {
      "type": "task_created",
      "task_id": 42,
      "requires_confirmation": false,
      "task": {
        "id": 42,
        "title": "Prepare presentation",
        "completed": false,
        "created_via_ai": true
      }
    }
  }
}
```

---

### Flow 2: Ambiguous Query (Clarification)

**1. User Message**:
```json
{
  "type": "user_message",
  "payload": {
    "text": "Delete the meeting task"
  }
}
```

**2. AI detects 3 tasks with "meeting" in title**

**3. AI Response (Clarification)**:
```json
{
  "type": "ai_response",
  "payload": {
    "text": "I found 3 tasks with 'meeting'. Which one?",
    "intent": "clarification",
    "action": {
      "type": "clarification_requested",
      "requires_confirmation": true,
      "clarification_question": "Which task?",
      "tasks": [
        {"id": 10, "title": "Team meeting notes"},
        {"id": 15, "title": "Prepare meeting agenda"},
        {"id": 20, "title": "Schedule client meeting"}
      ]
    },
    "suggestions": [
      "Team meeting notes",
      "Prepare meeting agenda",
      "Schedule client meeting"
    ]
  }
}
```

**4. User Response**:
```json
{
  "type": "user_message",
  "payload": {
    "text": "The team meeting notes one",
    "context": {
      "clarification_context": "delete_task",
      "candidate_task_ids": [10, 15, 20]
    }
  }
}
```

**5. AI Confirmation**:
```json
{
  "type": "ai_response",
  "payload": {
    "text": "Are you sure you want to delete 'Team meeting notes'?",
    "intent": "delete_task",
    "action": {
      "type": "task_deleted",
      "task_id": 10,
      "requires_confirmation": true
    }
  }
}
```

---

## Error Handling

### Error Response Format

```json
{
  "version": "1.0",
  "message_id": "err-uuid",
  "timestamp": "2025-12-16T10:30:00Z",
  "user_id": "user-uuid",
  "type": "system_event",
  "payload": {
    "event_type": "error",
    "severity": "error",
    "message": "Failed to create task",
    "details": {
      "error_code": "TASK_CREATION_FAILED",
      "reason": "Title exceeds 200 characters",
      "original_input": "Add task with very long title..."
    }
  }
}
```

### Error Codes

| Code | Description | Retry? |
|------|-------------|--------|
| `OPENAI_API_ERROR` | OpenAI API unavailable | Yes |
| `INTENT_DETECTION_FAILED` | Could not understand user intent | No |
| `TASK_CREATION_FAILED` | Task validation failed | No |
| `TASK_NOT_FOUND` | Referenced task doesn't exist | No |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Yes (after delay) |
| `UNAUTHORIZED` | User not authenticated | No |
| `AI_NOT_ENABLED` | User hasn't opted in | No |

---

## Session Management

### Session Lifecycle

1. **Session Start**: When user sends first message
   ```json
   {
     "type": "system_event",
     "payload": {
       "event_type": "session_started",
       "session_id": "new-session-uuid"
     }
   }
   ```

2. **Session Context**: Maintained in Agents SDK
   - Recent conversation history (last 10 messages)
   - User task summary
   - Pending clarifications
   - User preferences

3. **Session End**: After 30 minutes of inactivity or explicit logout
   ```json
   {
     "type": "system_event",
     "payload": {
       "event_type": "session_ended",
       "reason": "inactivity | logout"
     }
   }
   ```

### Context Window

MCP Server maintains context window for AI:
- **Short-term**: Last 10 messages in current session
- **Task summary**: User's task count, recent tasks
- **User prefs**: Language, timezone (future)
- **Clarification state**: If awaiting user response

---

## WebSocket Protocol (Optional Real-Time)

For real-time chat experience:

**Connection**: `wss://api.example.com/api/users/{user_id}/chat/ws`

**Authentication**: JWT token in query param or header

**Message Format**: Same MCP JSON format

**Events**:
- `connected`: Client connected
- `message`: New message (user or AI)
- `typing`: AI is processing (optional)
- `error`: Error occurred
- `disconnect`: Connection closed

---

## Implementation Notes

### Backend (FastAPI)

```python
# MCP Message Handler
class MCPMessage(BaseModel):
    version: str = "1.0"
    message_id: str
    timestamp: datetime
    user_id: str
    session_id: str
    type: str  # user_message, ai_response, system_event
    payload: dict

# Intent Detection
async def detect_intent(text: str, language: str) -> tuple[str, float]:
    """Returns (intent, confidence_score)"""
    # Use OpenAI API with system prompt
    pass

# Action Execution
async def execute_task_action(
    user_id: str,
    intent: str,
    entities: dict
) -> Action:
    """Perform task CRUD based on detected intent"""
    pass
```

### Frontend (Next.js/TypeScript)

```typescript
// MCP Client
interface MCPMessage {
  version: string;
  message_id: string;
  timestamp: string;
  user_id: string;
  session_id: string;
  type: 'user_message' | 'ai_response' | 'system_event';
  payload: any;
}

async function sendMessage(text: string): Promise<MCPMessage> {
  const message: MCPMessage = {
    version: '1.0',
    message_id: generateUUID(),
    timestamp: new Date().toISOString(),
    user_id: currentUserId,
    session_id: currentSessionId,
    type: 'user_message',
    payload: {
      text,
      language: detectedLanguage || 'en'
    }
  };

  const response = await apiCall('/api/users/{userId}/chat/messages', {
    method: 'POST',
    body: JSON.stringify(message)
  });

  return response;
}
```

---

## Version History

- **1.0.0** (2025-12-16): Initial MCP specification
  - Base message format
  - Intent and action types
  - Error handling
  - Session management
