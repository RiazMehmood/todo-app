# Implementation Plan: Intermediate & Advanced Features

**Branch**: `005-cloud-native-deployment` | **Date**: 2025-12-23 | **Spec**: [intermediate-advanced-features.md](./intermediate-advanced-features.md)
**Input**: User request for advanced search/filtering, task templates/bulk operations, real-time collaboration, and analytics/reporting features

## Summary

This plan implements four major feature sets to transform the Todo application into a professional-grade task management platform:

1. **Advanced Search & Filtering**: Full-text search with boolean operators, multi-criteria filtering, and saved searches (P1)
2. **Task Templates & Bulk Operations**: Reusable task templates with placeholders and bulk update/delete operations (P1)
3. **Real-Time Collaboration**: WebSocket-based live updates, presence indicators, and collaborative editing (P2)
4. **Analytics & Reporting**: Dashboard with charts, time tracking, and CSV/PDF export capabilities (P2)

**Technical Approach**: Extend existing PostgreSQL schema with new tables (SavedSearch, TaskTemplate, TimeEntry, PresenceSession), implement full-text search using PostgreSQL GIN indexes, add WebSocket server with Redis pub/sub for scaling, and create analytics endpoints with charting on frontend.

## Technical Context

**Language/Version**: Python 3.13+ (backend), Node.js 18+ / TypeScript (frontend)

**Primary Dependencies**:
- Backend: FastAPI, SQLModel ORM, Dapr SDK, WebSocket support, ReportLab (PDF generation)
- Frontend: Next.js 16+, TypeScript, Chart.js or Recharts, WebSocket client
- Infrastructure: PostgreSQL 14+ (full-text search, JSONB), Redis (WebSocket pub/sub)

**Storage**:
- Primary: Neon Serverless PostgreSQL (existing tasks + new tables for saved searches, templates, time entries)
- Cache: Redis for WebSocket pub/sub and presence tracking
- Indexes: GIN indexes for full-text search, B-tree indexes for user_id and date fields

**Testing**: Manual end-to-end testing for all four feature sets (automated tests optional per constitution)
- Search: Create 1000+ tasks, test search performance and accuracy
- Templates: Instantiate templates with various placeholders
- WebSocket: Open multiple browser windows, verify real-time updates
- Analytics: Generate reports for 30-day period, validate calculations

**Target Platform**: Web application deployed on Kubernetes (Minikube local, cloud-ready for DOKS/GKE/AKS)

**Project Type**: Full-stack web application (Next.js frontend + FastAPI backend + PostgreSQL database)

**Performance Goals**:
- Search queries: <500ms response time for 10,000 tasks
- Bulk operations: <3 seconds for 100 tasks
- WebSocket broadcast: <100ms latency for 100 concurrent connections
- Analytics dashboard: <2 seconds to load all charts
- Real-time updates: <2 seconds propagation to all clients

**Constraints**:
- Maintain backward compatibility with existing API endpoints
- No breaking changes to current task schema (additive only)
- Free tier limits: Neon PostgreSQL (3GB storage), Redpanda Cloud (10GB/month)
- Kubernetes resource limits: 4GB RAM allocated to Minikube
- Must work gracefully when WebSocket disconnected (offline-first for core CRUD)

**Scale/Scope**:
- 4 major feature sets
- 38 functional requirements (FR-001 to FR-038)
- 21 non-functional requirements (NFR-001 to NFR-021)
- 4 new database tables + full-text search index
- ~15-20 new API endpoints
- 10+ new frontend components
- Estimated: 12-17 days implementation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Specification-First Development
**Status**: PASS
**Evidence**: Working from comprehensive specification in `specs/005-cloud-native-deployment/intermediate-advanced-features.md` with detailed user stories, functional requirements, API contracts, and acceptance criteria. This plan documents the implementation approach before any code is written.

### ✅ Principle II: Clean Architecture
**Status**: PASS
**Evidence**:
- Clear separation: Models (new tables) → Services (search, template, analytics, websocket) → API routes → Frontend
- New services isolated in separate files: `search_service.py`, `template_service.py`, `analytics_service.py`, `websocket_service.py`
- No circular dependencies: Services depend on models, routes depend on services
- WebSocket logic separated from HTTP endpoints
- Each service has single responsibility (SRP compliance)

