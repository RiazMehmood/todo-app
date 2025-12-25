"""
Time Entry Model - Track time spent working on tasks

Implements: Time tracking entity from data-model.md
- Track task work sessions with start/end times
- Auto-calculate elapsed seconds
- Support for ongoing timers (ended_at = null)
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid


class TimeEntry(SQLModel, table=True):
    """
    Time tracking entry for tasks.

    Stores work sessions with automatic elapsed time calculation.
    """
    __tablename__ = "time_entries"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for time entry"
    )

    task_id: uuid.UUID = Field(
        foreign_key="tasks.id",
        index=True,
        description="Task being worked on"
    )

    user_id: str = Field(
        foreign_key="users.id",
        index=True,
        max_length=255,
        description="User who performed the work"
    )

    started_at: datetime = Field(
        description="When timer started"
    )

    ended_at: Optional[datetime] = Field(
        default=None,
        description="When timer stopped (null if still running)"
    )

    elapsed_seconds: Optional[int] = Field(
        default=None,
        description="Calculated duration in seconds"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional note about work done"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Entry creation timestamp"
    )

    def calculate_elapsed(self) -> int:
        """
        Calculate elapsed seconds between start and end time.

        Returns:
            Elapsed seconds, or 0 if timer still running
        """
        if self.ended_at and self.started_at:
            delta = self.ended_at - self.started_at
            return int(delta.total_seconds())
        return 0

    def stop_timer(self) -> None:
        """
        Stop the timer and calculate elapsed time.
        """
        if not self.ended_at:
            self.ended_at = datetime.utcnow()
            self.elapsed_seconds = self.calculate_elapsed()


# Pydantic models for API requests/responses

class TimeEntryCreate(SQLModel):
    """Request model for creating a time entry."""
    task_id: uuid.UUID
    started_at: datetime
    ended_at: Optional[datetime] = None
    description: Optional[str] = None


class TimeEntryUpdate(SQLModel):
    """Request model for updating a time entry."""
    ended_at: Optional[datetime] = None
    description: Optional[str] = None


class TimeEntryResponse(SQLModel):
    """Response model for time entry."""
    id: uuid.UUID
    task_id: uuid.UUID
    user_id: str
    started_at: datetime
    ended_at: Optional[datetime]
    elapsed_seconds: Optional[int]
    description: Optional[str]
    created_at: datetime
