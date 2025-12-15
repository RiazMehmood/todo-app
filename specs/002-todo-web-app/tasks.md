# Implementation Tasks: Full-Stack Web Application

**Feature**: 002-todo-web-app
**Branch**: `002-todo-web-app`
**Created**: 2025-12-09
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Overview

This document contains actionable implementation tasks for Phase 2: Full-Stack Web Application. Tasks are organized by user story priority to enable independent, incremental delivery.

**Tech Stack**:
- Backend: Python 3.13+ + FastAPI + SQLModel + JWT + Neon PostgreSQL
- Frontend: Next.js 16+ + TypeScript + Tailwind CSS + Better Auth

**Testing Approach**: Manual testing for Phase II (automated tests optional per constitution)

---

## Phase 1: Setup & Infrastructure

**Goal**: Initialize project structure and configure development environment

**Tasks**:

- [X] T001 Create Neon PostgreSQL database and obtain connection string
- [X] T002 [P] Configure backend environment variables in backend/.env (DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS)
- [X] T003 [P] Configure frontend environment variables in frontend/.env.local (NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL)
- [X] T004 Verify BETTER_AUTH_SECRET matches between backend/.env and frontend/.env.local
- [X] T005 [P] Install backend dependencies via UV in backend/
- [X] T006 [P] Install frontend dependencies via npm in frontend/
- [X] T007 Create database tables by running Python initialization script from backend/

**Acceptance**: Backend and frontend servers start without errors, database connection successful

---

## Phase 2: Foundational (Blocking Prerequisites)

**Goal**: Implement foundational infrastructure required by all user stories

**Tasks**:

### Backend Foundation

- [X] T008 Create User SQLModel in backend/src/models.py (id, email, name, password_hash, created_at, updated_at)
- [X] T009 Create Task SQLModel in backend/src/models.py (id, user_id, title, description, completed, created_at, updated_at)
- [X] T010 Implement database connection and session management in backend/src/db.py (engine, create_db_and_tables, get_session)
- [X] T011 Implement JWT verification middleware in backend/src/middleware/auth.py (verify_jwt function)
- [X] T012 Configure FastAPI app in backend/src/main.py (CORS middleware, startup event, health endpoint)

### Frontend Foundation

- [X] T013 Create TypeScript type definitions in frontend/lib/types.ts (Task, User, CreateTaskInput, etc.)
- [X] T014 Implement API client with JWT handling in frontend/lib/api.ts (apiCall, api.getTasks, api.createTask, etc.)
- [X] T015 Configure Better Auth in frontend/lib/auth.ts (auth config, getSession, signIn, signOut)
- [X] T016 Create root layout with metadata in frontend/app/layout.tsx
- [X] T017 Configure Tailwind CSS in frontend/tailwind.config.ts and frontend/app/globals.css

**Acceptance**: Backend API starts with /health endpoint, frontend compiles without errors, JWT middleware configured

---

## Phase 3: User Story 1 - User Account Creation (P1)

**Goal**: Enable new users to create accounts and receive JWT tokens

**Independent Test**: Signup with valid email/password → User created in database → JWT issued → Redirect to empty dashboard

**Story Tasks**:

### Backend (US1)

- [X] T018 [US1] Create signup endpoint POST /api/auth/signup in backend/src/routes/auth.py (validate input, hash password, create user, issue JWT)
- [X] T019 [US1] Add Pydantic request model for signup in backend/src/routes/auth.py (SignupRequest with email, password, name validation)
- [X] T020 [US1] Implement password hashing using passlib in backend/src/routes/auth.py
- [X] T021 [US1] Implement JWT token generation using python-jose in backend/src/routes/auth.py (include user_id, email, exp)
- [X] T022 [US1] Handle duplicate email error (HTTP 409) in signup endpoint

### Frontend (US1)

- [X] T023 [US1] Create signup page component in frontend/app/signup/page.tsx
- [X] T024 [US1] Create SignupForm client component in frontend/components/SignupForm.tsx (name, email, password, confirm password fields)
- [X] T025 [US1] Implement frontend validation in SignupForm (password min 8 chars, emails match, required fields)
- [X] T026 [US1] Implement signup API call in SignupForm (POST /api/auth/signup)
- [X] T027 [US1] Handle signup errors in SignupForm (display error messages for 409 duplicate email, 400 validation)
- [X] T028 [US1] Store JWT token after successful signup (localStorage or cookie)
- [X] T029 [US1] Redirect to /dashboard after successful signup

