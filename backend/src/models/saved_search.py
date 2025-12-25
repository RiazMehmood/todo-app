"""
SavedSearch Model

Stores user-defined search queries for quick access and reuse.
Supports complex filters including full-text search, status, priority, tags, and date ranges.
"""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4


class SavedSearch(SQLModel, table=True):
    """
    Model for storing saved search queries.

    Allows users to save complex search configurations and reuse them quickly.
    Query parameters are stored as JSONB for flexibility.
    """

    __tablename__ = "saved_searches"

    # Primary key
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the saved search"
    )

    # User reference
    user_id: str = Field(
        max_length=255,
        index=True,
        description="User who owns this saved search"
    )

    # Search metadata
    name: str = Field(
        min_length=1,
        max_length=100,
        description="User-friendly name for the search (e.g., 'Hot List', 'Overdue Tasks')"
    )

    # Query parameters stored as JSONB
    query_params: Dict[str, Any] = Field(
        default={},
        sa_column=Column(JSONB),
        description="Search parameters including query text, filters, sorting"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this search was created"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this search was last modified"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "name": "High Priority Work Tasks",
                "query_params": {
                    "query": "urgent meeting",
                    "filters": {
                        "status": ["pending", "in_progress"],
                        "priority": ["high"],
                        "tags": ["work"],
                        "created_after": "2025-12-01",
                        "due_before": "2025-12-31"
                    },
                    "sort_by": "due_date",
                    "sort_order": "asc"
                }
            }
        }


class SavedSearchCreate(SQLModel):
    """Schema for creating a new saved search"""
    name: str = Field(min_length=1, max_length=100)
    query_params: Dict[str, Any] = Field(default={})


class SavedSearchUpdate(SQLModel):
    """Schema for updating a saved search"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    query_params: Optional[Dict[str, Any]] = None


class SavedSearchResponse(SQLModel):
    """Schema for saved search API responses"""
    id: UUID
    user_id: str
    name: str
    query_params: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
