"""
Task management routes for CRUD operations (Phase V Enhanced).

This module handles:
- Creating tasks with advanced features (recurring, due dates, priorities, tags)
- Retrieving task lists with filtering, search, and sorting
- Updating tasks
- Deleting tasks
- Toggling task completion status (with recurring task handling)

All endpoints require JWT authentication and enforce user-level data isolation.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sqlmodel import Session, select, or_, and_
from typing import Optional, List
from datetime import datetime

from ..db import get_session
from ..models import Task, Priority
from ..middleware.auth import verify_jwt
from ..schemas import TaskCreateRequest, TaskUpdateRequest, TaskFilterParams
from ..utils import (
    serialize_tags,
    deserialize_tags,
    serialize_recurrence_days,
    deserialize_recurrence_days,
    calculate_next_occurrence,
    build_task_dict_response
)
from ..events import (
    sync_publish_event,
    publish_task_created,
    publish_task_updated,
    publish_task_completed,
    publish_task_deleted,
    publish_recurring_task_completed
)

# Create API router with JWT authentication
router = APIRouter(
    prefix="/api",
    tags=["tasks"],
    dependencies=[Depends(verify_jwt)]  # All routes require authentication
)


@router.get("/{user_id}/tasks")
def get_tasks(
    user_id: str,
    request: Request,
    session: Session = Depends(get_session),
    status: Optional[str] = Query("all", regex="^(all|pending|completed)$"),
    priority: Optional[str] = Query(None, regex="^(high|medium|low)$"),
    tags: Optional[str] = None,
    search: Optional[str] = None,
    due_date_before: Optional[datetime] = None,
    due_date_after: Optional[datetime] = None,
    is_recurring: Optional[bool] = None,
    sort_by: str = Query("created_at", regex="^(created_at|due_date|priority|title|updated_at)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get all tasks for the authenticated user with advanced filtering and sorting.

    Args:
        user_id: User ID from URL (must match authenticated user)
        request: FastAPI request with user_id in state
        session: Database session
        status: Filter by completion status (all|pending|completed)
        priority: Filter by priority (high|medium|low)
        tags: Comma-separated tags to filter by
        search: Search term for title/description
        due_date_before: Filter tasks due before this date
        due_date_after: Filter tasks due after this date
        is_recurring: Filter recurring tasks
        sort_by: Field to sort by
        sort_order: Sort order (asc|desc)
        limit: Maximum number of results
        offset: Number of results to skip

    Returns:
        List of Task dictionaries with deserialized tags and recurrence_days

    Raises:
        HTTPException 403: User ID mismatch
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Cannot access other user's tasks")

    # Build base query
    statement = select(Task).where(Task.user_id == user_id)

    # Apply status filter
    if status == "pending":
        statement = statement.where(Task.completed == False)
    elif status == "completed":
        statement = statement.where(Task.completed == True)

    # Apply priority filter
    if priority:
        statement = statement.where(Task.priority == priority)

    # Apply tags filter
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        for tag in tag_list:
            statement = statement.where(Task.tags.contains(tag))

    # Apply search filter
    if search:
        search_term = f"%{search}%"
        statement = statement.where(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term)
            )
        )

    # Apply due date filters
    if due_date_before:
        statement = statement.where(Task.due_date <= due_date_before)

    if due_date_after:
        statement = statement.where(Task.due_date >= due_date_after)

    # Apply recurring filter
    if is_recurring is not None:
        statement = statement.where(Task.is_recurring == is_recurring)

    # Apply sorting
    if sort_by == "priority":
        # Custom priority sorting (high > medium > low)
        if sort_order == "desc":
            statement = statement.order_by(
                Task.priority.desc()  # Will order alphabetically, but we can use CASE later
            )
        else:
            statement = statement.order_by(Task.priority.asc())
    else:
        order_column = getattr(Task, sort_by)
        if sort_order == "desc":
            statement = statement.order_by(order_column.desc())
        else:
            statement = statement.order_by(order_column.asc())

    # Apply pagination
    statement = statement.offset(offset).limit(limit)

    # Execute query
    tasks = session.exec(statement).all()

    # Convert to dicts with deserialized JSON fields
    return [build_task_dict_response(task) for task in tasks]


@router.post("/{user_id}/tasks", status_code=201)
def create_task(
    user_id: str,
    task_data: TaskCreateRequest,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Create a new task with advanced features.

    Args:
        user_id: User ID from URL
        task_data: Task creation data
        request: FastAPI request with user_id in state
        session: Database session

    Returns:
        Created Task dictionary

    Raises:
        HTTPException 403: User ID mismatch
        HTTPException 400: Validation error
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Cannot create task for other user")

    # Validate recurring task fields
    if task_data.is_recurring:
        if not task_data.recurrence_pattern:
            raise HTTPException(
                status_code=400,
                detail="recurrence_pattern is required for recurring tasks"
            )
        if task_data.recurrence_pattern == "weekly" and not task_data.recurrence_days:
            raise HTTPException(
                status_code=400,
                detail="recurrence_days is required for weekly recurring tasks"
            )

    # Create new task
    task = Task(
        user_id=user_id,
        title=task_data.title.strip(),
        description=task_data.description.strip() if task_data.description else None,
        completed=False,
        priority=task_data.priority if task_data.priority else Priority.MEDIUM.value,
        tags=serialize_tags(task_data.tags),
        due_date=task_data.due_date,
        remind_before_minutes=task_data.remind_before_minutes,
        reminder_sent=False,
        is_recurring=task_data.is_recurring or False,
        recurrence_pattern=task_data.recurrence_pattern,
        recurrence_interval=task_data.recurrence_interval,
        recurrence_days=serialize_recurrence_days(task_data.recurrence_days),
        recurrence_end_date=task_data.recurrence_end_date,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    # Build response
    task_dict = build_task_dict_response(task)

    # Publish task-created event to Kafka (Phase V)
    sync_publish_event("task-events", {
        "event_type": "created",
        "task_id": task.id,
        "user_id": user_id,
        "task_data": task_dict,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "source": "backend-api",
            "version": "1.0"
        }
    })

    return task_dict


@router.get("/{user_id}/tasks/{task_id}")
def get_task(
    user_id: str,
    task_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Get a single task by ID.

    Args:
        user_id: User ID from URL
        task_id: Task ID
        request: FastAPI request with user_id in state
        session: Database session

    Returns:
        Task dictionary

    Raises:
        HTTPException 403: User ID mismatch
        HTTPException 404: Task not found
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Get task
    task = session.get(Task, task_id)

    # Verify task exists and belongs to user
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    return build_task_dict_response(task)


@router.put("/{user_id}/tasks/{task_id}")
def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdateRequest,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Update a task's fields.

    Args:
        user_id: User ID from URL
        task_id: Task ID
        task_data: Updated task data
        request: FastAPI request with user_id in state
        session: Database session

    Returns:
        Updated Task dictionary

    Raises:
        HTTPException 403: User ID mismatch
        HTTPException 404: Task not found
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Get task
    task = session.get(Task, task_id)

    # Verify task exists and belongs to user
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Track changes for event publishing
    changes = {}

    # Update fields if provided
    if task_data.title is not None:
        changes["title"] = task_data.title.strip()
        task.title = task_data.title.strip()

    if task_data.description is not None:
        changes["description"] = task_data.description.strip() if task_data.description else None
        task.description = task_data.description.strip() if task_data.description else None

    if task_data.completed is not None:
        changes["completed"] = task_data.completed
        task.completed = task_data.completed

    if task_data.priority is not None:
        changes["priority"] = task_data.priority
        task.priority = task_data.priority

    if task_data.tags is not None:
        changes["tags"] = task_data.tags
        task.tags = serialize_tags(task_data.tags)

    if task_data.due_date is not None:
        changes["due_date"] = task_data.due_date.isoformat() if task_data.due_date else None
        task.due_date = task_data.due_date
        task.reminder_sent = False  # Reset reminder if due date changes

    if task_data.remind_before_minutes is not None:
        changes["remind_before_minutes"] = task_data.remind_before_minutes
        task.remind_before_minutes = task_data.remind_before_minutes

    # Update timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    # Build response
    task_dict = build_task_dict_response(task)

    # Publish task-updated events to Kafka (Phase V)
    if changes:
        # Audit event
        sync_publish_event("task-events", {
            "event_type": "updated",
            "task_id": task_id,
            "user_id": user_id,
            "task_data": task_dict,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "source": "backend-api",
                "version": "1.0",
                "changes": changes
            }
        })

        # Real-time sync event
        sync_publish_event("task-updates", {
            "event_type": "task_updated",
            "task_id": task_id,
            "user_id": user_id,
            "changes": changes,
            "timestamp": datetime.utcnow().isoformat()
        })

    return task_dict


@router.delete("/{user_id}/tasks/{task_id}")
def delete_task(
    user_id: str,
    task_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Permanently delete a task.

    Args:
        user_id: User ID from URL
        task_id: Task ID
        request: FastAPI request with user_id in state
        session: Database session

    Returns:
        Success message with deleted task ID

    Raises:
        HTTPException 403: User ID mismatch
        HTTPException 404: Task not found
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Get task
    task = session.get(Task, task_id)

    # Verify task exists and belongs to user
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Save task data for event before deletion
    task_dict = build_task_dict_response(task)

    # Delete task
    session.delete(task)
    session.commit()

    # Publish task-deleted event to Kafka (Phase V)
    sync_publish_event("task-events", {
        "event_type": "deleted",
        "task_id": task_id,
        "user_id": user_id,
        "task_data": task_dict,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "source": "backend-api",
            "version": "1.0"
        }
    })

    return {"message": "Task deleted successfully", "id": task_id}


@router.patch("/{user_id}/tasks/{task_id}/complete")
def toggle_task_completion(
    user_id: str,
    task_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Toggle task completion status.

    For recurring tasks, this will:
    1. Mark the current instance as complete
    2. Create a new task instance for the next occurrence

    Args:
        user_id: User ID from URL
        task_id: Task ID
        request: FastAPI request with user_id in state
        session: Database session

    Returns:
        Updated Task dictionary (and new task info if recurring)

    Raises:
        HTTPException 403: User ID mismatch
        HTTPException 404: Task not found
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Get task
    task = session.get(Task, task_id)

    # Verify task exists and belongs to user
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Toggle completion status
    was_completed = task.completed
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    # Build response
    task_dict = build_task_dict_response(task)
    response = {
        "task": task_dict
    }

    # Publish completion event (Phase V)
    if task.completed and not was_completed:
        sync_publish_event("task-events", {
            "event_type": "completed",
            "task_id": task_id,
            "user_id": user_id,
            "task_data": task_dict,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "source": "backend-api",
                "version": "1.0",
                "is_recurring": task.is_recurring
            }
        })

    # Handle recurring task completion
    if task.is_recurring and task.completed and not was_completed:
        # Task was just marked as complete (not uncompleted)
        # Create next instance if within recurrence end date

        if task.recurrence_end_date and datetime.utcnow() >= task.recurrence_end_date:
            response["message"] = "Task completed. Recurrence ended."
            return response

        try:
            # Calculate next occurrence
            next_date = calculate_next_occurrence(
                pattern=task.recurrence_pattern,
                interval=task.recurrence_interval or 1,
                recurrence_days=deserialize_recurrence_days(task.recurrence_days),
                current_date=task.due_date if task.due_date else datetime.utcnow()
            )

            # Check if next occurrence is before end date
            if task.recurrence_end_date and next_date > task.recurrence_end_date:
                response["message"] = "Task completed. No more recurrences."
                return response

            # Determine parent_task_id
            parent_id = task.parent_task_id if task.parent_task_id else task.id

            # Create new task instance
            new_task = Task(
                user_id=user_id,
                title=task.title,
                description=task.description,
                completed=False,
                priority=task.priority,
                tags=task.tags,
                due_date=next_date,
                remind_before_minutes=task.remind_before_minutes,
                reminder_sent=False,
                is_recurring=True,
                recurrence_pattern=task.recurrence_pattern,
                recurrence_interval=task.recurrence_interval,
                recurrence_days=task.recurrence_days,
                recurrence_end_date=task.recurrence_end_date,
                parent_task_id=parent_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(new_task)
            session.commit()
            session.refresh(new_task)

            # Build new task response
            new_task_dict = build_task_dict_response(new_task)
            response["next_task"] = new_task_dict
            response["message"] = "Task completed. Next occurrence created."

            # Publish recurring-tasks event (Phase V)
            sync_publish_event("recurring-tasks", {
                "event_type": "recurring_task_completed",
                "task_id": task_id,
                "parent_task_id": parent_id,
                "user_id": user_id,
                "recurrence_pattern": task.recurrence_pattern,
                "recurrence_interval": task.recurrence_interval or 1,
                "recurrence_days": deserialize_recurrence_days(task.recurrence_days),
                "next_occurrence": next_date.isoformat(),
                "recurrence_end_date": task.recurrence_end_date.isoformat() if task.recurrence_end_date else None,
                "task_data": task_dict,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Publish task-created event for new instance (Phase V)
            sync_publish_event("task-events", {
                "event_type": "created",
                "task_id": new_task.id,
                "user_id": user_id,
                "task_data": new_task_dict,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "source": "backend-api",
                    "version": "1.0",
                    "created_from_recurring": True,
                    "parent_task_id": parent_id
                }
            })

        except Exception as e:
            # If recurring task creation fails, still return the completed task
            response["message"] = f"Task completed, but failed to create next occurrence: {str(e)}"

    return response
