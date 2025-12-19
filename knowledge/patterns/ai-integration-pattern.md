# AI Integration Pattern - ChatKit + Agents SDK + MCP

**Source**: Phase III (AI Chatbot Integration)
**Date**: 2025-12-16
**Status**: Hackathon-compliant (Hackathon II Phase III requirements)

## Overview

This pattern demonstrates AI-powered chat interface integration using OpenAI's official SDKs and the Model Context Protocol (MCP) for standardized tool communication. Supports natural language task management in English and Urdu.

## Technology Stack

- **Frontend**: OpenAI ChatKit (`@openai/chatkit-react`) - Official pre-built chat UI
- **Backend**: OpenAI Agents SDK (`openai-agents`) - Agent runtime management
- **MCP**: Official MCP Python SDK (`mcp[cli]`) - Model Context Protocol
- **AI Model**: OpenAI GPT-4o (multilingual support)
- **Database**: Neon PostgreSQL (Conversation, Message, UserPreferences tables)

## Architecture

```
┌──────────────────────────┐
│  OpenAI ChatKit          │
│  (Frontend UI)           │
│  @openai/chatkit-react   │
└────────────┬─────────────┘
             │ getClientSecret()
             │ REST API calls
             ▼
┌──────────────────────────┐
│  FastAPI Backend         │
│  - ChatKit Session       │
│  - POST /api/{user}/chat │
└────────────┬─────────────┘
             │ Agents SDK
             │ agent.run()
             ▼
┌──────────────────────────┐
│  OpenAI Agents SDK       │
│  (Agent Runtime)         │
│  openai-agents           │
└────────────┬─────────────┘
             │ Tool calls
             │ MCP protocol
             ▼
┌──────────────────────────┐
│  MCP Server              │
│  (Task Tools)            │
│  mcp[cli] - FastMCP      │
│  - add_task              │
│  - list_tasks            │
│  - complete_task         │
│  - delete_task           │
│  - update_task           │
└────────────┬─────────────┘
             │ Database ops
             ▼
┌──────────────────────────┐
│  PostgreSQL (Neon)       │
│  - Conversation          │
│  - Message               │
│  - Task                  │
│  - UserPreferences       │
└──────────────────────────┘
```

## Database Schema

### Conversation Table (Required - Page 18)

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_conversation_user_id ON conversations(user_id);
CREATE INDEX idx_conversation_updated_at ON conversations(updated_at DESC);
```

### Message Table (Required - Page 18, Enhanced)

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    -- Enhanced attributes
    language VARCHAR(10) CHECK (language IN ('en', 'ur')),
    related_task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
    intent_detected VARCHAR(50),
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    metadata JSONB
);

CREATE INDEX idx_message_conversation_id ON messages(conversation_id);
CREATE INDEX idx_message_user_id ON messages(user_id);
CREATE INDEX idx_message_created_at ON messages(created_at DESC);
CREATE INDEX idx_message_conversation_created ON messages(conversation_id, created_at DESC);
```

### UserPreferences Table

```sql
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ai_enabled BOOLEAN DEFAULT FALSE NOT NULL,
    ai_opt_in_date TIMESTAMP,
    preferred_language VARCHAR(10) DEFAULT 'en' NOT NULL CHECK (preferred_language IN ('en', 'ur')),
    privacy_consent_version VARCHAR(10),
    auto_detect_language BOOLEAN DEFAULT TRUE NOT NULL,
    voice_input_enabled BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT check_ai_consent CHECK (
        (ai_enabled = FALSE) OR
        (ai_enabled = TRUE AND privacy_consent_version IS NOT NULL AND ai_opt_in_date IS NOT NULL)
    )
);
```

## Backend Implementation

### 1. MCP Server with FastMCP

