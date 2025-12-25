# Feature Specification: Intermediate & Advanced Features for Phase V

**Feature Branch**: `005-cloud-native-deployment`
**Created**: 2025-12-23
**Status**: Draft
**Input**: User request for advanced search/filtering, task templates/bulk operations, real-time collaboration, and analytics/reporting features

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Advanced Search and Filtering (Priority: P1)

A user with hundreds of tasks needs powerful search capabilities to quickly find specific tasks based on multiple criteria. They want to search by keywords, filter by tags, priority levels, date ranges, completion status, and save frequently used search queries for future use.

**Why this priority**: Search is fundamental for productivity with large task lists. Without it, users struggle to find tasks, leading to poor user experience. This is table stakes for any modern task management application.

**Independent Test**: Can be tested by creating 50+ diverse tasks with various tags, priorities, and dates, then executing complex searches (e.g., "high priority incomplete tasks tagged 'urgent' created in last 7 days") and verifying accurate, fast results.

**Acceptance Scenarios**:

1. **Given** a user has 100+ tasks in their list, **When** they search for "meeting" in the search box, **Then** system returns all tasks with "meeting" in title or description within 500ms
2. **Given** search results are displayed, **When** user applies filters (priority=high AND tags contains "work" AND due_date > today), **Then** system shows only tasks matching all criteria
3. **Given** user frequently searches for "incomplete high priority tasks", **When** they save this search as "Hot List", **Then** system stores the search and makes it available in saved searches dropdown
4. **Given** user has saved searches, **When** they click "Hot List" saved search, **Then** system executes the saved query and displays current results
5. **Given** search results are displayed, **When** user modifies a task that no longer matches criteria, **Then** real-time updates remove it from results immediately
6. **Given** user applies date range filter, **When** they select "Last 7 days", **Then** system shows only tasks created/modified in that timeframe
7. **Given** user searches for tasks, **When** they use advanced operators (AND, OR, NOT), **Then** system correctly parses and executes boolean search logic

---

### User Story 2 - Task Templates and Bulk Operations (Priority: P1)

A project manager regularly creates similar sets of tasks (e.g., weekly sprint planning, client onboarding) and needs to apply changes to multiple tasks simultaneously. They want reusable templates and bulk operations to save time and ensure consistency.

**Why this priority**: Templates and bulk operations dramatically improve efficiency for power users managing multiple projects or recurring workflows. This separates professional tools from basic to-do apps.

**Independent Test**: Can be tested by creating a template with 5 tasks, instantiating it 3 times with different parameters, then bulk-updating all tasks tagged "sprint-1" to change priority from medium to high, and verifying all changes applied correctly.

**Acceptance Scenarios**:

1. **Given** user has common task patterns, **When** they create a "Weekly Sprint Template" with 5 tasks (planning, development, review, testing, deployment), **Then** system saves template with all task properties (titles, priorities, tags, relative due dates)
2. **Given** a template exists, **When** user instantiates "Weekly Sprint Template" with start_date=2025-12-23, **Then** system creates 5 new tasks with due dates calculated from start_date (e.g., planning=Day 1, development=Day 2-4, etc.)
3. **Given** user selects 10 tasks via checkboxes, **When** they choose "Bulk Update → Priority → High", **Then** all 10 tasks update to priority=high with single API call
4. **Given** user has 20 incomplete tasks tagged "cleanup", **When** they execute "Bulk Delete" on filtered results, **Then** system prompts for confirmation and deletes all 20 tasks in single transaction
5. **Given** a template has placeholders (e.g., {{PROJECT_NAME}}), **When** user instantiates template and provides PROJECT_NAME="Apollo", **Then** all task titles/descriptions replace {{PROJECT_NAME}} with "Apollo"
6. **Given** user wants to modify a template, **When** they edit "Weekly Sprint Template" to add new task "Documentation", **Then** future instantiations include the new task, but existing task sets remain unchanged
7. **Given** user applies bulk operation, **When** operation affects 100+ tasks, **Then** system shows progress indicator and completes within 5 seconds

---

### User Story 3 - Real-Time Collaboration Features (Priority: P2)

Multiple team members work on shared tasks and need to see updates in real-time without manual refresh. They want to know who's currently viewing/editing tasks, see live changes, and get instant notifications when collaborators make updates.

**Why this priority**: Real-time collaboration is expected in modern web applications. It prevents conflicts, improves awareness, and creates a more engaging user experience. Builds on P1 features to create team-oriented workflows.

**Independent Test**: Can be tested by opening two browser windows (User A and User B), having User A update a task, and verifying User B sees the change within 2 seconds without refresh. Presence indicators show both users are online.

