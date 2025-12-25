# Data Model: Intermediate + Advanced Features
## Database Schema for Phase V Enhancement

**Date**: 2025-12-23
**Branch**: 005-cloud-native-deployment
**Status**: Design Complete

---

## Overview

This document defines the database schema extensions for 4 new feature sets:
1. **Advanced Search**: Saved searches with JSONB query storage
2. **Task Templates**: Reusable templates with placeholder replacement
3. **Analytics & Time Tracking**: Time entries for task work sessions
4. **Real-Time Collaboration**: WebSocket presence tracking (optional table)

All tables use **PostgreSQL** with appropriate indexes for performance.

---

## 1. Existing Tables (Modified)

### 1.1. `tasks` Table Extensions

**New Column**: `search_vector` for full-text search

```sql
-- Add full-text search vector (GENERATED column)
ALTER TABLE tasks ADD COLUMN search_vector tsvector GENERATED ALWAYS AS (
    setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(description, '')), 'B')
) STORED;

-- Create GIN index for fast full-text search
CREATE INDEX idx_tasks_search ON tasks USING GIN(search_vector)
    WITH (fastupdate = ON, gin_pending_list_limit = 128);
```

**Rationale**:
- `GENERATED ALWAYS AS` automatically maintains the search vector
- Weight A (highest) for title, weight B for description
- GIN index provides 50-100x faster search than LIKE queries

**Updated Table Schema**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Task identifier |
| user_id | VARCHAR(255) | NOT NULL, FOREIGN KEY → users(id) | Owner user |
| title | VARCHAR(200) | NOT NULL | Task title |
| description | TEXT | NULL | Task description |
| status | VARCHAR(20) | NOT NULL, CHECK (status IN ('pending', 'in_progress', 'completed')) | Current status |
| priority | VARCHAR(10) | NOT NULL, CHECK (priority IN ('low', 'medium', 'high')) | Priority level |
| tags | TEXT[] | DEFAULT '{}' | Task tags |
| due_date | TIMESTAMP WITH TIME ZONE | NULL | Due date |
| recurring_pattern | VARCHAR(50) | NULL | Recurrence pattern |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Last update timestamp |
| **search_vector** | **TSVECTOR** | **GENERATED ALWAYS AS** | **Full-text search vector** |

**Indexes**:
- PRIMARY KEY: `id`
- INDEX: `user_id` (for user task queries)
- INDEX: `status` (for filtering)
- INDEX: `priority` (for filtering)
- **GIN INDEX**: `search_vector` (for full-text search)

---

## 2. New Tables

### 2.1. `saved_searches` Table

**Purpose**: Store user-defined search queries for quick access

```sql
CREATE TABLE saved_searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    query_params JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT saved_searches_user_name_unique UNIQUE (user_id, name)
);

-- Indexes
CREATE INDEX idx_saved_searches_user_id ON saved_searches(user_id);
CREATE INDEX idx_saved_searches_query_params ON saved_searches USING GIN(query_params);
```

**Schema**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Search identifier |
| user_id | VARCHAR(255) | NOT NULL, FOREIGN KEY → users(id) | Owner user |
| name | VARCHAR(100) | NOT NULL | Search name (e.g., "Hot List") |
| query_params | JSONB | NOT NULL, DEFAULT '{}' | Full search parameters |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Last update timestamp |

**Constraints**:
- UNIQUE (user_id, name) - No duplicate search names per user
- ON DELETE CASCADE - Remove searches when user deleted

**Example JSONB query_params**:

```json
{
  "query": "urgent meeting",
  "filters": {
    "status": ["pending", "in_progress"],
    "priority": ["high"],
    "tags": ["work", "urgent"],
    "created_after": "2025-12-01",
    "due_before": "2025-12-31"
  },
  "sort_by": "due_date",
  "sort_order": "asc"
}
```

---

### 2.2. `task_templates` Table

**Purpose**: Store reusable task templates with placeholders

```sql
CREATE TABLE task_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    tasks_definition JSONB NOT NULL,
    placeholders TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT task_templates_user_name_unique UNIQUE (user_id, name),
    CONSTRAINT task_templates_max_placeholders CHECK (array_length(placeholders, 1) <= 10),
    CONSTRAINT task_templates_max_tasks CHECK (jsonb_array_length(tasks_definition) <= 50)
);

-- Indexes
CREATE INDEX idx_task_templates_user_id ON task_templates(user_id);
```

