# System Architecture - Phase II

## Overview

Phase II transforms the todo app into a **full-stack web application** with a clear separation between frontend, backend, and database layers. The architecture follows modern best practices for scalability, security, and maintainability.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Next.js 16+ Frontend (App Router)                       │   │
│  │  - React Server Components                                │   │
│  │  - Client Components for interactivity                    │   │
│  │  - Tailwind CSS styling                                   │   │
│  │  - Better Auth (client-side session management)          │   │
│  └─────────────────────┬────────────────────────────────────┘   │
└────────────────────────┼─────────────────────────────────────────┘
                         │
                         │ HTTPS/REST API
                         │ Authorization: Bearer <JWT>
                         │
┌────────────────────────┼─────────────────────────────────────────┐
│                        ▼                                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  FastAPI Backend                                          │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  JWT Middleware (verify token, extract user_id)   │  │   │
│  │  └──────────────────┬─────────────────────────────────┘  │   │
│  │                     ▼                                     │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  API Routes                                        │  │   │
│  │  │  - /api/{user_id}/tasks (GET, POST)               │  │   │
│  │  │  - /api/{user_id}/tasks/{id} (GET, PUT, DELETE)   │  │   │
│  │  │  - /api/{user_id}/tasks/{id}/complete (PATCH)     │  │   │
│  │  └──────────────────┬─────────────────────────────────┘  │   │
│  │                     ▼                                     │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  Business Logic Layer (SQLModel)                   │  │   │
│  │  │  - Task model with validation                      │  │   │
│  │  │  - User filtering and authorization                │  │   │
│  │  └──────────────────┬─────────────────────────────────┘  │   │
│  └────────────────────┬┘                                      │   │
└────────────────────────┼─────────────────────────────────────────┘
                         │
                         │ PostgreSQL Protocol
                         │ (connection string from env)
                         │
┌────────────────────────┼─────────────────────────────────────────┐
│                        ▼                                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Neon Serverless PostgreSQL                               │   │
│  │  ┌────────────────┐  ┌────────────────┐                  │   │
│  │  │  users table   │  │  tasks table   │                  │   │
│  │  │  (Better Auth) │  │  (user-scoped) │                  │   │
│  │  └────────────────┘  └────────────────┘                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Layer (Next.js 16+)

**Responsibilities:**
- Render UI components (tasks list, forms, auth pages)
- Handle user interactions (add task, mark complete, etc.)
- Manage client-side state and session
- Call backend API with JWT token in headers

**Key Technologies:**
- **Next.js 16+ App Router**: Server and client components
- **Better Auth**: Client-side authentication library
- **Tailwind CSS**: Utility-first styling
- **TypeScript**: Type safety

**File Structure:**
```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page
│   ├── login/
│   │   └── page.tsx        # Login page
│   ├── signup/
│   │   └── page.tsx        # Signup page
│   └── dashboard/
│       └── page.tsx        # Task dashboard (protected)
├── components/
│   ├── TaskList.tsx
│   ├── TaskItem.tsx
│   ├── AddTaskForm.tsx
│   └── Header.tsx
└── lib/
    └── api.ts              # API client with JWT handling
```

### Backend Layer (FastAPI)

**Responsibilities:**
- Expose RESTful API endpoints
- Verify JWT tokens and extract authenticated user
- Enforce user-level data isolation (users only see their tasks)
- Perform CRUD operations on database via SQLModel
- Return JSON responses

**Key Technologies:**
- **FastAPI**: Modern Python web framework
- **SQLModel**: ORM combining SQLAlchemy + Pydantic
- **Python JWT**: Token verification
- **Uvicorn**: ASGI server

**File Structure:**
```
backend/
├── src/
│   ├── main.py                 # FastAPI app entry point
│   ├── models.py               # SQLModel database models
│   ├── db.py                   # Database connection and session
│   ├── middleware/
│   │   └── auth.py             # JWT verification middleware
│   └── routes/
│       ├── tasks.py            # Task CRUD endpoints
│       └── auth.py             # Authentication endpoints (optional)
└── pyproject.toml
```

### Database Layer (Neon PostgreSQL)

**Responsibilities:**
- Persist user accounts (managed by Better Auth)
- Persist tasks with user ownership
- Provide ACID transactions
- Enable efficient querying with indexes

**Schema:**
```sql
-- users table (managed by Better Auth)
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR,
    password_hash VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);

-- tasks table (our application data)
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
```

