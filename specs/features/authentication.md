# Feature: User Authentication

## Overview

Implement user **signup and signin** functionality using Better Auth with JWT tokens. Enable multi-user support where each user has their own isolated task list.

## User Stories

### US-1: User Signup
**As a** new user
**I want to** create an account
**So that** I can start managing my tasks

**Acceptance Criteria:**
- User provides email, password, and name
- Email must be unique (not already registered)
- Password must be at least 8 characters
- Better Auth creates user in database
- Better Auth issues JWT token upon successful signup
- User is automatically logged in after signup
- Redirect to dashboard after successful signup

### US-2: User Signin
**As a** registered user
**I want to** log into my account
**So that** I can access my tasks

**Acceptance Criteria:**
- User provides email and password
- Better Auth verifies credentials against database
- Better Auth issues JWT token upon successful login
- JWT token stored on client (cookie or localStorage)
- Redirect to dashboard after successful login
- Show error message for invalid credentials

### US-3: Protected Routes
**As a** application developer
**I want to** protect dashboard routes
**So that** only authenticated users can access their tasks

**Acceptance Criteria:**
- Unauthenticated users redirected to login page
- Authenticated users can access dashboard
- JWT token sent with every API request in Authorization header
- Token verified by backend middleware

### US-4: User Logout
**As a** logged-in user
**I want to** log out of my account
**So that** I can secure my session

**Acceptance Criteria:**
- Logout button in navigation
- JWT token removed from client storage
- User redirected to login page
- Subsequent API requests fail with HTTP 401

## Architecture

### Better Auth + FastAPI Integration

```
┌──────────────────────────────────────────────────────────────┐
│ Frontend (Next.js + Better Auth)                             │
│                                                               │
│  1. User submits signup/login form                           │
│  2. Better Auth handles authentication                       │
│  3. Better Auth issues JWT token                             │
│  4. Token stored in browser (cookie/localStorage)            │
│  5. Token included in API requests:                          │
│     Authorization: Bearer <token>                            │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ HTTPS
                         │
┌────────────────────────┼─────────────────────────────────────┐
│ Backend (FastAPI)      ▼                                     │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ JWT Middleware                                         │  │
│  │  1. Extract token from Authorization header           │  │
│  │  2. Verify token signature with BETTER_AUTH_SECRET    │  │
│  │  3. Decode token to get user_id, email, etc.          │  │
│  │  4. Attach user info to request context               │  │
│  │  5. Verify user_id in URL matches token user_id       │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ API Routes                                             │  │
│  │  - Use authenticated user_id to filter queries        │  │
│  │  - Return only data belonging to authenticated user   │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

## Data Model

### User Entity (Managed by Better Auth)

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| id | string | Auto | Primary key, UUID | Unique user identifier |
| email | string | Yes | Unique, valid email | User email address |
| name | string | Yes | 1-100 chars | User display name |
| password_hash | string | Auto | Hashed by Better Auth | Hashed password |
| created_at | timestamp | Auto | Default: NOW() | Account creation time |

**Note**: Better Auth manages this table. We don't directly create/update users in application code.

## JWT Token Structure

```json
{
  "user_id": "abc123",
  "email": "user@example.com",
  "name": "John Doe",
  "iat": 1702300000,
  "exp": 1702905600
}
```

**Token Lifetime**: 7 days (configurable)

## Configuration

### Environment Variables

**Frontend (.env.local):**
```
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend (.env):**
```
BETTER_AUTH_SECRET=your-secret-key-here
DATABASE_URL=postgresql://user:pass@host/dbname
```

**Important**: Both frontend and backend must use the **same** `BETTER_AUTH_SECRET` for JWT signing and verification.

## Security Requirements

### Password Security
- Minimum 8 characters
- Better Auth handles hashing (bcrypt or similar)
- Never store plaintext passwords
- Never return password hashes in API responses

### JWT Security
- Secret key stored in environment variables (never in code)
- Tokens expire after configurable time (default: 7 days)
- Tokens signed with HS256 or RS256 algorithm
- Tokens verified on every API request

### HTTPS Only (Production)
- All authentication endpoints must use HTTPS in production
- Set secure flag on cookies in production
- Enable CORS for frontend domain only

### API Security
- All endpoints (except auth) require valid JWT
- Verify user_id in token matches user_id in URL
- Return HTTP 401 for missing/invalid tokens
- Return HTTP 403 for unauthorized access attempts

## API Endpoints (Auth)

