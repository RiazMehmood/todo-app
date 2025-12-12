# Feature Specification: Full-Stack Web Application

**Feature Branch**: `002-todo-web-app`
**Created**: 2025-12-09
**Status**: Draft
**Input**: User description: "Create specification for Phase 2: Full-Stack Web Application. Include: All 5 Basic Level features (Add, View, Update, Delete, Mark Complete), User authentication with Better Auth and JWT, Multi-user support with data isolation, RESTful API with FastAPI, Responsive UI with Next.js 16+, Persistent storage with Neon PostgreSQL"

## User Scenarios & Testing

### User Story 1 - User Account Creation (Priority: P1)

A new user creates an account to start managing their tasks independently.

**Why this priority**: Authentication is foundational - without it, multi-user support and data isolation are impossible. This is the entry point to the entire application.

**Independent Test**: Can be fully tested by signing up with email/password and verifying JWT token is issued, user record is created in database, and user is redirected to an empty dashboard.

**Acceptance Scenarios**:

1. **Given** I am a new user on the signup page, **When** I provide valid email, password (8+ chars), and name, **Then** my account is created, I receive a JWT token, and I'm redirected to the dashboard
2. **Given** I try to signup with an email that already exists, **When** I submit the form, **Then** I see an error message "Email already registered"
3. **Given** I provide a password shorter than 8 characters, **When** I attempt signup, **Then** the form shows a validation error and prevents submission

---

### User Story 2 - User Login (Priority: P1)

A registered user logs into their account to access their personal task list.

**Why this priority**: Login enables returning users to access their data. Along with signup, this completes the authentication foundation required for all other features.

**Independent Test**: Can be fully tested by logging in with existing credentials, verifying JWT token is issued, and confirming user is redirected to their dashboard with their existing tasks visible.

**Acceptance Scenarios**:

1. **Given** I am a registered user on the login page, **When** I enter correct email and password, **Then** I receive a JWT token and am redirected to my dashboard
2. **Given** I enter incorrect credentials, **When** I submit the login form, **Then** I see an error message "Invalid credentials" and remain on the login page
3. **Given** my JWT token has expired, **When** I attempt to access a protected route, **Then** I'm redirected to the login page with a message to log in again

---

### User Story 3 - Create New Task (Priority: P2)

A logged-in user creates a new task to track something they need to do.

**Why this priority**: This is the primary value-add feature - without the ability to create tasks, the app has no purpose. Depends on authentication (P1) but delivers immediate user value.

**Independent Test**: Can be fully tested by logging in, clicking "Add Task", entering a title and optional description, submitting, and verifying the new task appears in the task list with correct data and user_id.

**Acceptance Scenarios**:

1. **Given** I am logged in and on my dashboard, **When** I enter a task title "Buy groceries" and submit, **Then** a new task is created with `completed=false`, assigned to my user_id, and appears at the top of my task list
2. **Given** I try to create a task with a 201-character title, **When** I submit, **Then** I see a validation error "Title must be 200 characters or less"
3. **Given** I create a task without a description, **When** I submit, **Then** the task is created successfully with description set to null

---

### User Story 4 - View Task List (Priority: P2)

A logged-in user views all their tasks in one place to review what needs to be done.

**Why this priority**: Viewing tasks is essential for understanding what needs to be done. This feature enables users to see the value of creating tasks and completes the basic "create and view" workflow.

