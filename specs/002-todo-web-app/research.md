# Research & Technology Decisions

**Feature**: 002-todo-web-app
**Date**: 2025-12-09
**Purpose**: Document technology choices, best practices, and architectural decisions for the full-stack web application

## Technology Stack Research

### Frontend Framework: Next.js 16+ (App Router)

**Decision**: Use Next.js 16+ with App Router

**Rationale**:
- **React Server Components**: Improved performance with server-side rendering by default
- **Built-in Routing**: File-system based routing simplifies page creation
- **Vercel Deployment**: One-click deployment to Vercel with optimized CDN
- **TypeScript Support**: First-class TypeScript integration
- **Modern React**: Supports latest React 19 features

**Best Practices**:
- Use Server Components by default (no 'use client' directive)
- Use Client Components only for interactivity (forms, onClick handlers, useState)
- Leverage Next.js layouts for shared UI (Header, navigation)
- Use loading.tsx for loading states
- Use error.tsx for error boundaries

**Alternatives Considered**:
- Create React App: Rejected - deprecated, no SSR support
- Vite + React: Rejected - requires manual routing setup, no SSR by default
- Remix: Rejected - less familiar, smaller ecosystem

**References**:
- [Next.js App Router Documentation](https://nextjs.org/docs/app)
- [React Server Components](https://react.dev/reference/react/use-server)

---

### Backend Framework: FastAPI

**Decision**: Use FastAPI with async/await support

**Rationale**:
- **Performance**: Async/await for high throughput
- **Auto-Documentation**: Automatic OpenAPI (Swagger) docs generation
- **Type Safety**: Pydantic models provide runtime validation
- **SQLModel Integration**: Seamless integration with SQLModel ORM
- **Modern Python**: Leverages Python 3.13+ type hints

**Best Practices**:
- Use dependency injection with `Depends()` for DB sessions and auth
- Define Pydantic models for request/response validation
- Use async route handlers for database operations
- Enable CORS middleware for frontend origin
- Add JWT middleware to protect routes

**Alternatives Considered**:
- Django: Rejected - too heavy for API-only backend
- Flask: Rejected - lacks async support, manual OpenAPI setup
- Express.js (Node.js): Rejected - adds language complexity (Python + JS)

**References**:
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)

---

### ORM: SQLModel

**Decision**: Use SQLModel for database operations

**Rationale**:
- **Type Safety**: Combines SQLAlchemy (ORM) + Pydantic (validation)
- **Single Source of Truth**: Same models for DB and API validation
- **FastAPI Integration**: Designed to work with FastAPI
- **Migrations**: Compatible with Alembic for schema migrations
- **Developer Experience**: Excellent autocomplete and type checking

**Best Practices**:
- Define models with SQLModel base class and `table=True`
- Use `Field()` for constraints (max_length, foreign_key, index)
- Use `Optional[type]` for nullable fields
- Create database session dependency for route injection
- Use `Session.exec(select())` pattern for queries

**Alternatives Considered**:
- Raw SQL: Rejected - no type safety, SQL injection risk
- Django ORM: Rejected - requires Django framework
- Tortoise ORM: Rejected - less mature, smaller ecosystem

**References**:
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [SQLAlchemy Best Practices](https://docs.sqlalchemy.org/en/20/orm/queryguide/)

---

### Authentication: Better Auth + JWT

**Decision**: Use Better Auth on frontend with JWT tokens verified by backend

**Rationale**:
- **Stateless**: JWT tokens don't require server-side session storage
- **Scalability**: Backend can scale horizontally without session state
- **Better Auth**: Handles signup/login flows on frontend
- **Simple Integration**: JWT payload contains user_id for backend authorization
- **Industry Standard**: HS256 algorithm widely supported

**Architecture**:
1. Frontend: Better Auth handles signup/login → issues JWT token
2. Frontend: Store token in cookie or localStorage
3. Frontend: Send token in `Authorization: Bearer <token>` header
4. Backend: JWT middleware verifies token signature and extracts user_id
5. Backend: All queries filtered by user_id from token

**Best Practices**:
- Use same `BETTER_AUTH_SECRET` in both frontend and backend
- Set token expiry (7 days recommended for Phase II)
- Verify token on every backend request
- Match user_id in URL with user_id in token
- Return HTTP 401 for invalid/expired tokens
- Return HTTP 403 for unauthorized access attempts

**Security Considerations**:
- Secret key must be min 32 characters, stored in .env
- Use HTTPS in production to prevent token interception
- Implement token refresh for long-lived sessions (future phase)
- Consider HttpOnly cookies instead of localStorage (future phase)

**Alternatives Considered**:
- NextAuth: Rejected - complex setup for simple use case
- Session cookies: Rejected - requires server-side session store, not stateless
- Auth0/Clerk: Rejected - third-party dependency, costs

**References**:
- [Better Auth Documentation](https://better-auth.com)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [python-jose Library](https://python-jose.readthedocs.io/)

---

### Database: Neon Serverless PostgreSQL

**Decision**: Use Neon for hosted PostgreSQL database

**Rationale**:
- **Serverless**: Auto-scaling, pay-per-use pricing
- **Free Tier**: Sufficient for hackathon and development
- **Branching**: Database branching for testing (future use)
- **Connection Pooling**: Built-in connection pooling
- **PostgreSQL Compatibility**: Full PostgreSQL feature set

**Connection Pattern**:
```python
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True  # Verify connections before use
)
```

**Best Practices**:
- Use connection pooling to handle concurrent requests
- Enable `pool_pre_ping` to detect stale connections
- Create indexes on user_id and completion status
- Use transactions for multi-step operations
- Implement CASCADE DELETE for user → tasks relationship

**Schema Design**:
- `users` table: Managed by Better Auth
- `tasks` table: Foreign key to users.id with CASCADE DELETE
- Indexes: user_id (for filtering), completed (for future status filters)

**Alternatives Considered**:
- SQLite: Rejected - not suitable for production web app
- Supabase: Rejected - includes unnecessary features (auth, storage)
- MongoDB: Rejected - relational data is a better fit for tasks

**References**:
- [Neon Documentation](https://neon.tech/docs)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don't_Do_This)

---

### Styling: Tailwind CSS

**Decision**: Use Tailwind CSS for all styling

**Rationale**:
- **Utility-First**: Rapid development with utility classes
- **No CSS Files**: Styles colocated with components
- **Responsive**: Built-in responsive design utilities
- **Customization**: Easy theme configuration
- **Performance**: Purges unused CSS in production

**Best Practices**:
- Use utility classes directly in JSX
- Group related utilities for readability
- Use responsive prefixes (md:, lg:) for breakpoints
- Define custom colors in tailwind.config.ts
- Avoid inline styles (style={{ }})

**Color Palette**:
- Primary: blue-600 (buttons, links)
- Success: green-600 (completed tasks)
- Danger: red-600 (delete actions)
- Gray: gray-100 to gray-900 (backgrounds, text)

**Alternatives Considered**:
- CSS Modules: Rejected - more boilerplate
- Styled Components: Rejected - runtime CSS-in-JS overhead
- Bootstrap: Rejected - opinionated components, larger bundle

**References**:
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Tailwind Best Practices](https://tailwindcss.com/docs/reusing-styles)

---

### Package Management

**Frontend**: npm (default with Next.js)
**Backend**: UV (modern Python package manager)

**UV Benefits**:
- Fast dependency resolution
- Better dependency locking
- Compatible with pip and pyproject.toml
- Recommended in hackathon spec

---

## API Design Patterns

### RESTful Conventions

**Endpoint Structure**: `/api/{user_id}/{resource}/{id?}/{action?}`

**HTTP Methods**:
- GET: Retrieve resources
- POST: Create new resource
- PUT: Update entire resource
- PATCH: Partial update
- DELETE: Remove resource

**Status Codes**:
- 200 OK: Successful GET, PUT, PATCH
- 201 Created: Successful POST
- 204 No Content: Successful DELETE (optional)
- 400 Bad Request: Validation error
- 401 Unauthorized: Missing/invalid token
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Resource doesn't exist
- 500 Internal Server Error: Server error

**Response Format**:
```json
{
  "id": 1,
  "user_id": "abc123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-09T10:30:00Z",
  "updated_at": "2025-12-09T10:30:00Z"
}
```

**Error Format**:
```json
{
  "detail": "Task not found"
}
```

---

## Security Best Practices

### Input Validation
- Validate on both frontend and backend
- Frontend: Prevent submission, show inline errors
- Backend: Return HTTP 400 with error details
- Use SQLModel/Pydantic for automatic validation

### SQL Injection Prevention
- Use SQLModel ORM (parameterized queries)
- Never concatenate user input into SQL strings

### XSS Prevention
- React escapes JSX by default
- Avoid `dangerouslySetInnerHTML`
- Sanitize user input on display

### CORS Configuration
- Allow only trusted frontend origins
- Enable credentials for cookie-based auth
- Restrict in production to specific domains

### Environment Variables
- Never commit .env files
- Use .env.example as template
- Store secrets in environment, not code

---

## Performance Optimization

### Frontend
- Server Components reduce client-side JavaScript
- Code splitting via Next.js dynamic imports
- Image optimization with Next.js Image component
- Static generation for public pages

### Backend
- Connection pooling for database
- Indexes on frequently queried columns
- Async/await for non-blocking I/O
- Response caching for read-heavy endpoints (future)

### Database
- Index on tasks.user_id (required for all queries)
- Index on tasks.completed (for future filtering)
- Limit query results with pagination (future)

---

## Development Workflow

1. **Setup**:
   - Frontend: `cd frontend && npm install && npm run dev`
   - Backend: `cd backend && uv venv && source .venv/bin/activate && uv pip install -e . && uvicorn src.main:app --reload`

2. **Development**:
   - Frontend runs on http://localhost:3000
   - Backend runs on http://localhost:8000
   - Database: Neon cloud instance (connection string in .env)

3. **Environment Variables**:
   - Frontend: `.env.local` with NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET
   - Backend: `.env` with DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS

4. **Testing**:
   - Manual testing via browser for Phase II
   - Automated tests optional (Playwright for E2E, pytest for backend)

5. **Deployment**:
   - Frontend: Vercel (auto-deploy from GitHub)
   - Backend: Vercel Serverless Functions, Railway, or Render
   - Database: Neon (already cloud-hosted)

---

## Open Questions & Clarifications

All NEEDS CLARIFICATION items from Technical Context have been resolved:

- ✅ Language/Version: Confirmed Python 3.13+ and TypeScript with Next.js 16+
- ✅ Primary Dependencies: Documented (FastAPI, SQLModel, Next.js, Better Auth, etc.)
- ✅ Storage: Confirmed Neon Serverless PostgreSQL
- ✅ Testing: Optional for Phase II, manual testing priority
- ✅ Target Platform: Linux server for backend, web browsers for frontend
- ✅ Performance Goals: < 200ms API response, < 1s task list load
- ✅ Constraints: JWT expiry, string length limits, HTTPS production
- ✅ Scale/Scope: 100+ users, 1000+ tasks per user, 8 endpoints, 15+ components

**No further clarifications needed** - Proceed to Phase 1 (Data Model & Contracts)
