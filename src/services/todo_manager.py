"""TodoManager service for managing tasks."""

from typing import Dict, List, Optional
from src.models.task import Task


class TodoManager:
    """
    Manages todo tasks in memory.

    Attributes:
        _tasks: Dictionary mapping task IDs to Task objects
        _next_id: Counter for generating unique task IDs
    """

    def __init__(self):
        """Initialize empty todo manager."""
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(self, title: str, description: str = "") -> Task:
        """
        Add a new task to the manager.

        Args:
            title: Task title (required, non-empty)
            description: Task description (optional)

        Returns:
            Created Task object

        Raises:
            ValueError: If title validation fails
        """
        task_id = self._next_id
        task = Task(id=task_id, title=title, description=description)
        self._tasks[task_id] = task
        self._next_id += 1
        return task

    def list_tasks(self) -> List[Task]:
        """
        Get all tasks.

        Returns:
            List of all Task objects (may be empty)
        """
        return list(self._tasks.values())

    def toggle_completion(self, task_id: int) -> bool:
        """
        Toggle completion status of a task.

        Args:
            task_id: ID of the task to toggle

        Returns:
            True if task was toggled, False if task not found
        """
        task = self._tasks.get(task_id)
        if not task:
            return False

        task.completed = not task.completed
        return True

    def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> bool:
        """
        Update a task's title and/or description.

        Args:
            task_id: ID of the task to update
            title: New title (None to keep current)
            description: New description (None to keep current)

        Returns:
            True if task was updated, False if task not found

        Raises:
            ValueError: If validation fails (empty title, too long, etc.)
        """
        task = self._tasks.get(task_id)
        if not task:
            return False

        # Validate title if provided
        if title is not None:
            if not title or not title.strip():
                raise ValueError("Task title cannot be empty")
            if len(title) > 200:
                raise ValueError("Task title cannot exceed 200 characters")

        # Validate description if provided
        if description is not None:
            if len(description) > 1000:
                raise ValueError("Task description cannot exceed 1000 characters")

        # Update fields while preserving completion status
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description

        return True

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID.

        Args:
            task_id: ID of the task to delete

        Returns:
            True if task was deleted, False if task not found

        Note:
            Deleted task IDs are not reused - _next_id only increments
        """
        if task_id not in self._tasks:
            return False

        del self._tasks[task_id]
        return True