Better Auth typically handles these automatically, but if custom endpoints are needed:

### POST /api/auth/signup
Create new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}
```

**Response (201):**
```json
{
  "user": {
    "id": "abc123",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors:**
- 400: Validation error (weak password, invalid email)
- 409: Email already registered

### POST /api/auth/login
Authenticate existing user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "user": {
    "id": "abc123",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors:**
- 401: Invalid credentials

### POST /api/auth/logout (Optional)
Logout user (client-side token removal is usually sufficient).

## UI Components

### LoginPage
- Email input (required, email validation)
- Password input (required, password type)
- "Remember me" checkbox (optional)
- Submit button
- Link to signup page
- Error message display

### SignupPage
- Name input (required)
- Email input (required, email validation)
- Password input (required, min 8 chars)
- Confirm password input (must match password)
- Submit button
- Link to login page
- Error message display

### Navigation
- Show user name/email when logged in
- Logout button
- Hide login/signup links when authenticated
- Show login/signup links when not authenticated

## Frontend Implementation Notes

### Better Auth Setup
1. Install Better Auth: `npm install better-auth`
2. Configure Better Auth in `app/auth/config.ts`
3. Create auth provider wrapper
4. Wrap app in auth provider
5. Use `useSession()` hook to access user state

### API Client with JWT
```typescript
// lib/api.ts
async function apiCall(endpoint: string, options: RequestInit = {}) {
  const token = getToken(); // From cookie or localStorage

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (response.status === 401) {
    // Token expired or invalid - redirect to login
    window.location.href = '/login';
  }

  return response.json();
}
```

### Protected Route Pattern
```typescript
// app/dashboard/page.tsx
import { redirect } from 'next/navigation';
import { getSession } from '@/lib/auth';

export default async function DashboardPage() {
  const session = await getSession();

  if (!session) {
    redirect('/login');
  }

  return <Dashboard user={session.user} />;
}
```

## Backend Implementation Notes

### JWT Middleware
```python
# src/middleware/auth.py
from fastapi import Request, HTTPException
import jwt

async def verify_jwt(request: Request):
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth_header.split(' ')[1]

    try:
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=['HS256'])
        request.state.user_id = payload['user_id']
        request.state.user_email = payload['email']
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Route Protection
```python
# src/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from middleware.auth import verify_jwt

router = APIRouter(dependencies=[Depends(verify_jwt)])

@router.get("/api/{user_id}/tasks")
async def get_tasks(user_id: str, request: Request):
    # Verify user_id in URL matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Cannot access other user's tasks")

    # Query tasks for this user
    tasks = session.query(Task).filter(Task.user_id == user_id).all()
    return tasks
```

## Testing Scenarios

### Happy Path
1. User signs up → Account created → JWT issued → Redirected to dashboard
2. User logs in → Credentials verified → JWT issued → Redirected to dashboard
3. User accesses dashboard → JWT valid → Tasks loaded
4. User logs out → Token removed → Redirected to login

### Edge Cases
1. User tries to signup with existing email → HTTP 409
2. User enters wrong password → HTTP 401
3. User token expires → HTTP 401, redirect to login
4. User manipulates URL to access another user's tasks → HTTP 403

### Security Tests
1. User modifies JWT token → Backend rejects (signature invalid)
2. User accesses API without token → HTTP 401
3. User's token expires mid-session → Auto-logout on next request

## Migration from Phase I

Phase I had no authentication (single user). Phase II changes:

1. **Add user_id to tasks**: All tasks now have `user_id` field
2. **Filter by user**: All queries include `WHERE user_id = <authenticated_user>`
3. **Protect routes**: All routes require JWT authentication
4. **Multi-user UI**: Show only logged-in user's tasks

## Success Metrics

- User can signup in < 10 seconds
- User can login in < 5 seconds
- Zero data leakage between users
- Tokens remain valid for configured duration
- Invalid tokens properly rejected

## Future Enhancements (Not in Phase II)

- OAuth providers (Google, GitHub)
- Email verification
- Password reset flow
- Two-factor authentication (2FA)
- Session management (view active sessions)

## Dependencies

- **Better Auth**: Must be installed and configured
- **Neon PostgreSQL**: Database for user storage
- **Environment Variables**: BETTER_AUTH_SECRET configured

## References

- [Better Auth Documentation](https://better-auth.com)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Hackathon PDF: Better Auth + FastAPI Integration](../../Hackathon II - Todo Spec-Driven Development.pdf) (Pages 7-8)
