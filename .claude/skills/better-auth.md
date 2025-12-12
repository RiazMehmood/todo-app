# Better Auth Skill

**Description:** Implement and manage Better Auth authentication

## Overview
Better Auth is used for client-side authentication with JWT tokens. The backend verifies tokens but doesn't manage user sessions.

## Architecture
```
Frontend (Better Auth) → JWT Token → Backend (JWT Verification) → Database
```

## Installation

### Frontend
```bash
cd frontend
npm install better-auth
```

### Backend
```bash
cd backend
pip install python-jose[cryptography] passlib[bcrypt]
```

## Configuration

### Frontend (lib/auth.ts)
```typescript
import { betterAuth } from 'better-auth';

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET!,
  baseURL: process.env.BETTER_AUTH_URL!,
  // Add custom configuration here
});
```

### Backend JWT Verification (middleware/auth.py)
```python
from jose import jwt, JWTError
import os

SECRET = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

async def verify_jwt(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(401, "Missing token")

    token = auth_header.split(' ')[1]

    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        request.state.user_id = payload.get('user_id') or payload.get('sub')
    except JWTError:
        raise HTTPException(401, "Invalid token")
```

## Common Operations

### Signup Flow
1. User submits signup form (frontend)
2. Frontend calls backend `/api/auth/signup`
3. Backend hashes password, creates user
4. Backend generates JWT token
5. Frontend stores token (localStorage)
6. Frontend redirects to dashboard

### Login Flow
1. User submits login form (frontend)
2. Frontend calls backend `/api/auth/login`
3. Backend verifies credentials
4. Backend generates JWT token
5. Frontend stores token
6. Frontend redirects to dashboard

### Protected Routes
```typescript
// frontend/app/dashboard/page.tsx
'use client';

export default function Dashboard() {
  useEffect(() => {
    const token = getAuthToken();
    if (!token) {
      router.push('/login');
    }
  }, []);

  // ... dashboard code
}
```

### Backend Route Protection
```python
# backend/src/routes/tasks.py
from fastapi import APIRouter, Depends, Request
from ..middleware.auth import verify_jwt

router = APIRouter(dependencies=[Depends(verify_jwt)])

@router.get("/api/{user_id}/tasks")
def get_tasks(user_id: str, request: Request):
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(403, "Unauthorized")

    # ... fetch tasks
```

## Token Management

### Token Storage (Frontend)
```typescript
// Store token
localStorage.setItem('todo_auth_token', token);

// Retrieve token
const token = localStorage.getItem('todo_auth_token');

// Remove token (logout)
localStorage.removeItem('todo_auth_token');
```

### Token Verification (Backend)
```python
def create_jwt_token(user_id: str, email: str) -> str:
    expiration = datetime.utcnow() + timedelta(days=7)

    payload = {
        "user_id": user_id,
        "sub": user_id,  # Standard JWT subject
        "email": email,
        "exp": expiration,
        "iat": datetime.utcnow(),
    }

    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)
```

## Security Best Practices

### 1. Secret Management
- ✅ Use strong secrets (min 32 chars)
- ✅ Store in environment variables
- ✅ Never commit to git
- ✅ Match secret in frontend and backend

### 2. Token Expiration
- ✅ Set reasonable expiration (7 days default)
- ✅ Implement refresh tokens for long sessions
- ✅ Handle expired tokens gracefully

### 3. HTTPS
- ✅ Use HTTPS in production
- ✅ Prevent token interception
- ✅ Secure cookie options

### 4. Password Security
- ✅ Hash with bcrypt
- ✅ Minimum 8 characters
- ✅ Never store plain text
- ✅ Use strong hashing rounds

## Troubleshooting

### "Invalid token" errors
- Check BETTER_AUTH_SECRET matches in both frontend and backend
- Verify token format in Authorization header
- Check token expiration

### "Missing token" errors
- Verify token is being sent in request
- Check Authorization header format: `Bearer <token>`
- Ensure token is stored correctly

### Login redirects to login
- Check token is valid and not expired
- Verify protected route authentication logic
- Check localStorage has token

### CORS errors during auth
- Verify CORS_ORIGINS includes frontend URL
- Check credentials: true in fetch options
- Verify preflight OPTIONS requests

## Advanced Features

### Email Verification
Add email verification field to User model and implement verification flow

### Password Reset
Implement forgot password with email token verification

### OAuth Integration
Integrate Google/GitHub OAuth with Better Auth providers

### Two-Factor Authentication
Add 2FA with TOTP codes

### Session Management
Track active sessions and allow revocation

## Success Criteria
✅ Users can signup with email/password
✅ Users can login with credentials
✅ JWT tokens issued correctly
✅ Protected routes require authentication
✅ Token verification works
✅ Logout clears session
✅ Multi-user data isolated correctly
