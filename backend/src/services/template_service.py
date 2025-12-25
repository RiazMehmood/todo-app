"""
TemplateService

Provides template processing functionality including:
- Placeholder detection and validation
- Variable substitution with {{VARIABLE}} syntax
- Template instantiation with date offset calculations
- Transaction-safe multi-task creation
"""

from sqlmodel import Session
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import re

from ..models import Task
from ..models.task_template import TaskTemplate
from ..config import BULK_OPERATION_LIMIT


class TemplateProcessor:
    """
    Service for processing task templates with placeholder replacement.

    Handles validation, placeholder detection, and template instantiation.
    """

    # Placeholder pattern: {{VARIABLE_NAME}}
    PLACEHOLDER_PATTERN = r'\{\{([A-Z_][A-Z0-9_]*)\}\}'
    MAX_PLACEHOLDERS = 10
    MAX_TASKS_PER_TEMPLATE = 50

    @staticmethod
    def detect_placeholders(text: str) -> List[str]:
        """
        Extract all {{VARIABLE}} placeholders from text.

        Args:
            text: Text containing placeholders

        Returns:
            List of unique placeholder names (without braces)

        Example:
            >>> detect_placeholders("Hello {{NAME}}, welcome to {{COMPANY}}!")
            ['NAME', 'COMPANY']
        """
        if not text:
            return []

        matches = re.findall(TemplateProcessor.PLACEHOLDER_PATTERN, text)
        return list(set(matches))  # Remove duplicates

    @staticmethod
    def replace_placeholders(text: str, values: Dict[str, str]) -> str:
        """
        Replace {{VARIABLE}} placeholders with provided values.

        Args:
            text: Text containing placeholders
            values: Dict mapping placeholder names to replacement values

        Returns:
            Text with placeholders replaced

        Example:
            >>> replace_placeholders("Hello {{NAME}}", {"NAME": "John"})
            'Hello John'
        """
        if not text:
            return text

        result = text
        for var_name, var_value in values.items():
            # Sanitize value (prevent injection, limit length)
            sanitized_value = TemplateProcessor._sanitize_value(var_value)

            # Replace all occurrences of {{VAR_NAME}}
            pattern = r'\{\{' + re.escape(var_name) + r'\}\}'
            result = re.sub(pattern, sanitized_value, result)

        return result

    @staticmethod
    def _sanitize_value(value: str) -> str:
        """
        Sanitize placeholder value to prevent injection attacks.

        Args:
            value: Raw placeholder value

        Returns:
            Sanitized value (max 100 chars, safe characters only)
        """
        # Remove potentially harmful characters
        # Allow: letters, numbers, spaces, common punctuation
        sanitized = re.sub(r'[^\w\s.,!?@#$%&*()+-]', '', value)

        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]

        return sanitized.strip()

    @staticmethod
    def validate_template(
        tasks_definition: List[Dict[str, Any]]
    ) -> Tuple[bool, List[str], str]:
        """
        Validate template and extract placeholders.

        Checks:
        - Max 50 tasks per template
        - Max 10 unique placeholders across all tasks
        - All task definitions have required fields

        Args:
            tasks_definition: List of task objects from template

        Returns:
            Tuple of (is_valid, placeholders, error_message)

        Example:
            >>> tasks = [{"title": "{{NAME}} - Task 1", "priority": "high"}]
            >>> is_valid, placeholders, error = validate_template(tasks)
            >>> is_valid
            True
            >>> placeholders
            ['NAME']
        """
        # Check task count
        if len(tasks_definition) > TemplateProcessor.MAX_TASKS_PER_TEMPLATE:
            return (
                False,
                [],
                f"Template exceeds maximum of {TemplateProcessor.MAX_TASKS_PER_TEMPLATE} tasks"
            )

        if len(tasks_definition) == 0:
            return (False, [], "Template must contain at least one task")

        # Collect all placeholders
        all_placeholders = set()

        for idx, task_def in enumerate(tasks_definition):
            # Validate required fields
            if not task_def.get("title"):
                return (
                    False,
                    [],
                    f"Task {idx + 1} is missing required field: title"
                )

            # Extract placeholders from title
            if task_def.get("title"):
                placeholders = TemplateProcessor.detect_placeholders(task_def["title"])
                all_placeholders.update(placeholders)

            # Extract placeholders from description
            if task_def.get("description"):
                placeholders = TemplateProcessor.detect_placeholders(task_def["description"])
                all_placeholders.update(placeholders)

            # Extract placeholders from tags
            if task_def.get("tags"):
                for tag in task_def["tags"]:
                    placeholders = TemplateProcessor.detect_placeholders(tag)
                    all_placeholders.update(placeholders)

            # Validate priority if present
            if task_def.get("priority"):
                if task_def["priority"] not in ["low", "medium", "high"]:
                    return (
                        False,
                        [],
                        f"Task {idx + 1} has invalid priority: {task_def['priority']}"
                    )

        # Check placeholder count
        if len(all_placeholders) > TemplateProcessor.MAX_PLACEHOLDERS:
            return (
                False,
                list(all_placeholders),
                f"Template exceeds maximum of {TemplateProcessor.MAX_PLACEHOLDERS} placeholders"
            )

        return (True, sorted(list(all_placeholders)), "")

    @staticmethod
    def instantiate_template(
        session: Session,
        user_id: str,
        template: TaskTemplate,
        placeholder_values: Dict[str, str],
        base_due_date: Optional[datetime] = None
    ) -> Tuple[List[Task], List[str]]:
        """
        Instantiate a template by creating tasks with placeholder replacement.

        Args:
            session: Database session
            user_id: User ID to assign tasks to
            template: TaskTemplate to instantiate
            placeholder_values: Map of placeholder names to values
            base_due_date: Base date for calculating due_date_offset (defaults to today)

        Returns:
            Tuple of (created_tasks, errors)

        Raises:
            ValueError: If placeholder values are missing or invalid
        """
        # Validate all required placeholders are provided
        missing_placeholders = set(template.placeholders) - set(placeholder_values.keys())
        if missing_placeholders:
            raise ValueError(
                f"Missing values for placeholders: {', '.join(sorted(missing_placeholders))}"
            )

        # Use today as base date if not provided
        if base_due_date is None:
            base_due_date = datetime.utcnow()

        created_tasks = []
        errors = []

        # Process each task definition
        for idx, task_def in enumerate(template.tasks_definition):
            try:
                # Replace placeholders in title
                title = TemplateProcessor.replace_placeholders(
                    task_def.get("title", ""),
                    placeholder_values
                )

                # Replace placeholders in description
                description = None
                if task_def.get("description"):
                    description = TemplateProcessor.replace_placeholders(
                        task_def["description"],
                        placeholder_values
                    )

                # Replace placeholders in tags
                tags = []
                if task_def.get("tags"):
                    tags = [
                        TemplateProcessor.replace_placeholders(tag, placeholder_values)
                        for tag in task_def["tags"]
                    ]

                # Calculate due date from offset
                due_date = None
                if task_def.get("due_date_offset") is not None:
                    offset_days = int(task_def["due_date_offset"])
                    due_date = base_due_date + timedelta(days=offset_days)

                # Create task
                task = Task(
                    user_id=user_id,
                    title=title,
                    description=description,
                    priority=task_def.get("priority", "medium"),
                    status="pending",
                    tags=tags if tags else None,
                    due_date=due_date
                )

                session.add(task)
                created_tasks.append(task)

            except Exception as e:
                error_msg = f"Task {idx + 1} failed: {str(e)}"
                errors.append(error_msg)

        # Commit all tasks in a single transaction
        if created_tasks:
            try:
                session.commit()

                # Refresh all tasks to get IDs
                for task in created_tasks:
                    session.refresh(task)

            except Exception as e:
                session.rollback()
                raise ValueError(f"Failed to create tasks: {str(e)}")

        return (created_tasks, errors)