**Manual Test Checklist**:
1. Navigate to /signup
2. Enter valid email, password (8+ chars), name → User created, JWT issued, redirected to dashboard
3. Try to signup with existing email → See "Email already registered" error
4. Try signup with password < 8 chars → See validation error

---

## Phase 4: User Story 2 - User Login (P1)

**Goal**: Enable existing users to log in and access their data

**Independent Test**: Login with valid credentials → JWT issued → Redirect to dashboard with existing tasks visible

**Story Tasks**:

### Backend (US2)

- [X] T030 [US2] Create login endpoint POST /api/auth/login in backend/src/routes/auth.py (verify credentials, issue JWT)
- [X] T031 [US2] Add Pydantic request model for login in backend/src/routes/auth.py (LoginRequest with email, password)
- [X] T032 [US2] Implement password verification using passlib in backend/src/routes/auth.py
- [X] T033 [US2] Handle invalid credentials error (HTTP 401) in login endpoint

### Frontend (US2)

- [X] T034 [US2] Create login page component in frontend/app/login/page.tsx
- [X] T035 [US2] Create LoginForm client component in frontend/components/LoginForm.tsx (email, password fields)
- [X] T036 [US2] Implement frontend validation in LoginForm (required fields, email format)
- [X] T037 [US2] Implement login API call in LoginForm (POST /api/auth/login)
- [X] T038 [US2] Handle login errors in LoginForm (display "Invalid credentials" for 401)
- [X] T039 [US2] Store JWT token after successful login
- [X] T040 [US2] Redirect to /dashboard after successful login

### Protected Routes (US2)

- [X] T041 [US2] Create dashboard page in frontend/app/dashboard/page.tsx with authentication check
- [X] T042 [US2] Implement redirect to /login for unauthenticated users in dashboard page
- [X] T043 [US2] Handle JWT token expiry (redirect to /login with "Session expired" message)

**Manual Test Checklist**:
1. Navigate to /login
2. Enter valid credentials → JWT issued, redirected to dashboard
3. Enter incorrect password → See "Invalid credentials" error
4. Try to access /dashboard without login → Redirected to /login
5. After login, refresh page → Remain logged in (token persists)

---

## Phase 5: User Story 3 - Create New Task (P2)

**Goal**: Enable logged-in users to create new tasks

**Independent Test**: Login → Click "Add Task" → Enter title and description → Task created with user_id → Appears in list

**Story Tasks**:

### Backend (US3)

- [X] T044 [US3] Create POST /api/{user_id}/tasks endpoint in backend/src/routes/tasks.py (create task for user)
- [X] T045 [US3] Add Pydantic request model CreateTaskRequest in backend/src/routes/tasks.py (title 1-200 chars, description max 1000 chars)
- [X] T046 [US3] Implement JWT middleware dependency on tasks router in backend/src/routes/tasks.py
- [X] T047 [US3] Validate user_id in URL matches authenticated user_id from JWT token (return 403 if mismatch)
- [X] T048 [US3] Create Task record in database with auto-generated id, user_id, timestamps
- [X] T049 [US3] Return created task with HTTP 201 status

### Frontend (US3)

- [X] T050 [US3] Create AddTaskForm client component in frontend/components/AddTaskForm.tsx (title, description fields)
- [X] T051 [US3] Implement frontend validation in AddTaskForm (title required, max 200 chars; description max 1000 chars)
- [X] T052 [US3] Implement createTask API call with JWT in Authorization header
- [X] T053 [US3] Handle validation errors (HTTP 400) in AddTaskForm (display inline error messages)
- [X] T054 [US3] Clear form after successful task creation
- [X] T055 [US3] Refresh task list after successful creation (revalidate or optimistic update)

**Manual Test Checklist**:
1. Login and navigate to dashboard
2. Enter task title "Buy groceries" → Task created, appears in list
3. Try to create task with 201-char title → See validation error
4. Create task without description → Task created with null description
5. Verify task has correct user_id in database

---

## Phase 6: User Story 4 - View Task List (P2)

**Goal**: Enable users to view all their tasks