### ✅ Principle III: Code Quality Standards
**Status**: PASS
**Evidence**:
- Following existing codebase patterns (PEP 8 for Python, ESLint for TypeScript)
- Descriptive naming: `SavedSearch`, `TaskTemplate`, `instantiate_template()`, `bulk_update_tasks()`
- RESTful API conventions maintained
- Database models use SQLModel with type hints
- No magic numbers: constants for limits (BULK_OPERATION_LIMIT=500, WS_MAX_CONNECTIONS=1000)

### ✅ Principle IV: User-Friendly Error Handling
**Status**: PASS
**Evidence**:
- Search sanitization prevents SQL injection (parameterized queries)
- Bulk operations return detailed errors with affected task IDs: `{"success_count": 8, "failure_count": 2, "errors": [{"task_id": "...", "reason": "..."}]}`
- WebSocket disconnections show user-friendly "Reconnecting..." indicator
- Template instantiation validates placeholders before processing
- Clear error messages: "Search query too complex (max 5 terms)" vs internal errors

### ⚠️ Principle V: Test-Driven Development (TDD)
**Status**: ACCEPTABLE (tests optional per constitution)
**Evidence**: Manual testing approach documented in spec with specific test scenarios. Automated tests deferred to future work per constitution allowance. Critical paths (bulk operations, WebSocket) will have manual validation procedures.

### ✅ Principle VI: Simplicity and YAGNI
**Status**: PASS
**Evidence**:
- Using PostgreSQL built-in full-text search (no Elasticsearch unless proven necessary)
- Using FastAPI WebSocket support (no Socket.IO complexity unless needed)
- Simple last-write-wins conflict resolution (no operational transform complexity)
- Templates limited to 10 placeholders to prevent over-engineering
- Bulk operations capped at 500 tasks (no background job complexity for MVP)
- Only implementing features in spec (no "nice to have" additions)

**GATE RESULT**: ✅ PASS - All mandatory principles satisfied. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/005-cloud-native-deployment/
├── intermediate-advanced-features.md  # Feature specification (input)
├── plan.md                            # This file (implementation plan)
├── research.md                        # Phase 0 output (technology decisions, patterns)
├── data-model.md                      # Phase 1 output (database schemas)
├── quickstart.md                      # Phase 1 output (setup and testing guide)
└── contracts/                         # Phase 1 output (API contracts)
    ├── search-api.yaml                # Search and saved searches endpoints
    ├── templates-api.yaml             # Template CRUD and instantiation
    ├── bulk-operations-api.yaml       # Bulk update/delete
    ├── websocket-protocol.md          # WebSocket message formats
    └── analytics-api.yaml             # Analytics and reporting endpoints
```

### Source Code (repository root)

```text
# Backend (new files to create)
backend/src/
├── models/
│   ├── saved_search.py          # NEW: SavedSearch model
│   ├── task_template.py         # NEW: TaskTemplate model
│   ├── time_entry.py            # NEW: TimeEntry model
│   └── presence_session.py      # NEW: PresenceSession model (may use Redis)
├── services/
│   ├── search_service.py        # NEW: Search logic and query building
│   ├── template_service.py      # NEW: Template instantiation
│   ├── analytics_service.py     # NEW: Metrics calculation
│   ├── websocket_service.py     # NEW: WebSocket broadcast and presence
│   └── export_service.py        # NEW: CSV/PDF generation
├── routes/
│   ├── search.py                # NEW: Search and saved searches endpoints
│   ├── templates.py             # NEW: Template CRUD and instantiation
│   ├── bulk_operations.py       # NEW: Bulk update/delete
│   ├── websocket.py             # NEW: WebSocket connection handler
│   └── analytics.py             # NEW: Analytics and reporting
└── main.py                      # UPDATE: Register new routes

# Frontend (new files to create)
frontend/
├── app/
│   ├── search/                  # NEW: Search page
│   ├── templates/               # NEW: Template management page
│   └── analytics/               # NEW: Analytics dashboard
├── components/
│   ├── SearchBar.tsx            # NEW: Search with autocomplete
│   ├── FilterPanel.tsx          # NEW: Advanced filters UI
│   ├── TemplateForm.tsx         # NEW: Create/edit templates
│   ├── BulkActionsToolbar.tsx   # NEW: Bulk operations UI
│   ├── PresenceIndicator.tsx    # NEW: Active users display
│   ├── AnalyticsChart.tsx       # NEW: Chart components
│   ├── TimeTracker.tsx          # NEW: Timer UI
│   └── NotificationToast.tsx    # NEW: Real-time notifications
└── lib/
    ├── websocket.ts             # NEW: WebSocket client
    └── analytics.ts             # NEW: Chart data formatting

