# Kafka Event-Driven Architecture Specification

## Overview
Implement event-driven architecture using Kafka (Redpanda Cloud) for asynchronous communication between microservices.

## Kafka Service: Redpanda Cloud

### Why Redpanda?
- **Kafka-compatible**: Same APIs, existing clients work
- **No Zookeeper**: Simpler architecture
- **Free Serverless tier**: Perfect for hackathon
- **Fast setup**: Under 5 minutes
- **Cloud-native**: Built for Kubernetes

### Setup Steps

1. **Sign up**: https://redpanda.com/cloud
2. **Create Serverless Cluster**: Free tier
3. **Create Topics**:
   - `task-events`
   - `reminders`
   - `task-updates`
   - `recurring-tasks`
4. **Get Credentials**: Bootstrap server URL, SASL credentials
5. **Configure in Dapr**: Add credentials to component config

## Kafka Topics

### 1. task-events

**Purpose**: Log all task CRUD operations for audit trail and real-time sync

**Producers**:
- Backend API (via Dapr Pub/Sub)

**Consumers**:
- Audit Service
- Real-time Sync Service

**Event Schema**:
```json
{
  "event_type": "created" | "updated" | "completed" | "deleted",
  "task_id": 123,
  "user_id": "user123",
  "task_data": {
    "title": "Task title",
    "description": "Task description",
    "priority": "high",
    "tags": ["work", "urgent"],
    "due_date": "2025-12-31T17:00:00Z",
    "completed": false,
    "is_recurring": false
  },
  "timestamp": "2025-12-22T10:00:00Z",
  "metadata": {
    "source": "chat-api",
    "version": "1.0"
  }
}
```

### 2. reminders

**Purpose**: Trigger notifications for upcoming due tasks

**Producers**:
- Backend API (via Dapr Cron Binding)

**Consumers**:
- Notification Service

**Event Schema**:
```json
{
  "event_type": "reminder_due",
  "task_id": 123,
  "user_id": "user123",
  "title": "Submit report",
  "description": "Q4 financial report",
  "due_date": "2025-12-31T17:00:00Z",
  "remind_before_minutes": 1440,
  "priority": "high",
  "tags": ["work"],
  "timestamp": "2025-12-30T17:00:00Z"
}
```

### 3. task-updates

**Purpose**: Real-time sync across multiple clients

**Producers**:
- Backend API (on any task change)

**Consumers**:
- WebSocket Service
- Frontend clients (via WebSocket)

**Event Schema**:
```json
{
  "event_type": "task_updated",
  "task_id": 123,
  "user_id": "user123",
  "changes": {
    "title": "New title",
    "completed": true
  },
  "timestamp": "2025-12-22T10:00:00Z"
}
```

### 4. recurring-tasks

**Purpose**: Process recurring task completion and create next instance

**Producers**:
- Backend API (when recurring task completed)

**Consumers**:
- Recurring Task Service

**Event Schema**:
```json
{
  "event_type": "recurring_task_completed",
  "task_id": 123,
  "parent_task_id": 100,
  "user_id": "user123",
  "recurrence_pattern": "weekly",
  "recurrence_interval": 1,
  "recurrence_days": ["monday"],
  "next_occurrence": "2025-12-29T09:00:00Z",
  "recurrence_end_date": "2026-12-31T00:00:00Z",
  "timestamp": "2025-12-22T10:00:00Z"
}
```

## Microservices Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Frontend Pod │  │ Backend Pod  │  │ Notif Pod    │         │
│  │  (Next.js)   │  │ (FastAPI+MCP)│  │ (Notif Svc)  │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│                   ┌────────▼────────┐                           │
│                   │  Redpanda Cloud │                           │
│                   │   (Kafka)       │                           │
│                   │                 │                           │
│                   │ - task-events   │                           │
│                   │ - reminders     │                           │
│                   │ - task-updates  │                           │
│                   │ - recurring-    │                           │
│                   │   tasks         │                           │
│                   └────────┬────────┘                           │
│                            │                                    │
│         ┌──────────────────┼──────────────────┐                │
│         │                  │                  │                │
│  ┌──────▼───────┐  ┌───────▼──────┐  ┌───────▼──────┐         │
│  │ Recurring    │  │ Audit        │  │ WebSocket    │         │
│  │ Task Service │  │ Service      │  │ Service      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Service Implementations