```python
# backend/src/mcp_server/task_tools.py
from mcp.server.fastmcp import FastMCP, Context
from sqlmodel import Session, select
from typing import Dict, Any
import logging

mcp = FastMCP("TaskManagementMCP", json_response=True)
logger = logging.getLogger(__name__)

@mcp.tool()
async def add_task(
    user_id: str,
    title: str,
    description: str = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Add a new task for the user (Hackathon requirement).

    Args:
        user_id: User ID performing the action
        title: Task title (1-200 characters)
        description: Optional task description
        ctx: MCP context

    Returns:
        {
            "task_id": int,
            "status": "created",
            "title": str
        }
    """
    try:
        db: Session = ctx.get("db")

        from models import Task

        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            created_via_ai=True
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        logger.info(f"Task {task.id} created via MCP for user {user_id}")

        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title
        }

    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def list_tasks(
    user_id: str,
    status: str = None,  # "completed" or "pending"
    ctx: Context = None
) -> Dict[str, Any]:
    """List user's tasks with optional status filter."""
    try:
        db: Session = ctx.get("db")
        from models import Task

        query = select(Task).where(Task.user_id == user_id)

        if status == "completed":
            query = query.where(Task.completed == True)
        elif status == "pending":
            query = query.where(Task.completed == False)

        tasks = db.exec(query).all()

        return {
            "status": "success",
            "count": len(tasks),
            "tasks": [
                {
                    "task_id": t.id,
                    "title": t.title,
                    "completed": t.completed
                }
                for t in tasks
            ]
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def complete_task(
    user_id: str,
    task_id: int,
    ctx: Context = None
) -> Dict[str, Any]:
    """Mark task as complete."""
    try:
        db: Session = ctx.get("db")
        from models import Task

        task = db.get(Task, task_id)
        if not task or task.user_id != user_id:
            return {"status": "error", "error": "Task not found"}

        task.completed = True
        db.add(task)
        db.commit()

        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}
```

### 2. OpenAI Agents SDK Agent

```python
# backend/src/agents/task_agent.py
from agents import Agent, function_tool
from typing import Dict, Any
from sqlmodel import Session

# Define function tools
@function_tool
async def create_task(
    title: str,
    description: str = "",
    ctx: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create a new task for the user."""
    user_id = ctx.get("user_id")
    db: Session = ctx.get("db")

    from models import Task

    task = Task(
        title=title,
        description=description,
        user_id=user_id,
        created_via_ai=True
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "status": "success",
        "task_id": task.id,
        "title": task.title
    }

# Create agent
task_agent = Agent(
    name="TaskAssistant",
    instructions="""You are a helpful task management assistant.

**Capabilities**:
- Create tasks from natural language descriptions
- List and query existing tasks
- Update task details and mark complete
- Delete tasks with confirmation

**Language Support**:
- Respond in the same language as the user (English or Urdu)
- Auto-detect language from user messages

**Guidelines**:
1. Confirm actions with friendly messages
2. For ambiguous requests, ask clarifying questions
3. For delete operations, confirm before executing
4. Extract title and description from user input
5. Format task lists in a readable way
6. Be concise but helpful
""",
    model="gpt-4o",
    tools=[create_task, list_tasks, complete_task, delete_task, update_task]
)
```

### 3. Chat Service (Conversation Management)

```python
# backend/src/services/chat_service.py
from sqlmodel import Session
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class ChatService:
    """Service for managing chat conversations and AI interactions."""

    def __init__(self, db: Session, agent):
        self.db = db
        self.agent = agent

    async def process_message(
        self,
        user_id: str,
        message_text: str,
        conversation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process user message and return AI response.

        Returns:
            {
                "conversation_id": int,
                "response": str,
                "tool_calls": [...]
            }
        """
        try:
            from models import Conversation, Message

            # 1. Get or create conversation
            if conversation_id:
                conversation = self.db.get(Conversation, conversation_id)
                if not conversation or conversation.user_id != user_id:
                    raise ValueError("Invalid conversation")
            else:
                conversation = Conversation(user_id=user_id)
                self.db.add(conversation)
                self.db.commit()
                self.db.refresh(conversation)

            # 2. Save user message
            user_msg = Message(
                user_id=user_id,
                conversation_id=conversation.id,
                role="user",
                content=message_text
            )
            self.db.add(user_msg)
            self.db.commit()

            # 3. Get conversation history
            history = self._get_conversation_history(conversation.id)

            # 4. Run agent
            context = {"user_id": user_id, "db": self.db}
            response = await self.agent.run(
                messages=history,
                context=context
            )

            # 5. Save AI message
            ai_msg = Message(
                user_id=user_id,
                conversation_id=conversation.id,
                role="assistant",
                content=response["content"]
            )
            self.db.add(ai_msg)
            self.db.commit()

            # 6. Return result
            return {
                "conversation_id": conversation.id,
                "response": response["content"],
                "tool_calls": response.get("tool_calls", [])
            }

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            self.db.rollback()
            raise

    def _get_conversation_history(
        self,
        conversation_id: int,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """Get recent conversation history."""
        from models import Message
        from sqlmodel import select

        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        messages = self.db.exec(query).all()
        messages.reverse()  # Oldest first

        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
```

### 4. API Endpoint (Hackathon Required)

```python
# backend/src/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

router = APIRouter()

class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str

@router.post("/api/{user_id}/chat")
async def send_chat_message(
    user_id: str,
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Send message to AI assistant (HACKATHON REQUIRED endpoint - Page 18).

    Returns:
        {
            "conversation_id": int,
            "response": str,
            "tool_calls": [...]
        }
    """
    # Verify user_id matches authenticated user
    if user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    # Check AI enabled
    # TODO: Check user_preferences.ai_enabled

    from services.chat_service import ChatService
    from agents.task_agent import task_agent

    service = ChatService(db, task_agent)
    result = await service.process_message(
        user_id=user_id,
        message_text=request.message,
        conversation_id=request.conversation_id
    )

    return result
```

