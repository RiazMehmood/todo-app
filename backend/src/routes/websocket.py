"""
WebSocket Routes - Real-time communication endpoint.

Implements WebSocket protocol from:
specs/005-cloud-native-deployment/contracts/websocket-protocol.md

Features:
- JWT authentication via query parameter
- Heartbeat monitoring (10s interval, 30s timeout)
- Presence tracking (viewing, editing, idle status)
- Event broadcasting (task create/update/delete)
- Connection lifecycle management
"""

import json
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from jose import jwt, JWTError
import os

from ..services.websocket_service import (
    connection_manager,
    update_presence,
    get_active_users,
    publish_task_event
)

router = APIRouter()

# JWT configuration
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "your-secret-key-here")
ALGORITHM = "HS256"


def verify_jwt_token(token: str) -> dict:
    """
    Verify JWT token and extract payload.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


@router.websocket("/api/{user_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: str = Query(..., description="JWT authentication token")
):
    """
    WebSocket endpoint for real-time task updates and presence tracking.

    Implements: WebSocket protocol from websocket-protocol.md

    Args:
        websocket: WebSocket connection
        user_id: User ID from path parameter
        token: JWT authentication token (query parameter)

    Protocol:
        - Client sends heartbeat every 10 seconds
        - Server disconnects after 30 seconds without heartbeat
        - All messages are JSON with "type" field for routing

    Message Types (Client → Server):
        - heartbeat: Update presence and connection health
        - task_edit_start: Notify editing status
        - task_edit_end: Clear editing status

    Message Types (Server → Client):
        - welcome: Connection confirmation with session_id
        - task_created: Broadcast new task
        - task_updated: Broadcast task update
        - task_deleted: Broadcast task deletion
        - presence_update: User status changes
        - notification: System notifications
        - error: Error responses
    """
    session_id = None

    try:
        # Validate JWT token
        try:
            payload = verify_jwt_token(token)
            authenticated_user_id = payload.get("user_id") or payload.get("sub")

            # Verify user_id matches authenticated user
            if authenticated_user_id != user_id:
                await websocket.close(code=1008, reason="Unauthorized: user_id mismatch")
                return

        except Exception as e:
            print(f"❌ WebSocket auth failed: {e}")
            await websocket.close(code=1008, reason="Invalid or expired token")
            return

        # Accept connection and register with ConnectionManager
        session_id = await connection_manager.connect(websocket, user_id)

        # Send welcome message
        welcome_message = {
            "type": "welcome",
            "session_id": session_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_json(welcome_message)

        print(f"✅ WebSocket authenticated: user={user_id}, session={session_id}")

        # Message receive loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()
                message_type = data.get("type")

                if not message_type:
                    # Send error response
                    error_message = {
                        "type": "error",
                        "code": "INVALID_MESSAGE",
                        "message": "Missing 'type' field in message",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await websocket.send_json(error_message)
                    continue

                # Route message to appropriate handler
                if message_type == "heartbeat":
                    await handle_heartbeat(websocket, user_id, session_id, data)

                elif message_type == "task_edit_start":
                    await handle_task_edit_start(user_id, session_id, data)

                elif message_type == "task_edit_end":
                    await handle_task_edit_end(user_id, session_id, data)

                else:
                    # Unknown message type
                    error_message = {
                        "type": "error",
                        "code": "UNKNOWN_MESSAGE_TYPE",
                        "message": f"Unknown message type: {message_type}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await websocket.send_json(error_message)

            except json.JSONDecodeError:
                # Invalid JSON
                error_message = {
                    "type": "error",
                    "code": "INVALID_JSON",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket.send_json(error_message)

            except Exception as e:
                # Unexpected error during message processing
                print(f"❌ Error processing WebSocket message: {e}")
                error_message = {
                    "type": "error",
                    "code": "INTERNAL_ERROR",
                    "message": "Internal server error",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket.send_json(error_message)

    except WebSocketDisconnect:
        print(f"🔌 WebSocket client disconnected: user={user_id}, session={session_id}")

    except Exception as e:
        print(f"❌ WebSocket error: {e}")

    finally:
        # Clean up connection
        if session_id:
            await connection_manager.disconnect(user_id, session_id)


async def handle_heartbeat(
    websocket: WebSocket,
    user_id: str,
    session_id: str,
    data: dict
):
    """
    Handle heartbeat message from client.

    Updates presence tracking and connection health.

    Implements: Heartbeat protocol (10s interval, 30s timeout)

    Args:
        websocket: WebSocket connection
        user_id: User ID
        session_id: Session ID
        data: Heartbeat data with task_id and status
    """
    # Extract presence data
    task_id = data.get("task_id")
    status = data.get("status", "viewing")

    # Validate status
    if status not in ["viewing", "editing", "idle"]:
        status = "viewing"

    # Update heartbeat timestamp
    await connection_manager.update_heartbeat(session_id)

    # Update presence in Redis
    await update_presence(
        user_id=user_id,
        session_id=session_id,
        task_id=task_id,
        status=status
    )

    # No response needed for heartbeat (per protocol)


async def handle_task_edit_start(
    user_id: str,
    session_id: str,
    data: dict
):
    """
    Handle task edit start notification.

    Broadcasts presence update to other users viewing the same task.

    Args:
        user_id: User ID who started editing
        session_id: Session ID
        data: Message data with task_id
    """
    task_id = data.get("task_id")

    if not task_id:
        # Task ID is required
        return

    # Update presence to "editing"
    await update_presence(
        user_id=user_id,
        session_id=session_id,
        task_id=task_id,
        status="editing"
    )

    # Get all active users viewing this task
    active_users = await get_active_users(task_id=task_id)

    # Broadcast presence update
    presence_message = {
        "type": "presence_update",
        "users": active_users
    }
    await connection_manager.broadcast(presence_message)


async def handle_task_edit_end(
    user_id: str,
    session_id: str,
    data: dict
):
    """
    Handle task edit end notification.

    Broadcasts presence update to other users.

    Args:
        user_id: User ID who stopped editing
        session_id: Session ID
        data: Message data with task_id
    """
    task_id = data.get("task_id")

    # Update presence to "viewing"
    await update_presence(
        user_id=user_id,
        session_id=session_id,
        task_id=task_id if task_id else None,
        status="viewing"
    )

    # Get all active users
    active_users = await get_active_users(task_id=task_id)

    # Broadcast presence update
    presence_message = {
        "type": "presence_update",
        "users": active_users
    }
    await connection_manager.broadcast(presence_message)