**Independent Test**: Login → Dashboard shows only user's tasks → Ordered by creation date (newest first) → Empty state if no tasks

**Story Tasks**:

### Backend (US4)

- [X] T056 [US4] Create GET /api/{user_id}/tasks endpoint in backend/src/routes/tasks.py (list all user's tasks)
- [X] T057 [US4] Filter tasks by authenticated user_id (WHERE user_id = ?)
- [X] T058 [US4] Order tasks by created_at DESC (newest first)
- [X] T059 [US4] Add optional query parameter ?status=all|pending|completed for filtering
- [X] T060 [US4] Return task array with HTTP 200 status

### Frontend (US4)

- [X] T061 [US4] Create TaskList server component in frontend/components/TaskList.tsx (fetch and display tasks)
- [X] T062 [US4] Implement fetchTasks API call with JWT in Authorization header
- [X] T063 [US4] Create TaskItem client component in frontend/components/TaskItem.tsx (display single task)
- [X] T064 [US4] Display task title, description, completion status, created date in TaskItem
- [X] T065 [US4] Create EmptyState component for when user has no tasks
- [X] T066 [US4] Add TaskList to dashboard page (include AddTaskForm above list)

### Data Isolation Testing (US4)

- [X] T067 [US4] Create second user account and add tasks
- [X] T068 [US4] Verify User A only sees User A's tasks (not User B's tasks)

**Manual Test Checklist**:
1. Login and view dashboard
2. If tasks exist → See all tasks ordered by date (newest first)
3. If no tasks → See "No tasks yet. Create your first task!" message
4. Create 5 tasks → All 5 appear in list
5. Login as different user → See only that user's tasks

---

## Phase 7: User Story 5 - Mark Task Complete/Incomplete (P2)

**Goal**: Enable users to toggle task completion status

**Independent Test**: Create task → Click checkbox → Task marked complete (strikethrough) → Click again → Marked incomplete → Status persists on refresh

**Story Tasks**:

### Backend (US5)

- [X] T069 [US5] Create PATCH /api/{user_id}/tasks/{task_id}/complete endpoint in backend/src/routes/tasks.py (toggle completion)
- [X] T070 [US5] Get task from database and verify ownership (user_id matches authenticated user)
- [X] T071 [US5] Toggle task.completed (true ↔ false) and update task.updated_at timestamp
- [X] T072 [US5] Return updated task with HTTP 200 status
- [X] T073 [US5] Return HTTP 404 if task not found or doesn't belong to user

### Frontend (US5)

- [X] T074 [US5] Add checkbox input to TaskItem component
- [X] T075 [US5] Implement toggleTask API call (PATCH endpoint)
- [X] T076 [US5] Update local state optimistically when checkbox clicked
- [X] T077 [US5] Apply strikethrough styling (line-through text-gray-500) for completed tasks
- [X] T078 [US5] Handle toggle errors (revert optimistic update on error)
- [X] T079 [US5] Revalidate task list after toggle to ensure consistency

**Manual Test Checklist**:
1. Create uncompleted task
2. Click checkbox → Task shows strikethrough, checkbox checked
3. Click checkbox again → Strikethrough removed, checkbox unchecked
4. Toggle task, then refresh page → Status persists correctly
5. Verify updated_at timestamp changes in database

---

## Phase 8: User Story 6 - Update Task Details (P3)

**Goal**: Enable users to edit task title and description

**Independent Test**: Create task → Click "Edit" → Change title/description → Save → Changes persist → updated_at timestamp updated

**Story Tasks**:

### Backend (US6)

- [X] T080 [US6] Create PUT /api/{user_id}/tasks/{task_id} endpoint in backend/src/routes/tasks.py (update task)
- [X] T081 [US6] Add Pydantic request model UpdateTaskRequest (optional title, optional description)
- [X] T082 [US6] Get task from database and verify ownership
- [X] T083 [US6] Update task fields (title and/or description) and updated_at timestamp
- [X] T084 [US6] Validate title length (1-200 chars) and description length (max 1000 chars)
- [X] T085 [US6] Return updated task with HTTP 200 status
- [X] T086 [US6] Return HTTP 404 if task not found, HTTP 400 for validation errors

### Frontend (US6)