**Schema**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Template identifier |
| user_id | VARCHAR(255) | NOT NULL, FOREIGN KEY → users(id) | Owner user |
| name | VARCHAR(100) | NOT NULL | Template name |
| description | TEXT | NULL | Template description |
| tasks_definition | JSONB | NOT NULL | Array of task definitions |
| placeholders | TEXT[] | NOT NULL, DEFAULT '{}' | List of placeholder names |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Last update timestamp |

**Constraints**:
- UNIQUE (user_id, name) - No duplicate template names per user
- CHECK (array_length(placeholders, 1) <= 10) - Max 10 placeholders
- CHECK (jsonb_array_length(tasks_definition) <= 50) - Max 50 tasks
- ON DELETE CASCADE - Remove templates when user deleted

**Example tasks_definition JSONB**:

```json
[
  {
    "title": "{{CLIENT_NAME}} - Initial Meeting",
    "description": "Schedule kickoff call with {{CLIENT_NAME}}",
    "priority": "high",
    "tags": ["onboarding", "{{CLIENT_NAME}}"],
    "due_date_offset": 0
  },
  {
    "title": "{{CLIENT_NAME}} - Setup Account",
    "description": "Create account for {{CLIENT_NAME}} in system",
    "priority": "medium",
    "tags": ["onboarding", "{{CLIENT_NAME}}"],
    "due_date_offset": 1
  }
]
```

---

### 2.3. `time_entries` Table

**Purpose**: Track time spent working on tasks

```sql
CREATE TABLE time_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ended_at TIMESTAMP WITH TIME ZONE NULL,
    elapsed_seconds INTEGER NULL,
    description VARCHAR(500) NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT time_entries_valid_times CHECK (
        ended_at IS NULL OR ended_at > started_at
    ),
    CONSTRAINT time_entries_elapsed_calculation CHECK (
        (ended_at IS NULL AND elapsed_seconds IS NULL) OR
        (ended_at IS NOT NULL AND elapsed_seconds IS NOT NULL)
    )
);

-- Indexes
CREATE INDEX idx_time_entries_task_id ON time_entries(task_id);
CREATE INDEX idx_time_entries_user_id ON time_entries(user_id);
CREATE INDEX idx_time_entries_started_at ON time_entries(started_at);

-- Trigger to auto-calculate elapsed_seconds
CREATE OR REPLACE FUNCTION update_elapsed_seconds()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.ended_at IS NOT NULL AND NEW.started_at IS NOT NULL THEN
        NEW.elapsed_seconds = EXTRACT(EPOCH FROM (NEW.ended_at - NEW.started_at))::INTEGER;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_elapsed_seconds
    BEFORE INSERT OR UPDATE ON time_entries
    FOR EACH ROW
    EXECUTE FUNCTION update_elapsed_seconds();
```

**Schema**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Entry identifier |
| task_id | UUID | NOT NULL, FOREIGN KEY → tasks(id) | Task being timed |
| user_id | VARCHAR(255) | NOT NULL, FOREIGN KEY → users(id) | User who worked on task |
| started_at | TIMESTAMP WITH TIME ZONE | NOT NULL | When timer started |
| ended_at | TIMESTAMP WITH TIME ZONE | NULL | When timer stopped (null if running) |
| elapsed_seconds | INTEGER | NULL | Auto-calculated duration |
| description | VARCHAR(500) | NULL | Work description |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Entry creation time |

**Constraints**:
- CHECK (ended_at > started_at) - End must be after start
- CHECK (elapsed_seconds calculation valid) - Ensure consistency
- ON DELETE CASCADE - Remove entries when task/user deleted

**Indexes**:
- task_id - For querying all entries for a task
- user_id - For querying all entries for a user
- started_at - For date range queries

**Trigger Logic**:
- Automatically calculates `elapsed_seconds` when `ended_at` is set
- Formula: `EXTRACT(EPOCH FROM (ended_at - started_at))::INTEGER`

---

### 2.4. `presence_sessions` Table (Optional)

**Purpose**: Audit trail for WebSocket connections (optional - presence is primarily in Redis)

```sql
CREATE TABLE presence_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100) NOT NULL UNIQUE,
    task_id UUID NULL REFERENCES tasks(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('viewing', 'editing', 'idle')),
    connected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    disconnected_at TIMESTAMP WITH TIME ZONE NULL,
    last_heartbeat TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_presence_sessions_user_id ON presence_sessions(user_id);
CREATE INDEX idx_presence_sessions_task_id ON presence_sessions(task_id);
CREATE INDEX idx_presence_sessions_connected_at ON presence_sessions(connected_at);
CREATE INDEX idx_presence_sessions_active ON presence_sessions(disconnected_at)
    WHERE disconnected_at IS NULL;
```

