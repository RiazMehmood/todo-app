# Data Model: Redpanda Cloud Integration

**Date**: 2025-12-22
**Branch**: 004-kubernetes-deployment
**Purpose**: Define event schemas, Kafka topics, and data flows for Phase V event-driven architecture

## Overview

The Redpanda Cloud integration uses an event-driven architecture where the backend API publishes events to Kafka topics, and microservices consume these events for processing. All events follow CloudEvents specification principles.

## Kafka Topics

### Topic Architecture

| Topic Name | Purpose | Retention | Partitions | Consumers | Publishers |
|------------|---------|-----------|------------|-----------|------------|
| `task-events` | Audit trail for all task operations | 7 days | 3 | audit-service | backend-service |
| `task-updates` | Real-time sync across clients | 1 hour | 3 | (future: websocket-service) | backend-service |
| `reminders` | Due date reminder notifications | 24 hours | 2 | notification-service | backend-service, cron-service |
| `recurring-tasks` | Recurring task completion processing | 24 hours | 2 | (future: recurring-task-service) | backend-service |

### Topic Configuration

```yaml
# task-events
topic: task-events
partitions: 3
retention.ms: 604800000  # 7 days
retention.bytes: 5368709120  # 5 GB
cleanup.policy: delete
```

```yaml
# task-updates
topic: task-updates
partitions: 3
retention.ms: 3600000  # 1 hour
retention.bytes: 524288000  # 500 MB
cleanup.policy: delete
```

```yaml
# reminders
topic: reminders
partitions: 2
retention.ms: 86400000  # 24 hours
retention.bytes: 1073741824  # 1 GB
cleanup.policy: delete
```

```yaml
# recurring-tasks
topic: recurring-tasks
partitions: 2
retention.ms: 86400000  # 24 hours
retention.bytes: 1073741824  # 1 GB
cleanup.policy: delete
```

## Event Schemas

### Base Event Structure

All events follow this base structure:

```typescript
interface BaseEvent {
  event_type: string;           // Event type identifier
  timestamp: string;            // ISO 8601 timestamp (UTC)
  metadata: {
    source: string;             // Originating service (e.g., "backend-api")
    version: string;            // Event schema version (e.g., "1.0")
    [key: string]: any;         // Additional metadata
  };
}
```

### 1. Task Event Schema

**Topic**: `task-events`
**Purpose**: Audit trail for all task CRUD operations
**Published By**: backend-service
**Consumed By**: audit-service

#### Event Types

##### 1.1 Task Created Event

```json
{
  "event_type": "created",
  "task_id": 123,
  "user_id": "user_abc123",
  "task_data": {
    "id": 123,
    "user_id": "user_abc123",
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "completed": false,
    "priority": "high",
    "tags": ["shopping", "urgent"],
    "due_date": "2025-12-25T10:00:00Z",
    "remind_before_minutes": 30,
    "recurrence_pattern": null,
    "recurrence_interval": null,
    "recurrence_days": null,
    "recurrence_end_date": null,
    "parent_task_id": null,
    "ai_generated": false,
    "created_at": "2025-12-22T12:00:00Z",
    "updated_at": "2025-12-22T12:00:00Z"
  },
  "timestamp": "2025-12-22T12:00:00Z",
  "metadata": {
    "source": "backend-api",
    "version": "1.0"
  }
}
```

##### 1.2 Task Updated Event

```json
{
  "event_type": "updated",
  "task_id": 123,
  "user_id": "user_abc123",
  "task_data": {
    "id": 123,
    "title": "Buy groceries (updated)",
    "completed": false,
    "priority": "medium",
    ...
  },
  "timestamp": "2025-12-22T13:00:00Z",
  "metadata": {
    "source": "backend-api",
    "version": "1.0",
    "changes": {
      "title": "Buy groceries (updated)",
      "priority": "medium"
    }
  }
}
```

**Fields**:
- `changes`: Object containing only fields that changed (key-value pairs)

##### 1.3 Task Completed Event

```json
{
  "event_type": "completed",
  "task_id": 123,
  "user_id": "user_abc123",
  "task_data": {
    "id": 123,
    "completed": true,
    ...
  },
  "timestamp": "2025-12-22T14:00:00Z",
  "metadata": {
    "source": "backend-api",
    "version": "1.0",
    "is_recurring": false
  }
}
```

**Fields**:
- `metadata.is_recurring`: Boolean indicating if this is a recurring task

##### 1.4 Task Deleted Event

```json
{
  "event_type": "deleted",
  "task_id": 123,
  "user_id": "user_abc123",
  "task_data": {
    "id": 123,
    "title": "Buy groceries",
    ...
  },
  "timestamp": "2025-12-22T15:00:00Z",
  "metadata": {
    "source": "backend-api",
    "version": "1.0"
  }
}
```

**Note**: `task_data` contains full task snapshot before deletion

---

### 2. Task Update Event Schema (Real-time Sync)