- [X] T087 [US6] Create EditTaskModal client component in frontend/components/EditTaskModal.tsx
- [X] T088 [US6] Create Modal shared component in frontend/components/ui/Modal.tsx (overlay, close on Escape)
- [X] T089 [US6] Add "Edit" button to TaskItem component
- [X] T090 [US6] Pre-fill form fields with current task data in EditTaskModal
- [X] T091 [US6] Implement frontend validation (same as AddTaskForm)
- [X] T092 [US6] Implement updateTask API call (PUT endpoint)
- [X] T093 [US6] Handle validation errors (HTTP 400) and display inline error messages
- [X] T094 [US6] Close modal and refresh task list after successful update
- [X] T095 [US6] Add "Cancel" button to close modal without saving

**Manual Test Checklist**:
1. Create task "Buy groceries"
2. Click "Edit" → Modal opens with pre-filled data
3. Change title to "Buy organic groceries" → Save → Title updates in list
4. Try to save with empty title → See "Title is required" error
5. Verify updated_at timestamp changes in database
6. Click "Cancel" → Modal closes without saving changes

---

## Phase 9: User Story 7 - Delete Task (P3)

**Goal**: Enable users to permanently delete tasks

**Independent Test**: Create task → Click "Delete" → Confirm → Task removed from database and UI

**Story Tasks**:

### Backend (US7)

- [X] T096 [US7] Create DELETE /api/{user_id}/tasks/{task_id} endpoint in backend/src/routes/tasks.py (delete task)
- [X] T097 [US7] Get task from database and verify ownership
- [X] T098 [US7] Delete task from database (permanent deletion, no soft delete)
- [X] T099 [US7] Return success message with task ID, HTTP 200 status
- [X] T100 [US7] Return HTTP 404 if task not found or doesn't belong to user

### Frontend (US7)

- [X] T101 [US7] Add "Delete" button to TaskItem component
- [X] T102 [US7] Create confirmation modal or use window.confirm for delete confirmation
- [X] T103 [US7] Implement deleteTask API call (DELETE endpoint)
- [X] T104 [US7] Remove task from UI immediately after successful deletion
- [X] T105 [US7] Handle delete errors (show error message if deletion fails)
- [X] T106 [US7] Add "Cancel" option in confirmation to abort deletion

**Manual Test Checklist**:
1. Create task
2. Click "Delete" → See confirmation modal/dialog
3. Click "Confirm" → Task removed from list and database
4. Click "Delete" then "Cancel" → Task remains in list
5. Verify task is permanently deleted from database (not soft deleted)

---

## Phase 10: User Story 8 - User Logout (P3)

**Goal**: Enable users to log out and clear their session

**Independent Test**: Login → Click "Logout" → JWT removed from storage → Redirected to login → Cannot access dashboard without re-login

**Story Tasks**:

### Frontend (US8)

- [X] T107 [US8] Create LogoutButton client component in frontend/components/LogoutButton.tsx
- [X] T108 [US8] Implement logout function (remove JWT from localStorage/cookie)
- [X] T109 [US8] Call Better Auth signOut function
- [X] T110 [US8] Redirect to /login after logout
- [X] T111 [US8] Create Header server component in frontend/components/Header.tsx (show user name and logout button)
- [X] T112 [US8] Add Header to root layout (frontend/app/layout.tsx)
- [X] T113 [US8] Show "Login/Signup" links in Header when user not authenticated
- [X] T114 [US8] Show user name and logout button in Header when user authenticated

**Manual Test Checklist**:
1. Login to account
2. See user name displayed in header
3. Click "Logout" button → JWT removed, redirected to /login
4. Try to access /dashboard → Redirected back to /login
5. Try API request without token → Receive HTTP 401 Unauthorized

---

## Phase 11: Shared Components & Polish

**Goal**: Implement reusable UI components and polish user experience

**Tasks**:

### Shared UI Components

- [X] T115 Create Button component in frontend/components/ui/Button.tsx (variant: primary|secondary|danger, size: sm|md|lg)
- [X] T116 Create Input component in frontend/components/ui/Input.tsx (label, error message, validation states)
- [X] T117 Create Loading component in frontend/components/ui/Loading.tsx (spinner or skeleton loader)
- [X] T118 Create loading.tsx for dashboard in frontend/app/dashboard/loading.tsx (skeleton for task list)

### Error Handling & UX

