"""
Task Service for AI Agent Operations (Phase III).

Provides CRUD operations for tasks that are used by the AI agent through MCP tools.
Includes business logic for AI-created tasks and user isolation.
"""

from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models import Task


class TaskService:
    """
    Service layer for task operations used by AI agents.

    All operations enforce user isolation - tasks can only be accessed
    by the user who created them.
    """

    @staticmethod
    def create_task(
        session: Session,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        created_via_ai: bool = False,
        original_nl_input: Optional[str] = None,
        ai_suggested_priority: Optional[int] = None
    ) -> Task:
        """
        Create a new task for a user.

        Args:
            session: Database session
            user_id: User ID (for isolation)
            title: Task title (1-200 characters)
            description: Optional task description
            created_via_ai: Whether task was created by AI
            original_nl_input: Original natural language input from user
            ai_suggested_priority: AI-suggested priority (1-5)

        Returns:
            Created Task object

        Raises:
            ValueError: If validation fails
        """
        # Validate inputs
        if not title or len(title) > 200:
            raise ValueError("Title must be 1-200 characters")

        if description and len(description) > 1000:
            raise ValueError("Description must be max 1000 characters")

        if ai_suggested_priority and not (1 <= ai_suggested_priority <= 5):
            raise ValueError("AI priority must be between 1 and 5")

        # Create task
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            created_via_ai=created_via_ai,
            original_nl_input=original_nl_input,
            ai_suggested_priority=ai_suggested_priority,
            completed=False
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    @staticmethod
    def list_tasks(
        session: Session,
        user_id: str,
        completed: Optional[bool] = None,
        search: Optional[str] = None,
        limit: int = 100
    ) -> List[Task]:
        """
        List tasks for a user with optional filtering.

        Args:
            session: Database session
            user_id: User ID (for isolation)
            completed: Filter by completion status (None = all)
            search: Search term for title/description
            limit: Maximum number of tasks to return

        Returns:
            List of Task objects
        """
        # Base query with user isolation
        query = select(Task).where(Task.user_id == user_id)

        # Apply filters
        if completed is not None:
            query = query.where(Task.completed == completed)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (Task.title.like(search_pattern)) |
                (Task.description.like(search_pattern))
            )

        # Order by creation date (newest first) and limit
        query = query.order_by(Task.created_at.desc()).limit(limit)

        tasks = session.exec(query).all()
        return list(tasks)

    @staticmethod
    def get_task(
        session: Session,
        user_id: str,
        task_id: int
    ) -> Optional[Task]:
        """
        Get a single task by ID with user isolation.

        Args:
            session: Database session
            user_id: User ID (for isolation)
            task_id: Task ID

        Returns:
            Task object or None if not found
        """
        query = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        return session.exec(query).first()

    @staticmethod
    def update_task(
        session: Session,
        user_id: str,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        completed: Optional[bool] = None
    ) -> Optional[Task]:
        """
        Update an existing task.

        Args:
            session: Database session
            user_id: User ID (for isolation)
            task_id: Task ID
            title: New title (optional)
            description: New description (optional)
            completed: New completion status (optional)

        Returns:
            Updated Task object or None if not found

        Raises:
            ValueError: If validation fails
        """
        # Get task with user isolation
        task = TaskService.get_task(session, user_id, task_id)

        if not task:
            return None

        # Validate and update fields
        if title is not None:
            if not title or len(title) > 200:
                raise ValueError("Title must be 1-200 characters")
            task.title = title

        if description is not None:
            if len(description) > 1000:
                raise ValueError("Description must be max 1000 characters")
            task.description = description

        if completed is not None:
            task.completed = completed

        # Update timestamp
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    @staticmethod
    def delete_task(
        session: Session,
        user_id: str,
        task_id: int
    ) -> bool:
        """
        Delete a task.

        Args:
            session: Database session
            user_id: User ID (for isolation)
            task_id: Task ID

        Returns:
            True if deleted, False if not found
        """
        task = TaskService.get_task(session, user_id, task_id)

        if not task:
            return False

        session.delete(task)
        session.commit()

        return True

    @staticmethod
    def complete_task(
        session: Session,
        user_id: str,
        task_id: int
    ) -> Optional[Task]:
        """
        Mark a task as complete.

        Args:
            session: Database session
            user_id: User ID (for isolation)
            task_id: Task ID

        Returns:
            Updated Task object or None if not found
        """
        return TaskService.update_task(
            session,
            user_id,
            task_id,
            completed=True
        )

    @staticmethod
    def get_task_summary(
        session: Session,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get summary statistics for user's tasks.

        Args:
            session: Database session
            user_id: User ID (for isolation)

        Returns:
            Dictionary with task counts and statistics
        """
        all_tasks = TaskService.list_tasks(session, user_id, limit=1000)

        completed_tasks = [t for t in all_tasks if t.completed]
        pending_tasks = [t for t in all_tasks if not t.completed]
        ai_created_tasks = [t for t in all_tasks if t.created_via_ai]

        return {
            "total": len(all_tasks),
            "completed": len(completed_tasks),
            "pending": len(pending_tasks),
            "ai_created": len(ai_created_tasks),
            "completion_rate": len(completed_tasks) / len(all_tasks) if all_tasks else 0.0
        }