# Database migrations
backend/migrations/
├── 006_add_saved_searches.sql   # NEW: SavedSearch table
├── 007_add_task_templates.sql   # NEW: TaskTemplate table
├── 008_add_time_entries.sql     # NEW: TimeEntry table
├── 009_add_search_index.sql     # NEW: Full-text search index
└── 010_add_analytics_views.sql  # NEW: Optional materialized views

# Kubernetes (updates)
k8s/
├── configmaps/
│   ├── websocket-config.yaml    # NEW: WebSocket settings
│   └── analytics-config.yaml    # NEW: Export settings
├── secrets/
│   └── redis-credentials.yaml   # NEW: Redis connection (if external)
└── backend/
    └── deployment.yaml          # UPDATE: Add Redis sidecar or connection
```

**Structure Decision**: Extending existing web application architecture. New features add tables and services without breaking existing CRUD operations. WebSocket runs alongside HTTP server in same FastAPI application.

## Complexity Tracking

> **Potential complexity violations - documenting for transparency:**

1. **WebSocket + Redis Pub/Sub**: Adds infrastructure complexity (Redis deployment)
   - **Justification**: Required for horizontal scaling and real-time collaboration (FR-018 to FR-027)
   - **Mitigation**: Start with in-memory pub/sub for single instance, add Redis only when scaling needed
   - **Constitution alignment**: Acceptable complexity for P2 feature with clear user value

2. **Full-Text Search Indexing**: PostgreSQL GIN indexes add query planning complexity
   - **Justification**: Required for <500ms search on 10,000+ tasks (NFR-001)
   - **Mitigation**: Using built-in PostgreSQL features (not external Elasticsearch)
   - **Constitution alignment**: Simplest solution that meets performance requirements

3. **Template Placeholder System**: String replacement logic with validation
   - **Justification**: Core feature requirement (FR-011, FR-012)
   - **Mitigation**: Limited to 10 placeholders, simple regex replacement (no template engine)
   - **Constitution alignment**: Minimal abstraction, only what's needed

**No violations** - all complexity justified by functional requirements and minimized per Principle VI.

---

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **PostgreSQL Full-Text Search Best Practices**
   - Question: How to structure `ts_vector` and `ts_query` for multi-field search (title + description)?
   - Question: GIN index configuration for optimal performance with 10K+ tasks?
   - Research: Boolean operators (AND, OR, NOT) in `ts_query`
   - Research: Ranking/relevance scoring for search results

2. **FastAPI WebSocket Patterns**
   - Question: How to broadcast messages to all connected clients?
   - Question: Best practice for WebSocket authentication (JWT in query param or header)?
   - Research: Handling disconnections and reconnections gracefully
   - Research: Redis pub/sub integration for multi-instance deployments

3. **Bulk Operation Transaction Handling**
   - Question: How to handle partial failures in bulk operations (50 succeed, 50 fail)?
   - Research: SQLAlchemy transaction rollback strategies
   - Research: Progress reporting for long-running bulk operations (500 tasks)

4. **Analytics Report Generation**
   - Question: ReportLab vs Puppeteer for PDF generation (Python vs headless Chrome)?
   - Research: Chart rendering in PDFs (static images vs embedded charts)
   - Research: Large dataset export strategies (streaming CSV vs in-memory)

5. **Template Placeholder Implementation**
   - Question: Simple string replacement vs template engine (Jinja2)?
   - Research: Placeholder validation and error messaging
   - Research: Date offset calculation for relative due dates

6. **Real-Time Presence Tracking**
   - Question: Database vs Redis for storing active user sessions?
   - Research: Heartbeat interval tuning (10s vs 30s tradeoff)
   - Research: Cleanup of stale presence records (timeout strategies)

### Expected Outputs (research.md)

- **Decision 1**: PostgreSQL full-text search with GIN indexes (vs Elasticsearch)
- **Decision 2**: FastAPI WebSocket + Redis pub/sub for scaling
- **Decision 3**: Transaction-per-bulk-operation with detailed error reporting
- **Decision 4**: ReportLab for PDF generation (Python-native, no headless browser)
- **Decision 5**: Simple regex-based placeholder replacement (no Jinja2 complexity)
- **Decision 6**: Redis for presence tracking (TTL-based expiry, fast lookups)

Each decision will document:
- **Rationale**: Why chosen
- **Alternatives considered**: What else was evaluated
- **Tradeoffs**: Performance, complexity, cost

---

## Phase 1: Design & Contracts

### Data Model Design (data-model.md)

**New Entities**:

1. **SavedSearch**
   - Fields: id (UUID), user_id (UUID FK), name (String), query_params (JSONB), created_at, updated_at
   - Relationships: Many-to-One with User
   - Validation: name max 100 chars, query_params must be valid JSON
   - Indexes: user_id (for lookup), created_at (for sorting)

2. **TaskTemplate**
   - Fields: id (UUID), user_id (UUID FK), name (String), description (Text), tasks_definition (JSONB), placeholders (JSONB array), created_at, updated_at
   - Relationships: Many-to-One with User
   - Validation: name max 100 chars, max 10 placeholders, tasks_definition array max 50 items
   - Indexes: user_id

3. **TimeEntry**
   - Fields: id (UUID), task_id (UUID FK), user_id (UUID FK), started_at, ended_at (nullable), elapsed_seconds (Integer), description (Text), created_at
   - Relationships: Many-to-One with Task and User
   - Validation: started_at < ended_at (when ended), elapsed_seconds auto-calculated
   - Indexes: task_id, user_id, started_at

4. **PresenceSession** (Redis-backed, not PostgreSQL)
   - Fields: user_id, session_id, task_id (nullable), status (Enum), last_heartbeat
   - TTL: 30 seconds (auto-expire)
   - Key pattern: `presence:{user_id}:{session_id}`

**Schema Updates**:

1. **tasks table**
   - Add column: `search_vector` (tsvector) - generated column for full-text search
   - Add index: GIN index on `search_vector`
   - Add trigger: Auto-update `search_vector` on INSERT/UPDATE

### API Contracts (contracts/)

**1. Search API** (`contracts/search-api.yaml`):
- POST `/api/{user_id}/tasks/search` - Advanced search with filters
- GET `/api/{user_id}/saved-searches` - List saved searches
- POST `/api/{user_id}/saved-searches` - Create saved search
- DELETE `/api/{user_id}/saved-searches/{search_id}` - Delete saved search

**2. Templates API** (`contracts/templates-api.yaml`):
- GET `/api/{user_id}/templates` - List templates
- POST `/api/{user_id}/templates` - Create template
- PUT `/api/{user_id}/templates/{template_id}` - Update template
- DELETE `/api/{user_id}/templates/{template_id}` - Delete template
- POST `/api/{user_id}/templates/{template_id}/instantiate` - Instantiate template

**3. Bulk Operations API** (`contracts/bulk-operations-api.yaml`):
- POST `/api/{user_id}/tasks/bulk-update` - Update multiple tasks
- POST `/api/{user_id}/tasks/bulk-delete` - Delete multiple tasks

**4. WebSocket Protocol** (`contracts/websocket-protocol.md`):
- Connection: `ws://localhost:8000/api/{user_id}/ws?token={jwt}`
- Client → Server: heartbeat, task_edit_start, task_edit_end
- Server → Client: task_created, task_updated, task_deleted, presence_update, notification