**Schema**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Session identifier |
| user_id | VARCHAR(255) | NOT NULL, FOREIGN KEY → users(id) | Connected user |
| session_id | VARCHAR(100) | NOT NULL, UNIQUE | WebSocket session ID |
| task_id | UUID | NULL, FOREIGN KEY → tasks(id) | Currently viewing task |
| status | VARCHAR(20) | CHECK (status IN (...)) | User status |
| connected_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Connection time |
| disconnected_at | TIMESTAMP WITH TIME ZONE | NULL | Disconnection time (null if active) |
| last_heartbeat | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | Last heartbeat received |

**Note**: This table is **optional** and used for audit/analytics. Real-time presence is tracked in Redis with 30-second TTL.

---

## 3. Entity Relationships

```
┌─────────────┐
│    users    │
└──────┬──────┘
       │
       ├─────────────┬──────────────────┬──────────────┐
       │             │                  │              │
       ▼             ▼                  ▼              ▼
┌─────────────┐  ┌──────────────┐  ┌────────────────┐  ┌──────────────────┐
│    tasks    │  │saved_searches│  │task_templates  │  │presence_sessions │
│ + search    │  │(JSONB params)│  │(JSONB tasks)   │  │  (audit trail)   │
└──────┬──────┘  └──────────────┘  └────────────────┘  └──────────────────┘
       │
       ▼
┌──────────────┐
│time_entries  │
│(time track)  │
└──────────────┘
```

---

## 4. Storage Estimates

**Assumptions**:
- 1,000 users
- 10,000 tasks per user (10M total)
- 5 saved searches per user
- 2 templates per user
- 3 time entries per task (30M total)
- 100 active presence sessions at any time

**Estimated Storage**:

| Table | Rows | Avg Row Size | Total Size |
|-------|------|--------------|------------|
| tasks (with search_vector) | 10M | ~1.5 KB | 15 GB |
| saved_searches | 5K | ~500 B | 2.5 MB |
| task_templates | 2K | ~2 KB | 4 MB |
| time_entries | 30M | ~300 B | 9 GB |
| presence_sessions | 100 (active) | ~200 B | 20 KB |
| **Total** | - | - | **~24 GB** |

**Index Overhead**: ~30% = 7.2 GB

**Total Database Size**: ~31 GB (with indexes)

**Note**: PostgreSQL handles this scale easily. Consider partitioning `time_entries` by date if exceeds 100M rows.

---

## 5. Performance Considerations

### 5.1. Query Performance

**Full-Text Search** (with GIN index):
- Search 10K tasks: 5-10ms
- Search 1M tasks: 20-30ms
- Ranked search: +5-10ms overhead

**Time Entry Aggregation**:
```sql
-- Get total time for a task (indexed on task_id)
SELECT SUM(elapsed_seconds) FROM time_entries WHERE task_id = '...';
-- Performance: <5ms for 100 entries

-- Get time by date range (indexed on started_at)
SELECT task_id, SUM(elapsed_seconds)
FROM time_entries
WHERE user_id = '...' AND started_at BETWEEN '...' AND '...'
GROUP BY task_id;
-- Performance: <50ms for 10K entries
```

**Template Instantiation**:
- Fetch template: <5ms
- Replace placeholders: <1ms per task
- Create 10 tasks: <100ms total

### 5.2. Index Maintenance

**Weekly Tasks**:
```sql
-- Reindex full-text search
REINDEX INDEX idx_tasks_search;

-- Update statistics
ANALYZE tasks;
ANALYZE time_entries;
```

**Monthly Tasks**:
```sql
-- Archive old presence_sessions (optional)
DELETE FROM presence_sessions
WHERE disconnected_at < NOW() - INTERVAL '30 days';

-- Vacuum to reclaim space
VACUUM ANALYZE;
```

---

## Summary

**New Tables**: 4 (saved_searches, task_templates, time_entries, presence_sessions)

**Modified Tables**: 1 (tasks - added search_vector)

**Total Indexes**: 12 new indexes

**Storage Requirements**: ~31 GB for 10M tasks + time tracking

**Migration Time**: ~5-10 minutes for existing 10M task database

**Backward Compatibility**: Fully backward compatible - all new columns/tables are additive

---

**Data Model Complete**: Ready for implementation.
