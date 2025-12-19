"""
OpenAI Agents SDK Template - Agent Configuration Pattern

This template demonstrates the pattern for creating AI agents using the
official OpenAI Agents SDK (openai-agents).

Usage:
1. Copy this template
2. Define your agent's purpose and instructions
3. Create function tools for agent capabilities
4. Configure agent with model and tools
5. Handle agent responses and tool calls

Example from Phase III:
- task_agent.py with add_task, list_tasks, update_task, delete_task, complete_task tools
"""

from agents import Agent, function_tool
from typing import Dict, Any, List, Optional
import logging
from sqlmodel import Session

logger = logging.getLogger(__name__)


# ========================================
# 1. Define Function Tools for Agent
# ========================================

@function_tool
async def tool_name(
    param1: str,
    param2: Optional[str] = None,
    ctx: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Brief description of what this tool does.

    Args:
        param1: Description of parameter
        param2: Optional parameter description
        ctx: Context dictionary containing user_id, db session, etc.

    Returns:
        Dictionary with tool result
    """
    try:
        # Extract context
        user_id = ctx.get("user_id")
        db: Session = ctx.get("db")

        # Validate
        if not user_id:
            raise ValueError("user_id required in context")

        # Execute logic
        # TODO: Implement tool logic

        return {
            "status": "success",
            "result": "your_result_here"
        }

    except Exception as e:
        logger.error(f"Error in tool_name: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


# Example: Real tool from Phase III
@function_tool
async def create_task(
    title: str,
    description: str = "",
    ctx: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create a new task for the user."""
    try:
        user_id = ctx.get("user_id")
        db: Session = ctx.get("db")

        from models import Task

        task = Task(
            title=title,
            description=description,
            user_id=user_id,
            created_via_ai=True
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        return {
            "status": "success",
            "task_id": task.id,
            "title": task.title
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}


@function_tool
async def list_tasks(
    status: Optional[str] = None,
    ctx: Dict[str, Any] = None
) -> Dict[str, Any]:
    """List user's tasks, optionally filtered by status."""
    try:
        user_id = ctx.get("user_id")
        db: Session = ctx.get("db")

        from models import Task
        from sqlmodel import select

        query = select(Task).where(Task.user_id == user_id)

        if status == "completed":
            query = query.where(Task.completed == True)
        elif status == "pending":
            query = query.where(Task.completed == False)

        tasks = db.exec(query).all()

        return {
            "status": "success",
            "count": len(tasks),
            "tasks": [
                {"id": t.id, "title": t.title, "completed": t.completed}
                for t in tasks
            ]
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}


# ========================================
# 2. Create Agent with Tools
# ========================================

def create_agent(name: str, model: str = "gpt-4o") -> Agent:
    """
    Create an agent with specified tools and instructions.

    Args:
        name: Agent name
        model: OpenAI model to use (default: gpt-4o)

    Returns:
        Configured Agent instance
    """

    # Define agent instructions (system prompt)
    instructions = """
You are a helpful assistant that helps users manage their tasks through natural language.

**Capabilities**:
- Create new tasks from natural language descriptions
- List and query existing tasks
- Update task details and completion status
- Delete tasks with confirmation

**Language Support**:
- English and Urdu (respond in the same language as user input)
- Auto-detect language from user messages

**Guidelines**:
1. Always confirm actions with user-friendly messages
2. For ambiguous requests, ask clarifying questions
3. For destructive operations (delete), confirm before executing
4. When creating tasks, extract title and description from user input
5. Format task lists in a readable way
6. Be concise but helpful

**Examples**:
User: "Add task to buy milk tomorrow"
Assistant: [calls create_task with title="Buy milk", description="Tomorrow"]
Response: "I've created a task titled 'Buy milk' for tomorrow."

User: "What tasks are pending?"
Assistant: [calls list_tasks with status="pending"]
Response: "You have 3 pending tasks: [list]"
"""

    # Create agent with tools
    agent = Agent(
        name=name,
        instructions=instructions,
        model=model,
        tools=[
            create_task,
            list_tasks,
            # Add more tools here
        ]
    )

    return agent


# ========================================
# 3. Agent Execution Pattern
# ========================================

async def execute_agent(
    agent: Agent,
    user_message: str,
    user_id: str,
    db: Session,
    conversation_history: List[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Execute agent with user message and context.

    Args:
        agent: Configured Agent instance
        user_message: User's input message
        user_id: User ID for context
        db: Database session
        conversation_history: Previous messages for context

    Returns:
        {
            "response": "Agent's text response",
            "tool_calls": [list of tool calls made],
            "success": bool
        }
    """
    try:
        # Prepare context for tools
        context = {
            "user_id": user_id,
            "db": db,
            "config": {}
        }

        # Prepare messages with history
        messages = conversation_history or []
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Run agent
        response = await agent.run(
            messages=messages,
            context=context
        )

        # Extract response and tool calls
        agent_response = response.get("content", "")
        tool_calls = response.get("tool_calls", [])

        logger.info(f"Agent executed for user {user_id}, made {len(tool_calls)} tool calls")

        return {
            "response": agent_response,
            "tool_calls": tool_calls,
            "success": True
        }

    except Exception as e:
        logger.error(f"Agent execution error: {str(e)}")
        return {
            "response": "I encountered an error processing your request. Please try again.",
            "tool_calls": [],
            "success": False,
            "error": str(e)
        }


# ========================================
# 4. Usage Example
# ========================================

async def example_usage():
    """Example of how to use the agent."""

    # 1. Create agent
    task_agent = create_agent(
        name="TaskAssistant",
        model="gpt-4o"
    )

    # 2. Prepare context
    user_id = "user-123"
    db = get_db_session()  # Your DB session

    # 3. Execute with user message
    result = await execute_agent(
        agent=task_agent,
        user_message="Add task to buy groceries tomorrow",
        user_id=user_id,
        db=db
    )

    # 4. Handle result
    if result["success"]:
        print(f"Agent response: {result['response']}")
        print(f"Tool calls: {len(result['tool_calls'])}")
    else:
        print(f"Error: {result.get('error')}")


# ========================================
# Best Practices
# ========================================

# 1. Tool Design:
#    - Keep tools focused on single responsibility
#    - Use clear, descriptive tool names
#    - Provide detailed docstrings (agent reads these!)
#    - Return structured data from tools

# 2. Agent Instructions:
#    - Be specific about agent capabilities
#    - Provide examples of expected behavior
#    - Include language/tone guidelines
#    - Define error handling approach

# 3. Context Management:
#    - Always pass user_id for multi-user isolation
#    - Include necessary dependencies (db, config)
#    - Maintain conversation history for context
#    - Clean up context after execution

# 4. Error Handling:
#    - Wrap tool calls in try/except
#    - Return user-friendly error messages
#    - Log errors for debugging
#    - Don't expose internal errors to users

# 5. Testing:
#    - Test each tool independently
#    - Test agent with various user inputs
#    - Test conversation context handling
#    - Test error scenarios
#    - Test multi-user isolation

# 6. Performance:
#    - Use async/await for I/O operations
#    - Cache agent instances when possible
#    - Limit conversation history length
#    - Monitor OpenAI API costs
