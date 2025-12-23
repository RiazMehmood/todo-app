"""
Pydantic schemas for request/response validation (Phase V).

This module defines input/output models separate from database models
for better API design and validation.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from src.models import Priority


class TaskCreateRequest(BaseModel):
    """Request model for creating a new task"""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = Field(default=Priority.MEDIUM.value)
    tags: Optional[List[str]] = Field(default=None)

    # Advanced: Due Dates & Reminders
    due_date: Optional[datetime] = None
    remind_before_minutes: Optional[int] = Field(default=60, ge=0)

    # Advanced: Recurring Tasks
    is_recurring: Optional[bool] = False
    recurrence_pattern: Optional[str] = Field(default=None, pattern="^(daily|weekly|monthly)$")
    recurrence_interval: Optional[int] = Field(default=1, ge=1, le=365)
    recurrence_days: Optional[List[str]] = None  # ["monday", "tuesday", etc.]
    recurrence_end_date: Optional[datetime] = None

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        """Validate priority is one of: high, medium, low"""
        if v not in [Priority.HIGH.value, Priority.MEDIUM.value, Priority.LOW.value]:
            raise ValueError('Priority must be high, medium, or low')
        return v

    @field_validator('recurrence_days')
    @classmethod
    def validate_recurrence_days(cls, v, info):
        """Validate recurrence_days for weekly pattern"""
        if v is not None:
            valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            for day in v:
                if day.lower() not in valid_days:
                    raise ValueError(f'Invalid day: {day}')
        return v


class TaskUpdateRequest(BaseModel):
    """Request model for updating a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    remind_before_minutes: Optional[int] = Field(None, ge=0)

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        """Validate priority if provided"""
        if v is not None and v not in [Priority.HIGH.value, Priority.MEDIUM.value, Priority.LOW.value]:
            raise ValueError('Priority must be high, medium, or low')
        return v


class TaskResponse(BaseModel):
    """Response model for task data"""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    tags: Optional[str]  # JSON string

    # Advanced features
    due_date: Optional[datetime]
    remind_before_minutes: Optional[int]
    reminder_sent: bool
    is_recurring: bool
    recurrence_pattern: Optional[str]
    recurrence_interval: Optional[int]
    recurrence_days: Optional[str]  # JSON string
    recurrence_end_date: Optional[datetime]
    parent_task_id: Optional[int]

    # AI metadata
    created_via_ai: bool
    ai_suggested_priority: Optional[int]
    original_nl_input: Optional[str]

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskFilterParams(BaseModel):
    """Query parameters for filtering and searching tasks"""
    status: Optional[str] = "all"  # all, pending, completed
    priority: Optional[str] = None  # high, medium, low
    tags: Optional[str] = None  # Comma-separated: "work,urgent"
    search: Optional[str] = None  # Search in title/description
    due_date_before: Optional[datetime] = None
    due_date_after: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    sort_by: str = "created_at"  # created_at, due_date, priority, title, updated_at
    sort_order: str = "desc"  # asc, desc
    limit: Optional[int] = Field(default=100, le=1000)
    offset: Optional[int] = Field(default=0, ge=0)

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Validate status filter"""
        if v not in ["all", "pending", "completed"]:
            raise ValueError('Status must be all, pending, or completed')
        return v

    @field_validator('sort_by')
    @classmethod
    def validate_sort_by(cls, v):
        """Validate sort field"""
        valid_fields = ["created_at", "due_date", "priority", "title", "updated_at"]
        if v not in valid_fields:
            raise ValueError(f'sort_by must be one of: {", ".join(valid_fields)}')
        return v

    @field_validator('sort_order')
    @classmethod
    def validate_sort_order(cls, v):
        """Validate sort order"""
        if v not in ["asc", "desc"]:
            raise ValueError('sort_order must be asc or desc')
        return v
