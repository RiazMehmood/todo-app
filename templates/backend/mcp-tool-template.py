"""
MCP Tool Template - Official MCP Python SDK Pattern

This template demonstrates the pattern for creating MCP tools using the
official MCP Python SDK (mcp[cli]) with FastMCP.

Usage:
1. Copy this template
2. Replace TOOL_NAME with your tool name
3. Implement the tool logic
4. Add proper type hints and docstrings
5. Register tool with MCP server

Example from Phase III:
- add_task, list_tasks, complete_task, delete_task, update_task
"""

from mcp.server.fastmcp import FastMCP, Context
from sqlmodel import Session, select
from typing import Optional, List, Dict, Any
import logging

# Initialize MCP server (do this once per file)
mcp = FastMCP("YourMCPServerName", json_response=True)

logger = logging.getLogger(__name__)


@mcp.tool()
async def TOOL_NAME(
    user_id: str,
    required_param: str,
    optional_param: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    One-line description of what this tool does.

    Args:
        user_id: The user performing the action (required for multi-user isolation)
        required_param: Description of required parameter
        optional_param: Description of optional parameter
        ctx: MCP context object (provides access to db, config, etc.)

    Returns:
        Dictionary with standardized response format:
        {
            "status": "success" | "error",
            "data": {...},  # Tool-specific result data
            "message": "Human-readable message"
        }

    Raises:
        ValueError: If validation fails
        Exception: For unexpected errors
    """
    try:
        # 1. Get dependencies from context
        db: Session = ctx.get("db")
        config: dict = ctx.get("config", {})

        # 2. Input validation
        if not user_id:
            raise ValueError("user_id is required")
        if not required_param:
            raise ValueError("required_param is required")

        # 3. Business logic
        # TODO: Implement your tool logic here
        # Example: Query database, perform operations, etc.

        # result = await some_operation(user_id, required_param)

        # 4. Log operation
        logger.info(f"TOOL_NAME executed for user {user_id}")

        # 5. Return standardized response
        return {
            "status": "success",
            "data": {
                "result": "your_result_here"
            },
            "message": f"Successfully executed TOOL_NAME"
        }

    except ValueError as e:
        logger.error(f"Validation error in TOOL_NAME: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Validation failed"
        }
    except Exception as e:
        logger.error(f"Unexpected error in TOOL_NAME: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Tool execution failed"
        }


# Example: Real MCP tool from Phase III (add_task)
@mcp.tool()
async def add_task(
    user_id: str,
    title: str,
    description: str = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Add a new task for the user (Hackathon requirement).

    Args:
        user_id: User ID performing the action
        title: Task title (required)
        description: Task description (optional)
        ctx: MCP context

    Returns:
        {
            "task_id": int,
            "status": "created",
            "title": str
        }
    """
    try:
        db: Session = ctx.get("db")

        # Validation
        if not title or len(title) < 1 or len(title) > 200:
            raise ValueError("Title must be 1-200 characters")

        # Create task
        from models import Task

        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            created_via_ai=True
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        logger.info(f"Task {task.id} created via MCP for user {user_id}")

        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title
        }

    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


# Best Practices:
# 1. Always validate user_id for multi-user isolation
# 2. Use type hints for all parameters
# 3. Return standardized response format
# 4. Log all operations for debugging
# 5. Handle errors gracefully with try/except
# 6. Use async/await for database operations
# 7. Keep tools focused on single responsibility
# 8. Document with clear docstrings
# 9. Test with different user contexts
# 10. Follow MCP protocol specifications

# Testing:
# - Test with valid inputs
# - Test with invalid inputs (validation)
# - Test with different user_ids (isolation)
# - Test error handling
# - Test with missing optional parameters
