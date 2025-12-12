"""
Task management routes for CRUD operations.

This module handles:
- Creating tasks
- Retrieving task lists
- Updating tasks
- Deleting tasks
- Toggling task completion status

All endpoints require JWT authentication and enforce user-level data isolation.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlmodel import Session, select
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from ..db import get_session
from ..models import Task
from ..middleware.auth import verify_jwt

# Create API router with JWT authentication
router = APIRouter(
    prefix="/api",
    tags=["tasks"],
    dependencies=[Depends(verify_jwt)]  # All routes require authentication
)


# Pydantic models for request validation
class CreateTaskRequest(BaseModel):
    """Request model for creating a new task."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")


class UpdateTaskRequest(BaseModel):
    """Request model for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="New task title")
    description: Optional[str] = Field(None, max_length=1000, description="New task description")


@router.get("/{user_id}/tasks", response_model=List[Task])
def get_tasks(
    user_id: str,
    request: Request,
    session: Session = Depends(get_session),
    status: Optional[str] = "all"
):
    """
    Get all tasks for the authenticated user.

    Args:
        user_id: User ID from URL (must match authenticated user)
        request: FastAPI request with user_id in state
        session: Database session
        status: Filter by completion status (all|pending|completed)

    Returns:
        List of Task objects ordered by creation date (newest first)

    Raises:
        HTTPException 403: User ID mismatch (unauthorized access)
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot access other user's tasks"
        )

    # Build query
    statement = select(Task).where(Task.user_id == user_id)

    # Apply status filter
    if status == "pending":
        statement = statement.where(Task.completed == False)
    elif status == "completed":
        statement = statement.where(Task.completed == True)

    # Order by creation date (newest first)
    statement = statement.order_by(Task.created_at.desc())

    # Execute query
    tasks = session.exec(statement).all()
    return tasks


@router.post("/{user_id}/tasks", response_model=Task, status_code=201)
def create_task(
    user_id: str,
    task_data: CreateTaskRequest,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user.

    Args:
        user_id: User ID from URL (must match authenticated user)
        task_data: Task creation data (title, description)
        request: FastAPI request with user_id in state
        session: Database session

    Returns:
        Created Task object with generated ID and timestamps

    Raises:
        HTTPException 403: User ID mismatch
        HTTPException 400: Validation error
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot create task for other user"
        )

    # Create new task
    task = Task(
        user_id=user_id,
        title=task_data.title.strip(),
        description=task_data.description.strip() if task_data.description else None,
        completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.get("/{user_id}/tasks/{task_id}", response_model=Task)
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
        Task object

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

    return task


@router.put("/{user_id}/tasks/{task_id}", response_model=Task)
def update_task(
    user_id: str,
    task_id: int,
    task_data: UpdateTaskRequest,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Update a task's title and/or description.

    Args:
        user_id: User ID from URL
        task_id: Task ID
        task_data: Updated task data
        request: FastAPI request with user_id in state
        session: Database session

    Returns:
        Updated Task object

    Raises:
        HTTPException 403: User ID mismatch
        HTTPException 404: Task not found
        HTTPException 400: Validation error
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Get task
    task = session.get(Task, task_id)

    # Verify task exists and belongs to user
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields if provided
    if task_data.title is not None:
        task.title = task_data.title.strip()

    if task_data.description is not None:
        task.description = task_data.description.strip() if task_data.description else None

    # Update timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


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

    # Delete task
    session.delete(task)
    session.commit()

    return {"message": "Task deleted successfully", "id": task_id}


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=Task)
def toggle_task_completion(
    user_id: str,
    task_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Toggle task completion status (completed ↔ incomplete).

    Args:
        user_id: User ID from URL
        task_id: Task ID
        request: FastAPI request with user_id in state
        session: Database session

    Returns:
        Updated Task object with toggled completion status

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
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task
