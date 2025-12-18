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
from ..models import User, UserPreferences
from ..middleware.auth import verify_jwt
from fastapi import Request

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Helper function to get authenticated user ID
async def get_auth_user_id(request: Request) -> str:
    """Extract authenticated user ID from request after JWT verification."""
    await verify_jwt(request)
    return request.state.user_id

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


# Phase III: AI Opt-in/Preferences Models
class AIOptInRequest(BaseModel):
    """Request model for AI opt-in."""
    privacy_consent_version: str = Field(default="1.0.0", description="Privacy policy version")
    preferred_language: str = Field(default="en", description="Preferred language (en or ur)")


class AIPreferencesUpdate(BaseModel):
    """Request model for updating AI preferences."""
    preferred_language: str | None = Field(None, description="Preferred language (en or ur)")
    auto_detect_language: bool | None = Field(None, description="Auto-detect language")
    voice_input_enabled: bool | None = Field(None, description="Enable voice input")


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


# ============================================================================
# Phase III: AI Opt-in/Preferences Endpoints
# ============================================================================

@router.post("/users/{user_id}/ai/opt-in", status_code=201)
async def ai_opt_in(
    user_id: str,
    request: AIOptInRequest,
    session: Session = Depends(get_session),
    auth_user_id: str = Depends(get_auth_user_id)
):
    """
    Enable AI features for a user (Phase III).

    Creates or updates UserPreferences with AI enabled and privacy consent.

    Args:
        user_id: User ID from path
        request: Opt-in request with privacy consent version
        session: Database session
        auth_user_id: Authenticated user ID from JWT

    Returns:
        User preferences with AI enabled

    Raises:
        HTTPException 403: Cannot opt-in for another user
        HTTPException 400: Validation error
    """
    # Verify user can only opt-in for themselves
    if auth_user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot manage AI preferences for another user"
        )

    # Check if preferences already exist
    statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
    preferences = session.exec(statement).first()

    if preferences:
        # Update existing preferences
        preferences.ai_enabled = True
        preferences.ai_opt_in_date = datetime.utcnow()
        preferences.privacy_consent_version = request.privacy_consent_version
        preferences.preferred_language = request.preferred_language
        preferences.updated_at = datetime.utcnow()
    else:
        # Create new preferences
        preferences = UserPreferences(
            user_id=user_id,
            ai_enabled=True,
            ai_opt_in_date=datetime.utcnow(),
            privacy_consent_version=request.privacy_consent_version,
            preferred_language=request.preferred_language
        )
        session.add(preferences)

    session.commit()
    session.refresh(preferences)

    return {
        "user_id": preferences.user_id,
        "ai_enabled": preferences.ai_enabled,
        "preferred_language": preferences.preferred_language,
        "privacy_consent_version": preferences.privacy_consent_version,
        "message": "AI features enabled successfully"
    }


@router.post("/users/{user_id}/ai/opt-out")
async def ai_opt_out(
    user_id: str,
    delete_history: bool = False,
    session: Session = Depends(get_session),
    auth_user_id: str = Depends(get_auth_user_id)
):
    """
    Disable AI features for a user (Phase III).

    Optionally deletes chat history when opting out.

    Args:
        user_id: User ID from path
        delete_history: Whether to delete chat history
        session: Database session
        auth_user_id: Authenticated user ID from JWT

    Returns:
        Confirmation message

    Raises:
        HTTPException 403: Cannot opt-out for another user
        HTTPException 404: Preferences not found
    """
    # Verify user can only opt-out for themselves
    if auth_user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot manage AI preferences for another user"
        )

    # Get existing preferences
    statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
    preferences = session.exec(statement).first()

    if not preferences:
        raise HTTPException(
            status_code=404,
            detail="AI preferences not found - user has not opted in"
        )

    # Disable AI
    preferences.ai_enabled = False
    preferences.updated_at = datetime.utcnow()

    # Optionally delete chat history
    if delete_history:
        from ..models import Conversation, Message

        # Delete all conversations and messages
        conversations = session.exec(
            select(Conversation).where(Conversation.user_id == user_id)
        ).all()

        for conversation in conversations:
            # Delete messages first (foreign key constraint)
            messages = session.exec(
                select(Message).where(Message.conversation_id == conversation.id)
            ).all()
            for message in messages:
                session.delete(message)

            # Then delete conversation
            session.delete(conversation)

    session.commit()

    return {
        "user_id": user_id,
        "ai_enabled": False,
        "history_deleted": delete_history,
        "message": "AI features disabled successfully"
    }


@router.get("/users/{user_id}/ai/preferences")
async def get_ai_preferences(
    user_id: str,
    session: Session = Depends(get_session),
    auth_user_id: str = Depends(get_auth_user_id)
):
    """
    Get user's AI preferences (Phase III).

    Args:
        user_id: User ID from path
        session: Database session
        auth_user_id: Authenticated user ID from JWT

    Returns:
        User preferences or None if not opted in

    Raises:
        HTTPException 403: Cannot access another user's preferences
    """
    # Verify user can only access their own preferences
    if auth_user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot access another user's AI preferences"
        )

    # Get preferences
    statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
    preferences = session.exec(statement).first()

    if not preferences:
        return {
            "user_id": user_id,
            "ai_enabled": False,
            "message": "User has not opted in to AI features"
        }

    return {
        "user_id": preferences.user_id,
        "ai_enabled": preferences.ai_enabled,
        "preferred_language": preferences.preferred_language,
        "auto_detect_language": preferences.auto_detect_language,
        "voice_input_enabled": preferences.voice_input_enabled,
        "privacy_consent_version": preferences.privacy_consent_version,
        "ai_opt_in_date": preferences.ai_opt_in_date.isoformat() if preferences.ai_opt_in_date else None
    }


@router.patch("/users/{user_id}/ai/preferences")
async def update_ai_preferences(
    user_id: str,
    request: AIPreferencesUpdate,
    session: Session = Depends(get_session),
    auth_user_id: str = Depends(get_auth_user_id)
):
    """
    Update user's AI preferences (Phase III).

    Args:
        user_id: User ID from path
        request: Preferences update request
        session: Database session
        auth_user_id: Authenticated user ID from JWT

    Returns:
        Updated preferences

    Raises:
        HTTPException 403: Cannot update another user's preferences
        HTTPException 404: Preferences not found
        HTTPException 400: Validation error
    """
    # Verify user can only update their own preferences
    if auth_user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot update another user's AI preferences"
        )

    # Get existing preferences
    statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
    preferences = session.exec(statement).first()

    if not preferences:
        raise HTTPException(
            status_code=404,
            detail="AI preferences not found - please opt-in first"
        )

    # Update fields if provided
    if request.preferred_language is not None:
        if request.preferred_language not in ['en', 'ur']:
            raise HTTPException(
                status_code=400,
                detail="Invalid language - must be 'en' or 'ur'"
            )
        preferences.preferred_language = request.preferred_language

    if request.auto_detect_language is not None:
        preferences.auto_detect_language = request.auto_detect_language

    if request.voice_input_enabled is not None:
        preferences.voice_input_enabled = request.voice_input_enabled

    preferences.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(preferences)

    return {
        "user_id": preferences.user_id,
        "ai_enabled": preferences.ai_enabled,
        "preferred_language": preferences.preferred_language,
        "auto_detect_language": preferences.auto_detect_language,
        "voice_input_enabled": preferences.voice_input_enabled,
        "message": "Preferences updated successfully"
    }
