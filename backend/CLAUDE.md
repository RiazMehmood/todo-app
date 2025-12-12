# Backend Guidelines - FastAPI Todo App

## Overview

This is the **backend** API for the Todo app, built with Python FastAPI. It provides RESTful endpoints for task management with JWT authentication and PostgreSQL persistence.

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.13+
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: JWT token verification (Better Auth integration)
- **Server**: Uvicorn (ASGI)
- **Package Manager**: UV

## Project Structure

```
backend/
├── src/
│   ├── main.py                  # FastAPI app entry point
│   ├── db.py                    # Database connection and session
│   ├── models.py                # SQLModel database models
│   ├── middleware/
│   │   └── auth.py              # JWT verification middleware
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── tasks.py             # Task CRUD endpoints
│   │   └── auth.py              # Auth endpoints (optional)
│   └── __init__.py
├── pyproject.toml               # UV project configuration
├── .env.example                 # Environment variables template
└── README.md
```

## Development Setup

### 1. Install UV
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Create Virtual Environment
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
uv pip install fastapi sqlmodel uvicorn psycopg2-binary python-jose passlib python-dotenv
```

### 4. Environment Variables

Create `.env` file:
```
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
BETTER_AUTH_SECRET=your-secret-key-here
```

### 5. Run Server
```bash
uvicorn src.main:app --reload --port 8000
```

## Database Models

### Task Model

```python
# src/models.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, max_length=255)
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### User Model (Managed by Better Auth)

```python
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True, max_length=255)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=100)
    password_hash: str = Field(max_length=255)
    email_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Note**: Better Auth manages the `users` table. Don't modify it directly.

## Database Connection

```python
# src/db.py
from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production)
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True  # Verify connections before use
)

def create_db_and_tables():
    """Create all tables (for development)"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for database session"""
    with Session(engine) as session:
        yield session
```

## JWT Middleware

```python
# src/middleware/auth.py
from fastapi import Request, HTTPException, Depends
from jose import jwt, JWTError
import os

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

async def verify_jwt(request: Request):
    """Verify JWT token and extract user info"""
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header"
        )

    token = auth_header.split(' ')[1]

    try:
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=['HS256'])
        request.state.user_id = payload['user_id']
        request.state.user_email = payload.get('email')
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## API Routes

### Main Application

```python
# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db import create_db_and_tables
from src.routes import tasks

app = FastAPI(
    title="Todo API",
    description="RESTful API for todo task management",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourapp.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Include routers
app.include_router(tasks.router, prefix="/api", tags=["tasks"])

@app.get("/")
def root():
    return {"message": "Todo API - Phase II"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

### Task Routes

```python
# src/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from src.db import get_session
from src.models import Task
from src.middleware.auth import verify_jwt
from typing import List, Optional

router = APIRouter(dependencies=[Depends(verify_jwt)])

@router.get("/{user_id}/tasks", response_model=List[Task])
def get_tasks(
    user_id: str,
    request: Request,
    session: Session = Depends(get_session),
    status: Optional[str] = "all"
):
    """Get all tasks for authenticated user"""
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Cannot access other user's tasks")

    # Query tasks
    statement = select(Task).where(Task.user_id == user_id)

    if status == "pending":
        statement = statement.where(Task.completed == False)
    elif status == "completed":
        statement = statement.where(Task.completed == True)

    tasks = session.exec(statement).all()
    return tasks

@router.post("/{user_id}/tasks", response_model=Task, status_code=201)
def create_task(
    user_id: str,
    task_data: dict,
    request: Request,
    session: Session = Depends(get_session)
):
    """Create a new task"""
    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Cannot create task for other user")

    task = Task(
        user_id=user_id,
        title=task_data['title'],
        description=task_data.get('description')
    )

    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.get("/{user_id}/tasks/{task_id}", response_model=Task)
