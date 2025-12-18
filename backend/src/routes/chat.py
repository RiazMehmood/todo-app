"""
Chat Routes for AI Chatbot Integration (Phase III - US1).

Provides REST endpoints for AI-powered chat interactions.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from ..db import get_session
from ..middleware.auth import verify_jwt
from ..services.chat_service import ChatService
from ..services.ai_agent_manager import AIAgentManager
from ..models import Message
from ..utils.rate_limiter import chat_rate_limiter
import os


router = APIRouter(dependencies=[Depends(verify_jwt)])


class ChatMessageRequest(BaseModel):
    """Request model for chat messages."""
    message: str
    stream: bool = False  # Enable streaming responses


class ChatMessageResponse(BaseModel):
    """Response model for chat messages."""
    conversation_id: int
    user_message_id: int
    assistant_message_id: int
    response: str
    language: Optional[str] = None
    related_task_id: Optional[int] = None


class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history."""
    conversation_id: int
    messages: List[Dict[str, Any]]


# Initialize AI Agent Manager (singleton) - Gemini via OpenAI Agents SDK
from ..services.ai_agent_manager import get_agent_manager
agent_manager = get_agent_manager()


@router.post("/{user_id}/chat", response_model=ChatMessageResponse)
async def send_chat_message(
    user_id: str,
    request_data: ChatMessageRequest,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Send a chat message and get AI response.

    **HACKATHON REQUIRED ENDPOINT**: POST /api/{user_id}/chat

    This endpoint processes user messages through the AI agent,
    which can create, list, update, and delete tasks via MCP tools.

    Args:
        user_id: User ID
        request_data: Chat message request
        request: FastAPI request (for auth)
        session: Database session

    Returns:
        ChatMessageResponse with AI's response

    Raises:
        403: User not authorized or AI chatbot disabled
        400: Invalid request
        429: Rate limit exceeded
        500: AI processing error
    """
    # Verify user authorization
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot send chat messages for another user"
        )

    # Check rate limit
    if not chat_rate_limiter.is_allowed(user_id):
        remaining = chat_rate_limiter.get_remaining(user_id)
        reset_time = chat_rate_limiter.get_reset_time(user_id)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Please try again in {reset_time} seconds.",
            headers={
                "X-RateLimit-Limit": str(chat_rate_limiter.max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_time),
                "Retry-After": str(reset_time)
            }
        )

    # Check if user has AI chatbot enabled
    from ..models import UserPreferences
    from sqlmodel import select

    prefs_statement = select(UserPreferences).where(
        UserPreferences.user_id == user_id
    )
    preferences = session.exec(prefs_statement).first()

    if not preferences or not preferences.ai_enabled:
        raise HTTPException(
            status_code=403,
            detail="AI chatbot is disabled. Please enable it in settings to use chat features."
        )

    # Validate message
    if not request_data.message or len(request_data.message.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    if len(request_data.message) > 2000:
        raise HTTPException(
            status_code=400,
            detail="Message too long (max 2000 characters)"
        )

    try:
        # Process message through ChatService
        result = await ChatService.process_chat_message(
            session=session,
            user_id=user_id,
            message_content=request_data.message,
            agent_manager=agent_manager
        )

        return ChatMessageResponse(**result)

    except Exception as e:
        print(f"Error processing chat message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.post("/{user_id}/chat/stream")
async def send_chat_message_stream(
    user_id: str,
    request_data: ChatMessageRequest,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Send a chat message and stream AI response in real-time.

    This endpoint uses Server-Sent Events (SSE) to stream the response,
    providing a better user experience with incremental updates.

    Args:
        user_id: User ID
        request_data: Chat message request
        request: FastAPI request (for auth)
        session: Database session

    Returns:
        StreamingResponse with text/event-stream content type

    Raises:
        403: User not authorized or AI chatbot disabled
        400: Invalid request
        429: Rate limit exceeded
    """
    # Verify user authorization
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot send chat messages for another user"
        )

    # Check rate limit
    if not chat_rate_limiter.is_allowed(user_id):
        remaining = chat_rate_limiter.get_remaining(user_id)
        reset_time = chat_rate_limiter.get_reset_time(user_id)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Please try again in {reset_time} seconds.",
            headers={
                "X-RateLimit-Limit": str(chat_rate_limiter.max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_time),
                "Retry-After": str(reset_time)
            }
        )

    # Check if user has AI chatbot enabled
    from ..models import UserPreferences
    from sqlmodel import select

    prefs_statement = select(UserPreferences).where(
        UserPreferences.user_id == user_id
    )
    preferences = session.exec(prefs_statement).first()

    if not preferences or not preferences.ai_enabled:
        raise HTTPException(
            status_code=403,
            detail="AI chatbot is disabled. Please enable it in settings to use chat features."
        )

    # Validate message
    if not request_data.message or len(request_data.message.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    async def generate_stream():
        """Generator function for streaming response."""
        try:
            async for chunk in ChatService.stream_chat_message(
                session=session,
                user_id=user_id,
                message_content=request_data.message,
                agent_manager=agent_manager
            ):
                # Format as SSE (Server-Sent Events)
                yield f"data: {chunk}\n\n"

            # Send completion signal
            yield "data: [DONE]\n\n"

        except Exception as e:
            print(f"Error streaming chat message: {str(e)}")
            yield f"data: ERROR: {str(e)}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )


@router.get("/{user_id}/chat/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    user_id: str,
    request: Request,
    session: Session = Depends(get_session),
    limit: int = 50
):
    """
    Get conversation history for the user.

    Args:
        user_id: User ID
        request: FastAPI request (for auth)
        session: Database session
        limit: Maximum number of messages to retrieve

    Returns:
        ConversationHistoryResponse with messages

    Raises:
        403: User not authorized
        404: No conversation found
    """
    # Verify user authorization
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot access another user's chat history"
        )

    try:
        # Get or create conversation
        conversation = ChatService.get_or_create_conversation(session, user_id)

        # Get messages
        messages = ChatService.get_conversation_history(
            session=session,
            user_id=user_id,
            conversation_id=conversation.id,
            limit=limit
        )

        # Format messages
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
                "language": msg.language,
                "related_task_id": msg.related_task_id
            })

        return ConversationHistoryResponse(
            conversation_id=conversation.id,
            messages=formatted_messages
        )

    except Exception as e:
        print(f"Error retrieving conversation history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve conversation history"
        )


@router.delete("/{user_id}/chat/history")
async def delete_conversation_history(
    user_id: str,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Delete all conversation history for the user.

    This is used when user opts out of AI features with history deletion.

    Args:
        user_id: User ID
        request: FastAPI request (for auth)
        session: Database session

    Returns:
        Success message with count of deleted messages

    Raises:
        403: User not authorized
    """
    # Verify user authorization
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot delete another user's chat history"
        )

    try:
        count = ChatService.delete_conversation_history(
            session=session,
            user_id=user_id
        )

        return {
            "message": "Conversation history deleted successfully",
            "messages_deleted": count
        }

    except Exception as e:
        print(f"Error deleting conversation history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete conversation history"
        )