- [X] T119 Create error.tsx for dashboard in frontend/app/dashboard/error.tsx (user-friendly error boundary)
- [X] T120 Add loading states to all forms (disable submit button, show "Loading..." text)
- [X] T121 Add success feedback for create/update/delete actions (toast notification or inline message)
- [X] T122 Implement optimistic UI updates for task operations (immediate feedback before server response)

### API Error Handling

- [X] T123 Handle 401 errors globally in API client (auto-redirect to /login)
- [X] T124 Handle 403 errors in API client (show "Unauthorized" message)
- [X] T125 Handle 500 errors in API client (show "Service temporarily unavailable" message)
- [X] T126 Handle network errors in API client (show "Network error, please try again" message)

### Backend Enhancements

- [X] T127 Add GET /api/{user_id}/tasks/{task_id} endpoint in backend/src/routes/tasks.py (get single task)
- [X] T128 Add request logging middleware in backend/src/main.py (log all API requests with timestamp, method, path)
- [X] T129 Configure CORS with specific origins in backend/src/main.py (not wildcard *)
- [X] T130 Add database indexes to tasks table (CREATE INDEX idx_tasks_user_id, idx_tasks_completed)

### Home Page

- [X] T131 Create home page in frontend/app/page.tsx (redirect to /dashboard if authenticated, else /login)

**Manual Test Checklist**:
1. All forms show loading states during submission
2. Success messages appear after create/update/delete
3. Error messages are user-friendly (no stack traces)
4. Loading skeletons appear while data fetches
5. Optimistic updates work (immediate feedback)

---

## Dependencies & Execution Strategy

### User Story Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundation)
    ↓
┌───────────────────────┬───────────────────────┐
│ Phase 3: US1 (Signup) │ Phase 4: US2 (Login)  │ ← P1 (Must complete first)
└───────────────────────┴───────────────────────┘
              ↓
┌──────────────┬──────────────┬──────────────────┐
│ Phase 5: US3 │ Phase 6: US4 │ Phase 7: US5     │ ← P2 (Depend on P1)
│ (Create)     │ (View)       │ (Mark Complete)  │
└──────────────┴──────────────┴──────────────────┘
              ↓
┌──────────────┬──────────────┬──────────────────┐
│ Phase 8: US6 │ Phase 9: US7 │ Phase 10: US8    │ ← P3 (Optional enhancements)
│ (Update)     │ (Delete)     │ (Logout)         │
└──────────────┴──────────────┴──────────────────┘
              ↓
       Phase 11 (Polish)
