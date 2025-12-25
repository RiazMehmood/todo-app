---
description: "Actionable tasks for implementing intermediate & advanced features"
---

# Tasks: Intermediate & Advanced Features

**Input**: Design documents from `/specs/005-cloud-native-deployment/`
**Prerequisites**: plan.md, intermediate-advanced-features.md (spec), research.md, data-model.md, contracts/

**Tests**: Manual end-to-end testing (automated tests optional per constitution)

**Organization**: Tasks organized by user story to enable independent implementation and testing of each feature set.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/`
- **Database**: `backend/migrations/`
- **Documentation**: `docs/`, `specs/005-cloud-native-deployment/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [X] T001 Verify Python 3.13+ and Node.js 18+ installed on development system
- [X] T002 Install backend dependencies: redis, reportlab, matplotlib in backend/pyproject.toml
- [X] T003 [P] Install frontend dependencies: chart.js or recharts in frontend/package.json
- [X] T004 [P] Verify PostgreSQL 14+ supports full-text search and JSONB (check version)

**Checkpoint**: Development environment ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database schema, search indexes, and Redis infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Migrations

- [X] T005 Create migration 006_add_search_vector.sql: Add search_vector column to tasks table with GIN index
- [X] T006 [P] Create migration 007_add_saved_searches.sql: Create saved_searches table with JSONB query_params
- [X] T007 [P] Create migration 008_add_task_templates.sql: Create task_templates table with JSONB tasks_definition
- [X] T008 [P] Create migration 009_add_time_entries.sql: Create time_entries table with auto-calculation trigger
- [X] T009 Run all database migrations against Neon PostgreSQL instance

### Infrastructure Setup

- [X] T010 Configure Redis connection in backend/src/config.py (for WebSocket pub/sub and presence)
- [X] T011 Create Redis client singleton in backend/src/infrastructure/redis_client.py
- [X] T012 [P] Update backend/src/main.py to register new route modules (search, templates, bulk_operations, websocket, analytics)
- [X] T013 [P] Create environment variables in backend/.env for Redis, WebSocket, bulk operation limits

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Advanced Search & Filtering (Priority: P1) 🎯 MVP

**Goal**: Enable full-text search across tasks with boolean operators, multi-criteria filtering, and saved searches

**Independent Test**: Create 100+ tasks with diverse tags/priorities/dates, execute complex search (e.g., "meeting urgent" + priority=high + created_after=2025-12-01), verify results accurate and returned in <500ms

### Backend Models & Services

- [X] T014 [P] [US1] Create SavedSearch model in backend/src/models/saved_search.py with JSONB query_params field
- [X] T015 [US1] Implement SearchService in backend/src/services/search_service.py with full-text query builder using ts_vector
- [X] T016 [US1] Add boolean operator parsing (AND, OR, NOT) to SearchService.build_query() method
- [X] T017 [US1] Add relevance ranking using ts_rank() for search results ordering

### Backend API Endpoints

- [X] T018 [US1] Implement POST /api/{user_id}/tasks/search endpoint in backend/src/routes/search.py with pagination
- [X] T019 [P] [US1] Implement GET /api/{user_id}/saved-searches endpoint in backend/src/routes/search.py
- [X] T020 [P] [US1] Implement POST /api/{user_id}/saved-searches endpoint for creating saved searches
- [X] T021 [P] [US1] Implement DELETE /api/{user_id}/saved-searches/{search_id} endpoint
- [X] T022 [US1] Add input sanitization and SQL injection prevention in search query parsing
- [X] T023 [US1] Add date range filter support (last_7_days, last_30_days, custom_range) in SearchService

### Frontend Components & Pages

- [X] T024 [US1] Create SearchBar component in frontend/components/SearchBar.tsx with autocomplete for tags
- [X] T025 [US1] Create FilterPanel component in frontend/components/FilterPanel.tsx with multi-select for status/priority/tags
- [X] T026 [US1] Create SavedSearches dropdown component in frontend/components/SavedSearches.tsx
- [X] T027 [US1] Create /search page in frontend/app/search/page.tsx integrating SearchBar, FilterPanel, and results display
- [X] T028 [US1] Add search term highlighting in task titles/descriptions in search results
- [X] T029 [US1] Implement save search dialog in frontend/components/SaveSearchDialog.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional - search works, filters apply, saved searches persist and execute

---

## Phase 4: User Story 2 - Templates & Bulk Operations (Priority: P1)

**Goal**: Enable creating reusable task templates with placeholders and performing bulk updates/deletes on multiple tasks