**5. Analytics API** (`contracts/analytics-api.yaml`):
- GET `/api/{user_id}/analytics/overview` - Dashboard metrics
- GET `/api/{user_id}/analytics/export?format=csv` - CSV export
- GET `/api/{user_id}/analytics/export?format=pdf` - PDF export
- POST `/api/{user_id}/time-entries` - Start/stop timer
- GET `/api/{user_id}/time-entries?task_id={id}` - Get time entries

### Quickstart Guide (quickstart.md)

**Setup Steps**:
1. Database migrations: Run migration scripts 006-010
2. Redis setup: Deploy Redis or use local instance
3. Environment variables: Add WebSocket and analytics config
4. Backend: Install new dependencies (reportlab, redis-py)
5. Frontend: Install charting library (chart.js or recharts)
6. Build and deploy updated services

**Testing Procedures**:
1. **Search**: Create 100 tasks, execute complex search, verify <500ms
2. **Templates**: Create template, instantiate with placeholders
3. **Bulk Operations**: Select 50 tasks, bulk update priority
4. **WebSocket**: Open 2 browser tabs, create task in tab 1, verify appears in tab 2 within 2s
5. **Analytics**: View dashboard, export CSV and PDF reports

**Troubleshooting**:
- WebSocket connection failures → Check JWT token, Redis connectivity
- Search performance slow → Verify GIN index created, run VACUUM ANALYZE
- Bulk operation timeouts → Reduce batch size below 500