**Acceptance Scenarios**:

1. **Given** two users (Alice, Bob) viewing same task list, **When** Alice creates a new task, **Then** Bob sees the new task appear in his list within 2 seconds without page refresh
2. **Given** Alice is editing task "Design Homepage", **When** Bob opens the same task, **Then** Bob sees presence indicator "Alice is editing" and receives suggestion to avoid conflicting changes
3. **Given** Bob updates task priority while Alice has it open, **When** change is saved, **Then** Alice's UI updates immediately with visual indication (e.g., highlight animation) showing the field changed
4. **Given** user has notifications enabled, **When** collaborator completes a task assigned to them, **Then** user receives real-time browser notification and in-app badge update
5. **Given** 5 users are online, **When** viewing shared project, **Then** system shows presence indicators with user avatars/names of who's currently active
6. **Given** Alice deletes a task that Bob is viewing, **When** deletion occurs, **Then** Bob's view shows task as deleted with option to undo (if within grace period)
7. **Given** network connection is unstable, **When** WebSocket disconnects, **Then** system shows offline indicator and automatically reconnects, syncing missed updates
8. **Given** user enables collaborative cursor, **When** collaborators move between tasks, **Then** other users see colored cursors with names showing where team members are focused

---

### User Story 4 - Analytics and Reporting (Priority: P2)

A team lead wants data-driven insights into team productivity, task completion trends, bottlenecks, and workload distribution. They need visual dashboards, exportable reports, and time-tracking data to inform planning decisions and performance reviews.

**Why this priority**: Analytics transform raw task data into actionable insights for management and process improvement. Essential for teams using the tool professionally. Complements P1/P2 features by adding strategic value.

**Independent Test**: Can be tested by creating 50 tasks over a 30-day period with varied completion dates, then viewing dashboard to verify charts show completion trends, viewing "Tasks by Tag" breakdown, exporting CSV report with all metrics, and validating data accuracy.

**Acceptance Scenarios**:

1. **Given** user has completed tasks over 30 days, **When** they open Analytics dashboard, **Then** system displays line chart showing tasks completed per day with trend line
2. **Given** dashboard is loaded, **When** user views "Tasks by Priority" pie chart, **Then** chart accurately shows distribution (e.g., 45% high, 30% medium, 25% low) with color coding
3. **Given** user wants workload insights, **When** they view "Tasks by Tag" bar chart, **Then** system shows task count per tag, sorted by frequency, with drill-down capability
4. **Given** user tracks time on tasks, **When** they start/stop timers on 10 tasks, **Then** system records elapsed time and displays total time spent per task and per tag
5. **Given** analytics data is generated, **When** user clicks "Export to CSV", **Then** system generates downloadable CSV with task ID, title, status, priority, tags, created_at, completed_at, time_spent columns
6. **Given** user wants PDF report, **When** they select date range and click "Generate Report", **Then** system creates PDF with charts, tables, and summary statistics (total tasks, completion rate, average time)
7. **Given** dashboard shows metrics, **When** user hovers over data points, **Then** tooltips display detailed breakdowns (e.g., "Dec 15: 12 tasks completed - 8 high priority, 4 medium")
8. **Given** user filters analytics by date range, **When** they select "Last Quarter", **Then** all charts and metrics recalculate to show only data from that period
9. **Given** team lead views team analytics, **When** accessing multi-user report, **Then** system shows aggregated metrics across all team members with per-user breakdowns
10. **Given** user sets productivity goals, **When** viewing dashboard, **Then** system displays progress toward goals (e.g., "75% toward 100 tasks/month target") with visual indicators

---

### Edge Cases

**Search & Filtering:**
- What happens when search query contains special characters or SQL injection attempts? (Sanitization and parameterized queries)
- How does system handle searches with 0 results? (Clear "No results found" message with suggestions)
- What happens when saved search has >1000 results? (Pagination with "Showing 1-50 of 1234" message)
- How does full-text search perform with 10,000+ tasks? (Indexed search with <500ms response time)

**Templates & Bulk Operations:**
- What happens when bulk operation fails midway (network error on task 47 of 100)? (Transaction rollback or partial success report with retry option)
- How does system handle template instantiation with invalid date parameters? (Validation error with clear message)
- What happens when user tries to bulk delete 1000+ tasks? (Confirmation with count, background job with progress notification)
- How are template placeholders handled when user doesn't provide values? (Validation error listing missing placeholders)

