"""
Templates API Routes

Provides endpoints for:
- Task template CRUD operations
- Template instantiation with placeholder replacement
- Template validation and preview
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from typing import List
from uuid import UUID
from datetime import datetime

from ..db import get_session
from ..middleware.auth import verify_jwt
from ..models.task_template import (
    TaskTemplate,
    TaskTemplateCreate,
    TaskTemplateUpdate,
    TaskTemplateResponse,
    InstantiateTemplateRequest
)
from ..services.template_service import TemplateProcessor

router = APIRouter(dependencies=[Depends(verify_jwt)])


# === Template CRUD Endpoints ===

@router.get("/{user_id}/templates", response_model=List[TaskTemplateResponse])
def get_templates(
    user_id: str,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    **Get All Templates**

    Retrieves all task templates for the authenticated user.

    **Returns:**
    List of templates with tasks definitions and placeholders.
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot access other user's templates"
        )

    # Query templates
    statement = select(TaskTemplate).where(
        TaskTemplate.user_id == user_id
    ).order_by(TaskTemplate.created_at.desc())

    templates = session.exec(statement).all()

    return templates


@router.get("/{user_id}/templates/{template_id}", response_model=TaskTemplateResponse)
def get_template(
    user_id: str,
    template_id: UUID,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    **Get Template by ID**

    Retrieves a specific task template.

    **Returns:**
    Template details with tasks definition and placeholders.
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot access other user's templates"
        )

    # Query template
    template = session.get(TaskTemplate, template_id)

    if not template or template.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Template not found"
        )

    return template


@router.post("/{user_id}/templates", response_model=TaskTemplateResponse, status_code=201)
def create_template(
    user_id: str,
    template_data: TaskTemplateCreate,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    **Create Template**

    Creates a new task template with placeholder support.

    **Request Body:**
    - `name`: Template name (1-100 chars, unique per user)
    - `description`: Template description (optional, max 500 chars)
    - `tasks_definition`: Array of task objects with placeholders

    **Task Definition Format:**
    ```json
    {
      "title": "{{CLIENT_NAME}} - Initial Meeting",
      "description": "Schedule kickoff with {{CLIENT_NAME}}",
      "priority": "high",
      "tags": ["onboarding", "{{CLIENT_NAME}}"],
      "due_date_offset": 0
    }
    ```

    **Placeholder Syntax:**
    - Use `{{VARIABLE_NAME}}` format
    - Variable names must be UPPERCASE with underscores
    - Max 10 unique placeholders per template
    - Max 50 tasks per template

    **Due Date Offset:**
    - Relative days from base date (e.g., 0 = same day, 1 = next day, -1 = previous day)

    **Validation:**
    - Automatically detects placeholders from tasks
    - Validates task count and placeholder count
    - Ensures all tasks have required fields

    **Returns:**
    Created template with auto-detected placeholders.
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot create template for other user"
        )

    # Validate template
    is_valid, placeholders, error = TemplateProcessor.validate_template(
        template_data.tasks_definition
    )

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=error
        )

    # Check for duplicate name
    existing = session.exec(
        select(TaskTemplate).where(
            TaskTemplate.user_id == user_id,
            TaskTemplate.name == template_data.name
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Template with name '{template_data.name}' already exists"
        )

    # Create template
    template = TaskTemplate(
        user_id=user_id,
        name=template_data.name,
        description=template_data.description,
        tasks_definition=template_data.tasks_definition,
        placeholders=placeholders  # Auto-detected from tasks
    )

    session.add(template)
    session.commit()
    session.refresh(template)

    return template


@router.put("/{user_id}/templates/{template_id}", response_model=TaskTemplateResponse)
def update_template(
    user_id: str,
    template_id: UUID,
    template_data: TaskTemplateUpdate,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    **Update Template**

    Updates name, description, or tasks definition of a template.

    **Request Body:**
    - `name`: New name (optional)
    - `description`: New description (optional)
    - `tasks_definition`: New tasks array (optional)

    **Returns:**
    Updated template with re-detected placeholders.
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot update other user's templates"
        )

    # Get template
    template = session.get(TaskTemplate, template_id)

    if not template or template.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Template not found"
        )

    # Update fields
    if template_data.name is not None:
        # Check for duplicate name (excluding current template)
        existing = session.exec(
            select(TaskTemplate).where(
                TaskTemplate.user_id == user_id,
                TaskTemplate.name == template_data.name,
                TaskTemplate.id != template_id
            )
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Template with name '{template_data.name}' already exists"
            )

        template.name = template_data.name

    if template_data.description is not None:
        template.description = template_data.description

    if template_data.tasks_definition is not None:
        # Validate new tasks definition
        is_valid, placeholders, error = TemplateProcessor.validate_template(
            template_data.tasks_definition
        )

        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=error
            )

        template.tasks_definition = template_data.tasks_definition
        template.placeholders = placeholders  # Re-detect placeholders

    # Update timestamp
    template.updated_at = datetime.utcnow()

    session.add(template)
    session.commit()
    session.refresh(template)

    return template


@router.delete("/{user_id}/templates/{template_id}")
def delete_template(
    user_id: str,
    template_id: UUID,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    **Delete Template**

    Permanently deletes a task template.

    **Note**: This does not affect tasks created from this template.

    **Returns:**
    Success message with deleted template ID.
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot delete other user's templates"
        )

    # Get template
    template = session.get(TaskTemplate, template_id)

    if not template or template.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Template not found"
        )

    # Delete
    session.delete(template)
    session.commit()

    return {
        "message": "Template deleted successfully",
        "id": str(template_id)
    }


# === Template Instantiation Endpoint ===

@router.post("/{user_id}/templates/{template_id}/instantiate")
def instantiate_template(
    user_id: str,
    template_id: UUID,
    instantiate_request: InstantiateTemplateRequest,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    **Instantiate Template**

    Creates tasks from a template by replacing placeholders with values.

    **Request Body:**
    - `placeholder_values`: Dict mapping placeholder names to values
    - `base_due_date`: Optional base date for due_date_offset calculations (ISO format)

    **Example:**
    ```json
    {
      "placeholder_values": {
        "CLIENT_NAME": "Acme Corp",
        "PROJECT_TYPE": "Website"
      },
      "base_due_date": "2025-12-30T00:00:00Z"
    }
    ```

    **Process:**
    1. Validates all required placeholders are provided
    2. Replaces placeholders in titles, descriptions, and tags
    3. Calculates due dates from base_due_date + offset
    4. Creates all tasks in a single transaction

    **Returns:**
    - `created_tasks`: Array of created tasks with IDs
    - `template_name`: Name of the template used
    - `placeholder_values`: Values that were used
    - `errors`: List of any errors that occurred (per-task)
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot instantiate template for other user"
        )

    # Get template
    template = session.get(TaskTemplate, template_id)

    if not template or template.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Template not found"
        )

    # Parse base_due_date if provided
    base_due_date = None
    if instantiate_request.base_due_date:
        try:
            base_due_date = datetime.fromisoformat(instantiate_request.base_due_date)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail="Invalid base_due_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"
            )

    # Instantiate template
    try:
        created_tasks, errors = TemplateProcessor.instantiate_template(
            session=session,
            user_id=user_id,
            template=template,
            placeholder_values=instantiate_request.placeholder_values,
            base_due_date=base_due_date
        )

        return {
            "created_tasks": created_tasks,
            "template_name": template.name,
            "placeholder_values": instantiate_request.placeholder_values,
            "summary": {
                "total_tasks": len(template.tasks_definition),
                "created": len(created_tasks),
                "failed": len(errors)
            },
            "errors": errors if errors else []
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to instantiate template: {str(e)}"
        )


# === Template Validation Endpoint ===

@router.post("/{user_id}/templates/validate")
def validate_template(
    user_id: str,
    template_data: TaskTemplateCreate,
    request: Request
):
    """
    **Validate Template**

    Validates a template without saving it.

    Useful for client-side validation before creating template.

    **Returns:**
    - `is_valid`: Boolean indicating if template is valid
    - `placeholders`: List of detected placeholders
    - `error`: Error message if invalid (empty string if valid)
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot validate template for other user"
        )

    # Validate
    is_valid, placeholders, error = TemplateProcessor.validate_template(
        template_data.tasks_definition
    )

    return {
        "is_valid": is_valid,
        "placeholders": placeholders,
        "error": error,
        "task_count": len(template_data.tasks_definition),
        "placeholder_count": len(placeholders)
    }