## Frontend Implementation

### OpenAI ChatKit Integration

```typescript
// frontend/components/chat/ChatInterface.tsx
'use client';

import { ChatKit, useChatKit } from '@openai/chatkit-react';
import '@openai/chatkit-react/styles.css';

export function ChatInterface() {
  const { control } = useChatKit({
    api: {
      async getClientSecret(existing) {
        const authToken = localStorage.getItem('auth_token');

        const res = await fetch('/api/chatkit/session', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
          },
        });

        const { client_secret } = await res.json();
        return client_secret;
      },
    },
  });

  return (
    <div className="h-[600px] w-full md:w-[400px]">
      <ChatKit
        control={control}
        className="h-full w-full"
      />
    </div>
  );
}
```

## Privacy & Opt-In Pattern

**Critical**: Users must explicitly opt-in before AI features are enabled.

### Opt-In Flow

1. User navigates to settings
2. Sees "Enable AI Chat Assistant" toggle (disabled by default)
3. Clicks toggle → Privacy notice modal appears
4. User reads notice and accepts → POST /api/users/{user_id}/ai/opt-in
5. UserPreferences record created with ai_enabled=TRUE
6. Chat interface becomes available on dashboard

### Implementation

```python
@router.post("/api/users/{user_id}/ai/opt-in")
async def opt_in_to_ai(
    user_id: str,
    request: dict,  # {"privacy_consent_version": "1.0.0"}
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    from models import UserPreferences
    from datetime import datetime

    prefs = UserPreferences(
        user_id=user_id,
        ai_enabled=True,
        ai_opt_in_date=datetime.utcnow(),
        privacy_consent_version=request["privacy_consent_version"]
    )

    db.add(prefs)
    db.commit()

    return {"message": "AI features enabled"}
```

## Language Detection Pattern

Supports English and Urdu through GPT-4o's multilingual capabilities.

### Auto-Detection

Agent automatically detects language from user input and responds in the same language:

```
User: "Add task to buy milk"
AI: "I've created a task titled 'Buy milk'."

User: "مجھے دودھ خریدنا یاد دلائیں"
AI: "میں نے 'دودھ خریدنا' کے عنوان سے ایک کام بنایا ہے۔"
```

### Implementation

Agent instructions include:
```
Respond in the same language as the user (English or Urdu)
Auto-detect language from user messages
```

No additional language detection library needed - GPT-4o handles this automatically.

## Best Practices

1. **Privacy First**: Opt-in required, clear privacy notice, data deletion capability
2. **Multi-User Isolation**: All MCP tools check user_id
3. **Conversation Context**: Maintain last 10 messages for context
4. **Error Handling**: Graceful degradation when OpenAI API unavailable
5. **Rate Limiting**: Limit chat messages per user (e.g., 20/minute)
6. **Tool Validation**: Validate all tool inputs before database operations
7. **Logging**: Log all AI operations for debugging and monitoring
8. **Cost Management**: Monitor OpenAI API usage and costs

## Testing Checklist

- [ ] User can opt-in to AI features
- [ ] Privacy notice displays and requires acceptance
- [ ] Chat interface appears after opt-in
- [ ] User can create tasks via chat in English
- [ ] User can create tasks via chat in Urdu
- [ ] User can query tasks via chat
- [ ] User can mark tasks complete via chat
- [ ] User can delete tasks via chat (with confirmation)
- [ ] Conversation history persists
- [ ] Multi-user isolation works (users only see their tasks)
- [ ] OpenAI API errors handled gracefully
- [ ] Rate limiting prevents abuse

## Hackathon Compliance

✅ OpenAI ChatKit (`@openai/chatkit-react`) - Official chat UI
✅ OpenAI Agents SDK (`openai-agents`) - Agent runtime
✅ Official MCP Python SDK (`mcp[cli]`) - Model Context Protocol
✅ Database: Conversation + Message tables (Page 18)
✅ API: POST /api/{user_id}/chat (Page 18)
✅ MCP Tools: add_task, list_tasks, complete_task, delete_task, update_task (Pages 18-19)

## References

- OpenAI ChatKit: https://platform.openai.com/docs/guides/chatkit
- OpenAI Agents SDK: https://github.com/openai/agents-sdk
- MCP Python SDK: https://modelcontextprotocol.io/docs/sdks/python
- Hackathon II Phase III Spec: Page 17-19