**Real-Time Collaboration:**
- What happens when two users edit same field simultaneously? (Last-write-wins with conflict notification and merge option)
- How does system handle 100+ concurrent WebSocket connections? (Load testing ensures <100ms latency per event)
- What happens when user's network disconnects mid-update? (Optimistic UI updates + conflict resolution on reconnect)
- How are presence indicators cleared when user closes browser without explicit logout? (Heartbeat timeout after 30 seconds)

**Analytics & Reporting:**
- What happens when generating report for 50,000+ tasks? (Background job with email notification when ready, or streaming download)
- How does system handle time-tracking for tasks spanning midnight? (Correctly attributes time to date ranges)
- What happens when exporting PDF with charts but charts fail to render? (Graceful fallback with table data only)
- How are analytics calculated for deleted tasks? (Excluded by default, option to "Include Deleted" for historical accuracy)

---

## Requirements *(mandatory)*

### Functional Requirements

**Advanced Search & Filtering:**

- **FR-001**: System MUST support full-text search across task title and description fields with <500ms response time for 10,000 tasks
- **FR-002**: System MUST allow filtering by multiple criteria simultaneously (status, priority, tags, date ranges, assigned user)
- **FR-003**: System MUST support boolean operators (AND, OR, NOT) in search queries
- **FR-004**: System MUST allow users to save search queries with custom names and retrieve them from a saved searches list
- **FR-005**: System MUST support date range filters (last 7 days, last 30 days, custom range) for created_at, updated_at, and due_date fields
- **FR-006**: System MUST paginate search results (50 tasks per page) with total count display
- **FR-007**: System MUST highlight search terms in results (title and description)
- **FR-008**: Search API endpoint MUST return results with relevance scoring (exact match > partial match > description match)

**Task Templates & Bulk Operations:**

- **FR-009**: System MUST allow users to create task templates with template name, description, and array of task definitions
- **FR-010**: Each template task definition MUST support all task fields (title, description, priority, tags, relative due date offset)
- **FR-011**: System MUST support template placeholders using {{VARIABLE_NAME}} syntax in any text field
- **FR-012**: System MUST instantiate templates by replacing placeholders with user-provided values and calculating absolute dates from start_date
- **FR-013**: System MUST provide bulk update endpoint accepting task IDs array and partial task object with fields to update
- **FR-014**: System MUST provide bulk delete endpoint accepting task IDs array with transaction support (all-or-nothing)
- **FR-015**: Bulk operations MUST return detailed results (success count, failure count, array of errors with task IDs)
- **FR-016**: System MUST validate bulk operation size limits (max 500 tasks per operation) to prevent server overload
- **FR-017**: Template instantiation MUST create all tasks in a single database transaction

**Real-Time Collaboration:**

- **FR-018**: System MUST establish WebSocket connections for real-time updates between server and all connected clients
- **FR-019**: System MUST broadcast task create/update/delete events to all users subscribed to the same task list within 2 seconds
- **FR-020**: System MUST track active users and display presence indicators (user avatar/name, last activity timestamp)
- **FR-021**: System MUST show editing status when user opens task for editing, visible to other users viewing same task
- **FR-022**: System MUST implement optimistic UI updates (immediate local change + rollback on server error)
- **FR-023**: System MUST handle WebSocket disconnections with automatic reconnection and state synchronization
- **FR-024**: System MUST send real-time notifications for events (task assigned, task completed, comment added)
- **FR-025**: WebSocket server MUST support concurrent connections (100+ users) with <100ms message broadcast latency
- **FR-026**: System MUST clear presence indicators after 30-second inactivity timeout
- **FR-027**: System MUST implement conflict resolution for simultaneous edits (last-write-wins with notification)

**Analytics & Reporting:**

- **FR-028**: System MUST provide analytics dashboard with task completion trends (line chart by day/week/month)
- **FR-029**: System MUST display task distribution charts (pie charts for priority, status; bar charts for tags)
- **FR-030**: System MUST support time-tracking with start/stop timer per task and total elapsed time calculation
- **FR-031**: System MUST calculate and display metrics: total tasks, completion rate, average completion time, tasks by tag/priority
- **FR-032**: System MUST allow exporting analytics data to CSV format with all task fields and calculated metrics
- **FR-033**: System MUST generate PDF reports with charts, summary statistics, and customizable date ranges
- **FR-034**: Analytics endpoints MUST support date range filtering (all time, last 7/30/90 days, quarter, year, custom)
- **FR-035**: Dashboard charts MUST be interactive with tooltips showing detailed data on hover
- **FR-036**: System MUST aggregate analytics across multiple users for team-level reporting (when user has admin role)
- **FR-037**: Analytics queries MUST complete within 2 seconds for datasets up to 10,000 tasks
- **FR-038**: Time tracking MUST persist timer state across page refreshes (store in database, not just local storage)

