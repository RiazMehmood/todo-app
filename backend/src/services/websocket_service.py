"""
WebSocket Service

Provides WebSocket connection management, presence tracking, and event broadcasting.

Features:
- ConnectionManager for tracking active WebSocket connections
- Redis pub/sub integration for multi-instance broadcasting
- Presence tracking with 30-second TTL
- Heartbeat monitoring with automatic timeout
"""

import json
import asyncio
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from fastapi import WebSocket
import uuid

from ..infrastructure.redis_client import redis_client


class ConnectionManager:
    """
    Manages active WebSocket connections with Redis pub/sub for multi-instance support.

    Features:
    - Track connections per user
    - Broadcast messages to all connections or specific users
    - Redis pub/sub for horizontal scaling
    - Heartbeat monitoring with 30-second timeout
    """

    def __init__(self):
        """Initialize connection manager with empty connection tracking."""
        # Active connections: {user_id: {session_id: websocket}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

        # Heartbeat tracking: {session_id: last_heartbeat_time}
        self.heartbeats: Dict[str, datetime] = {}

        # Redis client for pub/sub
        self.redis = redis_client

        # Pub/sub channel for broadcasting
        self.broadcast_channel = "todo:websocket:broadcast"

        # Heartbeat timeout (30 seconds)
        self.heartbeat_timeout = 30

        # Heartbeat monitor task
        self.heartbeat_monitor_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket, user_id: str) -> str:
        """
        Accept WebSocket connection and register it.

        Args:
            websocket: FastAPI WebSocket connection
            user_id: User ID for this connection

        Returns:
            session_id: Unique session identifier for this connection
        """
        await websocket.accept()

        # Generate unique session ID
        session_id = str(uuid.uuid4())

        # Register connection
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}

        self.active_connections[user_id][session_id] = websocket

        # Initialize heartbeat
        self.heartbeats[session_id] = datetime.utcnow()

        # Start heartbeat monitor if not already running
        if not self.heartbeat_monitor_task or self.heartbeat_monitor_task.done():
            self.heartbeat_monitor_task = asyncio.create_task(self._monitor_heartbeats())

        print(f"✅ WebSocket connected: user={user_id}, session={session_id}")

        return session_id

    async def disconnect(self, user_id: str, session_id: str):
        """
        Disconnect WebSocket and clean up tracking.

        Args:
            user_id: User ID
            session_id: Session ID to disconnect
        """
        # Remove connection
        if user_id in self.active_connections:
            if session_id in self.active_connections[user_id]:
                del self.active_connections[user_id][session_id]

            # Clean up empty user dict
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        # Remove heartbeat tracking
        if session_id in self.heartbeats:
            del self.heartbeats[session_id]

        # Clean up presence in Redis
        await self._clear_presence(user_id, session_id)

        print(f"❌ WebSocket disconnected: user={user_id}, session={session_id}")

    async def send_personal_message(self, user_id: str, session_id: str, message: dict):
        """
        Send message to specific user session.

        Args:
            user_id: Target user ID
            session_id: Target session ID
            message: Message dictionary to send
        """
        if user_id in self.active_connections:
            if session_id in self.active_connections[user_id]:
                websocket = self.active_connections[user_id][session_id]
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    print(f"Error sending personal message: {e}")
                    # Connection might be dead, disconnect it
                    await self.disconnect(user_id, session_id)

    async def send_to_user(self, user_id: str, message: dict):
        """
        Send message to all sessions of a specific user.

        Args:
            user_id: Target user ID
            message: Message dictionary to send
        """
        if user_id in self.active_connections:
            # Send to all sessions for this user
            for session_id in list(self.active_connections[user_id].keys()):
                await self.send_personal_message(user_id, session_id, message)

    async def broadcast(self, message: dict, exclude_user: Optional[str] = None):
        """
        Broadcast message to all connected users (via Redis pub/sub for multi-instance).

        Args:
            message: Message dictionary to broadcast
            exclude_user: Optional user ID to exclude from broadcast
        """
        # Add metadata
        broadcast_message = {
            "message": message,
            "exclude_user": exclude_user,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Publish to Redis for multi-instance broadcasting
        try:
            await self.redis.publish(
                self.broadcast_channel,
                json.dumps(broadcast_message)
            )
        except Exception as e:
            print(f"Error publishing to Redis: {e}")
            # Fallback to local broadcast if Redis fails
            await self._broadcast_local(message, exclude_user)

    async def _broadcast_local(self, message: dict, exclude_user: Optional[str] = None):
        """
        Broadcast message to all connections on this instance only.

        Args:
            message: Message to broadcast
            exclude_user: Optional user ID to exclude
        """
        disconnected_sessions = []

        for user_id in list(self.active_connections.keys()):
            # Skip excluded user
            if exclude_user and user_id == exclude_user:
                continue

            for session_id in list(self.active_connections[user_id].keys()):
                websocket = self.active_connections[user_id][session_id]
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    print(f"Error broadcasting to {user_id}/{session_id}: {e}")
                    disconnected_sessions.append((user_id, session_id))

        # Clean up dead connections
        for user_id, session_id in disconnected_sessions:
            await self.disconnect(user_id, session_id)

    async def update_heartbeat(self, session_id: str):
        """
        Update heartbeat timestamp for a session.

        Args:
            session_id: Session ID to update
        """
        self.heartbeats[session_id] = datetime.utcnow()

    async def _monitor_heartbeats(self):
        """
        Background task to monitor heartbeats and disconnect stale connections.

        Runs every 10 seconds and checks for connections with no heartbeat for >30 seconds.
        """
        while True:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds

                now = datetime.utcnow()
                timeout_threshold = timedelta(seconds=self.heartbeat_timeout)

                # Find stale sessions
                stale_sessions = []
                for session_id, last_heartbeat in self.heartbeats.items():
                    if now - last_heartbeat > timeout_threshold:
                        stale_sessions.append(session_id)

                # Disconnect stale sessions
                for session_id in stale_sessions:
                    # Find user_id for this session
                    user_id = None
                    for uid, sessions in self.active_connections.items():
                        if session_id in sessions:
                            user_id = uid
                            break

                    if user_id:
                        print(f"⏰ Heartbeat timeout: user={user_id}, session={session_id}")
                        await self.disconnect(user_id, session_id)

                        # Try to close the websocket gracefully
                        try:
                            websocket = self.active_connections.get(user_id, {}).get(session_id)
                            if websocket:
                                await websocket.close(code=1000, reason="Heartbeat timeout")
                        except:
                            pass

            except Exception as e:
                print(f"Error in heartbeat monitor: {e}")

    async def get_active_users_count(self) -> int:
        """
        Get count of currently active users.

        Returns:
            Number of unique users with active connections
        """
        return len(self.active_connections)

    async def get_active_sessions_count(self) -> int:
        """
        Get count of active WebSocket sessions.

        Returns:
            Total number of active sessions across all users
        """
        return sum(len(sessions) for sessions in self.active_connections.values())

    async def _clear_presence(self, user_id: str, session_id: str):
        """
        Clear presence data from Redis when user disconnects.

        Args:
            user_id: User ID
            session_id: Session ID
        """
        try:
            # Remove presence key
            presence_key = f"presence:{user_id}:{session_id}"
            await self.redis.delete(presence_key)
        except Exception as e:
            print(f"Error clearing presence: {e}")


# Global connection manager instance
connection_manager = ConnectionManager()


async def update_presence(
    user_id: str,
    session_id: str,
    task_id: Optional[str] = None,
    status: str = "viewing"
) -> None:
    """
    Update user presence in Redis with 30-second TTL.

    Args:
        user_id: User ID
        session_id: Session ID
        task_id: Currently viewing/editing task ID (optional)
        status: Presence status (viewing, editing, idle)
    """
    redis = redis_client

    presence_data = {
        "user_id": user_id,
        "session_id": session_id,
        "task_id": task_id,
        "status": status,
        "last_seen": datetime.utcnow().isoformat()
    }

    # Store in Redis with 30-second TTL
    presence_key = f"presence:{user_id}:{session_id}"
    try:
        await redis.setex(
            presence_key,
            30,  # 30-second TTL
            json.dumps(presence_data)
        )
    except Exception as e:
        print(f"Error updating presence: {e}")


async def get_active_users(task_id: Optional[str] = None) -> List[dict]:
    """
    Get list of currently active users.

    Args:
        task_id: Optional filter to only get users viewing/editing this task

    Returns:
        List of presence data dictionaries
    """
    redis = redis_client

    try:
        # Scan for all presence keys
        presence_keys = []
        cursor = 0
        while True:
            cursor, keys = await redis.scan(cursor, match="presence:*", count=100)
            presence_keys.extend(keys)
            if cursor == 0:
                break

        # Get all presence data
        active_users = []
        for key in presence_keys:
            data = await redis.get(key)
            if data:
                presence = json.loads(data)

                # Filter by task_id if specified
                if task_id is None or presence.get("task_id") == task_id:
                    active_users.append(presence)

        return active_users

    except Exception as e:
        print(f"Error getting active users: {e}")
        return []


async def publish_task_event(event_type: str, task: dict, user_id: str, changes: Optional[List[str]] = None):
    """
    Publish task event to WebSocket clients via Redis pub/sub.

    Args:
        event_type: Event type (task_created, task_updated, task_deleted)
        task: Task data (or task_id for delete events)
        user_id: User ID who triggered the event
        changes: List of changed fields (for update events)
    """
    message = {
        "type": event_type,
        "timestamp": datetime.utcnow().isoformat()
    }

    if event_type == "task_created":
        message["task"] = task
        message["created_by"] = user_id

    elif event_type == "task_updated":
        message["task"] = task
        message["updated_by"] = user_id
        message["updated_at"] = datetime.utcnow().isoformat()
        message["changes"] = changes or []

    elif event_type == "task_deleted":
        message["task_id"] = task.get("id") if isinstance(task, dict) else task
        message["deleted_by"] = user_id

    # Broadcast to all connected clients
    await connection_manager.broadcast(message)