**Independent Test**: Can be fully tested by logging in, creating 2-3 tasks, and verifying only those tasks (not other users' tasks) are displayed with correct title, completion status, and creation date.

**Acceptance Scenarios**:

1. **Given** I have created 5 tasks, **When** I visit my dashboard, **Then** I see all 5 tasks listed, ordered by creation date (newest first)
2. **Given** another user has created tasks, **When** I view my dashboard, **Then** I only see my tasks, not theirs
3. **Given** I have no tasks, **When** I visit my dashboard, **Then** I see an empty state message "No tasks yet. Create your first task!"

---

### User Story 5 - Mark Task Complete/Incomplete (Priority: P2)

A logged-in user toggles a task's completion status to track progress.

**Why this priority**: Marking tasks complete is the primary action users take. This delivers the satisfaction of checking off completed work and is core to the todo app experience.

**Independent Test**: Can be fully tested by creating a task, clicking its checkbox to mark it complete (verify `completed=true`), clicking again to mark it incomplete (verify `completed=false`), and confirming UI updates correctly.

**Acceptance Scenarios**:

1. **Given** I have an incomplete task, **When** I click its checkbox, **Then** the task is marked as completed, the checkbox shows checked, and `updated_at` timestamp is updated
2. **Given** I have a completed task, **When** I click its checkbox, **Then** the task is marked as incomplete and the checkbox shows unchecked
3. **Given** I toggle a task's status, **When** I refresh the page, **Then** the task's completion status persists

---

### User Story 6 - Update Task Details (Priority: P3)

A logged-in user edits a task's title or description to correct or clarify information.

**Why this priority**: While useful, editing is less critical than creating and marking complete. Users can work around missing edit functionality by deleting and recreating tasks.

**Independent Test**: Can be fully tested by creating a task, clicking "Edit", modifying the title and/or description, saving, and verifying the changes persist and `updated_at` is updated.

**Acceptance Scenarios**:

1. **Given** I have a task with title "Buy groceries", **When** I edit it to "Buy organic groceries", **Then** the title is updated, `updated_at` timestamp changes, and the new title displays in the list
2. **Given** I try to update a task with an empty title, **When** I submit, **Then** I see a validation error "Title is required"
3. **Given** I try to edit another user's task by manipulating the URL, **When** I submit the edit, **Then** I receive HTTP 403 Forbidden

---

### User Story 7 - Delete Task (Priority: P3)

A logged-in user deletes a task to remove it permanently.

**Why this priority**: Deletion is helpful for cleanup but not essential for core workflow. Users can ignore unwanted tasks rather than delete them.

**Independent Test**: Can be fully tested by creating a task, clicking "Delete", confirming deletion in a modal, and verifying the task is removed from the database and UI.

**Acceptance Scenarios**:

1. **Given** I have a task, **When** I click delete and confirm, **Then** the task is permanently removed from the database and no longer appears in my list
2. **Given** I accidentally click delete, **When** I see the confirmation modal and click "Cancel", **Then** the task is not deleted and remains in my list
3. **Given** I try to delete another user's task by manipulating the API, **When** I send the request, **Then** I receive HTTP 403 Forbidden

---

### User Story 8 - User Logout (Priority: P3)

A logged-in user logs out to secure their session.

**Why this priority**: Logout is a security best practice but less critical than core task management features. Sessions expire naturally after 7 days.

**Independent Test**: Can be fully tested by logging in, clicking "Logout", and verifying JWT token is removed from client storage and user is redirected to login page.

**Acceptance Scenarios**:

1. **Given** I am logged in, **When** I click the "Logout" button, **Then** my JWT token is removed and I'm redirected to the login page
2. **Given** I have logged out, **When** I try to access the dashboard directly via URL, **Then** I'm redirected to the login page
3. **Given** I log out, **When** I attempt any API call, **Then** I receive HTTP 401 Unauthorized

---

### Edge Cases

- What happens when a user tries to create a task with a 1001-character description?
  → Frontend validation prevents submission; backend returns HTTP 400 if bypassed

- What happens when a user's JWT token expires mid-session?
  → Next API call returns HTTP 401, user is auto-redirected to login page with session expired message

- What happens when two users simultaneously edit the same task ID but belonging to different users?
  → Each operation is isolated by user_id; no conflict occurs as they're editing different tasks in different user contexts

- What happens when a user deletes their account?
  → All their tasks are cascade-deleted (foreign key constraint), ensuring no orphaned data

- What happens when the database connection is lost?
  → Backend returns HTTP 500, frontend shows "Service temporarily unavailable" message

- What happens when a user manipulates the URL to access `/api/{different_user_id}/tasks`?
  → JWT middleware detects mismatch between token user_id and URL user_id, returns HTTP 403 Forbidden

## Requirements

### Functional Requirements

- **FR-001**: System MUST allow users to create accounts with email, password (min 8 chars), and name
- **FR-002**: System MUST authenticate users via Better Auth and issue JWT tokens upon successful login/signup
- **FR-003**: System MUST verify JWT tokens on every API request and extract authenticated user_id
- **FR-004**: Users MUST be able to create tasks with title (1-200 chars, required) and description (max 1000 chars, optional)
- **FR-005**: Users MUST be able to view a list of all their tasks, ordered by creation date (newest first)
- **FR-006**: Users MUST be able to view details of a single task
- **FR-007**: Users MUST be able to update a task's title and/or description
- **FR-008**: Users MUST be able to delete a task permanently
- **FR-009**: Users MUST be able to toggle a task's completion status (completed ↔ incomplete)
- **FR-010**: System MUST enforce user-level data isolation - users can only access their own tasks
- **FR-011**: System MUST return HTTP 401 for missing or invalid JWT tokens
- **FR-012**: System MUST return HTTP 403 when a user attempts to access another user's data
- **FR-013**: System MUST persist all data in Neon PostgreSQL database
- **FR-014**: System MUST automatically set `created_at` timestamp when creating tasks
- **FR-015**: System MUST automatically update `updated_at` timestamp when modifying tasks
- **FR-016**: Frontend MUST redirect unauthenticated users to the login page when accessing protected routes
- **FR-017**: Frontend MUST display user-friendly error messages for validation failures
- **FR-018**: Frontend MUST be responsive and work on mobile, tablet, and desktop screens
- **FR-019**: Backend MUST provide OpenAPI documentation at `/docs` endpoint
- **FR-020**: Backend MUST enforce CORS restrictions to allow requests only from trusted frontend origins

### Key Entities

- **User**: Represents an authenticated account. Attributes: id (UUID), email (unique), name, password_hash, created_at. Managed by Better Auth.

- **Task**: Represents a todo item belonging to one user. Attributes: id (auto-increment), user_id (foreign key to User), title (1-200 chars), description (optional, max 1000 chars), completed (boolean, default false), created_at, updated_at. Relationship: Many tasks belong to one user.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can complete account signup in under 10 seconds from landing on signup page
- **SC-002**: Users can create a new task in under 3 seconds (click "Add Task" → enter title → submit → see in list)
- **SC-003**: Users can mark a task complete with a single click and see immediate visual feedback
- **SC-004**: Task list loads in under 1 second for users with up to 100 tasks
- **SC-005**: Zero data leakage - users can never see or access tasks belonging to other users
- **SC-006**: 100% of API requests with invalid JWT tokens are rejected with HTTP 401
- **SC-007**: 100% of attempts to access another user's data via URL manipulation result in HTTP 403
- **SC-008**: Application is responsive and usable on screens from 320px to 2560px width
- **SC-009**: Frontend successfully deploys to Vercel with no build errors
- **SC-010**: Backend successfully connects to Neon PostgreSQL and runs CRUD operations without errors
