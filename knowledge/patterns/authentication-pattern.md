# Authentication Pattern - JWT with Better Auth

**Source**: Phase II (Todo Web App)
**Date**: 2025-12-16
**Status**: Production-ready

## Overview

This pattern demonstrates JWT-based authentication using Better Auth with FastAPI backend and Next.js frontend. Supports multi-user data isolation and secure session management.

## Technology Stack

- **Backend**: FastAPI + Better Auth (Python)
- **Frontend**: Next.js 16+ App Router + Better Auth Client
- **Database**: Neon PostgreSQL (User table)
- **Token**: JWT (JSON Web Token)

## Architecture

```
┌─────────────────┐
│  Next.js        │
│  Frontend       │
│  (Client)       │
└────────┬────────┘
         │ JWT Token
         │ (localStorage)
         ▼
┌─────────────────┐
│  FastAPI        │
│  Backend        │
│  (Server)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL     │
│  (Users Table)  │
└─────────────────┘
```

## Database Schema

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

## Backend Implementation

### 1. User Model (SQLModel)

```python
# backend/src/models.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. Password Hashing

```python
# backend/src/middleware/auth.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

### 3. JWT Token Generation

```python
# backend/src/middleware/auth.py
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "your-secret-key"  # Use environment variable in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

### 4. Authentication Endpoints

```python
# backend/src/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel
from models import User
from middleware.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/signup")
async def signup(request: SignupRequest, db: Session = Depends(get_session)):
    """Create new user account."""
    # Check if email exists
    existing = db.exec(select(User).where(User.email == request.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        email=request.email,
        name=request.name,
        password_hash=hash_password(request.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate token
    token = create_access_token(data={"sub": str(user.id)})

    return {
        "token": token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        }
    }

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_session)):
    """Login existing user."""
    # Find user
    user = db.exec(select(User).where(User.email == request.email)).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate token
    token = create_access_token(data={"sub": str(user.id)})

    return {
        "token": token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        }
    }
```

### 5. Protected Route Dependency

```python
# backend/src/middleware/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security)
) -> dict:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email")
    }

# Usage in protected routes:
@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['user_id']}"}
```

## Frontend Implementation

### 1. Auth Context (Next.js)

```typescript
// frontend/lib/auth-context.tsx
'use client';

import { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextType {
  user: any | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<any | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    // Load token from localStorage
    const savedToken = localStorage.getItem('auth_token');
    const savedUser = localStorage.getItem('auth_user');

    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    setToken(data.token);
    setUser(data.user);
    localStorage.setItem('auth_token', data.token);
    localStorage.setItem('auth_user', JSON.stringify(data.user));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      login,
      signup,
      logout,
      isAuthenticated: !!token
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

### 2. Protected Route Component

```typescript
// frontend/components/ProtectedRoute.tsx
'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return <div>Loading...</div>;
  }

  return <>{children}</>;
}
```

## Multi-User Data Isolation

**Critical Pattern**: ALWAYS include user_id in queries to prevent cross-user data access.

### Backend Service Pattern

```python
# CORRECT: User isolation enforced
def get_user_tasks(user_id: str, db: Session) -> List[Task]:
    tasks = db.exec(select(Task).where(Task.user_id == user_id)).all()
    return tasks

# INCORRECT: No isolation - security vulnerability!
def get_all_tasks(db: Session) -> List[Task]:
    tasks = db.exec(select(Task)).all()  # Returns ALL users' tasks!
    return tasks
```

### API Endpoint Pattern

```python
@router.get("/api/users/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Verify user_id matches authenticated user
    if user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    tasks = get_user_tasks(user_id, db)
    return {"tasks": tasks}
```

## Security Best Practices

1. **Password Hashing**: Use bcrypt with salt (via passlib)
2. **Token Storage**: Store JWT in localStorage (frontend)
3. **Token Validation**: Verify JWT signature and expiration on every request
4. **HTTPS Only**: Use HTTPS in production for token transmission
5. **Secret Key**: Store SECRET_KEY in environment variables
6. **Token Expiration**: Set reasonable expiration time (30 minutes recommended)
7. **User Isolation**: ALWAYS check user_id in database queries
8. **Input Validation**: Validate email format, password strength
9. **Rate Limiting**: Implement rate limiting on auth endpoints
10. **SQL Injection**: Use parameterized queries (SQLModel does this automatically)

## Testing Checklist

- [ ] Signup with valid credentials succeeds
- [ ] Signup with existing email fails
- [ ] Login with valid credentials succeeds
- [ ] Login with invalid credentials fails
- [ ] JWT token is returned and saved
- [ ] Protected routes require authentication
- [ ] Invalid JWT tokens are rejected
- [ ] Expired tokens are rejected
- [ ] User can only access their own data
- [ ] Logout clears token and redirects

## Common Issues & Solutions

### Issue: "401 Unauthorized" on protected routes
- **Cause**: Token not included in request or invalid
- **Solution**: Check Authorization header format: `Bearer <token>`

### Issue: User can see other users' data
- **Cause**: Missing user_id check in queries
- **Solution**: Always filter by user_id in database queries

### Issue: Token expires too quickly
- **Cause**: Short expiration time
- **Solution**: Increase ACCESS_TOKEN_EXPIRE_MINUTES or implement refresh tokens

### Issue: CORS errors
- **Cause**: Frontend and backend on different origins
- **Solution**: Configure CORS middleware in FastAPI:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Related Patterns

- [Database Pattern](./database-pattern.md) - PostgreSQL + SQLModel
- [API Pattern](./api-pattern.md) - FastAPI REST endpoints

## References

- Better Auth Documentation: https://betterauth.com
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- JWT.io: https://jwt.io/