```

### Parallel Execution Opportunities

**Within Phase 2 (Foundation)**:
- T008-T009 (Models) can run in parallel
- T013-T014 (Frontend types/API) can run after models but parallel to each other
- T015-T017 (Frontend config) can run in parallel

**Within Phase 3 (US1 - Signup)**:
- T023-T029 (Frontend signup) can run in parallel with T018-T022 (Backend signup) if API contract is agreed

**Within Phase 4 (US2 - Login)**:
- T034-T040 (Frontend login) can run in parallel with T030-T033 (Backend login)

**Within Phase 5 (US3 - Create Task)**:
- T050-T055 (Frontend) can run in parallel with T044-T049 (Backend)

**Across P2 User Stories**:
- US3 (Create), US4 (View), US5 (Mark Complete) are mostly independent and can be developed in parallel by different developers

**Across P3 User Stories**:
- US6 (Update), US7 (Delete), US8 (Logout) are fully independent and can be developed in parallel

### MVP Scope (Minimum Viable Product)

**MVP = Phase 1 + Phase 2 + Phase 3 + Phase 4 + Phase 5 + Phase 6**

This provides:
- User signup and login (authentication)
- Create new tasks
- View task list
- Basic user experience

This is the minimum to deliver "working todo app with multi-user support."

### Incremental Delivery Strategy

1. **Sprint 1** (MVP): Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
   - Deliverable: Users can signup, login, create tasks, view tasks
   - **Independent Test**: Create account → Add 3 tasks → See tasks in list

2. **Sprint 2** (Core Features): Phase 7
   - Deliverable: Users can mark tasks complete
   - **Independent Test**: Mark task complete → See strikethrough → Persists on refresh

3. **Sprint 3** (Enhancements): Phase 8 → Phase 9 → Phase 10
   - Deliverable: Edit, delete, logout functionality
   - **Independent Test**: Edit task → Delete task → Logout

4. **Sprint 4** (Polish): Phase 11
   - Deliverable: Improved UX, shared components, error handling
   - **Independent Test**: All user flows work smoothly with good UX

---

## Task Summary

**Total Tasks**: 131 tasks

**Task Breakdown by Phase**:
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundation): 10 tasks (5 backend, 5 frontend)
- Phase 3 (US1 - Signup): 12 tasks (5 backend, 7 frontend)
- Phase 4 (US2 - Login): 14 tasks (4 backend, 7 frontend, 3 protected routes)
- Phase 5 (US3 - Create): 12 tasks (6 backend, 6 frontend)
- Phase 6 (US4 - View): 13 tasks (5 backend, 6 frontend, 2 data isolation tests)
- Phase 7 (US5 - Mark Complete): 11 tasks (5 backend, 6 frontend)
- Phase 8 (US6 - Update): 16 tasks (7 backend, 9 frontend)
- Phase 9 (US7 - Delete): 11 tasks (5 backend, 6 frontend)
- Phase 10 (US8 - Logout): 8 tasks (0 backend, 8 frontend)
- Phase 11 (Polish): 17 tasks (4 backend, 13 frontend/UX)

**Parallelizable Tasks**: 21 tasks marked with [P]

**MVP Task Count**: 68 tasks (Phases 1-6)

---

## Format Validation

✅ All tasks follow required checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
✅ Task IDs sequential (T001 to T131)
✅ User story labels present for story-specific tasks ([US1] to [US8])
✅ Parallel markers [P] present where appropriate
✅ File paths specified in task descriptions
✅ Tasks organized by user story priority

---

## Implementation Notes

1. **Start with MVP**: Focus on Phases 1-6 first to deliver core value quickly
2. **Test Incrementally**: After each phase, run manual test checklist to verify functionality
3. **Use Validation Checklist**: Reference specs/002-todo-web-app/checklists/requirements.md throughout implementation
4. **Follow Guidelines**: Refer to backend/CLAUDE.md and frontend/CLAUDE.md for coding patterns
5. **Independent Testing**: Each user story phase can be tested independently using the "Independent Test" criteria
6. **Parallel Development**: Tasks marked [P] can be worked on simultaneously if multiple developers available
7. **Create PHRs**: Document implementation sessions in history/prompts/002-todo-web-app/

---

## Phase 12: Production Deployment

**Goal**: Deploy backend to Railway.app and frontend to Vercel for production access

**Tasks**:

### Backend Deployment to Railway.app

- [X] T132 [DEPLOY] Create Railway.app account and new project for backend
- [X] T133 [DEPLOY] Connect Railway project to GitHub repository (002-todo-web-app branch)
- [X] T134 [DEPLOY] Configure Railway to deploy from backend/ directory (railway.json configured)
- [X] T135 [DEPLOY] Add environment variables to Railway project (DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS)
- [ ] T136 [DEPLOY] Update CORS_ORIGINS to include Vercel frontend URL (https://*.vercel.app)
- [X] T137 [DEPLOY] Configure Nixpacks for Python 3.13+ with UV package manager (backend/railway.json)
- [X] T138 [DEPLOY] Set Railway start command (uvicorn src.main:app --host 0.0.0.0 --port $PORT)
- [X] T139 [DEPLOY] Verify Railway deployment succeeds and health endpoint returns 200 OK
- [ ] T140 [DEPLOY] Test Railway backend URL with Postman or curl (GET /health)
- [ ] T141 [DEPLOY] Document Railway backend URL in deployment docs

### Frontend Deployment to Vercel

- [ ] T142 [DEPLOY] Create Vercel account and import GitHub repository
- [ ] T143 [DEPLOY] Configure Vercel project settings (Framework: Next.js, Root Directory: frontend/)
- [ ] T144 [DEPLOY] Add environment variables to Vercel project settings:
  - NEXT_PUBLIC_API_URL (Railway backend URL from T141)
  - BETTER_AUTH_SECRET (same value as backend)
  - BETTER_AUTH_URL (Vercel deployment URL, will be auto-assigned)
- [X] T145 [DEPLOY] Fix frontend/vercel.json schema validation errors (removed invalid env config - commit ee00c9c)
- [X] T146 [DEPLOY] Fix frontend/tsconfig.json jsx setting (changed to "preserve" - commit 96293e5)
- [ ] T147 [DEPLOY] Trigger Vercel deployment and monitor build logs
- [ ] T148 [DEPLOY] Verify Vercel build completes successfully without errors
- [ ] T149 [DEPLOY] Test Vercel frontend URL in browser (verify login/signup pages load)
- [ ] T150 [DEPLOY] Update BETTER_AUTH_URL in Vercel environment variables with actual deployment URL

### Integration Testing (Production Environment)

- [ ] T151 [DEPLOY] Test signup flow on production (create new account → JWT issued → redirected to dashboard)
- [ ] T152 [DEPLOY] Test login flow on production (login with credentials → access dashboard)
- [ ] T153 [DEPLOY] Test create task on production (add task → verify in database → appears in list)
- [ ] T154 [DEPLOY] Test mark complete on production (toggle checkbox → status persists)
- [ ] T155 [DEPLOY] Test edit task on production (update title/description → changes persist)
- [ ] T156 [DEPLOY] Test delete task on production (delete task → removed from database)
- [ ] T157 [DEPLOY] Test logout on production (logout → JWT removed → cannot access dashboard)
- [ ] T158 [DEPLOY] Test multi-user isolation on production (User A cannot see User B's tasks)
- [ ] T159 [DEPLOY] Verify CORS allows frontend to call backend (no CORS errors in browser console)
- [ ] T160 [DEPLOY] Test on mobile devices (responsive design works correctly)

### Deployment Documentation

- [X] T161 [DEPLOY] Create deployment guide in specs/002-todo-web-app/deployment.md
- [X] T162 [DEPLOY] Document Railway deployment steps (account setup, env vars, configuration)
- [X] T163 [DEPLOY] Document Vercel deployment steps (account setup, env vars, build settings)
- [X] T164 [DEPLOY] Document environment variable requirements and how to obtain values
- [X] T165 [DEPLOY] Add troubleshooting section for common deployment issues
- [ ] T166 [DEPLOY] Update README.md with production URLs and deployment status
- [X] T167 [DEPLOY] Create deployment checklist in specs/002-todo-web-app/checklists/deployment.md

### Monitoring & Maintenance

- [ ] T168 [DEPLOY] Set up Railway deployment notifications (email or Slack)
- [ ] T169 [DEPLOY] Set up Vercel deployment notifications
- [X] T170 [DEPLOY] Configure automatic deployments from GitHub (Railway and Vercel auto-deploy on push)
- [ ] T171 [DEPLOY] Test rollback procedure (revert to previous deployment if issues occur)
- [X] T172 [DEPLOY] Document how to view Railway logs for debugging (documented in deployment.md)
- [X] T173 [DEPLOY] Document how to view Vercel build logs for debugging (documented in deployment.md)

**Acceptance**:
- Backend deployed to Railway.app with public URL
- Frontend deployed to Vercel with public URL
- All 8 user stories work correctly in production
- Environment variables configured correctly
- CORS configured to allow frontend-backend communication
- Deployment documentation complete

**Manual Test Checklist**:
1. Visit Vercel frontend URL → See login page
2. Create new account → Account created, redirected to dashboard
3. Add 3 tasks → All tasks appear in list
4. Mark task complete → Checkbox updates, strikethrough applied
5. Edit task → Changes persist
6. Delete task → Task removed
7. Logout → Redirected to login, cannot access dashboard
8. Login again → Previous tasks still visible
9. Create second user → Cannot see first user's tasks
10. Test on mobile device → Responsive design works

---

## Updated Dependencies & Execution Strategy

### Extended User Story Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundation)
    ↓
┌───────────────────────┬───────────────────────┐
│ Phase 3: US1 (Signup) │ Phase 4: US2 (Login)  │ ← P1 (Must complete first)
└───────────────────────┴───────────────────────┘
              ↓
┌──────────────┬──────────────┬──────────────────┐
│ Phase 5: US3 │ Phase 6: US4 │ Phase 7: US5     │ ← P2 (Depend on P1)
│ (Create)     │ (View)       │ (Mark Complete)  │
└──────────────┴──────────────┴──────────────────┘
              ↓
┌──────────────┬──────────────┬──────────────────┐
│ Phase 8: US6 │ Phase 9: US7 │ Phase 10: US8    │ ← P3 (Optional enhancements)
│ (Update)     │ (Delete)     │ (Logout)         │
└──────────────┴──────────────┴──────────────────┘
              ↓
       Phase 11 (Polish)
              ↓
       Phase 12 (Deployment) ← Production release
```