### 1. Chat API Service (FastAPI + MCP)

**Responsibilities**:
- Handle chat requests
- Invoke MCP tools for task operations
- Publish events to Kafka via Dapr

**Kafka Integration**:
```python
import httpx

async def publish_task_event(event_data: dict):
    """Publish event via Dapr Pub/Sub"""
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
            json=event_data
        )

# Example usage in MCP tool
@mcp_tool
async def add_task(user_id: str, title: str, **kwargs):
    # Create task in database
    task = Task(user_id=user_id, title=title, **kwargs)
    session.add(task)
    session.commit()

    # Publish event
    await publish_task_event({
        "event_type": "created",
        "task_id": task.id,
        "user_id": user_id,
        "task_data": task.dict(),
        "timestamp": datetime.utcnow().isoformat()
    })

    return {"task_id": task.id, "status": "created"}
```

### 2. Notification Service

**Responsibilities**:
- Consume reminder events from Kafka
- Send email/push notifications to users
- Track notification delivery status

**Implementation**:
```python
from dapr.ext.grpc import App
import json

app = App()

@app.subscribe(pubsub_name="kafka-pubsub", topic="reminders")
def handle_reminder(event: dict):
    """Handle reminder event"""
    data = json.loads(event.data)

    user_id = data["user_id"]
    task_title = data["title"]
    due_date = data["due_date"]

    # Send notification (email, push, SMS, etc.)
    send_notification(
        user_id=user_id,
        message=f"Reminder: '{task_title}' is due on {due_date}",
        notification_type="reminder"
    )

    print(f"Sent reminder to {user_id} for task: {task_title}")

app.run(50051)  # Dapr gRPC app port
```

### 3. Recurring Task Service

**Responsibilities**:
- Consume recurring task completion events
- Calculate next occurrence
- Create new task instance

**Implementation**:
```python
from dapr.ext.grpc import App
from datetime import datetime, timedelta
import json

app = App()

@app.subscribe(pubsub_name="kafka-pubsub", topic="recurring-tasks")
def handle_recurring_task(event: dict):
    """Handle recurring task completion"""
    data = json.loads(event.data)

    parent_task_id = data["parent_task_id"]
    user_id = data["user_id"]
    pattern = data["recurrence_pattern"]
    interval = data["recurrence_interval"]
    end_date = datetime.fromisoformat(data["recurrence_end_date"])

    # Calculate next occurrence
    next_date = calculate_next_occurrence(
        pattern=pattern,
        interval=interval,
        recurrence_days=data.get("recurrence_days"),
        current_date=datetime.utcnow()
    )

    # Check if within recurrence range
    if next_date > end_date:
        print(f"Recurrence ended for task {parent_task_id}")
        return

    # Create new task instance
    parent_task = session.query(Task).get(parent_task_id)

    new_task = Task(
        user_id=user_id,
        title=parent_task.title,
        description=parent_task.description,
        priority=parent_task.priority,
        tags=parent_task.tags,
        due_date=next_date,
        is_recurring=True,
        recurrence_pattern=pattern,
        recurrence_interval=interval,
        recurrence_days=data.get("recurrence_days"),
        recurrence_end_date=end_date,
        parent_task_id=parent_task_id
    )

    session.add(new_task)
    session.commit()

    print(f"Created recurring task instance: {new_task.id}")

app.run(50052)
```

### 4. Audit Service

**Responsibilities**:
- Consume all task events
- Store in audit log table
- Provide audit trail API

**Database Model**:
```python
class AuditLog(SQLModel, table=True):
    id: int = Field(primary_key=True)
    event_type: str
    task_id: int
    user_id: str
    task_data: str  # JSON
    timestamp: datetime
    metadata: str  # JSON
```

