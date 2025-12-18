"""
AI Agent Manager for OpenAI Agents SDK Integration (Phase III).

Manages AI agent lifecycle, session state, and coordinates between
the MCP server and OpenAI Agents SDK.
"""

import os
import logging
from typing import Dict, Any, Optional
from agents import Agent, Runner, RunConfig, OpenAIChatCompletionsModel, function_tool
from openai import AsyncOpenAI
from sqlmodel import Session
from .task_service import TaskService

# Configure logger for AI operations
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class AIAgentManager:
    """
    Manages AI agents using OpenAI Agents SDK with Gemini.

    Handles:
    - Agent creation and configuration
    - Gemini model integration via AsyncOpenAI
    - Context passing (user_id, db session)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash-exp"
    ):
        """
        Initialize AI Agent Manager with Gemini.

        Args:
            api_key: Gemini API key
            model: Gemini model to use (default: gemini-2.0-flash-exp)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("AI_MODEL", "gemini-2.0-flash-exp")
        self.db_session = None  # Will be set per request
        self.current_user_id = None  # Will be set per request

        # Create AsyncOpenAI client configured for Gemini API
        self.external_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/"
        )

        # Create OpenAI-compatible model wrapper for Gemini
        self.model = OpenAIChatCompletionsModel(
            model=self.model_name,
            openai_client=self.external_client
        )

        # Create run config with Gemini model
        self.run_config = RunConfig(
            model=self.model,
            model_provider=self.external_client,
            tracing_disabled=True
        )

        # Create task agent (function tools will be added dynamically)
        self.task_agent = self._create_task_agent()

    def _create_task_agent(self) -> Agent:
        """
        Create the task management agent with tools and instructions.

        Returns:
            Configured Agent instance
        """
        agent = Agent(
            name="TaskAssistant",
            instructions="""You are a helpful task management assistant.

You can help users:
- Create new tasks from natural language descriptions
- View their existing tasks (all, completed, or pending)
- Update task titles, descriptions, or mark tasks as complete
- Delete tasks (always ask for confirmation first)
- Undo recently created tasks

You communicate in both English and Urdu (اردو).
Automatically detect the user's language and respond accordingly.

Examples:
- "Add task to buy milk" → Use add_task(title="Buy milk")
- "دودھ خریدنے کا کام شامل کریں" → Use add_task(title="دودھ خریدنا")
- "What's on my list?" → Use list_tasks()
- "Show pending tasks" → Use list_tasks(status="pending")
- "Mark the milk task as done" → First list_tasks() to find task ID, then complete_task(task_id)
- "Change 'buy milk' to 'buy organic milk'" → First list_tasks() to find task ID, then update_task(task_id, title="buy organic milk")
- "Update the description of task 5 to 'urgent priority'" → Use update_task(task_id=5, description="urgent priority")
- "Rename the meeting task" → Ask what new name, then use update_task(task_id, title=new_name)
- "Delete the shopping task" → First list_tasks() to find task ID, ASK FOR CONFIRMATION, then delete_task(task_id)

CRITICAL RULES FOR DELETIONS:
1. ALWAYS use list_tasks() first to find the correct task ID before deleting
2. ALWAYS ask for explicit confirmation before calling delete_task()
3. When user confirms (says "yes", "confirm", "sure", etc.), THEN call delete_task(task_id)
4. Show the task title and ID when asking for confirmation
5. After deletion, explicitly confirm which task was deleted

UNDO FUNCTIONALITY:
- When user says "undo", "undo that", "delete that task", or "remove that task":
  1. Look at the conversation history to identify the most recently created task
  2. If you just created a task in the previous message, delete it WITHOUT asking for confirmation (since undo implies intent to remove)
  3. Confirm what was undone: "Undone! I've deleted the task '[task title]'."
  4. If you cannot determine which task to undo, ask the user for clarification
- Undo requests DO NOT require confirmation (unlike regular deletions) because the user is explicitly requesting to reverse an action
- Examples:
  * User: "Add task to buy groceries" → AI: "Task created: 'Buy groceries' (ID: 42)"
  * User: "undo" → AI deletes task 42 and says "Undone! I've deleted the task 'Buy groceries'."
  * User: "Add task to buy milk" then "actually, undo that" → AI deletes the milk task immediately

Important:
- When updating or deleting, ALWAYS call list_tasks() first to get the correct task ID
- If multiple tasks match, list them and ask user to clarify which one
- For updates, you can change title, description, or both
- Always confirm what was updated/deleted after operations
- Preserve the user's language in task titles/descriptions
- Be concise and friendly
- Always provide helpful responses even if the user makes mistakes
- If a task operation succeeds, confirm it and show the updated task details
- Read the conversation history carefully to maintain context
- For undo requests, you can skip the confirmation step and delete immediately (user intent is clear)
""",
            model=self.model,
            tools=self._get_tools()  # Use function tools
        )

        return agent

    def _get_tools(self):
        """Get list of function tools for the agent."""
        # Tools automatically use current user context (self.current_user_id)
        @function_tool
        def add_task(title: str, description: str = "") -> str:
            """Create a new task. Just provide the title and optional description."""
            if not self.db_session or not self.current_user_id:
                logger.error(f"add_task called without context")
                return "Error: Context not available"
            try:
                logger.info(f"AI creating task for user {self.current_user_id}: title='{title}'")
                task = TaskService.create_task(
                    session=self.db_session,
                    user_id=self.current_user_id,
                    title=title,
                    description=description or None,
                    created_via_ai=True
                )
                logger.info(f"AI task created successfully: task_id={task.id}, title='{task.title}', user={self.current_user_id}")
                return f"Task created successfully: '{task.title}' (ID: {task.id})"
            except Exception as e:
                logger.error(f"AI task creation failed for user {self.current_user_id}: {str(e)}")
                return f"Error creating task: {str(e)}"

        @function_tool
        def list_tasks(status: str = "all") -> str:
            """List all tasks. Status can be 'all', 'pending', or 'completed'."""
            if not self.db_session or not self.current_user_id:
                return "Error: Context not available"
            try:
                # Convert status string to completed boolean
                completed_filter = None
                if status == "pending":
                    completed_filter = False
                elif status == "completed":
                    completed_filter = True
                # If status == "all", leave completed_filter as None

                tasks = TaskService.list_tasks(
                    session=self.db_session,
                    user_id=self.current_user_id,
                    completed=completed_filter
                )
                if not tasks:
                    if status == "pending":
                        return "You have no pending tasks."
                    elif status == "completed":
                        return "You have no completed tasks."
                    else:
                        return "You have no tasks."

                result = []
                for task in tasks:
                    status_icon = "✓" if task.completed else "○"
                    result.append(f"{status_icon} {task.title} (ID: {task.id})")
                return "\n".join(result)
            except Exception as e:
                return f"Error listing tasks: {str(e)}"

        @function_tool
        def complete_task(task_id: int) -> str:
            """Mark a task as complete. Just provide the task ID."""
            if not self.db_session or not self.current_user_id:
                logger.error(f"complete_task called without context")
                return "Error: Context not available"
            try:
                logger.info(f"AI completing task for user {self.current_user_id}: task_id={task_id}")
                task = TaskService.complete_task(
                    session=self.db_session,
                    user_id=self.current_user_id,
                    task_id=task_id
                )
                logger.info(f"AI task completed successfully: task_id={task_id}, title='{task.title}', user={self.current_user_id}")
                return f"Task '{task.title}' marked as complete!"
            except Exception as e:
                logger.error(f"AI task completion failed for user {self.current_user_id}, task_id={task_id}: {str(e)}")
                return f"Error completing task: {str(e)}"

        @function_tool
        def delete_task(task_id: int) -> str:
            """Delete a task. Just provide the task ID."""
            if not self.db_session or not self.current_user_id:
                logger.error(f"delete_task called without context")
                return "Error: Context not available"
            try:
                # Get task details before deleting for confirmation message
                task = TaskService.get_task(
                    session=self.db_session,
                    user_id=self.current_user_id,
                    task_id=task_id
                )

                if not task:
                    logger.warning(f"AI attempted to delete non-existent task: task_id={task_id}, user={self.current_user_id}")
                    return f"Error: Task with ID {task_id} not found or already deleted."

                task_title = task.title
                logger.info(f"AI deleting task for user {self.current_user_id}: task_id={task_id}, title='{task_title}'")

                # Now delete the task
                deleted = TaskService.delete_task(
                    session=self.db_session,
                    user_id=self.current_user_id,
                    task_id=task_id
                )

                if deleted:
                    logger.info(f"AI task deleted successfully: task_id={task_id}, title='{task_title}', user={self.current_user_id}")
                    return f"Task '{task_title}' (ID: {task_id}) has been deleted successfully."
                else:
                    logger.error(f"AI task deletion failed: task_id={task_id}, user={self.current_user_id}")
                    return f"Error: Could not delete task with ID {task_id}. Task may not exist."
            except Exception as e:
                logger.error(f"AI task deletion error for user {self.current_user_id}, task_id={task_id}: {str(e)}")
                return f"Error deleting task: {str(e)}"

        @function_tool
        def update_task(task_id: int, title: str = None, description: str = None) -> str:
            """Update a task's title or description. Provide task ID and at least one field to update."""
            if not self.db_session or not self.current_user_id:
                logger.error(f"update_task called without context")
                return "Error: Context not available"
            try:
                if title is None and description is None:
                    logger.warning(f"AI update_task called with no fields to update: task_id={task_id}, user={self.current_user_id}")
                    return "Error: Must provide at least title or description to update"

                logger.info(f"AI updating task for user {self.current_user_id}: task_id={task_id}, title={title}, description={description}")
                task = TaskService.update_task(
                    session=self.db_session,
                    user_id=self.current_user_id,
                    task_id=task_id,
                    title=title,
                    description=description
                )

                if not task:
                    logger.warning(f"AI attempted to update non-existent task: task_id={task_id}, user={self.current_user_id}")
                    return f"Error: Task with ID {task_id} not found"

                updates = []
                if title:
                    updates.append(f"title to '{title}'")
                if description:
                    updates.append(f"description to '{description}'")

                logger.info(f"AI task updated successfully: task_id={task_id}, user={self.current_user_id}, updates={', '.join(updates)}")
                return f"Task updated successfully: {', '.join(updates)}"
            except Exception as e:
                logger.error(f"AI task update error for user {self.current_user_id}, task_id={task_id}: {str(e)}")
                return f"Error updating task: {str(e)}"

        return [add_task, list_tasks, complete_task, delete_task, update_task]

    def _get_friendly_error_message(self, error: Exception) -> str:
        """
        Convert technical errors into user-friendly messages.

        Args:
            error: The exception that occurred

        Returns:
            User-friendly error message
        """
        error_str = str(error).lower()

        # Rate limit / quota errors (Gemini free tier)
        if any(keyword in error_str for keyword in ['rate limit', 'quota', 'resource exhausted', '429']):
            return (
                "I'm temporarily unavailable due to high usage. "
                "This usually happens when the free tier limit is reached. "
                "Please try again in a few minutes."
            )

        # Authentication / API key errors
        if any(keyword in error_str for keyword in ['unauthorized', '401', 'invalid api key', 'authentication']):
            return (
                "There's an authentication issue with the AI service. "
                "Please contact the administrator to check the API configuration."
            )

        # Network / connection errors
        if any(keyword in error_str for keyword in ['connection', 'timeout', 'network', 'unreachable']):
            return (
                "I'm having trouble connecting to the AI service. "
                "Please check your internet connection and try again."
            )

        # Service unavailable / server errors
        if any(keyword in error_str for keyword in ['500', '502', '503', '504', 'internal server', 'service unavailable']):
            return (
                "The AI service is temporarily unavailable. "
                "Our team has been notified. Please try again in a few moments."
            )

        # Model / API errors
        if any(keyword in error_str for keyword in ['model not found', 'invalid model', 'api error']):
            return (
                "There's an issue with the AI model configuration. "
                "Please contact the administrator."
            )

        # Context length / token limit errors
        if any(keyword in error_str for keyword in ['context length', 'token limit', 'too long']):
            return (
                "Your message is too long. Please try breaking it into smaller requests."
            )

        # Generic fallback
        return (
            "I encountered an unexpected error while processing your request. "
            "Please try again, or contact support if the issue persists."
        )

    async def process_message(
        self,
        user_id: str,
        message: str,
        db_session: Session,
        conversation_id: Optional[int] = None,
        conversation_history: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Process a user message through the AI agent.

        Args:
            user_id: User ID for context and authorization
            message: User's message text
            db_session: Database session for tools
            conversation_id: Optional conversation ID for history
            conversation_history: List of previous messages for context

        Returns:
            Dictionary with response text and metadata
        """
        # Set context for function tools to use
        self.db_session = db_session
        self.current_user_id = user_id

        logger.info(f"AI processing message for user {user_id}: message_length={len(message)}, conversation_id={conversation_id}")

        try:
            # Build conversation context from history
            # Format: Recent messages help the AI remember what was discussed
            context_messages = []
            if conversation_history and len(conversation_history) > 0:
                # Get last 10 messages for context (limit to avoid token limits)
                recent_history = conversation_history[-10:]
                for msg in recent_history:
                    role = msg.role  # 'user' or 'assistant'
                    content = msg.content
                    context_messages.append(f"{role}: {content}")

            # Prepend context to current message if history exists
            full_message = message
            if context_messages:
                context_str = "\n".join(context_messages)
                full_message = f"[Conversation History]\n{context_str}\n\n[Current Message]\n{message}"

            # Run agent with message and Gemini config
            result = await Runner.run(
                starting_agent=self.task_agent,
                input=full_message,
                run_config=self.run_config
            )

            logger.info(f"AI message processed successfully for user {user_id}: response_length={len(result.final_output)}")
            return {
                "response": result.final_output,
                "status": "success",
                "conversation_id": conversation_id
            }

        except Exception as e:
            logger.error(f"Error in AI Agent for user {user_id}: {str(e)}", exc_info=True)

            # Categorize error and provide user-friendly message
            error_message = self._get_friendly_error_message(e)

            return {
                "response": error_message,
                "status": "error",
                "error": str(e)
            }
        finally:
            # Clean up
            self.db_session = None
            self.current_user_id = None

    async def stream_message(
        self,
        user_id: str,
        message: str,
        db_session: Session,
        conversation_id: Optional[int] = None
    ):
        """
        Stream a user message through the AI agent (for real-time responses).

        Args:
            user_id: User ID for context and authorization
            message: User's message text
            db_session: Database session for tools
            conversation_id: Optional conversation ID for history

        Yields:
            Chunks of the agent's response
        """
        # Set context for function tools to use
        self.db_session = db_session
        self.current_user_id = user_id

        logger.info(f"AI streaming message for user {user_id}: message_length={len(message)}, conversation_id={conversation_id}")

        try:
            # Stream agent responses with Gemini config
            async for chunk in Runner.stream(
                starting_agent=self.task_agent,
                input=message,
                run_config=self.run_config
            ):
                yield chunk

            logger.info(f"AI streaming completed for user {user_id}")

        except Exception as e:
            logger.error(f"Error streaming for user {user_id}: {str(e)}", exc_info=True)

            # Get user-friendly error message
            error_message = self._get_friendly_error_message(e)
            yield f"Error: {error_message}"
        finally:
            # Clean up
            self.db_session = None
            self.current_user_id = None


    async def detect_language(self, text: str) -> str:
        """
        Detect the language of user input.

        Args:
            text: User's message text

        Returns:
            Language code ('en' or 'ur')
        """
        # Simple heuristic: if text contains Urdu characters, it's Urdu
        urdu_chars = set('ابپتٹثجچحخدڈذرڑزژسشصضطظعغفقکگلمنںوہھءیےۃ')
        if any(char in urdu_chars for char in text):
            return 'ur'
        return 'en'

    def validate_task_operation(
        self,
        operation: str,
        user_id: str,
        **kwargs
    ) -> bool:
        """
        Validate a task operation before execution.

        Args:
            operation: Operation name ('create', 'update', 'delete', etc.)
            user_id: User ID
            **kwargs: Additional parameters

        Returns:
            True if valid, raises ValueError otherwise
        """
        if not user_id:
            raise ValueError("User ID is required")

        if operation == "create":
            if not kwargs.get("title"):
                raise ValueError("Title is required for creating tasks")

        elif operation in ["update", "delete", "complete"]:
            if not kwargs.get("task_id"):
                raise ValueError("Task ID is required")

        return True


# Singleton instance
_agent_manager: Optional[AIAgentManager] = None


def get_agent_manager() -> AIAgentManager:
    """
    Get singleton instance of AI Agent Manager.

    Returns:
        AIAgentManager instance
    """
    global _agent_manager

    if _agent_manager is None:
        _agent_manager = AIAgentManager(
            api_key=os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"),
            model=os.getenv("AI_MODEL", "gemini-2.0-flash-exp")
        )

    return _agent_manager