### Agent Context Update

After completing Phase 1 design, run:
```bash
.specify/scripts/bash/update-agent-context.sh claude
```

This will add new technologies to `CLAUDE.md`:
- PostgreSQL Full-Text Search (GIN indexes)
- Redis (WebSocket pub/sub, presence tracking)
- FastAPI WebSocket
- ReportLab (PDF generation)
- Chart.js or Recharts (frontend charting)

---

## Phase 2: Tasks Generation (Not in this command)

**Note**: Tasks are generated by `/sp.tasks` command, not `/sp.plan`.

Expected task structure:
- Phase 1: Database migrations and schema setup
- Phase 2: Backend services and API endpoints (search, templates, bulk ops)
- Phase 3: WebSocket server and real-time features
- Phase 4: Analytics and reporting
- Phase 5: Frontend components and integration
- Phase 6: End-to-end testing and validation

---

## Success Criteria

### Phase 0 Complete
- [ ] All research questions answered in `research.md`
- [ ] Technology decisions documented with rationale
- [ ] No remaining "NEEDS CLARIFICATION" items

### Phase 1 Complete
- [ ] `data-model.md` defines all 4 new entities with validation rules
- [ ] All API contracts in `/contracts/` with OpenAPI specs
- [ ] `quickstart.md` provides step-by-step setup and testing guide
- [ ] Agent context updated with new technologies

### Re-check Constitution (Post-Design)
- [ ] Principle I (Spec-First): Design follows specification ✅
- [ ] Principle II (Clean Architecture): Clear separation of concerns ✅
- [ ] Principle III (Code Quality): Consistent naming and patterns ✅
- [ ] Principle IV (Error Handling): User-friendly error messages planned ✅
- [ ] Principle V (TDD): Manual testing approach documented ✅
- [ ] Principle VI (YAGNI): No over-engineering, minimal abstractions ✅

---

## Risks and Mitigations

### Risk 1: WebSocket Scaling Complexity
**Likelihood**: Medium | **Impact**: High (app unusable with 100+ users)
**Mitigation**: Start with in-memory pub/sub for MVP, add Redis when proven necessary through load testing

### Risk 2: Search Performance Degradation
**Likelihood**: Low | **Impact**: Medium (slow user experience)
**Mitigation**: GIN indexes proven to handle millions of rows, monitor query times, paginate results

### Risk 3: Bulk Operation Transaction Failures
**Likelihood**: Medium | **Impact**: High (data inconsistency)
**Mitigation**: Strict transaction boundaries, detailed error reporting, retry mechanisms

### Risk 4: Template Complexity Explosion
**Likelihood**: Low | **Impact**: Low (usability issue)
**Mitigation**: Limit to 10 placeholders, validate before instantiation, provide preview UI

### Risk 5: Real-Time Conflict Resolution
**Likelihood**: Medium | **Impact**: Medium (user frustration)
**Mitigation**: Last-write-wins with notification, optimistic UI updates with rollback

---

## Out of Scope (Explicitly Excluded)

- Elasticsearch integration (using PostgreSQL FTS instead)
- Socket.IO library (using FastAPI WebSocket)
- Operational Transform for conflict resolution (using last-write-wins)
- Background job queue (Celery) for bulk operations (synchronous for MVP)
- Shared task lists between users (single-user lists only)
- External calendar integrations
- AI-powered task suggestions
- Multi-language support

---

## Dependencies

**External Services**:
- Redis (WebSocket pub/sub, presence tracking) - NEW
- PostgreSQL 14+ (existing, adding FTS capabilities)

**Python Packages** (backend):
- `redis` - Redis client for pub/sub
- `reportlab` - PDF generation
- No new frontend build dependencies (FastAPI WebSocket built-in)

**Frontend Packages**:
- `chart.js` or `recharts` - Chart rendering
- `@types/chart.js` - TypeScript definitions
- WebSocket API (built into browsers)

---

## Next Steps

1. **Run this command**: Complete Phase 0 research and Phase 1 design
2. **Review outputs**: Validate research.md, data-model.md, contracts/, quickstart.md
3. **Run `/sp.tasks`**: Generate actionable implementation tasks
4. **Run `/sp.implement`**: Execute tasks in dependency order

**Estimated Timeline**: 12-17 days from tasks generation to completion

---

**Plan Status**: ✅ Ready for Phase 0 Research