### Updated Incremental Delivery Strategy

1. **Sprint 1** (MVP): Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
   - Deliverable: Users can signup, login, create tasks, view tasks
   - **Independent Test**: Create account → Add 3 tasks → See tasks in list

2. **Sprint 2** (Core Features): Phase 7
   - Deliverable: Users can mark tasks complete
   - **Independent Test**: Mark task complete → See strikethrough → Persists on refresh

3. **Sprint 3** (Enhancements): Phase 8 → Phase 9 → Phase 10
   - Deliverable: Edit, delete, logout functionality
   - **Independent Test**: Edit task → Delete task → Logout

4. **Sprint 4** (Polish): Phase 11
   - Deliverable: Improved UX, shared components, error handling
   - **Independent Test**: All user flows work smoothly with good UX

5. **Sprint 5** (Production Deployment): Phase 12
   - Deliverable: App live on Railway.app (backend) + Vercel (frontend)
   - **Independent Test**: Full user flow works on production URLs
   - **Public URL**: https://your-app.vercel.app

---

## Updated Task Summary

**Total Tasks**: 173 tasks (was 131, added 42 deployment tasks)

**Task Breakdown by Phase**:
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundation): 10 tasks (5 backend, 5 frontend)
- Phase 3 (US1 - Signup): 12 tasks (5 backend, 7 frontend)
- Phase 4 (US2 - Login): 14 tasks (4 backend, 7 frontend, 3 protected routes)
- Phase 5 (US3 - Create): 12 tasks (6 backend, 6 frontend)
- Phase 6 (US4 - View): 13 tasks (5 backend, 6 frontend, 2 data isolation tests)
- Phase 7 (US5 - Mark Complete): 11 tasks (5 backend, 6 frontend)
- Phase 8 (US6 - Update): 16 tasks (7 backend, 9 frontend)
- Phase 9 (US7 - Delete): 11 tasks (5 backend, 6 frontend)
- Phase 10 (US8 - Logout): 8 tasks (0 backend, 8 frontend)
- Phase 11 (Polish): 17 tasks (4 backend, 13 frontend/UX)
- **Phase 12 (Deployment): 42 tasks (10 Railway, 9 Vercel, 10 integration tests, 7 docs, 6 monitoring)**

