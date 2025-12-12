# Database Schema

## Overview

The todo application uses **Neon Serverless PostgreSQL** for persistent data storage. The schema supports multi-user functionality with proper isolation and relationships.

## Connection

**Connection String Format:**
```
postgresql://username:password@host:port/database?sslmode=require
```

**Environment Variable:**
```
DATABASE_URL=postgresql://user:pass@ep-cool-name-12345.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Connection Pooling:**
- Use SQLModel/SQLAlchemy connection pooling
- Pool size: 5-10 connections (for serverless)
- Max overflow: 10

## Tables

### 1. users

Managed by Better Auth. Contains user account information.

**Table Definition:**
```sql
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Columns:**

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | VARCHAR(255) | NO | UUID | Unique user identifier |
| email | VARCHAR(255) | NO | - | User email (unique) |
| name | VARCHAR(100) | NO | - | User display name |
| password_hash | VARCHAR(255) | NO | - | Bcrypt hashed password |
| email_verified | BOOLEAN | NO | FALSE | Email verification status |
| created_at | TIMESTAMP | NO | NOW() | Account creation time |
| updated_at | TIMESTAMP | NO | NOW() | Last update time |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);
```

**SQLModel Definition:**
```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=100)
    password_hash: str = Field(max_length=255)
    email_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Note**: Better Auth manages this table. Application code should NOT directly create/update users.

---

### 2. tasks

Application-managed table containing todo tasks.

**Table Definition:**
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Columns:**

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | SERIAL (INTEGER) | NO | AUTO | Unique task identifier |
| user_id | VARCHAR(255) | NO | - | Foreign key to users.id |
| title | VARCHAR(200) | NO | - | Task title |
| description | TEXT | YES | NULL | Task description |
| completed | BOOLEAN | NO | FALSE | Completion status |
| created_at | TIMESTAMP | NO | NOW() | Task creation time |
| updated_at | TIMESTAMP | NO | NOW() | Last update time |

**Constraints:**
- **Primary Key**: `id`
- **Foreign Key**: `user_id` REFERENCES `users(id)` ON DELETE CASCADE
  - If user is deleted, all their tasks are deleted
- **NOT NULL**: `id`, `user_id`, `title`, `completed`, `created_at`, `updated_at`

**Indexes:**
```sql
-- User filtering (most common query)
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Status filtering (for future features)
CREATE INDEX idx_tasks_completed ON tasks(completed);

-- Composite index for user + status queries
CREATE INDEX idx_tasks_user_status ON tasks(user_id, completed);
```

**SQLModel Definition:**
```python
from sqlmodel import SQLModel, Field, Relationship
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

    # Optional: Relationship to User
    # user: Optional[User] = Relationship(back_populates="tasks")
```

---

## Relationships

```
users (1) ──────< (N) tasks
  │                    │
  │                    │
  id  <─────────  user_id (FK)
```

- One user can have many tasks
- Each task belongs to exactly one user
- Cascading delete: Deleting a user deletes all their tasks

## Database Migrations

### Initial Migration (Create Tables)

**Using Alembic:**
```bash
# Install alembic
pip install alembic

# Initialize alembic
alembic init migrations

# Edit alembic.ini with DATABASE_URL

# Create migration
alembic revision --autogenerate -m "Create users and tasks tables"

# Apply migration
alembic upgrade head
```

**Or Manual SQL Script:**
```sql
-- migrations/001_initial_schema.sql

-- Create users table (Better Auth)
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Create tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, completed);
```

### Applying Migrations on Neon

1. Connect to Neon database via psql or pgAdmin
2. Run SQL script to create tables
3. Or use SQLModel's `create_all()` for development:

```python
from sqlmodel import create_engine, SQLModel

engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)
```

**Note**: Use migrations (Alembic) for production to track schema changes.

## Query Examples

### Get all tasks for a user
```python
from sqlmodel import Session, select

tasks = session.exec(
    select(Task).where(Task.user_id == "user123")
).all()
```