**Topic**: `task-updates`
**Purpose**: Real-time synchronization across clients (WebSocket, SSE)
**Published By**: backend-service
**Consumed By**: (future) websocket-service

```json
{
  "event_type": "task_updated",
  "task_id": 123,
  "user_id": "user_abc123",
  "changes": {
    "title": "New title",
    "priority": "high",
    "tags": ["urgent", "shopping"]
  },
  "timestamp": "2025-12-22T13:00:00Z"
}
```

**Purpose**: Lightweight event for real-time UI updates (only changed fields)

---

### 3. Reminder Event Schema

**Topic**: `reminders`
**Purpose**: Trigger reminder notifications before task due dates
**Published By**: backend-service (on task create/update), cron-service (scheduled)
**Consumed By**: notification-service

```json
{
  "event_type": "reminder_due",
  "task_id": 123,
  "user_id": "user_abc123",
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "due_date": "2025-12-25T10:00:00Z",
  "remind_before_minutes": 30,
  "priority": "high",
  "tags": ["shopping", "urgent"],
  "timestamp": "2025-12-22T12:00:00Z"
}
```

**Fields**:
- `due_date`: ISO 8601 timestamp of when task is due
- `remind_before_minutes`: Minutes before due date to send reminder (e.g., 30 = remind at 09:30)

**Trigger Logic**:
- Cron service checks database every 5 minutes
- Publishes reminder event when `current_time >= due_date - remind_before_minutes`
- Notification service sends email/push notification

---

### 4. Recurring Task Event Schema

**Topic**: `recurring-tasks`
**Purpose**: Automatically create next instance of recurring task when completed
**Published By**: backend-service (on recurring task completion)
**Consumed By**: (future) recurring-task-service, backend-service

```json
{
  "event_type": "recurring_task_completed",
  "task_id": 123,
  "parent_task_id": 120,
  "user_id": "user_abc123",
  "recurrence_pattern": "weekly",
  "recurrence_interval": 1,
  "recurrence_days": ["monday", "wednesday", "friday"],
  "next_occurrence": "2025-12-29T10:00:00Z",
  "recurrence_end_date": "2026-01-01T00:00:00Z",
  "task_data": {
    "title": "Weekly standup",
    "description": "Team sync meeting",
    "priority": "medium",
    "tags": ["meeting", "recurring"]
  },
  "timestamp": "2025-12-22T14:00:00Z"
}
```

**Fields**:
- `parent_task_id`: ID of the original recurring task (or self if first completion)
- `recurrence_pattern`: `"daily"` | `"weekly"` | `"monthly"`
- `recurrence_interval`: Every N days/weeks/months (e.g., 2 = every 2 weeks)
- `recurrence_days`: For weekly pattern, days of week (`["monday", "friday"]`)
- `next_occurrence`: ISO timestamp for next task due date
- `recurrence_end_date`: Optional end date (null = infinite recurrence)

**Processing Logic**:
1. Backend publishes this event when user completes a recurring task
2. Recurring-task-service (or backend itself) consumes event
3. Creates new Task with `due_date = next_occurrence` and `parent_task_id = current_task_id`
4. Publishes `task-events` "created" event for new task

---

## Data Entities

### Task (Primary Entity)

**Table**: `tasks`
**ORM**: SQLModel (SQLAlchemy + Pydantic)

```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # Core fields
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, max_length=255)
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)

    # Phase V fields
    priority: str = Field(default="medium", max_length=20)  # "low", "medium", "high"
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    due_date: Optional[datetime] = Field(default=None)
    remind_before_minutes: Optional[int] = Field(default=None)

    # Recurring task fields
    recurrence_pattern: Optional[str] = Field(default=None, max_length=20)
    recurrence_interval: Optional[int] = Field(default=None)
    recurrence_days: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    recurrence_end_date: Optional[datetime] = Field(default=None)
    parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")

    # AI generation
    ai_generated: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Validation Rules**:
- `title`: Required, 1-200 characters
- `priority`: Must be one of ["low", "medium", "high"]
- `tags`: Array of strings, max 10 tags, each max 30 characters
- `due_date`: Must be in the future (on creation)
- `remind_before_minutes`: Must be >0 if set, max 10080 (1 week)
- `recurrence_pattern`: Must be one of ["daily", "weekly", "monthly"] if set
- `recurrence_interval`: Must be >0 if recurring, max 365
- `recurrence_days`: Required if pattern is "weekly", must be valid day names

**Indexes**:
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_parent_id ON tasks(parent_task_id) WHERE parent_task_id IS NOT NULL;
```

---

### AuditLog (Audit Service Entity)

**Table**: `audit_logs`
**Purpose**: Persistent audit trail of all task operations
**Service**: audit-service

```python
class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str = Field(max_length=50, index=True)  # "created", "updated", "completed", "deleted"
    task_id: int = Field(index=True)
    user_id: str = Field(max_length=255, index=True)
    task_data: dict = Field(sa_column=Column(JSON))  # Full task snapshot
    changes: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # For "updated" events
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    source: str = Field(default="backend-api", max_length=50)
```