class BulkOperationService:
    """
    Service for bulk task operations with detailed error tracking.

    Provides methods for bulk update and delete with item-level error reporting.
    """

    @staticmethod
    def bulk_update_tasks(
        session: Session,
        user_id: str,
        task_ids: List[int],
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update multiple tasks with detailed error tracking.

        Args:
            session: Database session
            user_id: User ID (for authorization)
            task_ids: List of task IDs to update
            updates: Dict of fields to update (e.g., {"priority": "high", "status": "completed"})

        Returns:
            Dict with:
            - summary: {total, succeeded, failed, success_rate}
            - successful_ids: List of task IDs that were updated
            - failures: List of error objects with task_id and reason
            - error_summary: Count of errors by type
        """
        # Enforce limit
        if len(task_ids) > BULK_OPERATION_LIMIT:
            raise ValueError(
                f"Bulk operation exceeds limit of {BULK_OPERATION_LIMIT} tasks"
            )

        successful_ids = []
        failures = []

        # Validate updates dict
        allowed_fields = {"title", "description", "status", "priority", "tags", "due_date"}
        invalid_fields = set(updates.keys()) - allowed_fields
        if invalid_fields:
            raise ValueError(f"Invalid fields in updates: {', '.join(invalid_fields)}")

        # Process each task individually
        for task_id in task_ids:
            try:
                # Get task
                task = session.query(Task).filter(
                    Task.id == task_id,
                    Task.user_id == user_id
                ).first()

                if not task:
                    failures.append({
                        "task_id": task_id,
                        "error_type": "not_found",
                        "message": "Task not found or unauthorized"
                    })
                    continue

                # Apply updates
                for field, value in updates.items():
                    setattr(task, field, value)

                # Update timestamp
                task.updated_at = datetime.utcnow()

                session.add(task)
                session.commit()
                successful_ids.append(task_id)

            except Exception as e:
                session.rollback()
                failures.append({
                    "task_id": task_id,
                    "error_type": "update_failed",
                    "message": str(e)
                })

        # Categorize errors
        error_summary = {}
        for failure in failures:
            error_type = failure["error_type"]
            error_summary[error_type] = error_summary.get(error_type, 0) + 1

        return {
            "summary": {
                "total": len(task_ids),
                "succeeded": len(successful_ids),
                "failed": len(failures),
                "success_rate": f"{(len(successful_ids) / len(task_ids) * 100):.1f}%"
            },
            "successful_ids": successful_ids,
            "failures": failures,
            "error_summary": error_summary
        }

    @staticmethod
    def bulk_delete_tasks(
        session: Session,
        user_id: str,
        task_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Delete multiple tasks with authorization checks.

        Args:
            session: Database session
            user_id: User ID (for authorization)
            task_ids: List of task IDs to delete

        Returns:
            Dict with summary, successful_ids, and failures
        """
        # Enforce limit
        if len(task_ids) > BULK_OPERATION_LIMIT:
            raise ValueError(
                f"Bulk operation exceeds limit of {BULK_OPERATION_LIMIT} tasks"
            )

        successful_ids = []
        failures = []

        # Process each task individually
        for task_id in task_ids:
            try:
                # Get task
                task = session.query(Task).filter(
                    Task.id == task_id,
                    Task.user_id == user_id
                ).first()

                if not task:
                    failures.append({
                        "task_id": task_id,
                        "error_type": "not_found",
                        "message": "Task not found or unauthorized"
                    })
                    continue

                # Delete task
                session.delete(task)
                session.commit()
                successful_ids.append(task_id)

            except Exception as e:
                session.rollback()
                failures.append({
                    "task_id": task_id,
                    "error_type": "delete_failed",
                    "message": str(e)
                })

        # Categorize errors
        error_summary = {}
        for failure in failures:
            error_type = failure["error_type"]
            error_summary[error_type] = error_summary.get(error_type, 0) + 1

        return {
            "summary": {
                "total": len(task_ids),
                "succeeded": len(successful_ids),
                "failed": len(failures),
                "success_rate": f"{(len(successful_ids) / len(task_ids) * 100):.1f}%"
            },
            "successful_ids": successful_ids,
            "failures": failures,
            "error_summary": error_summary
        }