**Independent Test**: Create template "Client Onboarding" with 5 tasks and {{CLIENT_NAME}} placeholder, instantiate with CLIENT_NAME="Acme Corp", verify 5 tasks created with correct placeholders replaced. Then bulk-update all tasks tagged "sprint-1" to priority=high, verify all updated.

### Backend Models & Services (Templates)

- [X] T030 [P] [US2] Create TaskTemplate model in backend/src/models/task_template.py with JSONB tasks_definition and placeholders array
- [X] T031 [US2] Implement TemplateProcessor class in backend/src/services/template_service.py with detect_placeholders() method
- [X] T032 [US2] Implement replace_placeholders() method using regex for {{VARIABLE}} syntax
- [X] T033 [US2] Implement validate_template() method to enforce max 10 placeholders and max 50 tasks per template
- [X] T034 [US2] Implement instantiate_template() method with date offset calculation and transaction support

### Backend Models & Services (Bulk Operations)

- [X] T035 [US2] Implement bulk_update_tasks() method in backend/src/services/bulk_operations_service.py with item-level error tracking
- [X] T036 [US2] Implement bulk_delete_tasks() method with authorization check (verify user owns all tasks)
- [X] T037 [US2] Add detailed error response schema with success_count, failure_count, and per-task error messages

### Backend API Endpoints (Templates)

- [X] T038 [P] [US2] Implement GET /api/{user_id}/templates endpoint in backend/src/routes/templates.py
- [X] T039 [P] [US2] Implement POST /api/{user_id}/templates endpoint for creating templates
- [X] T040 [P] [US2] Implement PUT /api/{user_id}/templates/{template_id} endpoint for updating templates
- [X] T041 [P] [US2] Implement DELETE /api/{user_id}/templates/{template_id} endpoint
- [X] T042 [US2] Implement POST /api/{user_id}/templates/{template_id}/instantiate endpoint with placeholder validation

### Backend API Endpoints (Bulk Operations)

- [X] T043 [P] [US2] Implement POST /api/{user_id}/tasks/bulk-update endpoint in backend/src/routes/bulk_operations.py with 500 task limit
- [X] T044 [P] [US2] Implement POST /api/{user_id}/tasks/bulk-delete endpoint with confirmation requirement
- [X] T045 [US2] Add rate limiting to bulk operations endpoints (max 10 requests/minute per user)

### Frontend Components & Pages

- [X] T046 [US2] Create TemplateForm component in frontend/components/TemplateForm.tsx for creating/editing templates
- [X] T047 [US2] Create /templates page in frontend/app/templates/page.tsx for template management
- [X] T048 [US2] Create InstantiateTemplateDialog component in frontend/components/InstantiateTemplateDialog.tsx with placeholder input fields
- [X] T049 [US2] Create BulkActionsToolbar component in frontend/components/BulkActionsToolbar.tsx with checkboxes for task selection
- [X] T050 [US2] Add bulk operation progress indicator and detailed error display in frontend

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - templates instantiate correctly, bulk operations process with detailed error reporting

---

## Phase 5: User Story 3 - Real-Time Collaboration (Priority: P2)

**Goal**: Enable real-time task updates via WebSocket, presence tracking, and collaborative editing notifications

**Independent Test**: Open 2 browser windows (User A, User B), User A creates/updates task, User B sees update within 2 seconds without refresh. Presence indicators show both users online.

### Backend WebSocket Infrastructure

- [X] T051 [US3] Create ConnectionManager class in backend/src/services/websocket_service.py for managing active WebSocket connections
- [X] T052 [US3] Implement Redis pub/sub integration in ConnectionManager for multi-instance broadcasting
- [X] T053 [US3] Implement connect(), disconnect(), send_personal_message(), broadcast() methods in ConnectionManager
- [X] T054 [US3] Create WebSocket endpoint at /api/{user_id}/ws in backend/src/routes/websocket.py with JWT authentication
- [X] T055 [US3] Implement heartbeat message handling (every 10 seconds) with 30-second timeout

### Backend Presence Tracking

- [X] T056 [US3] Implement update_presence() function in backend/src/services/websocket_service.py using Redis with 30s TTL
- [X] T057 [US3] Implement get_active_users() function to retrieve presence data from Redis by task_id filter
- [X] T058 [US3] Add presence_update message type to WebSocket server for broadcasting user status changes

### Backend Event Broadcasting