def get_task(
    user_id: str,
    task_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """Get a single task"""
    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@router.put("/{user_id}/tasks/{task_id}", response_model=Task)
def update_task(
    user_id: str,
    task_id: int,
    task_data: dict,
    request: Request,
    session: Session = Depends(get_session)
):
    """Update a task"""
    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields
    if 'title' in task_data:
        task.title = task_data['title']
    if 'description' in task_data:
        task.description = task_data['description']

    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/{user_id}/tasks/{task_id}")
def delete_task(
    user_id: str,
    task_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """Delete a task"""
    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return {"message": "Task deleted successfully", "id": task_id}

@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=Task)
def toggle_task(
    user_id: str,
    task_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """Toggle task completion status"""
    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

## API Conventions

### Response Format

**Success** (200/201):
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries",
  "completed": false
}
```

**Error** (4xx/5xx):
```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes

- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE (optional)
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Missing/invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource doesn't exist
- `500 Internal Server Error` - Server error

## Validation

Use Pydantic models for request/response validation:

```python
from pydantic import BaseModel, Field

class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

@router.post("/{user_id}/tasks", response_model=Task)
def create_task(
    user_id: str,
    task_data: CreateTaskRequest,  # Use Pydantic model
    request: Request,
    session: Session = Depends(get_session)
):
    # task_data.title and task_data.description are validated
    ...
```

## Error Handling

### Custom Exception Handler

```python
# src/main.py
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()}
    )
```

### Graceful Error Messages

```python
try:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
except Exception as e:
    raise HTTPException(status_code=500, detail="Internal server error")
```

## Security Best Practices

1. **Environment Variables**: Never hardcode secrets
2. **SQL Injection Prevention**: Use SQLModel/SQLAlchemy (parameterized queries)
3. **JWT Verification**: Always verify token signature
4. **User Isolation**: Filter all queries by `user_id`
5. **HTTPS Only**: Use HTTPS in production
6. **CORS**: Allow only trusted origins

## Database Migrations (Optional)

Use Alembic for schema migrations:

```bash
uv pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Create tasks table"
alembic upgrade head
```

## Testing (Future)

Use pytest for unit and integration tests:

```python
# tests/test_tasks.py
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_get_tasks():
    response = client.get("/api/user123/tasks", headers={
        "Authorization": "Bearer valid-token"
    })
    assert response.status_code == 200
```

## Logging

Add logging for debugging:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/{user_id}/tasks")
def create_task(...):
    logger.info(f"Creating task for user {user_id}")
    ...
```

## API Documentation

FastAPI auto-generates OpenAPI docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Deployment

### Local Development
```bash
uvicorn src.main:app --reload --port 8000
```

### Production (Example with Gunicorn)
```bash
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables
- Development: `.env` file
- Production: Set via cloud provider dashboard

## Specifications

Before implementing features, always read:
- `@specs/api/rest-endpoints.md` - API endpoint specifications
- `@specs/database/schema.md` - Database schema
- `@specs/features/task-crud.md` - Feature requirements
- `@specs/features/authentication.md` - Auth requirements

## Common Tasks

### Add a new endpoint
1. Define route in `src/routes/tasks.py`
2. Follow specification in `@specs/api/rest-endpoints.md`
3. Add JWT authentication with `Depends(verify_jwt)`
4. Verify user authorization

### Add a new model
1. Define SQLModel in `src/models.py`
2. Follow schema in `@specs/database/schema.md`
3. Run migrations if using Alembic

### Update database schema
1. Update model in `src/models.py`
2. Create migration: `alembic revision --autogenerate -m "Description"`
3. Apply migration: `alembic upgrade head`

## Best Practices

1. **Type Hints**: Use type hints for all functions
2. **Dependency Injection**: Use FastAPI's `Depends()` for sessions and auth
3. **Error Handling**: Always return appropriate HTTP status codes
4. **Validation**: Use Pydantic models for request validation
5. **Security**: Verify JWT and user authorization on every endpoint
6. **Database**: Use SQLModel for type-safe ORM
7. **Logging**: Log important events for debugging

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python JWT (python-jose)](https://python-jose.readthedocs.io/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
