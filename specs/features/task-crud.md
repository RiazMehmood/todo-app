# Feature: Task CRUD Operations

## Overview

Enable users to **Create, Read, Update, Delete, and Mark Complete** their todo tasks through a web interface. Each user can only access and manage their own tasks.

## User Stories

### US-1: Create Task
**As a** logged-in user
**I want to** create a new task
**So that** I can track things I need to do

**Acceptance Criteria:**
- User must be authenticated (JWT token required)
- Title is required (1-200 characters)
- Description is optional (max 1000 characters)
- Task is automatically associated with the authenticated user
- Task starts with `completed = false`
- Task gets a unique ID and timestamps (`created_at`, `updated_at`)
- Success returns HTTP 201 with the created task

### US-2: View All Tasks
**As a** logged-in user
**I want to** see a list of all my tasks
**So that** I can review what I need to do

**Acceptance Criteria:**
- User must be authenticated
- Only shows tasks belonging to the authenticated user
- Displays task ID, title, completion status, and created date
- Tasks ordered by creation date (newest first)
- Success returns HTTP 200 with task array

### US-3: View Single Task
**As a** logged-in user
**I want to** view details of a specific task
**So that** I can see its full information

**Acceptance Criteria:**
- User must be authenticated
- User can only view their own tasks (not other users' tasks)
- Returns full task details (id, title, description, completed, timestamps)
- Returns HTTP 404 if task doesn't exist or doesn't belong to user
- Success returns HTTP 200 with task object

### US-4: Update Task
**As a** logged-in user
**I want to** modify a task's title or description
**So that** I can correct or clarify my todos

**Acceptance Criteria:**
- User must be authenticated
- User can only update their own tasks
- Can update title (1-200 characters) and/or description (max 1000 characters)
- `updated_at` timestamp is automatically set to current time
- Returns HTTP 404 if task doesn't exist or doesn't belong to user
- Success returns HTTP 200 with updated task

### US-5: Delete Task
**As a** logged-in user
**I want to** remove a task
**So that** I can clean up completed or irrelevant items

**Acceptance Criteria:**
- User must be authenticated
- User can only delete their own tasks
- Task is permanently removed from database
- Returns HTTP 404 if task doesn't exist or doesn't belong to user
- Success returns HTTP 200 or HTTP 204

### US-6: Mark Task Complete/Incomplete
**As a** logged-in user
**I want to** toggle a task's completion status
**So that** I can track my progress

**Acceptance Criteria:**
- User must be authenticated
- User can only modify their own tasks
- Toggles `completed` field between `true` and `false`
- `updated_at` timestamp is automatically set to current time
- Returns HTTP 404 if task doesn't exist or doesn't belong to user
- Success returns HTTP 200 with updated task

## Data Model

### Task Entity

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| id | integer | Auto | Primary key | Unique task identifier |
| user_id | string | Yes | Foreign key to users.id | Task owner |
| title | string | Yes | 1-200 chars | Task title |
| description | string | No | Max 1000 chars | Detailed description |
| completed | boolean | Auto | Default: false | Completion status |
| created_at | timestamp | Auto | Default: NOW() | Creation timestamp |
| updated_at | timestamp | Auto | Default: NOW() | Last update timestamp |

### Indexes
- `idx_tasks_user_id` on `user_id` (for efficient user filtering)
- `idx_tasks_completed` on `completed` (for future filtering by status)

## API Endpoints

See [API Specification](../api/rest-endpoints.md) for detailed endpoint definitions.

**Summary:**
- `GET /api/{user_id}/tasks` - List all user's tasks
- `POST /api/{user_id}/tasks` - Create new task
- `GET /api/{user_id}/tasks/{id}` - Get single task
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion

## UI Components

See [UI Specification](../ui/components.md) for component details.

**Required Components:**
- `TaskList` - Display all tasks in a list/table
- `TaskItem` - Individual task row with actions
- `AddTaskForm` - Form to create new task
- `EditTaskModal` - Modal to edit existing task
- `DeleteConfirmation` - Confirmation dialog for delete

## Validation Rules

### Frontend Validation
- Title: Required, 1-200 characters
- Description: Optional, max 1000 characters
- Show inline error messages for validation failures
- Disable submit button while form is invalid

### Backend Validation
- Verify JWT token is valid
- Verify user_id in URL matches authenticated user
- Validate title length (1-200 chars)
- Validate description length (max 1000 chars)
- Return HTTP 400 with error details for validation failures
- Return HTTP 401 if authentication fails
- Return HTTP 403 if user tries to access another user's task

## Error Handling

### Frontend
- Display user-friendly error messages
- Handle network errors gracefully
- Show loading states during API calls
- Optimistic UI updates with rollback on error

### Backend
- HTTP 400: Bad request (validation errors)
- HTTP 401: Unauthorized (missing/invalid JWT)
- HTTP 403: Forbidden (accessing another user's task)
- HTTP 404: Not found (task doesn't exist)
- HTTP 500: Internal server error (database errors, etc.)

## Security Requirements

1. **Authentication**: All endpoints require valid JWT token
2. **Authorization**: Users can only access their own tasks
3. **Data Isolation**: Database queries filter by `user_id`
4. **Input Validation**: Prevent SQL injection via ORM
5. **XSS Prevention**: Sanitize user input on display

## Business Rules

1. **Task Ownership**: A task belongs to exactly one user
2. **Immutable User ID**: Cannot change task ownership after creation
3. **Soft Delete Not Required**: Tasks are permanently deleted
4. **No Archive**: No archive/restore functionality in Phase II
5. **Single Status**: Only completed/incomplete (no "in progress", "blocked", etc.)

## Success Metrics

- User can create task in < 3 seconds
- User can mark task complete with single click
- Task list loads in < 1 second
- Zero data leakage between users

## Future Enhancements (Not in Phase II)

- Filter tasks by completion status
- Search tasks by title/description
- Sort tasks by different fields
- Priorities and tags
- Recurring tasks
- Due dates and reminders

## Dependencies

- **Authentication**: Better Auth must be implemented first
- **Database**: Neon PostgreSQL connection configured
- **API**: FastAPI backend with JWT middleware

## Testing Scenarios

### Happy Path
1. User logs in → Creates task → Task appears in list
2. User marks task complete → Checkbox is checked
3. User edits task → Changes are saved
4. User deletes task → Task is removed

### Edge Cases
1. User tries to access another user's task → HTTP 403
2. User creates task with 201-character title → HTTP 400
3. User tries to update non-existent task → HTTP 404
4. User submits empty title → Frontend validation prevents submit

### Security Tests
1. Unauthenticated user tries to create task → HTTP 401
2. User manipulates URL to access task with different user_id → HTTP 403
3. JWT token expired → HTTP 401, redirect to login