- [X] T059 [US3] Create publish_task_event() function in backend/src/services/websocket_service.py for Redis pub/sub
- [X] T060 [US3] Integrate publish_task_event() into create_task(), update_task(), delete_task() methods to broadcast events
- [X] T061 [US3] Implement WebSocket message types: task_created, task_updated, task_deleted, presence_update, notification

### Frontend WebSocket Client

- [X] T062 [US3] Create WebSocketClient class in frontend/lib/websocket.ts with connect(), disconnect(), send() methods
- [X] T063 [US3] Implement automatic reconnection with exponential backoff (1s → 30s max delay)
- [X] T064 [US3] Implement heartbeat sender (every 10 seconds) with current task_id and status
- [X] T065 [US3] Create WebSocket event handlers for task_created, task_updated, task_deleted messages

### Frontend Real-Time UI

- [X] T066 [US3] Create PresenceIndicator component in frontend/components/PresenceIndicator.tsx showing active users with avatars
- [X] T067 [US3] Create NotificationToast component in frontend/components/NotificationToast.tsx for real-time notifications
- [X] T068 [US3] Implement optimistic UI updates in task list (immediate local update + rollback on error)
- [X] T069 [US3] Add visual indicators (animations, badges) for real-time updates in task list
- [X] T070 [US3] Add "User X is editing" presence indicator when viewing same task as another user

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - WebSocket updates propagate in <2 seconds, presence tracking works, conflicts notify users

---

## Phase 6: User Story 4 - Analytics & Reporting (Priority: P2)

**Goal**: Provide analytics dashboard with completion trends, task distribution charts, time tracking, and CSV/PDF export

**Independent Test**: Create 50 tasks over 30-day period with varied completion dates, view analytics dashboard showing completion trend chart, tasks by priority pie chart, export CSV report with all data, generate PDF report with charts

### Backend Models & Services (Analytics)

- [X] T071 [US4] Create TimeEntry model in backend/src/models/time_entry.py (already migrated in Phase 2)
- [X] T072 [US4] Implement AnalyticsService class in backend/src/services/analytics_service.py with calculate_metrics() method
- [X] T073 [US4] Implement get_completion_trend() method using PostgreSQL date aggregation queries
- [X] T074 [US4] Implement get_tasks_by_priority(), get_tasks_by_status(), get_tasks_by_tag() aggregation methods
- [X] T075 [US4] Add time tracking methods: start_timer(), stop_timer(), get_time_entries() in TimeService

### Backend Services (Export)

- [X] T076 [US4] Create ExportService class in backend/src/services/export_service.py for report generation
- [X] T077 [US4] Implement generate_csv_export() method with streaming for large datasets (>1000 tasks)
- [X] T078 [US4] Implement AnalyticsReportGenerator class using ReportLab for PDF generation
- [X] T079 [US4] Implement _generate_trend_chart() method using matplotlib to create line chart image
- [X] T080 [US4] Implement _generate_priority_chart() method to create pie chart for priority distribution

### Backend API Endpoints (Analytics)

- [X] T081 [US4] Implement GET /api/{user_id}/analytics/overview endpoint in backend/src/routes/analytics.py with date range filtering
- [X] T082 [P] [US4] Implement POST /api/{user_id}/time-entries endpoint for starting/stopping timers
- [X] T083 [P] [US4] Implement GET /api/{user_id}/time-entries endpoint with task_id filtering
- [X] T084 [US4] Implement GET /api/{user_id}/analytics/export endpoint with format=csv|pdf query parameter
- [X] T085 [US4] Add caching for analytics queries (5-minute TTL) to reduce database load

### Frontend Components & Pages (Analytics)

- [X] T086 [US4] Create AnalyticsChart component in frontend/components/AnalyticsChart.tsx using Chart.js/Recharts
- [X] T087 [US4] Create LineChart subcomponent for completion trends
- [X] T088 [US4] Create PieChart subcomponent for task distribution (priority, status)
- [X] T089 [US4] Create BarChart subcomponent for tasks by tag
- [X] T090 [US4] Create /analytics page in frontend/app/analytics/page.tsx with dashboard layout

### Frontend Components & Pages (Time Tracking)

- [X] T091 [US4] Create TimeTracker component in frontend/components/TimeTracker.tsx with start/stop button
- [X] T092 [US4] Implement elapsed time display with live countdown timer
- [X] T093 [US4] Add timer state persistence across page refreshes (store started_at in localStorage as backup)
- [X] T094 [US4] Integrate TimeTracker into task detail view

### Frontend Export Functionality