**Indexes**:
```sql
CREATE INDEX idx_audit_task_id ON audit_logs(task_id);
CREATE INDEX idx_audit_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_event_type ON audit_logs(event_type);
```

**Retention Policy**: Keep audit logs for 90 days, then archive or delete

---

## Event Flow Diagrams

### 1. Task Creation Flow

```
User → Frontend → Backend API → Dapr Sidecar → Redpanda (task-events)
                                                        ↓
                                           Audit Service ← Dapr Sidecar
                                                        ↓
                                              PostgreSQL (audit_logs)
```

### 2. Reminder Flow

```
Cron Service (every 5 min) → Check DB for due tasks
                                    ↓
                          Publish to Redpanda (reminders)
                                    ↓
                        Notification Service ← Dapr Sidecar
                                    ↓
                          Send Email/Push Notification
```

### 3. Recurring Task Flow

```
User completes recurring task → Backend API → Publish (recurring-tasks)
                                                        ↓
                                           Backend/Service ← Dapr Sidecar
                                                        ↓
                                         Create new Task (next occurrence)
                                                        ↓
                                          Publish (task-events: created)
```

---

## State Transitions

### Task Completion States

```
[Not Started] →(complete)→ [Completed]
      ↑                          ↓
      └──────(uncomplete)────────┘
```

**Events Published**:
- Complete: `task-events` ("completed"), `recurring-tasks` (if recurring)
- Uncomplete: `task-events` ("updated" with `completed=false`)

---

## Error Handling

### Event Publishing Failures

**Behavior**: Graceful degradation
- If Dapr unavailable: Log error, continue processing HTTP request
- If Kafka unavailable: Dapr retries (3 attempts, exponential backoff)
- Backend never blocks on event publishing (async fire-and-forget)

**Code**:
```python
# backend/src/events.py
async def publish_event(topic: str, event_data: dict) -> bool:
    if not KAFKA_ENABLED:
        return False  # Silent skip

    try:
        response = await client.post(dapr_url, json=event_data)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Event publish failed: {e}")
        return False  # Don't fail the request
```

### Event Consumption Failures

**Behavior**: Retry with backoff
- Consumer service crashes: Kubernetes restarts pod automatically
- Message processing error: Log error, continue to next message (at-least-once delivery)
- Database error: Retry 3 times with backoff, then skip message

**Kafka Consumer Config**:
```yaml
maxRetries: 3
backOffDuration: 5s
initialOffset: latest  # Don't replay old messages on startup
```

---

## Data Consistency

### Consistency Model

**Approach**: Eventual consistency
- Backend commits to PostgreSQL first (tasks table)
- Then publishes events to Kafka (best-effort)
- Audit service eventually receives event and writes to audit_logs table

**Guarantees**:
- At-least-once delivery (messages may be duplicated)
- No guaranteed ordering across partitions
- Idempotent consumers (audit service deduplicates by task_id + timestamp)

### Failure Scenarios

| Scenario | Impact | Mitigation |
|----------|--------|------------|
| Backend commits to DB but Kafka publish fails | Audit log missing entry | Manual backfill from DB snapshots |
| Audit service down | Events queued in Kafka | Consume on restart (consumer group offset) |
| Redpanda cluster down | Events lost | Backend continues to function (degraded mode) |
| Consumer processes duplicate | Duplicate audit logs | Audit service checks for existing entry |

---

## Performance Considerations

### Throughput Targets

- Backend event publishing: <50ms overhead per API call
- Event consumption latency: <1s from publish to consumer processing
- Audit query response time: <200ms for typical queries

### Optimization Strategies

1. **Batch Publishing** (future): Batch multiple events in single Dapr call
2. **Async Publishing**: Never block HTTP response on event publishing
3. **Connection Pooling**: Reuse HTTP connections to Dapr
4. **Partition Key**: Use `user_id` as partition key for ordering

---

## Version Evolution

### Schema Versioning Strategy

**Approach**: Forward-compatible changes only
- New fields: Optional with defaults
- Removed fields: Mark as deprecated, keep for 2 versions
- Breaking changes: Increment `metadata.version` field

**Example Migration**:
```json
// Version 1.0
{
  "event_type": "created",
  "task_id": 123,
  "metadata": { "version": "1.0" }
}

// Version 1.1 (add optional field)
{
  "event_type": "created",
  "task_id": 123,
  "assignee_id": "user456",  // NEW optional field
  "metadata": { "version": "1.1" }
}
```

**Consumer Compatibility**:
- Consumers ignore unknown fields
- Consumers provide defaults for missing optional fields

---

## Summary

This data model defines:
- **4 Kafka topics** with retention and partitioning strategies
- **4 event types** with JSON schemas for task operations
- **2 database entities** (Task, AuditLog) with validation rules
- **3 event flows** (creation, reminders, recurring tasks)
- **Error handling** and consistency guarantees

**Next Steps**: Create API contracts (JSON schemas) and quickstart guide.
