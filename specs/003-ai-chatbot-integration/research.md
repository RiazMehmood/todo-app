# Research & Technology Decisions

**Feature**: 003-ai-chatbot-integration
**Date**: 2025-12-16 (Updated for Strict Hackathon Compliance)
**Purpose**: Document technology choices for AI chatbot integration using **OpenAI ChatKit**, **OpenAI Agents SDK**, and **Official MCP Python SDK**

---

## IMPORTANT: Hackathon Compliance Update

This research document has been updated to ensure **strict compliance** with Hackathon II Phase III requirements. All technology decisions align with the official hackathon specification.

**Required Technologies** (per Hackathon Document Page 17):
- ✅ **OpenAI ChatKit** (frontend UI framework)
- ✅ **OpenAI Agents SDK** (AI agent runtime management)
- ✅ **Official MCP Python SDK** (Model Context Protocol implementation)
- ✅ **FastAPI** (backend framework)
- ✅ **Neon PostgreSQL** (database)
- ✅ **Better Auth** (authentication)

---

## 1. OpenAI ChatKit Integration

### Decision

**Use OpenAI ChatKit (`@openai/chatkit-react`) for chat interface**

### What is ChatKit?

**OpenAI ChatKit** is OpenAI's official production-ready framework for building AI-powered conversational interfaces. It provides a drop-in chat solution that handles UI state, streaming, tool visualization, and conversation management automatically.

**Key Features**:
- **Pre-built Chat UI**: Complete chat interface with message bubbles, input field, typing indicators
- **Response Streaming**: Built-in real-time message streaming
- **Tool Integration**: Automatic visualization of agentic actions and reasoning
- **File Handling**: Support for uploads (images, documents)
- **Conversation Management**: Thread and message organization
- **Framework-Agnostic**: Works with React, Vue, vanilla JS
- **Customizable**: Style with Tailwind CSS or custom themes

### Installation

```bash
# Frontend (Next.js)
npm install @openai/chatkit-react

# Or add CDN script
<script src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js" async></script>
```

### Implementation Pattern

**Frontend (Next.js):**

```typescript
// components/chat/ChatInterface.tsx
'use client';

import { ChatKit, useChatKit } from '@openai/chatkit-react';

export function ChatInterface() {
  const { control } = useChatKit({
    api: {
      async getClientSecret(existing) {
        // Call backend to get client token
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
    <ChatKit
      control={control}
      className="h-[600px] w-full md:w-[400px]"
    />
  );
}
```

**Backend (FastAPI):**

```python
# backend/src/routes/chatkit.py
from fastapi import APIRouter, Depends
from openai import OpenAI
import os

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/api/chatkit/session")
async def create_chatkit_session(
    user: User = Depends(get_current_user)
):
    """Create ChatKit session and return client secret"""

    # Create session with OpenAI
    session = client.chatkit.sessions.create({
        "user_id": user.id,
        "agent_id": os.getenv("OPENAI_AGENT_ID"),
        "metadata": {
            "user_email": user.email
        }
    })

    return {
        "client_secret": session.client_secret,
        "session_id": session.id
    }
```

### Architecture

ChatKit provides two integration options:

**Option A: Simple Integration (Recommended for MVP)**
- Frontend: ChatKit component with `getClientSecret`
- Backend: FastAPI endpoint that generates client tokens
- OpenAI: Agent hosted on OpenAI servers (using Agent Builder)
- No custom backend agent logic needed

**Option B: Advanced Integration (Custom Backend)**
- Frontend: ChatKit component
- Backend: Custom agent logic using Agents SDK + MCP
- Full control over agent behavior and tool execution
- More complex but flexible

**We will use Option B** to meet hackathon requirements for custom Agents SDK + MCP implementation.

### Customization

```typescript
// Customize ChatKit appearance
import { ChatKit, useChatKit } from '@openai/chatkit-react';

export function CustomChatInterface() {
  const { control } = useChatKit({
    api: {
      async getClientSecret(existing) {
        return await fetchClientSecret();
      },
    },
    // Customize behavior
    config: {
      enableFileUploads: false,  // Disable for MVP
      placeholder: "Ask me to create, update, or delete tasks...",
      theme: {
        primaryColor: "#3b82f6",  // Match app theme
        fontFamily: "Inter, sans-serif"
      }
    }
  });

  return (
    <div className="chat-container">
      <ChatKit
        control={control}
        className="h-full w-full"
      />
    </div>
  );
}
```

