"""
Authentication routes for user signup and login.

This module handles user registration and authentication,
issuing JWT tokens for successful logins.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel, Field, EmailStr
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
import uuid

from ..db import get_session
from ..models import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_DAYS = int(os.getenv("JWT_EXPIRATION_DAYS", "7"))

# Create API router
router = APIRouter(prefix="/api/auth", tags=["auth"])


# Pydantic models for request validation
class SignupRequest(BaseModel):
    """Request model for user signup."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    name: str = Field(..., min_length=1, max_length=100, description="User display name")


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class AuthResponse(BaseModel):
    """Response model for successful authentication."""
    user: dict = Field(..., description="User information")
    token: str = Field(..., description="JWT authentication token")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt_token(user_id: str, email: str) -> str:
    """
    Create a JWT token for authenticated user.

    Args:
        user_id: User's unique identifier
        email: User's email address

    Returns:
        JWT token string
    """
    expiration = datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS)

    payload = {
        "user_id": user_id,
        "sub": user_id,  # Standard JWT subject claim
        "email": email,
        "exp": expiration,
        "iat": datetime.utcnow(),
    }

    token = jwt.encode(payload, BETTER_AUTH_SECRET, algorithm=JWT_ALGORITHM)
    return token


@router.post("/signup", response_model=AuthResponse, status_code=201)
def signup(
    request: SignupRequest,
    session: Session = Depends(get_session)
):
    """
    Register a new user account.

    - Validates email is not already registered
    - Hashes password securely
    - Creates user record in database
    - Issues JWT token

    Returns:
        AuthResponse with user info and JWT token

    Raises:
        HTTPException 409: Email already registered
        HTTPException 400: Validation error
    """
    # Check if email already exists
    statement = select(User).where(User.email == request.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    # Create new user
    user_id = f"usr_{uuid.uuid4().hex[:12]}"  # Generate unique user ID
    hashed_password = hash_password(request.password)

    new_user = User(
        id=user_id,
        email=request.email,
        name=request.name,
        password_hash=hashed_password,
        email_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Generate JWT token
    token = create_jwt_token(new_user.id, new_user.email)

    # Return user info (excluding password hash) and token
    return {
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "name": new_user.name
        },
        "token": token
    }


@router.post("/login", response_model=AuthResponse)
def login(
    request: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Authenticate user and issue JWT token.

    - Validates credentials
    - Issues JWT token on success

    Returns:
        AuthResponse with user info and JWT token

    Raises:
        HTTPException 401: Invalid credentials
    """
    # Find user by email
    statement = select(User).where(User.email == request.email)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # Generate JWT token
    token = create_jwt_token(user.id, user.email)

    # Return user info and token
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        },
        "token": token
    }