- [X] T095 [US4] Create ExportButton component in frontend/components/ExportButton.tsx with CSV/PDF options
- [X] T096 [US4] Implement file download handling for CSV and PDF responses
- [X] T097 [US4] Add loading indicator and progress tracking for large exports
- [X] T098 [US4] Add date range selector for analytics dashboard (last 7/30/90 days, quarter, year, custom)

**Checkpoint**: All 4 user stories should now be independently functional - Analytics dashboard displays charts, time tracking persists, CSV/PDF exports work

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, optimization, and final validation

### Performance Optimization

- [ ] T099 [P] Add database indexes for analytics queries (created_at, user_id, status) if not already present
- [ ] T100 [P] Optimize search queries with EXPLAIN ANALYZE and adjust GIN index configuration
- [ ] T101 [P] Add connection pooling for Redis to handle 100+ concurrent WebSocket connections
- [ ] T102 Run load testing: 100 concurrent WebSocket connections, 1000 tasks search, 100 tasks bulk update

### Security Hardening

- [ ] T103 [P] Verify SQL injection prevention in search queries (parameterized queries check)
- [ ] T104 [P] Verify JWT authentication on all WebSocket connections
- [ ] T105 [P] Verify user authorization checks in bulk operations (user can only modify own tasks)
- [ ] T106 Add rate limiting to search endpoints (100 requests/minute per user)

### Documentation & Validation

- [ ] T107 [P] Update quickstart.md with setup instructions for Redis, WebSocket testing, analytics usage
- [ ] T108 [P] Create API documentation for all new endpoints in docs/api-reference.md
- [ ] T109 [P] Update frontend README with component documentation
- [ ] T110 Verify all 4 user stories work independently by running test scenarios from spec
- [ ] T111 Run manual end-to-end test: Search → Template instantiation → Real-time updates → Analytics export

### Deployment Preparation

- [ ] T112 Create Kubernetes ConfigMap for WebSocket settings in k8s/configmaps/websocket-config.yaml
- [ ] T113 Create Kubernetes ConfigMap for analytics settings in k8s/configmaps/analytics-config.yaml
- [ ] T114 Update backend deployment to include Redis connection and increased memory (512MB → 1GB)
- [ ] T115 Deploy Redis to Kubernetes or configure external Redis connection
- [ ] T116 Update environment variables documentation in .env.example with all new variables

**Checkpoint**: System is production-ready with all 4 feature sets functional, documented, and deployed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories CAN proceed in parallel if staffed
  - Or sequentially in priority order: US1 (P1) → US2 (P1) → US3 (P2) → US4 (P2)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational - Integrates with US1/US2 for broadcasting events but independently testable
- **User Story 4 (P2)**: Can start after Foundational - Uses task data from US1/US2 but independently testable

### Within Each User Story

- Models before services (e.g., T014 before T015)
- Services before endpoints (e.g., T015 before T018)
- Backend endpoints before frontend components (e.g., T018 before T024)
- Core implementation before integration
- Story validation at checkpoint before moving to next priority

### Parallel Opportunities

**Phase 2 - Database Migrations**:
```bash
# Launch migration creation in parallel:
Task T006: "Create migration 007_add_saved_searches.sql"
Task T007: "Create migration 008_add_task_templates.sql"
Task T008: "Create migration 009_add_time_entries.sql"
```

**Phase 3 - User Story 1 Backend Endpoints**:
```bash
# Launch CRUD endpoints in parallel (different route handlers):
Task T019: "GET /api/{user_id}/saved-searches"
Task T020: "POST /api/{user_id}/saved-searches"
Task T021: "DELETE /api/{user_id}/saved-searches/{search_id}"
```

**Phase 4 - User Story 2 API Endpoints**:
```bash
# Launch template CRUD in parallel:
Task T038: "GET /api/{user_id}/templates"
Task T039: "POST /api/{user_id}/templates"
Task T040: "PUT /api/{user_id}/templates/{template_id}"
Task T041: "DELETE /api/{user_id}/templates/{template_id}"

# Launch bulk operations in parallel:
Task T043: "POST /api/{user_id}/tasks/bulk-update"
Task T044: "POST /api/{user_id}/tasks/bulk-delete"
```