### Best Practices

1. **Token Management**: Backend must securely generate client secrets using OpenAI API
2. **Authentication**: Validate JWT before issuing client tokens
3. **Session Persistence**: ChatKit manages conversation state automatically
4. **Error Handling**: Provide fallback UI if ChatKit fails to load
5. **Styling**: Use Tailwind classes for responsive layout

### References

- [OpenAI ChatKit JS Repository](https://github.com/openai/chatkit-js)
- [Next.js ChatKit Integration Guide](https://www.buildwithmatija.com/blog/chatkit-nextjs-integration)
- [ChatKit with FastAPI Tutorial](https://dev.to/rajeev_3ce9f280cbae73b234/--3hhn)

---

## 2. OpenAI Agents SDK Integration

### Decision

**Use OpenAI Agents SDK (`openai-agents`) for AI agent runtime management**

### What is OpenAI Agents SDK?

The **OpenAI Agents SDK** (`openai-agents`) is OpenAI's production-ready framework for building multi-agent workflows with minimal abstractions. Released in 2025, it replaces the experimental Swarm framework.

**Repository**: https://github.com/openai/openai-agents-python
**Documentation**: https://openai.github.io/openai-agents-python/

**Core Primitives**:
1. **Agents**: LLMs equipped with instructions and tools
2. **Handoffs**: Allow agents to delegate tasks to specialized agents
3. **Guardrails**: Validate agent inputs/outputs for safety
4. **Sessions**: Automatically maintain conversation history

### Installation

```bash
# Backend (Python)
cd backend
uv add openai-agents

# Or with optional features
uv add "openai-agents[voice,redis]"
```

### Key Features

- **Multi-Agent Workflows**: Built-in agent handoffs and orchestration
- **Provider-Agnostic**: Works with OpenAI and 100+ other LLM providers
- **Automatic Session Management**: SQLiteSession (local), RedisSession (distributed)
- **Built-in Tracing**: Integration with Logfire, AgentOps, Braintrust
- **Function Tools**: Convert Python functions to agent tools with automatic schema generation
- **Structured Output**: Type-safe agent responses using Pydantic models
- **MCP Integration**: Native support for MCP servers (4 integration options)

### Implementation Pattern

**Create Task Agent:**

```python
# backend/src/agents/task_agent.py
from agents import Agent, function_tool
from sqlmodel import Session, select
from ..models import Task
from ..database import get_db

@function_tool
async def create_task(
    title: str,
    description: str = "",
    ctx: dict = None
) -> dict:
    """Create a new task for the user"""
    user_id = ctx.get("user_id")
    db: Session = ctx.get("db")

    task = Task(
        title=title,
        description=description,
        user_id=user_id,
        created_via_ai=True,
        original_nl_input=ctx.get("original_message", "")
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "status": "success",
        "task_id": task.id,
        "title": task.title
    }

@function_tool
async def list_tasks(
    completed: bool = None,
    ctx: dict = None
) -> list[dict]:
    """List user's tasks, optionally filtered by completion status"""
    user_id = ctx.get("user_id")
    db: Session = ctx.get("db")

    query = select(Task).where(Task.user_id == user_id)
    if completed is not None:
        query = query.where(Task.completed == completed)

    tasks = db.exec(query).all()

    return [{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "completed": t.completed
    } for t in tasks]

@function_tool
async def update_task(
    task_id: int,
    title: str = None,
    description: str = None,
    completed: bool = None,
    ctx: dict = None
) -> dict:
    """Update an existing task"""
    user_id = ctx.get("user_id")
    db: Session = ctx.get("db")

    task = db.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        return {"status": "error", "message": "Task not found"}

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if completed is not None:
        task.completed = completed

    db.commit()
    db.refresh(task)

    return {
        "status": "success",
        "task_id": task.id
    }

@function_tool
async def delete_task(task_id: int, ctx: dict = None) -> dict:
    """Delete a task (requires confirmation)"""
    user_id = ctx.get("user_id")
    db: Session = ctx.get("db")

    task = db.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        return {"status": "error", "message": "Task not found"}

    title = task.title
    db.delete(task)
    db.commit()

    return {
        "status": "success",
        "message": f"Deleted task: {title}",
        "task_id": task_id
    }

# Create agent with tools
task_agent = Agent(
    name="TaskAssistant",
    instructions="""You are a helpful task management assistant.

You can help users:
- Create new tasks from natural language descriptions
- View their existing tasks (all, completed, or pending)
- Update task details or mark tasks as complete
- Delete tasks (always ask for confirmation first)

You communicate in both English and Urdu (اردو).
Automatically detect the user's language and respond accordingly.

Examples:
- "Add task to buy milk" → Use create_task(title="Buy milk")
- "دودھ خریدنے کا کام شامل کریں" → Use create_task(title="دودھ خریدنا")
- "What's on my list?" → Use list_tasks()
- "Mark the milk task as done" → Find task, then update_task(completed=True)
- "Delete the shopping task" → ASK FOR CONFIRMATION, then delete_task()

Important:
- When updating or deleting, ask for confirmation if ambiguous
- If multiple tasks match, list them and ask user to clarify
- Preserve the user's language in task titles/descriptions
- Be concise and friendly""",
    model="gpt-4o",
    tools=[create_task, list_tasks, update_task, delete_task]
)
```

**FastAPI Integration:**

```python
# backend/src/routes/chat.py
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from agents import Runner, SQLiteSession
from sqlmodel import Session
from ..agents.task_agent import task_agent
from ..auth import get_current_user
from ..database import get_db
from ..models import User
import json

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/message")
async def chat_message(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process chat message (non-streaming)"""

    # Create session for conversation history
    session = SQLiteSession(
        db_path="./conversations.db",
        user_id=user.id
    )

    # Run agent
    result = await Runner.run(
        agent=task_agent,
        input=request.message,
        session=session,
        context={
            "user_id": user.id,
            "db": db,
            "original_message": request.message
        }
    )

    return {
        "response": result.final_output,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stream chat responses with Server-Sent Events"""

    async def generate():
        session = SQLiteSession(
            db_path="./conversations.db",
            user_id=user.id
        )

        try:
            # Stream agent responses
            async for chunk in Runner.stream(
                agent=task_agent,
                input=request.message,
                session=session,
                context={
                    "user_id": user.id,
                    "db": db,
                    "original_message": request.message
                }
            ):
                yield f"data: {json.dumps({'type': 'chunk', 'text': chunk})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
```

### Session Management

The Agents SDK provides **built-in persistent session management**:

```python
from agents import Agent, Runner, SQLiteSession, RedisSession

# Development: SQLite-backed sessions
session = SQLiteSession(
    db_path="./conversations.db",
    user_id="user_123"
)

# Production: Redis-backed sessions (distributed)
session = RedisSession(
    redis_url="redis://localhost:6379",
    user_id="user_123"
)

# Run agent with session memory
result = await Runner.run(
    agent=task_agent,
    input="My name is Sarah",
    session=session
)

# Next message remembers context
result = await Runner.run(
    agent=task_agent,
    input="What's my name?",  # Remembers "Sarah"
    session=session
)
```

### Differences from OpenAI Function Calling

| Feature | OpenAI Function Calling | Agents SDK |
|---------|------------------------|------------|
| **Session Management** | Manual | Automatic (SQLiteSession/RedisSession) |
| **Multi-Agent** | Not supported | Built-in handoffs |
| **Tool Execution** | Manual loop | Automatic agent loop |
| **Context Passing** | Manual | Context parameter in tools |
| **Guardrails** | Manual validation | Built-in guardrails |
| **Tracing** | Manual | Automatic with multiple providers |

### MCP Integration in Agents SDK

The Agents SDK has **native MCP support** with four integration options:

```python
from agents import Agent
from agents.mcp import MCPServerStreamableHttp

# Connect agent to MCP server
mcp_server = MCPServerStreamableHttp(
    url="http://localhost:8000/mcp",
    headers={"Authorization": f"Bearer {token}"}
)

agent = Agent(
    name="TaskAgent",
    instructions="Use MCP tools for task management",
    model="gpt-4o",
    mcp_servers=[mcp_server]  # Connect to MCP server
)
```

### Best Practices

1. **Agent State Management**: Sessions automatically manage conversation history
2. **Function Execution Safety**: Validate all function arguments before execution
3. **Retry Logic**: Agents SDK handles retries automatically
4. **Context Injection**: Pass user_id, db, and other context to tools via `ctx` parameter
5. **Guardrails**: Use built-in guardrails for input validation

### References

- [OpenAI Agents SDK GitHub](https://github.com/openai/openai-agents-python)
- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [Agents SDK MCP Integration](https://openai.github.io/openai-agents-python/mcp/)
- [FastAPI + Agents SDK Example](https://github.com/ahmad2b/openai-agents-streaming-api)

---

## 3. Model Context Protocol (MCP) with Official Python SDK

### Decision

**Use Official MCP Python SDK (`mcp[cli]`) to implement Model Context Protocol server**

### What is MCP?

The **Model Context Protocol** is a standardized protocol developed by Anthropic for connecting AI models to external tools and data sources. It separates context provision from LLM interaction.

**Official Repository**: https://github.com/modelcontextprotocol/python-sdk
**Documentation**: https://modelcontextprotocol.github.io/python-sdk/
**Latest Version**: 1.24.0 (as of Dec 12, 2025)

**Core Concepts:**
1. **Resources**: Read-only data endpoints (like GET in REST)
2. **Tools**: Executable actions with side effects (like POST in REST)
3. **Prompts**: Reusable templates for LLM interactions

### Installation

```bash
# Backend (Python)
cd backend
uv add "mcp[cli]"

# Includes FastMCP for easy server creation
```

### Implementation Pattern

**Create MCP Server for Task Operations:**

```python
# backend/src/mcp_server/task_tools.py
from mcp.server.fastmcp import FastMCP, Context
from sqlmodel import Session, select
from ..models import Task

mcp = FastMCP("TaskManagementMCP", json_response=True)

@mcp.tool()
async def add_task(
    user_id: str,
    title: str,
    description: str = None,
    ctx: Context = None
) -> dict:
    """
    Add a new task for the user

    Required by hackathon: add_task(user_id, title, description)
    Returns: {"task_id": int, "status": str, "title": str}
    """
    db: Session = ctx.get("db")

    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        created_via_ai=True,
        original_nl_input=ctx.get("original_message", "")
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    await ctx.info(f"Created task: {task.title}")

    return {
        "task_id": task.id,
        "status": "created",
        "title": task.title
    }

@mcp.tool()
async def list_tasks(
    user_id: str,
    status: str = None,
    ctx: Context = None
) -> list[dict]:
    """
    List user's tasks, optionally filtered

    Required by hackathon: list_tasks(user_id, status)
    Returns: Array of task objects
    """
    db: Session = ctx.get("db")

    query = select(Task).where(Task.user_id == user_id)

    if status == "completed":
        query = query.where(Task.completed == True)
    elif status == "pending":
        query = query.where(Task.completed == False)

    tasks = db.exec(query).all()

    return [{
        "id": t.id,
        "user_id": t.user_id,
        "title": t.title,
        "description": t.description,
        "completed": t.completed,
        "created_at": t.created_at.isoformat(),
        "updated_at": t.updated_at.isoformat()
    } for t in tasks]

@mcp.tool()
async def complete_task(
    user_id: str,
    task_id: int,
    ctx: Context = None
) -> dict:
    """
    Mark a task as complete

    Required by hackathon: complete_task(user_id, task_id)
    Returns: {"task_id": int, "status": str, "title": str}
    """
    db: Session = ctx.get("db")

    task = db.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        return {
            "status": "error",
            "message": "Task not found",
            "task_id": task_id
        }

    task.completed = True
    db.commit()
    db.refresh(task)

    return {
        "task_id": task.id,
        "status": "completed",
        "title": task.title
    }

@mcp.tool()
async def delete_task(
    user_id: str,
    task_id: int,
    ctx: Context = None
) -> dict:
    """
    Delete a task

    Required by hackathon: delete_task(user_id, task_id)
    Returns: {"task_id": int, "status": str, "title": str}
    """
    db: Session = ctx.get("db")

    task = db.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        return {
            "status": "error",
            "message": "Task not found",
            "task_id": task_id
        }

    title = task.title
    db.delete(task)
    db.commit()

    return {
        "task_id": task_id,
        "status": "deleted",
        "title": title
    }

@mcp.tool()
async def update_task(
    user_id: str,
    task_id: int,
    title: str = None,
    description: str = None,
    ctx: Context = None
) -> dict:
    """
    Update an existing task

    Required by hackathon: update_task(user_id, task_id, title, description)
    Returns: {"task_id": int, "status": str, "title": str}
    """
    db: Session = ctx.get("db")

    task = db.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        return {
            "status": "error",
            "message": "Task not found",
            "task_id": task_id
        }

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description

    db.commit()
    db.refresh(task)

    return {
        "task_id": task.id,
        "status": "updated",
        "title": task.title
    }

@mcp.resource("tasks://summary")
async def get_task_summary(ctx: Context = None) -> dict:
    """Get summary of user's tasks"""
    user_id = ctx.get("user_id")
    db: Session = ctx.get("db")

    tasks = db.exec(select(Task).where(Task.user_id == user_id)).all()

    return {
        "total": len(tasks),
        "completed": sum(1 for t in tasks if t.completed),
        "pending": sum(1 for t in tasks if not t.completed)
    }
```

**Embed MCP Server in FastAPI:**

```python
# backend/src/main.py
from fastapi import FastAPI
from .mcp_server.task_tools import mcp

app = FastAPI()

# Mount MCP server at /mcp endpoint
app.mount("/mcp", mcp.app)

# Regular FastAPI routes continue to work
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# MCP server accessible at http://localhost:8000/mcp
```

**Alternative: Auto-Generate MCP from FastAPI:**

```python
# backend/src/main.py (Alternative approach)
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

app = FastAPI()

# Regular FastAPI endpoints
@app.post("/tasks/")
async def create_task(title: str):
    return {"id": 123, "title": title}

@app.get("/tasks/")
async def list_tasks():
    return {"tasks": []}

# Auto-generate MCP server from FastAPI
mcp = FastApiMCP(app)
mcp.mount()  # MCP available at /mcp endpoint
```

### Connect Agents SDK to MCP Server

```python
# backend/src/agents/task_agent.py
from agents import Agent
from agents.mcp import MCPServerStreamableHttp

# Connect to embedded MCP server
mcp_server = MCPServerStreamableHttp(
    url="http://localhost:8000/mcp",
    headers={"X-Internal-Service": "agent"}
)

task_agent = Agent(
    name="TaskAssistant",
    instructions="""You are a helpful task management assistant.
    Use MCP tools to create, view, update, and delete tasks.
    Support English and Urdu languages.""",
    model="gpt-4o",
    mcp_servers=[mcp_server]  # Connect to MCP
)
```

### Transport Options

MCP supports multiple transport mechanisms:

```python
# Stdio (for local processes)
mcp.run(transport="stdio")

# HTTP with Server-Sent Events (recommended for web)
mcp.run(transport="sse", host="0.0.0.0", port=8001)

# Streamable HTTP (bidirectional)
mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)
```

### Testing MCP Servers

**MCP Inspector (official testing tool):**

```bash
# Start inspector
npx -y @modelcontextprotocol/inspector

# Test MCP server
# Navigate to http://localhost:6274
# Connect to http://localhost:8000/mcp
```

**Testing in Python:**

```python
# Run server locally
uv run server.py

# Test with MCP client
from mcp.client import Client

async with Client("server.py") as client:
    tools = await client.list_tools()
    result = await client.call_tool("add_task", {
        "user_id": "user_123",
        "title": "Test Task"
    })
    print(result)
```

### Best Practices

1. **Tool Naming**: Match hackathon specification exactly (add_task, not create_task)
2. **Parameter Validation**: Validate all tool inputs before execution
3. **Error Messages**: Return helpful error messages in tool responses
4. **Context Injection**: Pass db session and user info via Context
5. **Progress Reporting**: Use `ctx.info()` and `ctx.report_progress()` for long operations

### References

- [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Python SDK Documentation](https://modelcontextprotocol.github.io/python-sdk/)
- [MCP Specification](https://github.com/modelcontextprotocol)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [fastapi-mcp Library](https://github.com/tadata-org/fastapi_mcp)

---

## 4. Hybrid Architecture: ChatKit + Agents SDK + MCP

### Recommended Architecture for Phase III

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js)                      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │   ChatKit Component (@openai/chatkit-react)         │  │
│  │   - Pre-built chat UI                               │  │
│  │   - Streaming support                               │  │
│  │   - Auto-managed state                              │  │
│  └─────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          │ getClientSecret()                │
│                          ▼                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                        │
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │  POST /api/chatkit/session                        │    │
│  │  - Generate client_secret via OpenAI API          │    │
│  └───────────────────────────────────────────────────┘    │
│                          │                                  │
│  ┌───────────────────────▼───────────────────────────┐    │
│  │     Agents SDK (openai-agents)                    │    │
│  │     - Agent runtime management                    │    │
│  │     - Session persistence (SQLiteSession)         │    │
│  │     - Tool execution loop                         │    │
│  └───────────────────────┬───────────────────────────┘    │
│                          │                                  │
│                          │ MCP Protocol                     │
│                          ▼                                  │
│  ┌───────────────────────────────────────────────────┐    │
│  │     MCP Server (mcp[cli])                         │    │
│  │     - add_task, list_tasks, complete_task         │    │
│  │     - delete_task, update_task                    │    │
│  │     - Embedded at /mcp endpoint                   │    │
│  └───────────────────────┬───────────────────────────┘    │
│                          │                                  │
│                          │ Database Operations              │
│                          ▼                                  │
│  ┌───────────────────────────────────────────────────┐    │
│  │     Task Service Layer                            │    │
│  │     - CRUD operations                             │    │
│  │     - Business logic                              │    │
│  └───────────────────────────────────────────────────┘    │
│                          │                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ SQL Queries
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              NEON POSTGRESQL DATABASE                       │
│                                                             │
│  - tasks table                                              │
│  - conversations table (new)                                │
│  - messages table (new)                                     │
│  - user_preferences table (new)                             │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

**User Types Message:**
1. ChatKit captures user input
2. Calls `getClientSecret()` to get session token
3. Sends message to OpenAI API (ChatKit manages this)
4. OpenAI routes to our backend agent
5. Agents SDK processes message with MCP tools
6. MCP Server executes task CRUD operations
7. Response streams back through ChatKit to user

**Benefits of This Architecture:**
- ✅ **Hackathon Compliant**: Uses all required technologies
- ✅ **Separation of Concerns**: UI (ChatKit), Logic (Agents SDK), Tools (MCP)
- ✅ **Maintainable**: Clear boundaries between components
- ✅ **Testable**: Each layer can be tested independently
- ✅ **Scalable**: Can add more agents and tools easily

---

## 5. Urdu Language Support

### Decision

**Use OpenAI GPT-4o for Urdu language support with automatic language detection**

### Implementation Notes

Same as before - GPT-4o has excellent native Urdu support. No changes needed to Urdu section (lines 741-898 in original).

**Key Points:**
- GPT-4o trained on diverse Urdu text
- Automatic language detection (no manual selection)
- Preserve user's language in task titles
- Frontend: Use Noto Nastaliq Urdu font, RTL text direction
- Database: UTF-8 encoding (Neon default)

---

## 6. Privacy Compliance & Opt-in AI Features

### Decision

**Implement explicit opt-in flow with clear privacy notice before enabling AI features**

Same as before - this section remains unchanged (lines 901-1210 in original).

**Key Requirements:**
- Default: AI disabled
- Explicit consent required
- GDPR/CCPA compliant
- Easy opt-out with data deletion

---

## Summary & Updated Recommendations

### Technology Decisions Summary

| Component | Decision | Rationale |
|-----------|----------|-----------|
| **Chat UI** | **OpenAI ChatKit** (`@openai/chatkit-react`) | Official pre-built UI, hackathon requirement |
| **AI Agent Runtime** | **OpenAI Agents SDK** (`openai-agents`) | Production-ready, session management, hackathon requirement |
| **MCP Implementation** | **Official MCP Python SDK** (`mcp[cli]`) | Standardized protocol, FastAPI integration, hackathon requirement |
| **AI Model** | **OpenAI GPT-4o** | Best multilingual support (Urdu), function calling |
| **Real-time Streaming** | **ChatKit built-in + SSE** | ChatKit handles streaming automatically |
| **Language Support** | **GPT-4o native Urdu** | No translation API needed, auto-detection |
| **Privacy** | **Explicit opt-in with notice** | GDPR/CCPA compliance, builds trust |

### Implementation Priorities (Updated)

**Phase III MVP (P1):**
1. ✅ Install ChatKit, Agents SDK, MCP SDK
2. ✅ Implement ChatKit frontend component
3. ✅ Create backend `/api/chatkit/session` endpoint
4. ✅ Build Agents SDK task agent with function tools
5. ✅ Create MCP server with 5 required tools (add_task, list_tasks, complete_task, delete_task, update_task)
6. ✅ Integrate Agents SDK with MCP server
7. ✅ Privacy opt-in flow and consent tracking
8. ✅ Test English + Urdu support

**Phase III Enhancements (P2):**
9. Chat history persistence in database
10. Improved error handling and fallbacks
11. Rate limiting and cost controls
12. Conversation management (Conversation table)

**Phase IV Bonus Features (P3):**
13. Voice input (speech-to-text) - +200 points
14. Advanced AI task organization
15. Analytics on AI usage patterns

### Key Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| ChatKit learning curve | Medium | Follow official guides, starter templates |
| Agents SDK + MCP complexity | High | Use provided examples, test incrementally |
| OpenAI API costs | High | Rate limiting, token limits, usage alerts |
| Privacy compliance issues | High | Legal review, explicit opt-in, audit logging |
| Poor Urdu accuracy | Medium | Test with native speakers, feedback loop |

### Next Steps

1. ✅ Complete updated research documentation (this file)
2. ⏭️ Update data-model.md to add Conversation and Message tables
3. ⏭️ Update contracts/chat-api.yaml to match hackathon spec
4. ⏭️ Update plan.md with correct architecture
5. ⏭️ Update tasks.md with ChatKit + Agents SDK + MCP implementation tasks
6. ⏭️ Update quickstart.md with correct setup instructions

---

**Research completed**: 2025-12-16
**Status**: ✅ Updated for Strict Hackathon Compliance
**Ready for**: Data model and contract updates

---

## Sources

- [OpenAI ChatKit JS Repository](https://github.com/openai/chatkit-js)
- [Build with Matija: ChatKit Next.js Integration](https://www.buildwithmatija.com/blog/chatkit-nextjs-integration)
- [Medium: Ship an AI Chat UI in Minutes](https://medium.com/@dorangao/ship-an-ai-chat-ui-in-minutes-openai-chatkit-next-js-with-a-ready-to-fork-starter-d1a3208c6e6c)
- [DEV: Integrating OpenAI's ChatKit with FastAPI](https://dev.to/rajeev_3ce9f280cbae73b234/--3hhn)
- [OpenAI Agents SDK GitHub](https://github.com/openai/openai-agents-python)
- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [OpenAI Agents SDK MCP Integration](https://openai.github.io/openai-agents-python/mcp/)
- [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Python SDK Documentation](https://modelcontextprotocol.github.io/python-sdk/)
- [GitHub: openai-agents-streaming-api (FastAPI Example)](https://github.com/ahmad2b/openai-agents-streaming-api)
- [GitHub: poc-agent-sdk (FastAPI Example)](https://github.com/kooljo/poc-agent-sdk)
- [DEV: Building Production-Ready AI Agents](https://dev.to/parupati/building-production-ready-ai-agents-with-openai-agents-sdk-and-fastapi-abd)
