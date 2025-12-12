# Implementation Plan: Full-Stack Web Application

**Branch**: `002-todo-web-app` | **Date**: 2025-12-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-todo-web-app/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Transform the console todo application into a full-stack web application with multi-user support. The system implements user authentication via Better Auth + JWT, RESTful API with FastAPI, responsive frontend with Next.js 16+ App Router, and persistent storage with Neon PostgreSQL. All 5 basic CRUD operations (Add, View, Update, Delete, Mark Complete) are supported with strict user-level data isolation.

**Technical Approach**: Monorepo architecture with separate frontend and backend. Frontend uses Next.js 16+ with React Server Components for performance, Better Auth for client-side authentication, and Tailwind CSS for responsive styling. Backend uses FastAPI with SQLModel ORM for type-safe database operations, JWT middleware for authentication verification, and Neon Serverless PostgreSQL for persistent storage. Both services communicate via RESTful API with JWT tokens in Authorization headers.

## Technical Context

**Language/Version**:
- Backend: Python 3.13+ with UV package manager
- Frontend: TypeScript with Next.js 16+

**Primary Dependencies**:
- Backend: FastAPI >=0.115.0, SQLModel >=0.0.22, python-jose >=3.3.0, psycopg2-binary >=2.9.10, uvicorn
- Frontend: next ^16.0.0, react ^19.0.0, better-auth ^1.0.0, tailwindcss ^3.4.0

**Storage**: Neon Serverless PostgreSQL (cloud-hosted, auto-scaling)

**Testing**:
- Backend: pytest (Python unit/integration tests)
- Frontend: Playwright or Cypress (E2E tests)

**Target Platform**:
- Backend: Linux server (development), Cloud deployment (production: Vercel Serverless, Railway, or Render)
- Frontend: Web browsers (Chrome, Firefox, Safari, Edge), deployed to Vercel CDN

**Project Type**: Web application (frontend + backend monorepo)

**Performance Goals**:
- API response time: <200ms for CRUD operations
- Task list load time: <1 second for 100 tasks
- Frontend bundle size: <500KB initial load
- Database query optimization via indexes

**Constraints**:
- JWT tokens expire after 7 days (configurable)
- Title length: 1-200 characters
- Description length: max 1000 characters
- User data isolation: 100% enforcement via JWT verification and user_id filtering
- HTTPS only in production
- CORS restricted to trusted frontend origins

**Scale/Scope**:
- Target: 100+ concurrent users during hackathon demo
- Database: 1000+ tasks per user supported
- Frontend: 15+ React components, 4 pages
- Backend: 8 API endpoints, 2 database tables
- Deployment: Single-region for Phase II (multi-region in future phases)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Specification-First Development ✅ PASS

**Status**: COMPLIANT

- Feature specification created at `specs/002-todo-web-app/spec.md` with 8 user stories, 20 functional requirements, and 10 success criteria
- All implementation must follow approved specification
- Changes require specification updates first

### Principle II: Clean Architecture ✅ PASS (Adapted for Web)

**Status**: COMPLIANT with web architecture adaptation

- Clear separation: Frontend (presentation) → Backend API (business logic) → Database (data)
- Frontend structure: Components → Services (API client) → Pages
- Backend structure: Routes → Services → Models → Database
- Dependency flow: UI → API Client → API Routes → Business Logic → Data Models
- No circular dependencies across frontend/backend boundary

**Adaptation Note**: Constitution originally defined for console app (CLI → Services → Models). Phase II adapts this to web architecture with explicit frontend/backend separation while maintaining clean architecture principles.

### Principle III: Code Quality Standards ✅ PASS

**Status**: COMPLIANT

- Backend: PEP 8 style guidelines, type hints with SQLModel and Pydantic
- Frontend: TypeScript for type safety, ESLint + Prettier for consistency
- Naming conventions:
  - Python: snake_case for functions/variables, PascalCase for classes
  - TypeScript: camelCase for functions/variables, PascalCase for components/classes
- Single responsibility per module and component
- Self-documenting code with clear names

### Principle IV: User-Friendly Error Handling ✅ PASS

**Status**: COMPLIANT

- Frontend: User-friendly error messages, no stack traces exposed
- Backend: HTTP status codes with descriptive error messages
- Validation errors caught and explained (FR-017)
- Graceful handling of edge cases (token expiry, network errors, etc.)
- No crashes on invalid inputs

### Principle V: Test-Driven Development (Optional) ⚠️ DEFERRED

**Status**: TESTING OPTIONAL (per constitution)

- Testing encouraged but NOT mandatory for Phase II due to time constraints
- Focus on spec-driven development and manual testing
- Automated tests can be added in future phases

**Rationale**: Constitution explicitly states "Testing is encouraged but NOT mandatory" to prioritize learning Spec-Driven Development.

### Principle VI: Simplicity and YAGNI ✅ PASS

**Status**: COMPLIANT

- Only implementing features in specification (8 user stories)
- No premature abstractions or over-engineering
- Monorepo chosen for simplicity over microservices
- Direct SQLModel queries (no repository pattern) unless needed
- Better Auth used instead of building custom auth system

### Additional Gates

**Project Scope**: ✅ PASS
- Within constitution's "In Scope": Python 3.13+, UV package manager, Spec-Kit Plus, Claude Code
- Extends scope with: Next.js, TypeScript, PostgreSQL, Better Auth (Phase II requirements)