**Implementation**:
```python
from dapr.ext.grpc import App
import json

app = App()

@app.subscribe(pubsub_name="kafka-pubsub", topic="task-events")
def handle_task_event(event: dict):
    """Log all task events for audit trail"""
    data = json.loads(event.data)

    audit_entry = AuditLog(
        event_type=data["event_type"],
        task_id=data["task_id"],
        user_id=data["user_id"],
        task_data=json.dumps(data["task_data"]),
        timestamp=datetime.fromisoformat(data["timestamp"]),
        metadata=json.dumps(data.get("metadata", {}))
    )

    session.add(audit_entry)
    session.commit()

    print(f"Logged audit entry: {audit_entry.id}")

app.run(50053)
```

## Dapr Pub/Sub Component

**File**: `k8s/dapr-components/pubsub-kafka.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "your-cluster.cloud.redpanda.com:9092"
    - name: authType
      value: "password"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password
    - name: consumerGroup
      value: "todo-service-group"
```

## Event Flow Examples

### Example 1: Task Creation Flow

```
User → ChatKit UI
         │
         ▼
Backend API (add_task MCP tool)
         │
         ├──► Save to Neon DB
         │
         └──► Publish to Kafka (task-events)
                     │
                     ├──► Audit Service → Log to audit table
                     │
                     └──► WebSocket Service → Broadcast to clients
```

### Example 2: Recurring Task Flow

```
User completes recurring task
         │
         ▼
Backend API (complete_task)
         │
         ├──► Mark task as complete in DB
         │
         └──► Publish to Kafka (recurring-tasks)
                     │
                     ▼
         Recurring Task Service
                     │
                     ├──► Calculate next occurrence
                     │
                     └──► Create new task instance in DB
```

### Example 3: Reminder Flow

```
Dapr Cron Binding (every 5 minutes)
         │
         ▼
Backend API (/reminder-cron endpoint)
         │
         ├──► Query DB for upcoming due tasks
         │
         └──► For each task → Publish to Kafka (reminders)
                     │
                     ▼
         Notification Service
                     │
                     └──► Send email/push notification to user
```

## Deployment

### Kubernetes Resources

**Deployments**:
1. `frontend-deployment.yaml`
2. `backend-deployment.yaml`
3. `notification-service-deployment.yaml`
4. `recurring-task-service-deployment.yaml`
5. `audit-service-deployment.yaml`

Each deployment includes Dapr sidecar annotations:
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "backend-service"
  dapr.io/app-port: "8000"
  dapr.io/config: "tracing"
```

### Secrets

Create Kubernetes secret for Kafka credentials:
```bash
kubectl create secret generic kafka-secrets \
  --from-literal=username='your-username' \
  --from-literal=password='your-password'
```

## Monitoring & Observability

### Kafka Metrics
- **Message throughput**: Messages/second per topic
- **Consumer lag**: How far behind consumers are
- **Error rate**: Failed message processing

### Service Metrics
- **Event processing time**: Time to process each event
- **Success/failure rate**: Percentage of successful processing
- **Queue depth**: Number of pending messages

### Logging
- Log all published events
- Log all consumed events
- Log processing errors with stack traces

## Testing

### Unit Tests
- Test event serialization/deserialization
- Test event schema validation
- Test business logic in consumers

### Integration Tests
- Test end-to-end event flow
- Test Dapr Pub/Sub integration
- Test multiple consumers receiving same event

### Load Tests
- Test high volume event publishing
- Test consumer processing under load
- Test Kafka cluster performance

## Success Criteria

- ✅ All Kafka topics created in Redpanda Cloud
- ✅ Dapr Pub/Sub component configured and working
- ✅ Backend publishes events to Kafka
- ✅ All microservices consume events correctly
- ✅ Recurring tasks auto-create next instance
- ✅ Reminders sent before due date
- ✅ Audit trail maintained for all operations
- ✅ No message loss or duplication
- ✅ System handles failures gracefully
