# Advanced Features Specification

## Overview
Implement Advanced and Intermediate level features for comprehensive task management capabilities.

## Advanced Level Features

### 1. Recurring Tasks

#### User Stories
- As a user, I can create a task that repeats daily, weekly, or monthly
- As a user, I can see when my recurring task will occur next
- As a user, when I complete a recurring task, a new instance is automatically created

#### Data Model
```python
class Task(SQLModel, table=True):
    # ... existing fields ...
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None  # "daily", "weekly", "monthly"
    recurrence_interval: Optional[int] = 1  # Every N days/weeks/months
    recurrence_days: Optional[str] = None  # JSON array for weekly: ["monday", "friday"]
    recurrence_end_date: Optional[datetime] = None
    parent_task_id: Optional[int] = None  # Link to original recurring task
```

#### Recurrence Patterns
1. **Daily**: Repeats every N days
   - Example: Every 1 day, Every 2 days
2. **Weekly**: Repeats on specific days of week
   - Example: Every Monday and Friday
3. **Monthly**: Repeats on specific day of month
   - Example: 1st of every month, 15th of every month

#### API Endpoints

**Create Recurring Task**
```
POST /api/{user_id}/tasks
{
  "title": "Weekly team meeting",
  "description": "Discuss project progress",
  "is_recurring": true,
  "recurrence_pattern": "weekly",
  "recurrence_interval": 1,
  "recurrence_days": ["monday"],
  "recurrence_end_date": "2026-12-31T00:00:00Z"
}
```

**Complete Recurring Task**
```
PATCH /api/{user_id}/tasks/{task_id}/complete
```
- Marks current instance as complete
- Publishes event to Kafka topic `recurring-tasks`
- Recurring Task Service creates next instance

#### Kafka Integration
**Topic**: `recurring-tasks`

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
  "timestamp": "2025-12-22T10:00:00Z"
}
```

### 2. Due Dates & Time Reminders

#### User Stories
- As a user, I can set a due date and time for a task
- As a user, I receive a reminder notification before my task is due
- As a user, I can customize when I receive reminders (e.g., 1 hour before, 1 day before)

#### Data Model
```python
class Task(SQLModel, table=True):
    # ... existing fields ...
    due_date: Optional[datetime] = None
    remind_before_minutes: Optional[int] = 60  # Default: 1 hour before
    reminder_sent: bool = False
```

#### API Endpoints

**Create Task with Due Date**
```
POST /api/{user_id}/tasks
{
  "title": "Submit report",
  "description": "Q4 financial report",
  "due_date": "2025-12-31T17:00:00Z",
  "remind_before_minutes": 1440  // 24 hours before
}
```

#### Reminder System

**Architecture**:
```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Dapr Cron   │──────│  Backend     │──────│    Kafka     │
│  Binding     │      │  /reminder   │      │  "reminders" │
│  (Every 5min)│      │  Endpoint    │      │    Topic     │
└──────────────┘      └──────────────┘      └──────────────┘
                                                    │
                                                    ▼
                                            ┌──────────────┐
                                            │ Notification │
                                            │   Service    │
                                            └──────────────┘
```

**Dapr Cron Binding**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "*/5 * * * *"  # Every 5 minutes
```

**Reminder Check Logic**:
```python
@app.post("/reminder-cron")
async def check_reminders():
    now = datetime.utcnow()
    upcoming_threshold = now + timedelta(minutes=5)

    # Find tasks due soon that need reminders
    tasks = session.query(Task).filter(
        Task.due_date.isnot(None),
        Task.reminder_sent == False,
        Task.due_date - Task.remind_before_minutes * 60 <= upcoming_threshold
    ).all()

    for task in tasks:
        # Publish reminder event to Kafka
        await publish_reminder_event(task)
        task.reminder_sent = True

    session.commit()
```

**Kafka Event**:
```json
{
  "event_type": "reminder_due",
  "task_id": 123,
  "user_id": "user123",
  "title": "Submit report",
  "due_date": "2025-12-31T17:00:00Z",
  "remind_before_minutes": 1440,
  "timestamp": "2025-12-30T17:00:00Z"
}
```

## Intermediate Level Features

### 3. Priorities & Tags/Categories

#### User Stories
- As a user, I can assign a priority (High, Medium, Low) to a task
- As a user, I can add multiple tags to organize tasks
- As a user, I can filter tasks by priority or tags

#### Data Model
```python
from enum import Enum

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Task(SQLModel, table=True):
    # ... existing fields ...
    priority: Priority = Priority.MEDIUM
    tags: Optional[str] = None  # JSON array: ["work", "urgent", "client-x"]
```

#### API Endpoints

**Create Task with Priority and Tags**
```
POST /api/{user_id}/tasks
{
  "title": "Fix production bug",
  "description": "Critical API error",
  "priority": "high",
  "tags": ["work", "urgent", "bug-fix"]
}
```

**Filter by Priority**
```
GET /api/{user_id}/tasks?priority=high
```

**Filter by Tags**
```
GET /api/{user_id}/tasks?tags=work,urgent
```

### 4. Search & Filter

