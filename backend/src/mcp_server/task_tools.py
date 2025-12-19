"""
MCP Server for Task Management Tools (Phase III).

Implements the 5 required MCP tools per Hackathon specification:
- add_task
- list_tasks
- complete_task
- delete_task
- update_task

Uses FastMCP for easy server creation and tool registration.
"""

from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, List, Dict, Any
from sqlmodel import Session
from ..models import Task
from ..services.task_service import TaskService


# Initialize FastMCP server
mcp = FastMCP(
    name="TaskManagementMCP",
    version="1.0.0",
    description="MCP server for todo task management operations"
)


@mcp.tool()
async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Add a new task for the user.

    Required by Hackathon: add_task(user_id, title, description)

    Args:
        user_id: User ID for task ownership
        title: Task title (1-200 characters)
        description: Optional task description

    Returns:
        {"task_id": int, "status": "created", "title": str}
    """
    # Get database session from context
    session: Session = ctx.request_context.get("db")
    original_message: str = ctx.request_context.get("original_message", "")

    try:
        # Create task using TaskService
        task = TaskService.create_task(
            session=session,
            user_id=user_id,
            title=title,
            description=description,
            created_via_ai=True,
            original_nl_input=original_message
        )

        # Log progress
        await ctx.info(f"Created task: {task.title}")

        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title,
            "description": task.description,
            "completed": task.completed
        }

    except ValueError as e:
        await ctx.error(f"Validation error: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }
    except Exception as e:
        await ctx.error(f"Error creating task: {str(e)}")
        return {
            "status": "error",
            "message": "Failed to create task"
        }


@mcp.tool()
async def list_tasks(
    user_id: str,
    status: Optional[str] = None,
    search: Optional[str] = None,
    ctx: Context = None
) -> List[Dict[str, Any]]:
    """
    List user's tasks, optionally filtered.

    Required by Hackathon: list_tasks(user_id, status)

    Args:
        user_id: User ID for task ownership
        status: Filter by status ('completed', 'pending', or None for all)
        search: Optional search term

    Returns:
        Array of task objects
    """
    # Get database session from context
    session: Session = ctx.request_context.get("db")

    try:
        # Determine completed filter
        completed_filter = None
        if status == "completed":
            completed_filter = True
        elif status == "pending":
            completed_filter = False

        # Get tasks using TaskService
        tasks = TaskService.list_tasks(
            session=session,
            user_id=user_id,
            completed=completed_filter,
            search=search
        )

        # Convert to dictionaries
        result = []
        for task in tasks:
            result.append({
                "id": task.id,
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "created_via_ai": task.created_via_ai
            })

        await ctx.info(f"Found {len(result)} tasks")

        return result

    except Exception as e:
        await ctx.error(f"Error listing tasks: {str(e)}")
        return []


@mcp.tool()
async def complete_task(
    user_id: str,
    task_id: int,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Mark a task as complete.

    Required by Hackathon: complete_task(user_id, task_id)

    Args:
        user_id: User ID for authorization
        task_id: Task ID to complete

    Returns:
        {"task_id": int, "status": "completed", "title": str}
    """
    # Get database session from context
    session: Session = ctx.request_context.get("db")

    try:
        # Complete task using TaskService
        task = TaskService.complete_task(
            session=session,
            user_id=user_id,
            task_id=task_id
        )

        if not task:
            await ctx.warn(f"Task {task_id} not found")
            return {
                "status": "error",
                "message": "Task not found",
                "task_id": task_id
            }

        await ctx.info(f"Completed task: {task.title}")

        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title,
            "completed": task.completed
        }

    except Exception as e:
        await ctx.error(f"Error completing task: {str(e)}")
        return {
            "status": "error",
            "message": "Failed to complete task",
            "task_id": task_id
        }


@mcp.tool()
async def delete_task(
    user_id: str,
    task_id: int,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Delete a task.

    Required by Hackathon: delete_task(user_id, task_id)

    Args:
        user_id: User ID for authorization
        task_id: Task ID to delete

    Returns:
        {"task_id": int, "status": "deleted", "title": str}
    """
    # Get database session from context
    session: Session = ctx.request_context.get("db")

    try:
        # Get task first to capture title
        task = TaskService.get_task(session, user_id, task_id)

        if not task:
            await ctx.warn(f"Task {task_id} not found")
            return {
                "status": "error",
                "message": "Task not found",
                "task_id": task_id
            }

        title = task.title

        # Delete task using TaskService
        deleted = TaskService.delete_task(
            session=session,
            user_id=user_id,
            task_id=task_id
        )

        if deleted:
            await ctx.info(f"Deleted task: {title}")
            return {
                "task_id": task_id,
                "status": "deleted",
                "title": title
            }
        else:
            return {
                "status": "error",
                "message": "Failed to delete task",
                "task_id": task_id
            }

    except Exception as e:
        await ctx.error(f"Error deleting task: {str(e)}")
        return {
            "status": "error",
            "message": "Failed to delete task",
            "task_id": task_id
        }


@mcp.tool()
async def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Update an existing task.

    Required by Hackathon: update_task(user_id, task_id, title, description)

    Args:
        user_id: User ID for authorization
        task_id: Task ID to update
        title: New title (optional)
        description: New description (optional)
        completed: New completion status (optional)

    Returns:
        {"task_id": int, "status": "updated", "title": str}
    """
    # Get database session from context
    session: Session = ctx.request_context.get("db")

    try:
        # Update task using TaskService
        task = TaskService.update_task(
            session=session,
            user_id=user_id,
            task_id=task_id,
            title=title,
            description=description,
            completed=completed
        )

        if not task:
            await ctx.warn(f"Task {task_id} not found")
            return {
                "status": "error",
                "message": "Task not found",
                "task_id": task_id
            }

        await ctx.info(f"Updated task: {task.title}")

        return {
            "task_id": task.id,
            "status": "updated",
            "title": task.title,
            "description": task.description,
            "completed": task.completed
        }

    except ValueError as e:
        await ctx.error(f"Validation error: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "task_id": task_id
        }
    except Exception as e:
        await ctx.error(f"Error updating task: {str(e)}")
        return {
            "status": "error",
            "message": "Failed to update task",
            "task_id": task_id
        }


@mcp.resource("tasks://summary")
async def get_task_summary(ctx: Context = None) -> Dict[str, Any]:
    """
    Get summary of user's tasks (MCP Resource).

    Returns task statistics: total, completed, pending, etc.
    """
    user_id = ctx.request_context.get("user_id")
    session: Session = ctx.request_context.get("db")

    try:
        summary = TaskService.get_task_summary(session, user_id)
        await ctx.info(f"Generated task summary for user {user_id}")
        return summary
    except Exception as e:
        await ctx.error(f"Error generating summary: {str(e)}")
        return {
            "status": "error",
            "message": "Failed to generate summary"
        }


# Export the MCP server instance
__all__ = ["mcp"]