---

### Non-Functional Requirements

**Performance:**

- **NFR-001**: Search queries MUST return results within 500ms for 10,000 tasks (database indexing required)
- **NFR-002**: Bulk operations MUST process 100 tasks within 3 seconds
- **NFR-003**: WebSocket message broadcast MUST have <100ms latency for 100 concurrent users
- **NFR-004**: Analytics dashboard MUST load all charts within 2 seconds
- **NFR-005**: Real-time updates MUST propagate to all clients within 2 seconds of server event

**Scalability:**

- **NFR-006**: WebSocket server MUST handle 500+ concurrent connections without degradation
- **NFR-007**: Search index MUST scale to 100,000+ tasks without performance degradation
- **NFR-008**: Analytics queries MUST use database aggregation/indexes to avoid loading all tasks into memory

**Reliability:**

- **NFR-009**: Bulk operations MUST use database transactions to ensure atomicity (all succeed or all fail)
- **NFR-010**: WebSocket disconnections MUST trigger automatic reconnection with exponential backoff
- **NFR-011**: Template instantiation failures MUST rollback all created tasks (no partial templates)
- **NFR-012**: Time tracking MUST persist timer state every 30 seconds to prevent data loss

**Security:**

- **NFR-013**: Search queries MUST be sanitized to prevent SQL injection attacks
- **NFR-014**: Bulk operations MUST verify user owns all target tasks before executing changes
- **NFR-015**: WebSocket connections MUST authenticate via JWT token on initial handshake
- **NFR-016**: Saved searches MUST be user-scoped (users cannot access others' saved searches)
- **NFR-017**: Analytics data MUST be filtered by user_id to prevent data leakage

**Usability:**

- **NFR-018**: Search UI MUST provide autocomplete suggestions for tags and common queries
- **NFR-019**: Bulk operation failures MUST display clear error messages with affected task IDs
- **NFR-020**: Real-time updates MUST show visual indicators (animations, badges) to draw user attention
- **NFR-021**: Analytics charts MUST be responsive and render correctly on mobile devices

---

### Key Entities *(include if feature involves data)*

**SavedSearch** (new entity)
- `id`: UUID, primary key
- `user_id`: UUID, foreign key to User
- `name`: String, search name (e.g., "Hot List")
- `query_params`: JSONB, stores filter criteria {search_text, priority, tags, date_range, status}
- `created_at`: Timestamp
- `updated_at`: Timestamp

**TaskTemplate** (new entity)
- `id`: UUID, primary key
- `user_id`: UUID, foreign key to User
- `name`: String, template name (e.g., "Weekly Sprint")
- `description`: String, optional description
- `tasks_definition`: JSONB, array of task objects with placeholders
  ```json
  [
    {"title": "{{PROJECT_NAME}} - Planning", "priority": "high", "due_date_offset": 0},
    {"title": "{{PROJECT_NAME}} - Development", "priority": "medium", "due_date_offset": 3}
  ]
  ```
- `placeholders`: JSONB, array of required placeholder names ["PROJECT_NAME"]
- `created_at`: Timestamp
- `updated_at`: Timestamp

**TimeEntry** (new entity)
- `id`: UUID, primary key
- `task_id`: UUID, foreign key to Task
- `user_id`: UUID, foreign key to User
- `started_at`: Timestamp, when timer started
- `ended_at`: Timestamp, nullable, when timer stopped
- `elapsed_seconds`: Integer, calculated duration
- `description`: String, optional note about work done
- `created_at`: Timestamp

**PresenceSession** (new entity, may be in-memory/Redis instead of DB)
- `user_id`: UUID
- `session_id`: UUID, unique per browser tab
- `task_id`: UUID, nullable, currently viewing/editing this task
- `last_heartbeat`: Timestamp, updated every 10 seconds
- `status`: Enum (viewing, editing, idle)

**AnalyticsSnapshot** (optional, for pre-computed metrics)
- `id`: UUID
- `user_id`: UUID
- `date`: Date, metrics for this specific day
- `tasks_created`: Integer
- `tasks_completed`: Integer
- `tasks_deleted`: Integer
- `time_spent_seconds`: Integer, total time tracked this day
- `created_at`: Timestamp

---

### API Contracts *(include if feature involves backend/API)*

**Advanced Search & Filtering:**

```http
POST /api/{user_id}/tasks/search
Content-Type: application/json
Authorization: Bearer {jwt_token}

Request:
{
  "query": "meeting urgent",           // Full-text search
  "filters": {
    "status": ["pending", "in_progress"],  // Array for OR
    "priority": ["high"],
    "tags": ["work", "client"],        // Tasks with ANY of these tags
    "created_after": "2025-12-01",
    "created_before": "2025-12-23",
    "due_before": "2025-12-31"
  },
  "sort_by": "due_date",               // created_at, updated_at, priority, title
  "sort_order": "asc",                 // asc or desc
  "page": 1,
  "per_page": 50
}

Response (200 OK):
{
  "tasks": [...],                      // Array of Task objects
  "total_count": 47,
  "page": 1,
  "per_page": 50,
  "total_pages": 1
}
```

```http
GET /api/{user_id}/saved-searches
Authorization: Bearer {jwt_token}

Response (200 OK):
{
  "saved_searches": [
    {
      "id": "uuid",
      "name": "Hot List",
      "query_params": {...},
      "created_at": "2025-12-20T10:00:00Z"
    }
  ]
}
```

```http
POST /api/{user_id}/saved-searches
Content-Type: application/json
Authorization: Bearer {jwt_token}

Request:
{
  "name": "High Priority Work Tasks",
  "query_params": {
    "filters": {"priority": ["high"], "tags": ["work"]}
  }
}

Response (201 Created):
{
  "id": "uuid",
  "name": "High Priority Work Tasks",
  "query_params": {...},
  "created_at": "2025-12-23T12:00:00Z"
}
```

**Task Templates & Bulk Operations:**

```http
GET /api/{user_id}/templates
Authorization: Bearer {jwt_token}

Response (200 OK):
{
  "templates": [
    {
      "id": "uuid",
      "name": "Weekly Sprint",
      "description": "Standard sprint tasks",
      "tasks_definition": [...],
      "placeholders": ["PROJECT_NAME", "SPRINT_NUMBER"],
      "created_at": "2025-12-01T10:00:00Z"
    }
  ]
}
```

```http
POST /api/{user_id}/templates
Content-Type: application/json
Authorization: Bearer {jwt_token}

Request:
{
  "name": "Client Onboarding",
  "description": "Tasks for new client setup",
  "tasks_definition": [
    {
      "title": "{{CLIENT_NAME}} - Initial Meeting",
      "description": "Schedule kickoff call",
      "priority": "high",
      "tags": ["onboarding", "{{CLIENT_NAME}}"],
      "due_date_offset": 0
    },
    {
      "title": "{{CLIENT_NAME}} - Setup Account",
      "priority": "medium",
      "due_date_offset": 1
    }
  ],
  "placeholders": ["CLIENT_NAME"]
}

Response (201 Created):
{
  "id": "uuid",
  "name": "Client Onboarding",
  ...full template object
}
```

```http
POST /api/{user_id}/templates/{template_id}/instantiate
Content-Type: application/json
Authorization: Bearer {jwt_token}

Request:
{
  "start_date": "2025-12-24",
  "placeholder_values": {
    "CLIENT_NAME": "Acme Corp",
    "SPRINT_NUMBER": "12"
  }
}

Response (201 Created):
{
  "created_tasks": [
    {...},  // Array of created Task objects
    {...}
  ],
  "count": 2
}
```

```http
POST /api/{user_id}/tasks/bulk-update
Content-Type: application/json
Authorization: Bearer {jwt_token}

Request:
{
  "task_ids": ["uuid1", "uuid2", "uuid3"],
  "updates": {
    "priority": "high",
    "tags": ["urgent"]  // Replaces tags, not appends
  }
}

Response (200 OK):
{
  "success_count": 3,
  "failure_count": 0,
  "updated_tasks": [...]  // Array of updated Task objects
}
```

```http
POST /api/{user_id}/tasks/bulk-delete
Content-Type: application/json
Authorization: Bearer {jwt_token}

Request:
{
  "task_ids": ["uuid1", "uuid2", "uuid3"]
}

Response (200 OK):
{
  "deleted_count": 3,
  "failed_ids": []  // IDs that failed to delete with reasons
}
```

**Real-Time Collaboration (WebSocket):**

```
WebSocket Endpoint: ws://localhost:8000/api/{user_id}/ws
Authentication: ?token={jwt_token}

Client → Server (Heartbeat):
{
  "type": "heartbeat",
  "task_id": "uuid-or-null",  // Currently viewing this task
  "status": "viewing"          // viewing, editing, idle
}

Server → Client (Task Update):
{
  "type": "task_updated",
  "task": {...},               // Full Task object
  "updated_by": "user-uuid",
  "updated_at": "2025-12-23T12:34:56Z",
  "changes": ["priority", "tags"]  // Fields that changed
}

Server → Client (Presence Update):
{
  "type": "presence_update",
  "users": [
    {
      "user_id": "uuid",
      "username": "Alice",
      "task_id": "uuid-or-null",
      "status": "editing",
      "last_seen": "2025-12-23T12:34:56Z"
    }
  ]
}

Server → Client (Notification):
{
  "type": "notification",
  "title": "Task Completed",
  "message": "Bob completed 'Design Homepage'",
  "task_id": "uuid",
  "action": "task_completed"
}
```

**Analytics & Reporting:**

```http
GET /api/{user_id}/analytics/overview?start_date=2025-12-01&end_date=2025-12-23
Authorization: Bearer {jwt_token}

Response (200 OK):
{
  "date_range": {
    "start": "2025-12-01",
    "end": "2025-12-23"
  },
  "metrics": {
    "total_tasks": 150,
    "completed_tasks": 120,
    "completion_rate": 80.0,
    "average_completion_time_hours": 48.5,
    "total_time_spent_hours": 120.5
  },
  "tasks_by_priority": {
    "high": 45,
    "medium": 60,
    "low": 45
  },
  "tasks_by_status": {
    "completed": 120,
    "in_progress": 20,
    "pending": 10
  },
  "tasks_by_tag": [
    {"tag": "work", "count": 80},
    {"tag": "personal", "count": 40},
    {"tag": "urgent", "count": 30}
  ],
  "completion_trend": [
    {"date": "2025-12-01", "completed": 5},
    {"date": "2025-12-02", "completed": 8},
    ...
  ]
}
```

```http
POST /api/{user_id}/time-entries
Content-Type: application/json
Authorization: Bearer {jwt_token}

Request:
{
  "task_id": "uuid",
  "started_at": "2025-12-23T10:00:00Z",
  "ended_at": "2025-12-23T12:30:00Z",  // Nullable if timer still running
  "description": "Implemented search feature"
}

Response (201 Created):
{
  "id": "uuid",
  "task_id": "uuid",
  "user_id": "uuid",
  "started_at": "2025-12-23T10:00:00Z",
  "ended_at": "2025-12-23T12:30:00Z",
  "elapsed_seconds": 9000,
  "description": "Implemented search feature",
  "created_at": "2025-12-23T12:30:05Z"
}
```

```http
GET /api/{user_id}/analytics/export?format=csv&start_date=2025-12-01&end_date=2025-12-23
Authorization: Bearer {jwt_token}

Response (200 OK):
Content-Type: text/csv
Content-Disposition: attachment; filename="tasks_report_2025-12-23.csv"

id,title,status,priority,tags,created_at,completed_at,time_spent_hours
uuid1,"Design Homepage",completed,high,"work,design","2025-12-01T10:00:00Z","2025-12-03T15:30:00Z",12.5
...
```

```http
GET /api/{user_id}/analytics/export?format=pdf&start_date=2025-12-01&end_date=2025-12-23
Authorization: Bearer {jwt_token}

Response (200 OK):
Content-Type: application/pdf
Content-Disposition: attachment; filename="tasks_report_2025-12-23.pdf"

[Binary PDF data with charts and tables]
```

---

## Implementation Notes

### Technology Choices

**Search Implementation:**
- PostgreSQL full-text search using `ts_vector` and `ts_query` with GIN indexes
- Alternative: Elasticsearch for very large datasets (10M+ tasks)
- Saved searches stored as JSONB in PostgreSQL

**WebSocket Implementation:**
- FastAPI WebSocket support (built-in)
- Redis Pub/Sub for broadcasting between multiple backend instances (horizontal scaling)
- Alternative: Socket.IO for more robust reconnection handling

**Analytics:**
- PostgreSQL aggregation queries with proper indexes (created_at, user_id, status)
- Chart rendering: Chart.js or Recharts (frontend)
- PDF generation: ReportLab (Python backend) or Puppeteer (headless Chrome)
- CSV export: Python csv module

**Bulk Operations:**
- PostgreSQL transactions for atomicity
- Background jobs (Celery) for very large operations (1000+ tasks)
- Progress tracking via WebSocket or polling endpoint

### Database Schema Changes

```sql
-- SavedSearch table
CREATE TABLE saved_searches (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  query_params JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_saved_searches_user_id ON saved_searches(user_id);

-- TaskTemplate table
CREATE TABLE task_templates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  tasks_definition JSONB NOT NULL,
  placeholders JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_task_templates_user_id ON task_templates(user_id);

-- TimeEntry table
CREATE TABLE time_entries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  started_at TIMESTAMP NOT NULL,
  ended_at TIMESTAMP,
  elapsed_seconds INTEGER,
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_time_entries_task_id ON time_entries(task_id);
CREATE INDEX idx_time_entries_user_id ON time_entries(user_id);

-- Full-text search index on tasks
ALTER TABLE tasks ADD COLUMN search_vector tsvector;
CREATE INDEX idx_tasks_search ON tasks USING GIN(search_vector);

-- Trigger to update search_vector
CREATE OR REPLACE FUNCTION tasks_search_vector_update() RETURNS TRIGGER AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tasks_search_vector_trigger
BEFORE INSERT OR UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION tasks_search_vector_update();
```

### Frontend Components

**New Pages/Views:**
- `/search` - Advanced search interface with filters
- `/templates` - Template management (list, create, edit)
- `/analytics` - Dashboard with charts and metrics
- `/settings/saved-searches` - Manage saved searches

**New Components:**
- `SearchBar` with autocomplete
- `FilterPanel` with multi-select dropdowns
- `TemplateForm` for creating/editing templates
- `BulkActionsToolbar` for selected tasks
- `PresenceIndicator` showing active users
- `AnalyticsChart` (line, pie, bar charts)
- `TimeTracker` with start/stop button and elapsed time display
- `NotificationToast` for real-time updates

### Backend Structure

**New Routes:**
- `backend/src/routes/search.py` - Search and saved searches endpoints
- `backend/src/routes/templates.py` - Template CRUD and instantiation
- `backend/src/routes/analytics.py` - Analytics metrics and exports
- `backend/src/routes/websocket.py` - WebSocket connection management
- `backend/src/routes/bulk_operations.py` - Bulk update/delete

**New Services:**
- `backend/src/services/search_service.py` - Search logic and query building
- `backend/src/services/template_service.py` - Template instantiation and placeholder replacement
- `backend/src/services/analytics_service.py` - Metrics calculation and report generation
- `backend/src/services/websocket_service.py` - WebSocket broadcast and presence tracking
- `backend/src/services/export_service.py` - CSV/PDF generation

**New Models:**
- `backend/src/models/saved_search.py`
- `backend/src/models/task_template.py`
- `backend/src/models/time_entry.py`

---

## Success Criteria

### MVP Acceptance

All four user stories (P1 and P2) must be fully functional:

1. **Search & Filtering**: Can execute complex searches, save searches, and get results in <500ms
2. **Templates & Bulk Operations**: Can create templates, instantiate them, and bulk update/delete tasks
3. **Real-Time Collaboration**: WebSocket updates propagate within 2 seconds, presence indicators work
4. **Analytics**: Dashboard displays charts, can export CSV/PDF reports

### Quality Gates

- [ ] All API endpoints return within performance requirements (NFR-001 to NFR-005)
- [ ] Database transactions ensure data integrity (NFR-009, NFR-011)
- [ ] Security requirements validated (SQL injection tests, JWT authentication)
- [ ] WebSocket handles 100 concurrent connections without errors
- [ ] Bulk operations handle 100 tasks within 3 seconds
- [ ] Search indexed for 10,000+ tasks with <500ms queries
- [ ] Frontend responsive on mobile devices
- [ ] Real-time updates work across multiple browser tabs/windows

### Testing Checklist

- [ ] Create 1000+ tasks and verify search performance
- [ ] Test bulk update/delete with 100 tasks
- [ ] Open 10 browser windows and verify real-time updates propagate
- [ ] Create template with placeholders and instantiate successfully
- [ ] Generate analytics for 30-day period and export to CSV/PDF
- [ ] Test WebSocket reconnection after network interruption
- [ ] Verify presence indicators clear after timeout
- [ ] Test concurrent edits and conflict resolution
- [ ] Validate saved searches persist and execute correctly
- [ ] Test time tracking across page refreshes

---

## Out of Scope

- Shared task lists between users (collaboration is within same list only)
- External calendar integrations (Google Calendar, Outlook)
- Mobile native apps (web app is responsive but not native)
- Automated task suggestions via AI/ML
- Gantt chart or timeline visualization
- Voice commands or dictation
- Third-party integrations (Slack, Jira, Trello)
- Custom workflows or automation rules
- Role-based permissions (all users have equal access to their tasks)
- Multi-language support (English only)

---

## Risks and Mitigations

### Risk 1: WebSocket Scaling
**Risk**: WebSocket connections consume server resources; 1000+ concurrent users may overload single backend instance
**Likelihood**: Medium
**Impact**: High (app becomes unusable)
**Mitigation**: Use Redis Pub/Sub for horizontal scaling, load balancing across multiple backend instances, connection pooling limits

### Risk 2: Search Performance Degradation
**Risk**: Full-text search becomes slow with 100,000+ tasks despite indexing
**Likelihood**: Low (PostgreSQL GIN indexes handle millions of rows)
**Impact**: Medium (degraded user experience)
**Mitigation**: Monitor query performance, add pagination limits, consider Elasticsearch migration if needed

### Risk 3: Bulk Operation Failures
**Risk**: Bulk operations fail midway due to network/database errors, leaving inconsistent state
**Likelihood**: Medium
**Impact**: High (data corruption)
**Mitigation**: Use database transactions (all-or-nothing), implement retry logic, detailed error logging with affected task IDs

### Risk 4: Template Complexity
**Risk**: Complex templates with many placeholders become difficult for users to manage
**Likelihood**: Low
**Impact**: Low (usability issue, not functional)
**Mitigation**: Validate placeholder syntax, provide preview before instantiation, limit to 10 placeholders per template

### Risk 5: Real-Time Conflict Resolution
**Risk**: Simultaneous edits lead to data loss or confusing conflict resolution UX
**Likelihood**: Medium
**Impact**: Medium (user frustration, data loss)
**Mitigation**: Implement optimistic locking with version numbers, clear conflict notifications, merge tools for complex conflicts

---

## Dependencies

- PostgreSQL 14+ (for JSONB, full-text search, GIN indexes)
- Redis (for WebSocket pub/sub and presence tracking)
- FastAPI WebSocket support
- Frontend charting library (Chart.js or Recharts)
- PDF generation library (ReportLab or Puppeteer)
- JWT authentication (already implemented in Phase II)

---

## Deployment Considerations

### Kubernetes Additions

**New ConfigMaps:**
- `websocket-config`: WebSocket server settings (heartbeat interval, max connections)
- `analytics-config`: Export settings (max report size, PDF template)

**New Secrets:**
- `redis-credentials`: Redis connection string for pub/sub (if using external Redis)

**New Services:**
- WebSocket service may need sticky sessions (session affinity) for load balancing

**Resource Requirements:**
- Backend pods: Increase memory to 1GB (from 512MB) to handle WebSocket connections
- Redis deployment: 512MB memory, persistent volume for pub/sub state

### Environment Variables

```env
# Search
POSTGRES_SEARCH_LIMIT=1000          # Max search results
ENABLE_SEARCH_SUGGESTIONS=true      # Autocomplete suggestions

# WebSocket
WS_HEARTBEAT_INTERVAL=10            # Seconds between heartbeats
WS_PRESENCE_TIMEOUT=30              # Seconds before marking user offline
WS_MAX_CONNECTIONS=1000             # Per backend instance

# Bulk Operations
BULK_OPERATION_LIMIT=500            # Max tasks per bulk operation
BULK_OPERATION_TIMEOUT=30           # Seconds before timeout

# Analytics
ANALYTICS_CACHE_TTL=300             # Cache metrics for 5 minutes
MAX_EXPORT_SIZE=10000               # Max tasks in CSV export
ENABLE_PDF_EXPORT=true              # Enable PDF generation

# Redis (for WebSocket scaling)
REDIS_URL=redis://redis:6379/0
```

---

## Timeline Estimate

**Phase 1: Search & Filtering** (~2-3 days)
- Database schema + indexes
- Search API endpoint
- Saved searches CRUD
- Frontend search UI

**Phase 2: Templates & Bulk Operations** (~2-3 days)
- Template schema + API
- Placeholder replacement logic
- Bulk update/delete endpoints
- Frontend template management

**Phase 3: Real-Time Collaboration** (~3-4 days)
- WebSocket server setup
- Redis pub/sub integration
- Presence tracking
- Frontend WebSocket client + UI updates

**Phase 4: Analytics & Reporting** (~3-4 days)
- Analytics calculation endpoints
- Time tracking API
- Chart rendering (frontend)
- CSV/PDF export generation

**Phase 5: Integration & Testing** (~2-3 days)
- End-to-end testing
- Performance testing (load tests)
- Bug fixes
- Documentation updates

**Total Estimated Time**: 12-17 days (depends on complexity and testing thoroughness)

---

## References

- [PostgreSQL Full-Text Search](https://www.postgresql.org/docs/current/textsearch.html)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [Chart.js Documentation](https://www.chartjs.org/docs/latest/)
- [ReportLab PDF Generation](https://www.reportlab.com/docs/reportlab-userguide.pdf)