## Authentication & Authorization Flow

### 1. User Signup/Login
```
User → Frontend (Better Auth) → POST /api/auth/signup
                              → Better Auth creates user in DB
                              → Returns JWT token
Frontend stores JWT token (cookie/localStorage)
```

### 2. Authenticated API Request
```
User clicks "Add Task" → Frontend sends POST /api/{user_id}/tasks
                       → Headers: Authorization: Bearer <JWT>
                       → Backend JWT middleware:
                           - Verify token signature
                           - Extract user_id from token
                           - Match user_id in URL path
                       → Route handler:
                           - Create task with authenticated user_id
                           - Return task data
```

### 3. Security Guarantees
- **User Isolation**: All queries filtered by `user_id`
- **Token Expiry**: JWTs expire after configurable time (e.g., 7 days)
- **Stateless Auth**: Backend doesn't maintain session state
- **No Shared DB Access**: Each user can only access their own data

## API Design Principles

1. **RESTful Conventions**: Use HTTP methods correctly (GET, POST, PUT, DELETE, PATCH)
2. **User-Scoped Endpoints**: All endpoints include `{user_id}` in path
3. **Consistent Responses**: Standard JSON format with proper HTTP status codes
4. **Error Handling**: Descriptive error messages with appropriate status codes
5. **Validation**: Pydantic models for request/response validation

## Data Flow Example: Add Task

```
1. User fills form on frontend
2. Frontend calls: POST /api/user123/tasks
   Headers: Authorization: Bearer eyJ0eXAi...
   Body: { "title": "Buy groceries", "description": "Milk, eggs" }

3. Backend middleware verifies JWT, extracts user_id="user123"
4. Backend validates user_id in URL matches JWT user_id
5. Backend creates SQLModel task:
   Task(user_id="user123", title="Buy groceries", description="Milk, eggs")
6. Backend saves to database
7. Backend returns: { "id": 42, "user_id": "user123", "title": "Buy groceries", ... }
8. Frontend updates UI with new task
```

## Non-Functional Requirements

### Performance
- API response time: < 200ms for CRUD operations
- Database query optimization with indexes
- Connection pooling for database efficiency

### Scalability
- Stateless backend enables horizontal scaling
- Database connection pooling
- Frontend deployed on CDN (Vercel)

### Security
- JWT secret stored in environment variables
- HTTPS only in production
- SQL injection prevention via SQLModel ORM
- CORS configuration for frontend domain

### Reliability
- Database transactions for data consistency
- Graceful error handling and logging
- Health check endpoints

## Deployment Architecture

### Development
```
Frontend: localhost:3000 (Next.js dev server)
Backend: localhost:8000 (Uvicorn)
Database: Neon cloud instance
```

### Production
```
Frontend: Vercel CDN (vercel.app)
Backend: Cloud provider (Vercel serverless, Railway, Render, etc.)
Database: Neon Serverless PostgreSQL
```

## Technology Decisions

### Why Next.js 16+ App Router?
- Server components for better performance
- Built-in routing and layouts
- Easy deployment to Vercel
- Modern React patterns

### Why FastAPI?
- Fast performance (async/await support)
- Automatic API documentation (OpenAPI)
- Excellent type hints with Pydantic
- Easy integration with SQLModel

### Why SQLModel?
- Combines SQLAlchemy (ORM) + Pydantic (validation)
- Type safety with Python type hints
- Automatic migration generation
- Compatible with FastAPI

### Why Better Auth?
- JWT token support out of the box
- Flexible and lightweight
- Easy integration with Next.js
- Supports multiple providers

### Why Neon PostgreSQL?
- Serverless with automatic scaling
- Free tier for development
- Branching for testing
- Built-in connection pooling

## Migration from Phase I

Phase I had in-memory storage. Phase II migrates to persistent storage:

**Phase I:**
```python
tasks = []  # In-memory list
```

**Phase II:**
```python
# SQLModel with PostgreSQL
task = Task(user_id=user_id, title=title, ...)
session.add(task)
session.commit()
```

**Key Changes:**
1. Add `user_id` field to Task model
2. Replace list operations with database queries
3. Add JWT authentication
4. Create multi-user frontend

## Future Evolution

**Phase III**: Add MCP server layer for AI chatbot
**Phase IV**: Containerize and deploy to Kubernetes
**Phase V**: Add Kafka for event-driven architecture

This architecture provides a solid foundation for these future enhancements while maintaining clean separation of concerns.
