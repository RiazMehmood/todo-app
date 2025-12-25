"""
Bulk Operations API Routes

Provides endpoints for:
- Bulk task updates (update multiple tasks at once)
- Bulk task deletions (delete multiple tasks at once)
- Detailed error reporting with item-level tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from ..db import get_session
from ..middleware.auth import verify_jwt
from ..services.template_service import BulkOperationService
from ..config import BULK_OPERATION_LIMIT

router = APIRouter(dependencies=[Depends(verify_jwt)])


# === Request Schemas ===

class BulkUpdateRequest(BaseModel):
    """Schema for bulk update request"""
    task_ids: List[int] = Field(
        description=f"List of task IDs to update (max {BULK_OPERATION_LIMIT})"
    )
    updates: Dict[str, Any] = Field(
        description="Fields to update (title, description, status, priority, tags, due_date)"
    )


class BulkDeleteRequest(BaseModel):
    """Schema for bulk delete request"""
    task_ids: List[int] = Field(
        description=f"List of task IDs to delete (max {BULK_OPERATION_LIMIT})"
    )
    confirm: bool = Field(
        default=False,
        description="Confirmation flag (must be true to proceed)"
    )


# === Bulk Update Endpoint ===

@router.post("/{user_id}/tasks/bulk-update")
def bulk_update_tasks(
    user_id: str,
    bulk_request: BulkUpdateRequest,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    **Bulk Update Tasks**

    Updates multiple tasks with the same field values.

    **Use Cases:**
    - Mark multiple tasks as completed
    - Change priority for all tasks in a sprint
    - Apply tags to a group of tasks
    - Update status for project tasks

    **Request Body:**
    ```json
    {
      "task_ids": [1, 2, 3, 4, 5],
      "updates": {
        "status": "completed",
        "priority": "low"
      }
    }
    ```

    **Allowed Update Fields:**
    - `title`: Task title (string)
    - `description`: Task description (string)
    - `status`: Task status ('pending', 'in_progress', 'completed')
    - `priority`: Task priority ('low', 'medium', 'high')
    - `tags`: Task tags (array of strings)
    - `due_date`: Due date (ISO datetime string)

    **Limits:**
    - Max {BULK_OPERATION_LIMIT} tasks per request
    - Individual authorization checks (user must own all tasks)
    - Item-level error tracking (partial success supported)

    **Returns:**
    - `summary`: Overall statistics (total, succeeded, failed, success_rate)
    - `successful_ids`: Array of task IDs that were updated
    - `failures`: Array of error objects with task_id and reason
    - `error_summary`: Count of errors by type

    **Example Response:**
    ```json
    {
      "summary": {
        "total": 5,
        "succeeded": 4,
        "failed": 1,
        "success_rate": "80.0%"
      },
      "successful_ids": [1, 2, 3, 4],
      "failures": [
        {
          "task_id": 5,
          "error_type": "not_found",
          "message": "Task not found or unauthorized"
        }
      ],
      "error_summary": {
        "not_found": 1
      }
    }
    ```
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot update other user's tasks"
        )

    # Validate request
    if not bulk_request.task_ids:
        raise HTTPException(
            status_code=400,
            detail="task_ids array cannot be empty"
        )

    if not bulk_request.updates:
        raise HTTPException(
            status_code=400,
            detail="updates object cannot be empty"
        )

    # Perform bulk update
    try:
        result = BulkOperationService.bulk_update_tasks(
            session=session,
            user_id=user_id,
            task_ids=bulk_request.task_ids,
            updates=bulk_request.updates
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Bulk update failed: {str(e)}"
        )


# === Bulk Delete Endpoint ===

@router.post("/{user_id}/tasks/bulk-delete")
def bulk_delete_tasks(
    user_id: str,
    bulk_request: BulkDeleteRequest,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    **Bulk Delete Tasks**

    Permanently deletes multiple tasks at once.

    **⚠️ WARNING**: This action cannot be undone!

    **Use Cases:**
    - Clean up completed tasks
    - Remove cancelled project tasks
    - Delete spam/duplicate tasks

    **Request Body:**
    ```json
    {
      "task_ids": [1, 2, 3, 4, 5],
      "confirm": true
    }
    ```

    **Required:**
    - `confirm`: Must be `true` to proceed (safety mechanism)

    **Limits:**
    - Max {BULK_OPERATION_LIMIT} tasks per request
    - Individual authorization checks (user must own all tasks)
    - Item-level error tracking (partial success supported)

    **Returns:**
    - `summary`: Overall statistics (total, succeeded, failed, success_rate)
    - `successful_ids`: Array of task IDs that were deleted
    - `failures`: Array of error objects with task_id and reason
    - `error_summary`: Count of errors by type

    **Example Response:**
    ```json
    {
      "summary": {
        "total": 5,
        "succeeded": 5,
        "failed": 0,
        "success_rate": "100.0%"
      },
      "successful_ids": [1, 2, 3, 4, 5],
      "failures": [],
      "error_summary": {}
    }
    ```
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot delete other user's tasks"
        )

    # Validate request
    if not bulk_request.task_ids:
        raise HTTPException(
            status_code=400,
            detail="task_ids array cannot be empty"
        )

    # Require confirmation
    if not bulk_request.confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required. Set 'confirm' to true to proceed with deletion."
        )

    # Perform bulk delete
    try:
        result = BulkOperationService.bulk_delete_tasks(
            session=session,
            user_id=user_id,
            task_ids=bulk_request.task_ids
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Bulk delete failed: {str(e)}"
        )


# === Bulk Operation Limits Endpoint ===

@router.get("/{user_id}/tasks/bulk-limits")
def get_bulk_operation_limits(
    user_id: str,
    request: Request
):
    """
    **Get Bulk Operation Limits**

    Returns the current limits for bulk operations.

    Useful for client-side validation before submitting requests.

    **Returns:**
    - `max_tasks_per_request`: Maximum number of tasks per bulk operation
    - `rate_limit`: Rate limiting information (if implemented)
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot access other user's limits"
        )

    return {
        "max_tasks_per_request": BULK_OPERATION_LIMIT,
        "allowed_update_fields": [
            "title",
            "description",
            "status",
            "priority",
            "tags",
            "due_date"
        ],
        "rate_limit": {
            "requests_per_minute": 10,
            "note": "Rate limiting not yet implemented"
        }
    }
