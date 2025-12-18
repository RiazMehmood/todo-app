"""
Gemini AI Agent Manager using native Google Generative AI SDK.

This implementation uses Gemini's native function calling instead of
the OpenAI Agents SDK to avoid compatibility issues.
"""

import os
import json
from typing import Dict, Any, Optional, List
import google.generativeai as genai
from sqlmodel import Session
from .task_service import TaskService


class GeminiAgentManager:
    """
    Manages AI agents using Google Gemini native SDK.

    Handles:
    - Agent creation and configuration
    - Function calling (tools)
    - Context passing (user_id, db session)
    - Conversation history
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash"
    ):
        """
        Initialize Gemini Agent Manager.

        Args:
            api_key: Google AI Studio API key
            model: Gemini model to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")  # Reuse env var
        self.model_name = model or os.getenv("AI_MODEL", "gemini-2.5-flash")
        self.db_session = None  # Will be set per request

        # Configure Gemini SDK
        genai.configure(api_key=self.api_key)

        # Define function declarations for Gemini
        self.functions = self._create_function_declarations()

        # Create model with functions
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            tools=[self.functions]
        )

    def _create_function_declarations(self):
        """Create Gemini function declarations (tools)."""
        return [
            genai.protos.FunctionDeclaration(
                name="add_task",
                description="Create a new task for the user",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "user_id": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "title": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "description": genai.protos.Schema(type=genai.protos.Type.STRING),
                    },
                    required=["user_id", "title"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="list_tasks",
                description="List tasks for the user. Status can be 'all', 'pending', or 'completed'",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "user_id": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "status": genai.protos.Schema(type=genai.protos.Type.STRING),
                    },
                    required=["user_id"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="complete_task",
                description="Mark a task as complete",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "user_id": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "task_id": genai.protos.Schema(type=genai.protos.Type.INTEGER),
                    },
                    required=["user_id", "task_id"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="delete_task",
                description="Delete a task (always ask for confirmation first)",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "user_id": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "task_id": genai.protos.Schema(type=genai.protos.Type.INTEGER),
                    },
                    required=["user_id", "task_id"]
                )
            ),
        ]

    def _execute_function(self, function_name: str, args: Dict[str, Any]) -> str:
        """Execute a function call from Gemini."""
        if not self.db_session:
            return "Error: Database session not available"

        try:
            if function_name == "add_task":
                task = TaskService.create_task(
                    session=self.db_session,
                    user_id=args["user_id"],
                    title=args["title"],
                    description=args.get("description", ""),
                    created_via_ai=True
                )
                return f"Task created successfully: '{task.title}' (ID: {task.id})"

            elif function_name == "list_tasks":
                tasks = TaskService.list_tasks(
                    session=self.db_session,
                    user_id=args["user_id"],
                    status=args.get("status", "all")
                )
                if not tasks:
                    return "You have no tasks."

                result = []
                for task in tasks:
                    status_icon = "✓" if task.completed else "○"
                    result.append(f"{status_icon} {task.title} (ID: {task.id})")
                return "\n".join(result)

            elif function_name == "complete_task":
                task = TaskService.complete_task(
                    session=self.db_session,
                    user_id=args["user_id"],
                    task_id=int(args["task_id"])
                )
                return f"Task '{task.title}' marked as complete!"

            elif function_name == "delete_task":
                TaskService.delete_task(
                    session=self.db_session,
                    user_id=args["user_id"],
                    task_id=int(args["task_id"])
                )
                return "Task deleted successfully."

            else:
                return f"Unknown function: {function_name}"

        except Exception as e:
            return f"Error executing {function_name}: {str(e)}"

    async def process_message(
        self,
        user_id: str,
        message: str,
        db_session: Session,
        conversation_id: Optional[int] = None,
        chat_history: Optional[List] = None
    ) -> Dict[str, Any]:
        """
        Process a user message through Gemini.

        Args:
            user_id: User ID for context
            message: User's message text
            db_session: Database session for tools
            conversation_id: Optional conversation ID
            chat_history: Optional previous chat history

        Returns:
            Dictionary with response text and metadata
        """
        # Set db_session for function tools
        self.db_session = db_session

        try:
            # Start chat session with history
            chat = self.model.start_chat(history=chat_history or [])

            # System instruction via first message if no history
            if not chat_history:
                system_msg = f"""You are a helpful task management assistant for user {user_id}.

You can help users:
- Create new tasks from natural language descriptions
- View their existing tasks (all, completed, or pending)
- Update task details or mark tasks as complete
- Delete tasks (always ask for confirmation first)

You communicate in both English and Urdu (اردو).
Automatically detect the user's language and respond accordingly.

Examples:
- "Add task to buy milk" → Use add_task(user_id="{user_id}", title="Buy milk")
- "دودھ خریدنے کا کام شامل کریں" → Use add_task(user_id="{user_id}", title="دودھ خریدنا")
- "What's on my list?" → Use list_tasks(user_id="{user_id}")
- "Show pending tasks" → Use list_tasks(user_id="{user_id}", status="pending")
- "Mark the milk task as done" → Find task, then complete_task(user_id="{user_id}", task_id=X)
- "Delete the shopping task" → ASK FOR CONFIRMATION, then delete_task(user_id="{user_id}", task_id=X)

Important:
- When updating or deleting, ask for confirmation if ambiguous
- If multiple tasks match, list them and ask user to clarify
- Preserve the user's language in task titles/descriptions
- Be concise and friendly
- Always provide helpful responses even if the user makes mistakes"""

                # Send system instruction as first message
                intro_response = chat.send_message(system_msg)

            # Send user message
            response = chat.send_message(message)

            # Handle function calls
            while response.candidates[0].content.parts[0].function_call:
                function_call = response.candidates[0].content.parts[0].function_call
                function_name = function_call.name
                function_args = dict(function_call.args)

                # Execute function
                function_result = self._execute_function(function_name, function_args)

                # Send function result back to model
                response = chat.send_message(
                    genai.protos.Content(
                        parts=[genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=function_name,
                                response={"result": function_result}
                            )
                        )]
                    )
                )

            # Get final text response
            final_response = response.text

            return {
                "response": final_response,
                "status": "success",
                "conversation_id": conversation_id
            }

        except Exception as e:
            print(f"Error in Gemini agent: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "response": f"I encountered an error processing your request: {str(e)}",
                "status": "error",
                "error": str(e)
            }
        finally:
            # Clean up
            self.db_session = None


# Singleton instance
_gemini_agent_manager: Optional[GeminiAgentManager] = None


def get_gemini_agent_manager() -> GeminiAgentManager:
    """
    Get singleton instance of Gemini Agent Manager.

    Returns:
        GeminiAgentManager instance
    """
    global _gemini_agent_manager

    if _gemini_agent_manager is None:
        _gemini_agent_manager = GeminiAgentManager()

    return _gemini_agent_manager
