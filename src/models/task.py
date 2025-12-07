"""Task data model for the todo application."""

from dataclasses import dataclass


@dataclass
class Task:
    """
    Represents a todo item.

    Attributes:
        id: Unique task identifier (positive integer)
        title: Task title (required, non-empty, max 200 chars)
        description: Task description (optional, max 1000 chars)
        completed: Completion status (default False)
    """

    id: int
    title: str
    description: str = ""
    completed: bool = False

    def __post_init__(self):
        """Validate task data after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")
        if len(self.description) > 1000:
            raise ValueError("Task description cannot exceed 1000 characters")