#### User Stories
- As a user, I can search tasks by keywords in title or description
- As a user, I can filter tasks by status, priority, tags, and due date
- As a user, I can combine multiple filters

#### API Endpoints

**Search**
```
GET /api/{user_id}/tasks?search=report
```

**Combined Filters**
```
GET /api/{user_id}/tasks?status=pending&priority=high&tags=work&due_date_before=2025-12-31
```

#### Backend Implementation
```python
@app.get("/api/{user_id}/tasks")
async def list_tasks(
    user_id: str,
    status: Optional[str] = None,
    priority: Optional[Priority] = None,
    tags: Optional[str] = None,
    search: Optional[str] = None,
    due_date_before: Optional[datetime] = None,
    due_date_after: Optional[datetime] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    query = session.query(Task).filter(Task.user_id == user_id)

    if status:
        query = query.filter(Task.completed == (status == "completed"))

    if priority:
        query = query.filter(Task.priority == priority)

    if tags:
        tag_list = tags.split(",")
        for tag in tag_list:
            query = query.filter(Task.tags.contains(tag))

    if search:
        query = query.filter(
            or_(
                Task.title.ilike(f"%{search}%"),
                Task.description.ilike(f"%{search}%")
            )
        )

    if due_date_before:
        query = query.filter(Task.due_date <= due_date_before)

    if due_date_after:
        query = query.filter(Task.due_date >= due_date_after)

    # Sorting
    order_column = getattr(Task, sort_by)
    if sort_order == "desc":
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())

    return query.all()
```

### 5. Sort Tasks

#### User Stories
- As a user, I can sort tasks by due date, priority, created date, or title
- As a user, I can sort in ascending or descending order

#### API Endpoints

**Sort by Due Date**
```
GET /api/{user_id}/tasks?sort_by=due_date&sort_order=asc
```

**Sort by Priority**
```
GET /api/{user_id}/tasks?sort_by=priority&sort_order=desc
```

#### Supported Sort Fields
- `created_at` (default)
- `updated_at`
- `due_date`
- `priority`
- `title`

## Frontend Implementation

### Task Form Enhancements

```typescript
interface TaskFormData {
  title: string;
  description?: string;
  priority: 'high' | 'medium' | 'low';
  tags: string[];
  due_date?: Date;
  remind_before_minutes?: number;
  is_recurring: boolean;
  recurrence_pattern?: 'daily' | 'weekly' | 'monthly';
  recurrence_interval?: number;
  recurrence_days?: string[];
  recurrence_end_date?: Date;
}
```

### UI Components

1. **Priority Selector**: Dropdown with color-coded options
   - High: Red badge
   - Medium: Yellow badge
   - Low: Green badge

2. **Tag Input**: Multi-select tag input with autocomplete

3. **Due Date Picker**: DateTime picker with timezone support

4. **Reminder Settings**: Dropdown for reminder time
   - 15 minutes before
   - 1 hour before
   - 1 day before
   - 1 week before
   - Custom

5. **Recurrence Settings**: Modal/accordion for recurring task configuration
   - Pattern selector
   - Interval input
   - Day of week checkboxes (for weekly)
   - End date picker

### Filter & Search UI

```typescript
interface FilterState {
  status: 'all' | 'pending' | 'completed';
  priority?: 'high' | 'medium' | 'low';
  tags: string[];
  search: string;
  due_date_range?: {
    start?: Date;
    end?: Date;
  };
  sort_by: 'created_at' | 'due_date' | 'priority' | 'title';
  sort_order: 'asc' | 'desc';
}
```

## MCP Tools Updates

### Updated Tools

**add_task** - Add support for new fields:
```python
@mcp_tool
async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None,
    remind_before_minutes: int = 60,
    is_recurring: bool = False,
    recurrence_pattern: Optional[str] = None,
    recurrence_interval: int = 1,
    recurrence_days: Optional[List[str]] = None,
    recurrence_end_date: Optional[str] = None
) -> dict:
    # Implementation
    pass
```

**list_tasks** - Add filtering and sorting:
```python
@mcp_tool
async def list_tasks(
    user_id: str,
    status: str = "all",
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> List[dict]:
    # Implementation
    pass
```

## Testing Requirements

### Unit Tests
- Test recurring task creation logic
- Test reminder calculation
- Test tag and priority filtering
- Test search functionality
- Test sorting logic

### Integration Tests
- Test recurring task workflow (complete → create next)
- Test reminder notification flow
- Test Kafka event publishing/consuming
- Test Dapr cron binding

### E2E Tests
- Create recurring task via chatbot
- Complete recurring task and verify new instance
- Set due date and verify reminder
- Search and filter tasks
- Sort tasks by various fields

## Success Criteria

- ✅ Users can create daily, weekly, and monthly recurring tasks
- ✅ Completing a recurring task creates the next instance
- ✅ Users can set due dates with specific times
- ✅ Users receive reminders before tasks are due
- ✅ Users can assign priorities and tags
- ✅ Users can search tasks by keywords
- ✅ Users can filter by status, priority, tags, and due date
- ✅ Users can sort by any supported field
- ✅ All features work via AI chatbot natural language
- ✅ Events properly flow through Kafka
- ✅ Dapr cron triggers reminder checks