**Parallelizable Tasks**: 21 tasks marked with [P]

**MVP Task Count**: 68 tasks (Phases 1-6)

**Production-Ready Task Count**: 173 tasks (All phases including deployment)

---

## Format Validation

✅ All tasks follow required checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
✅ Task IDs sequential (T001 to T173)
✅ User story labels present for story-specific tasks ([US1] to [US8])
✅ Deployment labels present for deployment tasks ([DEPLOY])
✅ Parallel markers [P] present where appropriate
✅ File paths specified in task descriptions where applicable
✅ Tasks organized by user story priority and deployment stages

---

## Implementation Notes

1. **Start with MVP**: Focus on Phases 1-6 first to deliver core value quickly
2. **Test Incrementally**: After each phase, run manual test checklist to verify functionality
3. **Use Validation Checklist**: Reference specs/002-todo-web-app/checklists/requirements.md throughout implementation
4. **Follow Guidelines**: Refer to backend/CLAUDE.md and frontend/CLAUDE.md for coding patterns
5. **Independent Testing**: Each user story phase can be tested independently using the "Independent Test" criteria
6. **Parallel Development**: Tasks marked [P] can be worked on simultaneously if multiple developers available
7. **Create PHRs**: Document implementation sessions in history/prompts/002-todo-web-app/
8. **Deployment Best Practices**:
   - Test locally before deploying to production
   - Keep environment variables secure (never commit .env files)
   - Monitor deployment logs for errors
   - Test all user flows in production after deployment
   - Document deployment URLs for team reference

---

**Ready to deploy!** All implementation phases (1-11) are complete. Now proceed with Phase 12 (Deployment) to make the app publicly accessible.