**Structure Compliance**: ✅ PASS
- Constitution structure adapted for web: `backend/` and `frontend/` instead of single `src/`
- Spec-Kit Plus structure maintained: `specs/`, `history/`, `.specify/`

**Complexity Justification**: See Complexity Tracking section below

### Gate Result

**✅ ALL GATES PASS** - Proceed to Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
todo/                              # Monorepo root
├── backend/                       # FastAPI backend
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app entry point, CORS, startup
│   │   ├── db.py                 # Database connection, session management
│   │   ├── models.py             # SQLModel models (Task, User)
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   └── auth.py           # JWT verification middleware
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── tasks.py          # Task CRUD endpoints
│   │       └── auth.py           # Auth endpoints (optional, Better Auth may handle)
│   ├── tests/                    # Optional for Phase II
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_routes.py
│   │   └── test_auth.py
│   ├── pyproject.toml            # UV project config
│   ├── .env.example              # Environment variables template
│   ├── .env                      # Local environment (gitignored)
│   ├── README.md                 # Backend setup instructions
│   └── CLAUDE.md                 # Backend development guidelines
│
├── frontend/                     # Next.js 16+ frontend
│   ├── app/
│   │   ├── layout.tsx            # Root layout with Header
│   │   ├── page.tsx              # Home page (redirect based on auth)
│   │   ├── globals.css           # Global Tailwind styles
│   │   ├── login/
│   │   │   └── page.tsx          # Login page
│   │   ├── signup/
│   │   │   └── page.tsx          # Signup page
│   │   └── dashboard/
│   │       ├── page.tsx          # Dashboard page (protected)
│   │       └── loading.tsx       # Loading state
│   ├── components/
│   │   ├── Header.tsx            # Navigation header (server component)
│   │   ├── TaskList.tsx          # Task list (server component)
│   │   ├── TaskItem.tsx          # Task item (client component)
│   │   ├── AddTaskForm.tsx       # Add task form (client component)
│   │   ├── EditTaskModal.tsx     # Edit task modal (client component)
│   │   ├── LoginForm.tsx         # Login form (client component)
│   │   ├── SignupForm.tsx        # Signup form (client component)
│   │   └── ui/                   # Shared components
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Modal.tsx
│   │       └── Loading.tsx
│   ├── lib/
│   │   ├── api.ts                # API client with JWT handling
│   │   ├── auth.ts               # Better Auth configuration
│   │   └── types.ts              # TypeScript type definitions
│   ├── public/                   # Static assets
│   ├── tests/                    # Optional E2E tests
│   ├── package.json              # Node.js dependencies
│   ├── tsconfig.json             # TypeScript configuration
│   ├── tailwind.config.ts        # Tailwind CSS configuration
│   ├── next.config.js            # Next.js configuration
│   ├── .env.example              # Environment variables template
│   ├── .env.local                # Local environment (gitignored)
│   ├── README.md                 # Frontend setup instructions
│   └── CLAUDE.md                 # Frontend development guidelines
│
├── specs/                        # Spec-Kit Plus specifications
│   ├── 002-todo-web-app/         # This feature
│   │   ├── spec.md               # Feature specification
│   │   ├── plan.md               # This file - implementation plan
│   │   ├── research.md           # Phase 0 output (to be created)
│   │   ├── data-model.md         # Phase 1 output (to be created)
│   │   ├── quickstart.md         # Phase 1 output (to be created)
│   │   ├── contracts/            # Phase 1 output (to be created)
│   │   │   └── openapi.yaml      # OpenAPI spec for backend
│   │   ├── checklists/
│   │   │   └── requirements.md   # Validation checklist
│   │   └── tasks.md              # Phase 2 output (created by /sp.tasks)
│   ├── features/                 # Detailed feature specs (reference)
│   ├── api/                      # API specs (reference)
│   ├── database/                 # Database specs (reference)
│   └── ui/                       # UI specs (reference)
│
├── history/
│   ├── prompts/                  # Prompt History Records
│   │   ├── 002-todo-web-app/     # PHRs for this feature
│   │   ├── constitution/
│   │   └── general/
│   └── adr/                      # Architecture Decision Records
│
├── .specify/                     # Spec-Kit Plus framework
│   ├── memory/
│   │   └── constitution.md       # Project constitution
│   ├── templates/                # Templates for specs, plans, tasks
│   └── scripts/                  # Automation scripts
│
├── .gitignore                    # Updated for Node.js and Python
├── CLAUDE.md                     # Root-level Claude Code instructions
└── README.md                     # Project overview
```

**Structure Decision**: **Web application (Option 2)** - Monorepo with separate `backend/` and `frontend/` directories.

**Rationale**:
- **Monorepo**: Easier for Claude Code to make cross-cutting changes, simpler context management for hackathon timeline
- **Frontend/Backend Separation**: Clear boundary between presentation and business logic, enables independent deployment
- **Spec-Kit Plus Integration**: Maintains required structure (`specs/`, `history/`, `.specify/`)
- **Clean Architecture**: Each layer has clear responsibility and dependency flow

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected** - All constitution gates pass. No complexity justifications needed.

**Architecture Decisions**:
- Monorepo structure: Simplifies development for hackathon timeline
- Better Auth: Avoids building custom authentication (YAGNI principle)
- SQLModel ORM: Provides type safety without repository pattern complexity
- Next.js Server Components: Modern React pattern, not over-engineering