### Get completed tasks for a user
```python
tasks = session.exec(
    select(Task).where(
        Task.user_id == "user123",
        Task.completed == True
    )
).all()
```

### Create a task
```python
task = Task(
    user_id="user123",
    title="Buy groceries",
    description="Milk, eggs, bread"
)
session.add(task)
session.commit()
session.refresh(task)  # Get auto-generated ID
```

### Update a task
```python
task = session.get(Task, task_id)
if task and task.user_id == "user123":
    task.title = "Buy groceries and fruits"
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
```

### Delete a task
```python
task = session.get(Task, task_id)
if task and task.user_id == "user123":
    session.delete(task)
    session.commit()
```

### Toggle completion
```python
task = session.get(Task, task_id)
if task and task.user_id == "user123":
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
```

## Data Validation

### Database Level
- **NOT NULL** constraints on required fields
- **UNIQUE** constraint on `users.email`
- **Foreign Key** constraint ensures referential integrity
- **CHECK** constraints (future: e.g., `CHECK (LENGTH(title) >= 1)`)

### Application Level (SQLModel/Pydantic)
- `title`: 1-200 characters
- `description`: Max 1000 characters
- `email`: Valid email format
- `user_id`: Must exist in users table

## Performance Considerations

### Indexes
- `idx_tasks_user_id` - Most queries filter by user
- `idx_tasks_completed` - For status filtering (future)
- `idx_tasks_user_status` - Composite for user + status queries

### Connection Pooling
```python
from sqlmodel import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=5,        # Number of persistent connections
    max_overflow=10,    # Additional connections under load
    pool_pre_ping=True  # Verify connections before use
)
```

### Serverless Optimization
- Use Neon's auto-suspend feature (scales to zero when idle)
- Keep pool size small (5-10) for serverless
- Use `pool_pre_ping=True` to handle connection drops

## Neon-Specific Features

### Branching (Development/Testing)
```bash
# Create a branch for testing migrations
neonctl branches create --name testing

# Get connection string for branch
neonctl connection-string testing
```

### Auto-Suspend
- Database automatically suspends after inactivity
- Resumes instantly on first query
- No manual management needed

### Connection Pooling
- Neon provides built-in connection pooling
- Use pooled connection string for better performance:
  ```
  postgresql://user:pass@host/db?sslmode=require&pooler=true
  ```

## Security

### Password Storage
- Never store plaintext passwords
- Better Auth handles bcrypt hashing
- Use `password_hash` field

### SQL Injection Prevention
- Use SQLModel/SQLAlchemy (parameterized queries)
- Never concatenate user input into SQL strings

### Data Isolation
- All queries filter by `user_id`
- Backend middleware enforces user context
- Database constraints prevent orphaned tasks

## Backup and Recovery

Neon provides automated backups:
- Point-in-time recovery (PITR)
- Retention: 7 days (free tier) to 30 days (paid)
- No manual backup needed for development

## Future Schema Changes (Not in Phase II)

### Phase III (Chatbot)
```sql
-- Conversation history tables
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Phase V (Advanced Features)
```sql
-- Add priority and tags
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10);  -- 'high', 'medium', 'low'
ALTER TABLE tasks ADD COLUMN tags TEXT[];           -- Array of tags
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP;
ALTER TABLE tasks ADD COLUMN recurrence VARCHAR(50); -- 'daily', 'weekly', etc.
```

## Database Initialization Script

```python
# src/db.py
from sqlmodel import create_engine, SQLModel, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production)
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)

def create_db_and_tables():
    """Create all tables (for development)"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session for dependency injection"""
    with Session(engine) as session:
        yield session
```

## Summary

- **2 tables**: `users` (Better Auth), `tasks` (application)
- **Foreign key**: `tasks.user_id` → `users.id` (CASCADE DELETE)
- **Indexes**: Optimized for user filtering and status queries
- **SQLModel**: Type-safe ORM with Pydantic validation
- **Neon**: Serverless PostgreSQL with auto-scaling