**Phase 7 - Documentation & Hardening**:
```bash
# Launch all polish tasks in parallel:
Task T099: "Add database indexes"
Task T100: "Optimize search queries"
Task T101: "Add connection pooling"
Task T103: "Verify SQL injection prevention"
Task T104: "Verify JWT authentication"
Task T105: "Verify user authorization"
Task T107: "Update quickstart.md"
Task T108: "Create API documentation"
Task T109: "Update frontend README"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (install dependencies)
2. Complete Phase 2: Foundational (database migrations, Redis setup) - CRITICAL
3. Complete Phase 3: User Story 1 (Advanced Search & Filtering)
4. **STOP and VALIDATE**: Test search with 100+ tasks, verify <500ms response, test saved searches
5. Deploy/demo if ready - MVP is functional!

### Two P1 Stories (Search + Templates)

1. Complete Setup + Foundational → Foundation ready
2. Complete User Story 1 → Test independently → Deploy/Demo
3. Complete User Story 2 → Test independently → Deploy/Demo
4. System now has search AND templates - substantial value

### Full Feature Set

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (P1) → Test independently → Deploy
3. Add User Story 2 (P1) → Test independently → Deploy
4. Add User Story 3 (P2) → Test independently → Deploy
5. Add User Story 4 (P2) → Test independently → Deploy
6. Complete Polish → Production ready

### Parallel Team Strategy

With 4 developers after Foundational phase completes:

- Developer A: User Story 1 (Search)
- Developer B: User Story 2 (Templates)
- Developer C: User Story 3 (WebSocket)
- Developer D: User Story 4 (Analytics)

All stories complete in parallel, then integrate and polish together.

---

## Task Summary

**Total Tasks**: 116

**By Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 9 tasks (4 parallel migration creates)
- Phase 3 (User Story 1 - Search): 16 tasks (MVP target)
- Phase 4 (User Story 2 - Templates/Bulk): 21 tasks
- Phase 5 (User Story 3 - WebSocket): 20 tasks
- Phase 6 (User Story 4 - Analytics): 28 tasks
- Phase 7 (Polish): 18 tasks (10 parallel hardening/docs)

**Parallel Tasks**: 35 tasks marked [P]

**Critical Path**: Phase 1 → Phase 2 (Foundational - BLOCKS all stories) → User Story 1 (MVP) → User Story 2 → User Story 3 → User Story 4 → Polish

**MVP Scope**: Phases 1-3 (Setup + Foundational + User Story 1) = Advanced Search & Filtering functional

**P1 Scope**: Phases 1-4 (MVP + User Story 2) = Search + Templates/Bulk Operations

**Full Scope**: All phases = Complete intermediate & advanced feature set

**Estimated Time** (sequential implementation):
- Setup: 2-3 hours
- Foundational: 4-6 hours (database migrations, Redis setup)
- User Story 1: 2-3 days (search implementation)
- User Story 2: 2-3 days (templates and bulk operations)
- User Story 3: 3-4 days (WebSocket and real-time features)
- User Story 4: 3-4 days (analytics and reporting)
- Polish: 1-2 days (optimization, docs, deployment)
- **Total: 12-17 days** (matches plan.md estimate)

---

## Notes

- [P] tasks = different files, no dependencies between them
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are manual end-to-end tests per constitution (no automated test tasks)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Redis is required for User Story 3 (WebSocket) but can be skipped if only implementing US1/US2
- PostgreSQL full-text search requires GIN index (Phase 2, T005) before search works
- All bulk operations enforce 500 task limit to prevent server overload
- WebSocket requires sticky sessions in Kubernetes load balancer for multi-instance deployments
- Analytics caching (T085) reduces database load but requires cache invalidation on task updates

**Success Criteria**: When all 4 user story checkpoints pass, the intermediate & advanced feature set is complete and production-ready.

---

## Quick Reference: Feature Dependencies

```
Foundational Phase (MUST complete first)
    ├── Database migrations (tasks, saved_searches, task_templates, time_entries)
    ├── Search vector & GIN index on tasks table
    └── Redis connection configured

User Story 1 (Advanced Search) - Independent
    ├── Depends on: search_vector column & GIN index
    └── Delivers: Full-text search, filters, saved searches

User Story 2 (Templates/Bulk) - Independent
    ├── Depends on: task_templates table, existing task service
    └── Delivers: Template instantiation, bulk update/delete

User Story 3 (Real-Time) - Integrates with US1/US2
    ├── Depends on: Redis pub/sub
    ├── Integrates: Broadcasts events from US1/US2 task operations
    └── Delivers: WebSocket updates, presence tracking

User Story 4 (Analytics) - Consumes data from US1/US2
    ├── Depends on: time_entries table, task completion data
    ├── Uses: Task data created/updated via US1/US2
    └── Delivers: Dashboard charts, time tracking, CSV/PDF export
```

Each user story delivers value independently. Real-time updates (US3) enhance US1/US2 experience but aren't required for core functionality.
