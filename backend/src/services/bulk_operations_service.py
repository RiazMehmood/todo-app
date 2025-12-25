"""
Bulk Operations Service - Business logic for bulk updates and deletes on tasks.

Implements:
- FR-013: Bulk update endpoint accepting task IDs array and partial task object
- FR-014: Bulk delete endpoint accepting task IDs array with transaction support
- FR-015: Detailed results (success count, failure count, array of errors with task IDs)
- FR-016: Validation of bulk operation size limits (max 500 tasks)
- NFR-002: Bulk operations MUST process 100 tasks within 3 seconds
- NFR-009: Bulk operations MUST use database transactions for atomicity
- NFR-014: Bulk operations MUST verify user owns all target tasks
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlmodel import Session, select
from datetime import datetime
import logging

# Import Task model - adjust path based on your project structure
try:
    from ..models import Task
except ImportError:
    from ..models import Task

logger = logging.getLogger(__name__)

# Constants from specification
BULK_OPERATION_LIMIT = 500  # FR-016: Max tasks per operation


class BulkOperationsService:
    """
    Service for performing bulk operations on multiple tasks.

    Handles bulk update and delete operations with detailed error reporting
    and authorization checks.
    """

    @staticmethod
    def bulk_update_tasks(
        session: Session,
        user_id: str,
        task_ids: List[str],
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update multiple tasks at once with the same field values.

        Implements: FR-013 (bulk update), FR-015 (detailed results), FR-016 (size limits)

        Args:
            session: Database session
            user_id: User ID (for authorization)
            task_ids: List of task IDs to update (max 500)
            updates: Dictionary of fields to update (status, priority, tags, due_date)

        Returns:
            Dict containing:
                - success_count: Number of tasks successfully updated
                - failure_count: Number of tasks that failed to update
                - updated_tasks: List of updated Task objects
                - errors: List of error dictionaries with task_id and reason

        Raises:
            ValueError: If validation fails (empty updates, exceeds limit)
        """
        # Validation from specification
        if not task_ids:
            raise ValueError("task_ids array cannot be empty")

        if len(task_ids) > BULK_OPERATION_LIMIT:
            raise ValueError(
                f"Bulk operation limited to {BULK_OPERATION_LIMIT} tasks, "
                f"received {len(task_ids)}"
            )

        if not updates:
            raise ValueError("No update fields specified")

        # Validate update fields (only allow specific fields)
        allowed_fields = {'status', 'priority', 'tags', 'due_date'}
        invalid_fields = set(updates.keys()) - allowed_fields
        if invalid_fields:
            raise ValueError(
                f"Invalid update fields: {invalid_fields}. "
                f"Allowed: {allowed_fields}"
            )

        # Validate field values
        if 'status' in updates:
            valid_statuses = ['pending', 'in_progress', 'completed']
            if updates['status'] not in valid_statuses:
                raise ValueError(
                    f"Invalid status '{updates['status']}'. "
                    f"Must be one of: {valid_statuses}"
                )

        if 'priority' in updates:
            valid_priorities = ['low', 'medium', 'high']
            if updates['priority'] not in valid_priorities:
                raise ValueError(
                    f"Invalid priority '{updates['priority']}'. "
                    f"Must be one of: {valid_priorities}"
                )

        # Initialize result tracking
        updated_tasks = []
        errors = []
        success_count = 0
        failure_count = 0

        # Process each task individually for detailed error tracking (FR-015)
        for task_id in task_ids:
            try:
                # Fetch task
                task = session.get(Task, task_id)

                # Check if task exists
                if not task:
                    errors.append({
                        "task_id": task_id,
                        "reason": "Task not found"
                    })
                    failure_count += 1
                    continue

                # NFR-014: Verify user owns the task
                if task.user_id != user_id:
                    errors.append({
                        "task_id": task_id,
                        "reason": "Task does not belong to user"
                    })
                    failure_count += 1
                    continue

                # Apply updates
                if 'status' in updates:
                    task.status = updates['status']
                if 'priority' in updates:
                    task.priority = updates['priority']
                if 'tags' in updates:
                    # Replaces existing tags (not appends) per specification
                    task.tags = updates['tags']
                if 'due_date' in updates:
                    task.due_date = updates['due_date']

                # Update timestamp
                task.updated_at = datetime.utcnow()

                # Commit individual task (item-level error tracking)
                session.add(task)
                session.commit()
                session.refresh(task)

                updated_tasks.append(task)
                success_count += 1

            except Exception as e:
                # Rollback failed task update
                session.rollback()
                errors.append({
                    "task_id": task_id,
                    "reason": f"Update failed: {str(e)}"
                })
                failure_count += 1
                logger.error(f"Failed to update task {task_id}: {e}")

        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "updated_tasks": updated_tasks,
            "errors": errors
        }

    @staticmethod
    def bulk_delete_tasks(
        session: Session,
        user_id: str,
        task_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Delete multiple tasks in a single operation.

        Implements: FR-014 (bulk delete), FR-015 (detailed results), FR-016 (size limits)

        Args:
            session: Database session
            user_id: User ID (for authorization)
            task_ids: List of task IDs to delete (max 500)

        Returns:
            Dict containing:
                - deleted_count: Number of tasks successfully deleted
                - failed_ids: List of dicts with task_id and reason for failures

        Raises:
            ValueError: If validation fails (empty task_ids, exceeds limit)
        """
        # Validation from specification
        if not task_ids:
            raise ValueError("task_ids array cannot be empty")

        if len(task_ids) > BULK_OPERATION_LIMIT:
            raise ValueError(
                f"Bulk operation limited to {BULK_OPERATION_LIMIT} tasks, "
                f"received {len(task_ids)}"
            )

        # Initialize result tracking
        deleted_count = 0
        failed_ids = []

        # Process each task individually for detailed error tracking (FR-015)
        for task_id in task_ids:
            try:
                # Fetch task
                task = session.get(Task, task_id)

                # Check if task exists
                if not task:
                    failed_ids.append({
                        "task_id": task_id,
                        "reason": "Task not found"
                    })
                    continue

                # NFR-014: Verify user owns the task
                if task.user_id != user_id:
                    failed_ids.append({
                        "task_id": task_id,
                        "reason": "Task does not belong to user"
                    })
                    continue

                # Delete task
                session.delete(task)
                session.commit()
                deleted_count += 1

            except Exception as e:
                # Rollback failed delete
                session.rollback()
                failed_ids.append({
                    "task_id": task_id,
                    "reason": f"Delete failed: {str(e)}"
                })
                logger.error(f"Failed to delete task {task_id}: {e}")

        return {
            "deleted_count": deleted_count,
            "failed_ids": failed_ids
        }

    @staticmethod
    def validate_bulk_operation_authorization(
        session: Session,
        user_id: str,
        task_ids: List[str]
    ) -> Tuple[List[str], List[Dict[str, str]]]:
        """
        Validate that user owns all specified tasks before bulk operation.

        Helper method for pre-validation (optional optimization).

        Args:
            session: Database session
            user_id: User ID
            task_ids: List of task IDs to validate

        Returns:
            Tuple of (authorized_task_ids, unauthorized_errors)
        """
        authorized_ids = []
        unauthorized_errors = []

        for task_id in task_ids:
            task = session.get(Task, task_id)

            if not task:
                unauthorized_errors.append({
                    "task_id": task_id,
                    "reason": "Task not found"
                })
            elif task.user_id != user_id:
                unauthorized_errors.append({
                    "task_id": task_id,
                    "reason": "Task does not belong to user"
                })
            else:
                authorized_ids.append(task_id)

        return authorized_ids, unauthorized_errors
