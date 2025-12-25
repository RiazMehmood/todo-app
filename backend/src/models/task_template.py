"""
TaskTemplate Model

Stores reusable task templates with placeholders for customization.
Supports creating multiple tasks from a single template with variable substitution.
"""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID, uuid4


class TaskTemplate(SQLModel, table=True):
    """
    Model for storing task templates with placeholders.

    Allows users to create reusable templates for common task workflows
    (e.g., client onboarding, project setup, sprint planning).
    """

    __tablename__ = "task_templates"

    # Primary key
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the template"
    )

    # User reference
    user_id: str = Field(
        max_length=255,
        index=True,
        description="User who owns this template"
    )

    # Template metadata
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Template name (e.g., 'Client Onboarding', 'Sprint Setup')"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Template description explaining its purpose"
    )

    # Tasks definition stored as JSONB
    tasks_definition: List[Dict[str, Any]] = Field(
        default=[],
        sa_column=Column(JSONB),
        description="Array of task objects with placeholders (max 50 tasks)"
    )

    # Placeholders stored as JSONB array
    placeholders: List[str] = Field(
        default=[],
        sa_column=Column(JSONB),
        description="List of placeholder variable names (max 10 placeholders)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this template was created"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this template was last modified"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "name": "Client Onboarding",
                "description": "Standard onboarding workflow for new clients",
                "tasks_definition": [
                    {
                        "title": "{{CLIENT_NAME}} - Initial Meeting",
                        "description": "Schedule kickoff call with {{CLIENT_NAME}}",
                        "priority": "high",
                        "tags": ["onboarding", "{{CLIENT_NAME}}"],
                        "due_date_offset": 0
                    },
                    {
                        "title": "{{CLIENT_NAME}} - Setup Account",
                        "description": "Create account for {{CLIENT_NAME}} in system",
                        "priority": "medium",
                        "tags": ["onboarding", "setup"],
                        "due_date_offset": 1
                    }
                ],
                "placeholders": ["CLIENT_NAME"]
            }
        }


class TaskTemplateCreate(SQLModel):
    """Schema for creating a new task template"""
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    tasks_definition: List[Dict[str, Any]] = Field(default=[])


class TaskTemplateUpdate(SQLModel):
    """Schema for updating a task template"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    tasks_definition: Optional[List[Dict[str, Any]]] = None


class TaskTemplateResponse(SQLModel):
    """Schema for task template API responses"""
    id: UUID
    user_id: str
    name: str
    description: Optional[str]
    tasks_definition: List[Dict[str, Any]]
    placeholders: List[str]
    created_at: datetime
    updated_at: datetime


class InstantiateTemplateRequest(SQLModel):
    """Schema for template instantiation request"""
    placeholder_values: Dict[str, str] = Field(
        description="Map of placeholder names to values (e.g., {'CLIENT_NAME': 'Acme Corp'})"
    )
    base_due_date: Optional[str] = Field(
        None,
        description="Base due date for offset calculations (ISO format)"
    )
