"""
Database models for the Todo application.

This module defines SQLModel ORM models for User and Task entities.
User model is managed by Better Auth, Task model is managed by the application.
"""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String
from datetime import datetime
from typing import Optional


class User(SQLModel, table=True):
    """
    User model (managed by Better Auth).

    This table is created and managed by Better Auth library.
    The application should not modify user records directly.
    """
    __tablename__ = "users"

    id: str = Field(primary_key=True, max_length=255)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=100)
    password_hash: str = Field(max_length=255)
    email_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Task(SQLModel, table=True):
    """
    Task model for todo items.

    Each task belongs to a user (user_id foreign key).
    Supports title, description, completion status, and timestamps.

    Phase III Enhancement: Added AI metadata fields for chatbot integration.
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, max_length=255)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Phase III: AI Metadata
    created_via_ai: bool = Field(default=False, index=True)
    ai_suggested_priority: Optional[int] = Field(default=None, ge=1, le=5)
    original_nl_input: Optional[str] = Field(default=None)


class UserPreferences(SQLModel, table=True):
    """
    User preferences for AI features (Phase III).

    Stores user opt-in status, language preferences, and privacy consent.
    One record per user (enforced by unique constraint on user_id).
    """
    __tablename__ = "user_preferences"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", unique=True, index=True, max_length=255)
    ai_enabled: bool = Field(default=False)
    ai_opt_in_date: Optional[datetime] = Field(default=None)
    preferred_language: str = Field(default="en", max_length=10)
    privacy_consent_version: Optional[str] = Field(default=None, max_length=10)
    auto_detect_language: bool = Field(default=True)
    voice_input_enabled: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Conversation(SQLModel, table=True):
    """
    Chat conversation session (Phase III - Hackathon Page 18).

    Groups related messages into conversation sessions.
    Each user can have multiple conversations.
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    """
    Individual chat message (Phase III - Hackathon Page 18).

    Stores messages exchanged between user and AI assistant.
    Core attributes per hackathon spec + optional enhancements.
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, max_length=255)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=10)  # 'user' or 'assistant'
    content: str = Field(min_length=1, max_length=2000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Enhanced attributes (optional)
    language: Optional[str] = Field(default=None, max_length=10)  # 'en' or 'ur'
    related_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")
    intent_detected: Optional[str] = Field(default=None, max_length=50)
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    extra_data: Optional[str] = Field(default=None, sa_column=Column("metadata", String))  # Maps to 'metadata' column in DB
