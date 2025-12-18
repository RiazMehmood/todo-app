"""
Chat Service for AI Chatbot Integration (Phase III - US1).

Manages conversations and messages for AI-powered task management chat.
Integrates with AI Agent Manager for natural language processing.
"""

import logging
from typing import List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime
from sqlmodel import Session, select
from ..models import Conversation, Message, UserPreferences
from .ai_agent_manager import AIAgentManager

# Configure logger for chat service
logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat conversations and AI interactions."""

    @staticmethod
    def get_or_create_conversation(
        session: Session,
        user_id: str
    ) -> Conversation:
        """
        Get existing conversation or create a new one for the user.

        For MVP, we keep one conversation per user. In production,
        this could be enhanced to support multiple conversations.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            Conversation object
        """
        # Try to get existing conversation
        statement = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(Conversation.created_at.desc())

        conversation = session.exec(statement).first()

        if conversation:
            return conversation

        # Create new conversation if none exists
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        return conversation

    @staticmethod
    def save_message(
        session: Session,
        user_id: str,
        conversation_id: int,
        role: str,
        content: str,
        language: Optional[str] = None,
        related_task_id: Optional[int] = None,
        intent_detected: Optional[str] = None,
        confidence_score: Optional[float] = None
    ) -> Message:
        """
        Save a message to the database.

        Args:
            session: Database session
            user_id: User ID
            conversation_id: Conversation ID
            role: Message role ('user' or 'assistant')
            content: Message content
            language: Detected language ('en' or 'ur')
            related_task_id: Related task ID (if applicable)
            intent_detected: Detected intent (e.g., 'create_task')
            confidence_score: Intent confidence score

        Returns:
            Message object
        """
        message = Message(
            user_id=user_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            language=language,
            related_task_id=related_task_id,
            intent_detected=intent_detected,
            confidence_score=confidence_score
        )

        session.add(message)
        session.commit()
        session.refresh(message)

        return message

    @staticmethod
    def get_conversation_history(
        session: Session,
        user_id: str,
        conversation_id: int,
        limit: int = 50
    ) -> List[Message]:
        """
        Get conversation history for context.

        Args:
            session: Database session
            user_id: User ID
            conversation_id: Conversation ID
            limit: Maximum number of messages to retrieve

        Returns:
            List of messages ordered by creation time
        """
        statement = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id
        ).order_by(Message.created_at).limit(limit)

        messages = session.exec(statement).all()
        return list(messages)

    @staticmethod
    async def process_chat_message(
        session: Session,
        user_id: str,
        message_content: str,
        agent_manager: AIAgentManager
    ) -> Dict[str, Any]:
        """
        Process a chat message through the AI agent.

        This is the main entry point for chat interactions.

        Args:
            session: Database session
            user_id: User ID
            message_content: User's message content
            agent_manager: AI Agent Manager instance

        Returns:
            Dictionary with response and metadata:
            {
                "conversation_id": int,
                "user_message_id": int,
                "assistant_message_id": int,
                "response": str,
                "language": str,
                "related_task_id": int | None
            }
        """
        logger.info(f"Processing chat message for user {user_id}: message_length={len(message_content)}")

        # Get or create conversation
        conversation = ChatService.get_or_create_conversation(session, user_id)

        # Get user preferences for language context
        prefs_statement = select(UserPreferences).where(
            UserPreferences.user_id == user_id
        )
        preferences = session.exec(prefs_statement).first()

        # Determine language context
        language = None
        if preferences:
            language = preferences.preferred_language

        # Save user message
        user_message = ChatService.save_message(
            session=session,
            user_id=user_id,
            conversation_id=conversation.id,
            role="user",
            content=message_content,
            language=language
        )

        # Get conversation history for context (excluding current message)
        history = ChatService.get_conversation_history(
            session=session,
            user_id=user_id,
            conversation_id=conversation.id,
            limit=20
        )

        # Process message through AI agent WITH conversation history
        result = await agent_manager.process_message(
            user_id=user_id,
            message=message_content,
            db_session=session,
            conversation_id=conversation.id,
            conversation_history=history  # Pass history for context!
        )

        response_text = result.get("response", "I encountered an error processing your request.")

        # Save assistant response
        assistant_message = ChatService.save_message(
            session=session,
            user_id=user_id,
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
            language=language
        )

        logger.info(f"Chat message processed successfully for user {user_id}: conversation_id={conversation.id}, response_length={len(response_text)}")

        return {
            "conversation_id": conversation.id,
            "user_message_id": user_message.id,
            "assistant_message_id": assistant_message.id,
            "response": response_text,
            "language": language,
            "related_task_id": None  # Can be enhanced to detect task operations
        }

    @staticmethod
    async def stream_chat_message(
        session: Session,
        user_id: str,
        message_content: str,
        agent_manager: AIAgentManager
    ) -> AsyncGenerator[str, None]:
        """
        Stream a chat message response in real-time.

        This enables streaming responses for better UX.

        Args:
            session: Database session
            user_id: User ID
            message_content: User's message content
            agent_manager: AI Agent Manager instance

        Yields:
            Chunks of the assistant's response
        """
        # Get or create conversation
        conversation = ChatService.get_or_create_conversation(session, user_id)

        # Get user preferences
        prefs_statement = select(UserPreferences).where(
            UserPreferences.user_id == user_id
        )
        preferences = session.exec(prefs_statement).first()
        language = preferences.preferred_language if preferences else None

        # Save user message
        user_message = ChatService.save_message(
            session=session,
            user_id=user_id,
            conversation_id=conversation.id,
            role="user",
            content=message_content,
            language=language
        )

        # Stream response from agent
        full_response = ""
        async for chunk in agent_manager.stream_message(
            user_id=user_id,
            message=message_content,
            db_session=session,
            conversation_id=conversation.id
        ):
            full_response += chunk
            yield chunk

        # Save complete assistant response after streaming
        ChatService.save_message(
            session=session,
            user_id=user_id,
            conversation_id=conversation.id,
            role="assistant",
            content=full_response,
            language=language
        )

    @staticmethod
    def delete_conversation_history(
        session: Session,
        user_id: str,
        conversation_id: Optional[int] = None
    ) -> int:
        """
        Delete conversation history (for opt-out or privacy).

        Args:
            session: Database session
            user_id: User ID
            conversation_id: Specific conversation to delete (None = all)

        Returns:
            Number of messages deleted
        """
        if conversation_id:
            # Delete specific conversation
            statement = select(Message).where(
                Message.user_id == user_id,
                Message.conversation_id == conversation_id
            )
        else:
            # Delete all user's messages
            statement = select(Message).where(
                Message.user_id == user_id
            )

        messages = session.exec(statement).all()
        count = len(messages)

        for message in messages:
            session.delete(message)

        # Also delete conversation records
        if conversation_id:
            conv_statement = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        else:
            conv_statement = select(Conversation).where(
                Conversation.user_id == user_id
            )

        conversations = session.exec(conv_statement).all()
        for conversation in conversations:
            session.delete(conversation)

        session.commit()

        return count
