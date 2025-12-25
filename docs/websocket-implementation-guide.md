# FastAPI WebSocket Implementation Guide

## Executive Summary

This guide provides comprehensive patterns and best practices for implementing WebSocket features in FastAPI for real-time collaboration. It addresses four critical architectural questions:

1. Broadcasting messages to multiple connected clients
2. JWT authentication for WebSocket connections
3. Handling disconnections and automatic reconnections
4. Multi-instance deployment with Redis pub/sub

---

## 1. Broadcasting Messages to All Connected Clients

### Pattern 1A: In-Process Broadcasting (Single Instance)

For development and single-server deployments, use an in-memory connection manager:

```python
# backend/src/websocket/managers.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts messages.

    NOTE: This implementation is suitable only for single-process deployments.
    For multi-instance production, use Redis pub/sub (see Pattern 1B).
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected client."""
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                disconnected.append(connection)

        # Remove failed connections
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_text(self, text: str):
        """Send text message to all connected clients."""
        await self.broadcast({"type": "message", "data": text})

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to a specific client."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            self.disconnect(websocket)


# Global instance
manager = ConnectionManager()
```

### Example: Broadcasting Task Updates

```python
# backend/src/routes/tasks.py (partial)
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from src.websocket.managers import manager
from src.db import get_session
from src.models import Task
from src.middleware.auth import verify_jwt_ws
from sqlmodel import Session

router = APIRouter()


@router.post("/{user_id}/tasks", response_model=Task, status_code=201)
async def create_task(
    user_id: str,
    task_data: dict,
    request: Request,
    session: Session = Depends(get_session)
):
    """Create task and broadcast to all connected clients."""
    # Verify user (see JWT section below)
    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Create task
    task = Task(
        user_id=user_id,
        title=task_data['title'],
        description=task_data.get('description')
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Broadcast to all connected clients
    await manager.broadcast({
        "type": "task_created",
        "user_id": user_id,
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "created_at": task.created_at.isoformat()
        }
    })

    return task
```

### Pattern 1B: Redis Pub/Sub Broadcasting (Multi-Instance)

For production deployments with multiple servers, use Redis pub/sub:

```python
# backend/src/websocket/redis_manager.py
import json
import logging
from typing import List, Callable
from fastapi import WebSocket
import aioredis
import os

logger = logging.getLogger(__name__)


class RedisPubSubManager:
    """
    Manages WebSocket connections with Redis pub/sub for multi-instance deployments.

    Allows messages to be broadcast across all FastAPI instances behind a load balancer.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.redis_client = None
        self.pubsub = None

    async def init(self):
        """Initialize Redis connection."""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = await aioredis.create_redis_pool(redis_url)
        logger.info("Redis connection initialized")

    async def connect(self, websocket: WebSocket):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Local connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected client."""
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Local connections: {len(self.active_connections)}")

    async def broadcast(self, channel: str, message: dict):
        """
        Publish message to Redis channel.

        All FastAPI instances subscribed to this channel will receive the message
        and broadcast to their local WebSocket connections.
        """
        if not self.redis_client:
            await self.init()

        try:
            await self.redis_client.publish(channel, json.dumps(message))
            logger.info(f"Message published to channel '{channel}'")
        except Exception as e:
            logger.error(f"Failed to publish to Redis: {e}")

    async def subscribe(self, channel: str, callback: Callable):
        """
        Subscribe to Redis channel and execute callback on messages.

        This should be called at application startup for each channel.
        """
        if not self.redis_client:
            await self.init()

        channels = await self.redis_client.subscribe(channel)
        ch = channels[0]

        while True:
            try:
                message = await ch.get_json()
                await callback(message)
            except Exception as e:
                logger.error(f"Error in subscription callback: {e}")
                break

    async def broadcast_to_local(self, message: dict):
        """Send message to all locally connected WebSocket clients."""
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to local client: {e}")
                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect(connection)


# Global instance
redis_manager = RedisPubSubManager()
```

### Example: Redis-Backed Broadcasting

```python
# backend/src/routes/tasks.py (with Redis)
from src.websocket.redis_manager import redis_manager

# In main.py startup event:
# @app.on_event("startup")
# async def startup():
#     await redis_manager.init()
#     # Subscribe to task events channel
#     asyncio.create_task(
#         redis_manager.subscribe("tasks", redis_manager.broadcast_to_local)
#     )

@router.post("/{user_id}/tasks", response_model=Task, status_code=201)
async def create_task(
    user_id: str,
    task_data: dict,
    request: Request,
    session: Session = Depends(get_session)
):
    """Create task and broadcast via Redis."""
    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    task = Task(
        user_id=user_id,
        title=task_data['title'],
        description=task_data.get('description')
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Publish to Redis channel - reaches all FastAPI instances
    await redis_manager.broadcast("tasks", {
        "type": "task_created",
        "user_id": user_id,
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "created_at": task.created_at.isoformat()
        }
    })

    return task
```

---

## 2. WebSocket Authentication with JWT Tokens

### Best Practice: Query Parameter Authentication

Query parameters are the recommended approach for WebSocket authentication in 2025, as they are:
- Widely supported across browsers and clients
- Easier to debug and implement
- Compatible with WebSocket protocols that don't support custom headers

```python
# backend/src/middleware/websocket_auth.py
from fastapi import WebSocket, WebSocketException, status, Query
from jose import jwt, JWTError
import os
from typing import Annotated

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "your-secret-key")
ALGORITHM = "HS256"


async def get_token_from_query(
    websocket: WebSocket,
    token: Annotated[str | None, Query()] = None
) -> str:
    """
    Extract JWT token from query parameter.

    Usage: ws://localhost:8000/ws/tasks?token=eyJ0eXAi...
    """
    if token is None:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Token not provided"
        )
    return token


async def verify_websocket_token(token: str) -> dict:
    """
    Verify JWT token and return payload.

    Returns:
        dict: Decoded JWT payload containing user_id and email

    Raises:
        WebSocketException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")

        if user_id is None:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Invalid token payload"
            )

        return payload

    except JWTError as e:
        if "expired" in str(e).lower():
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Token expired"
            )
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token"
        )


async def verify_jwt_websocket(
    websocket: WebSocket,
    token: Annotated[str | None, Query()] = None
) -> dict:
    """
    Complete WebSocket authentication dependency.

    Combines token extraction and verification.
    Use as a dependency in WebSocket endpoints.

    Example:
        @app.websocket("/ws/tasks")
        async def websocket_endpoint(
            websocket: WebSocket,
            auth: dict = Depends(verify_jwt_websocket)
        ):
            await websocket.accept()
            user_id = auth["user_id"]
            ...
    """
    token = await get_token_from_query(websocket, token)
    return await verify_websocket_token(token)
```

### WebSocket Endpoint with JWT

```python
# backend/src/routes/websocket_routes.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from src.middleware.websocket_auth import verify_jwt_websocket
from src.websocket.managers import manager
from typing import Annotated
import json

router = APIRouter()


@router.websocket("/ws/tasks")
async def websocket_tasks_endpoint(
    websocket: WebSocket,
    auth: Annotated[dict, Depends(verify_jwt_websocket)]
):
    """
    WebSocket endpoint for real-time task updates.

    URL: ws://localhost:8000/ws/tasks?token=<JWT_TOKEN>

    Authentication:
        - JWT token passed as query parameter
        - Token verified before connection acceptance
        - Errors raised before accept() are handled by FastAPI

    Message Format:
        Incoming (from client):
            {
                "type": "subscribe_user_tasks",
                "user_id": "user123"
            }

        Outgoing (from server):
            {
                "type": "task_created",
                "user_id": "user123",
                "task": { ... }
            }
    """
    await manager.connect(websocket)
    user_id = auth["user_id"]

    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")

            # Example: Client requests to subscribe to their tasks
            if message_type == "subscribe_user_tasks":
                requested_user = data.get("user_id")

                # Verify user can only subscribe to their own tasks
                if requested_user != user_id:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": "Cannot subscribe to other user's tasks"
                    }, websocket)
                    continue

                # Confirm subscription
                await manager.send_personal_message({
                    "type": "subscribed",
                    "user_id": user_id
                }, websocket)

            # Example: Client sends a ping to stay alive
            elif message_type == "ping":
                await manager.send_personal_message({
                    "type": "pong"
                }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"User {user_id} disconnected")
```

### Alternative: Header Authentication (Limited Browser Support)

While headers are not recommended for WebSocket due to browser limitations, here's how to use cookies:

```python
# backend/src/middleware/websocket_auth_cookie.py
from fastapi import WebSocket, WebSocketException, status, Cookie
from typing import Annotated

async def verify_jwt_websocket_cookie(
    websocket: WebSocket,
    token: Annotated[str | None, Cookie()] = None
) -> dict:
    """
    WebSocket authentication via cookie.

    NOTE: Cookies are sent with the initial WebSocket upgrade request.
    This is more secure than query parameters but requires browsers to support it.

    Browsers automatically include cookies with WebSocket upgrade requests
    if the same origin makes the request.
    """
    if token is None:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Authentication cookie not found"
        )

    try:
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid authentication cookie"
        )
```

---

## 3. Handling Disconnections and Automatic Reconnections

### Server-Side: Connection Management

```python
# backend/src/websocket/connection_handler.py
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)


class WebSocketConnectionHandler:
    """
    Manages individual WebSocket connections with heartbeat and timeout.
    """

    def __init__(self, websocket: WebSocket, user_id: str):
        self.websocket = websocket
        self.user_id = user_id
        self.connected_at = datetime.utcnow()
        self.last_heartbeat = datetime.utcnow()
        self.heartbeat_timeout = 60  # seconds

    async def handle_connection(self, on_message_callback):
        """
        Main connection loop with heartbeat.

        Sends periodic heartbeat to client and listens for messages.
        If client fails to respond to heartbeat, connection is closed.
        """
        try:
            # Start heartbeat task
            heartbeat_task = asyncio.create_task(self.send_heartbeats())

            # Listen for messages
            while True:
                data = await self.websocket.receive_json()
                self.last_heartbeat = datetime.utcnow()

                # Handle message
                await on_message_callback(data)

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {self.user_id}")

        except asyncio.CancelledError:
            logger.info(f"WebSocket connection cancelled for user {self.user_id}")

        except Exception as e:
            logger.error(f"WebSocket error for user {self.user_id}: {e}")

        finally:
            heartbeat_task.cancel()
            await self.websocket.close()

    async def send_heartbeats(self):
        """
        Send periodic heartbeat messages to keep connection alive.

        Some proxies/firewalls close idle connections.
        Heartbeats prevent this.
        """
        while True:
            try:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds

                await self.websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })

                logger.debug(f"Heartbeat sent to user {self.user_id}")

            except Exception as e:
                logger.warning(f"Failed to send heartbeat: {e}")
                break

    async def send_message(self, message: dict):
        """Send message to client."""
        try:
            await self.websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
```

### Client-Side: Automatic Reconnection (TypeScript/React)

```typescript
// frontend/lib/websocket.ts
export class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private token: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000; // Start with 1 second
  private maxReconnectDelay = 30000; // Max 30 seconds
  private messageHandlers: Map<string, (data: any) => void> = new Map();
  private isManualClose = false;

  constructor(baseUrl: string, token: string) {
    this.url = `${baseUrl}?token=${token}`;
    this.token = token;
  }

  /**
   * Connect to WebSocket with automatic reconnection on failure.
   */
  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log("WebSocket connected");
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          this.handleMessage(event.data);
        };

        this.ws.onerror = (error) => {
          console.error("WebSocket error:", error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log("WebSocket closed");

          if (!this.isManualClose) {
            this.attemptReconnect();
          }
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Attempt reconnection with exponential backoff.
   *
   * Backoff strategy:
   * Attempt 1: 1s
   * Attempt 2: 2s
   * Attempt 3: 4s
   * Attempt 4: 8s
   * ... up to 30s max
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error("Max reconnection attempts reached");
      return;
    }

    this.reconnectAttempts++;

    // Calculate exponential backoff with jitter
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.maxReconnectDelay
    );
    const jitter = Math.random() * 0.1 * delay;
    const finalDelay = delay + jitter;

    console.log(
      `Attempting reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) ` +
      `in ${finalDelay.toFixed(0)}ms`
    );

    setTimeout(() => {
      this.connect().catch((error) => {
        console.error("Reconnection failed:", error);
        // Automatically retry
      });
    }, finalDelay);
  }

  /**
   * Handle incoming messages from server.
   */
  private handleMessage(data: string): void {
    try {
      const message = JSON.parse(data);

      // Handle server heartbeat
      if (message.type === "heartbeat") {
        this.sendMessage({ type: "pong" });
        return;
      }

      // Route to registered handlers
      const handler = this.messageHandlers.get(message.type);
      if (handler) {
        handler(message);
      } else {
        console.warn(`No handler for message type: ${message.type}`);
      }
    } catch (error) {
      console.error("Failed to parse message:", error);
    }
  }

  /**
   * Send message to server.
   */
  sendMessage(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.error("WebSocket not connected");
    }
  }

  /**
   * Register handler for message type.
   */
  on(messageType: string, handler: (data: any) => void): void {
    this.messageHandlers.set(messageType, handler);
  }

  /**
   * Manually close connection (no reconnect).
   */
  disconnect(): void {
    this.isManualClose = true;
    if (this.ws) {
      this.ws.close();
    }
  }

  /**
   * Check if connected.
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}
```

### React Hook for WebSocket Integration

```typescript
// frontend/lib/useWebSocket.ts
import { useEffect, useRef, useState } from "react";
import { WebSocketClient } from "./websocket";

export function useWebSocket(token: string) {
  const clientRef = useRef<WebSocketClient | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const client = new WebSocketClient(
      `${process.env.NEXT_PUBLIC_WS_URL}/ws/tasks`,
      token
    );

    clientRef.current = client;

    // Setup message handlers before connecting
    client.on("task_created", (data) => {
      console.log("Task created:", data);
      // Update UI
    });

    client.on("task_updated", (data) => {
      console.log("Task updated:", data);
      // Update UI
    });

    // Connect
    client
      .connect()
      .then(() => setIsConnected(true))
      .catch((error) => {
        console.error("Failed to connect:", error);
        setIsConnected(false);
      });

    // Cleanup on unmount
    return () => {
      client.disconnect();
    };
  }, [token]);

  const send = (message: any) => {
    if (clientRef.current) {
      clientRef.current.sendMessage(message);
    }
  };

  return {
    isConnected,
    send,
    client: clientRef.current,
  };
}
```

---

## 4. Multi-Instance Deployment with Redis Pub/Sub

### Architecture: Load-Balanced WebSocket Deployment

```
                    ┌─────────────────────────┐
                    │   Client Browser        │
                    │  (WebSocket TCP)        │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  Load Balancer (HAProxy │
                    │  or AWS ALB)            │
                    │  - WebSocket Sticky     │
                    │    Sessions (optional)  │
                    └────┬────────────────┬───┘
                         │                │
        ┌────────────────▼─┐    ┌────────▼──────────────┐
        │  FastAPI        │    │  FastAPI             │
        │  Instance 1     │    │  Instance 2          │
        │  (Uvicorn)      │    │  (Uvicorn)           │
        │                 │    │                      │
        │  - Handles      │    │  - Handles           │
        │    WS conns     │    │    WS conns          │
        │  - Subscribes   │    │  - Subscribes        │
        │    to Redis     │    │    to Redis          │
        └────────┬────────┘    └────────┬─────────────┘
                 │                      │
                 └──────────┬───────────┘
                            │
                    ┌───────▼──────────┐
                    │  Redis Pub/Sub   │
                    │  (Central Broker)│
                    │                  │
                    │  Channels:       │
                    │  - tasks         │
                    │  - user.{id}     │
                    │  - broadcasts    │
                    └──────────────────┘
```

### FastAPI Setup for Multi-Instance

```python
# backend/src/main.py (updated)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from src.websocket.redis_manager import redis_manager
from src.db import create_db_and_tables
from src.routes import tasks, websocket_routes

app = FastAPI(
    title="Todo API",
    description="RESTful API with WebSocket for todo management",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourapp.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Initialize database and Redis connections."""
    create_db_and_tables()

    # Initialize Redis for pub/sub
    await redis_manager.init()

    # Subscribe to channels in background
    asyncio.create_task(subscribe_to_channels())


async def subscribe_to_channels():
    """
    Subscribe to Redis channels for different event types.

    This allows messages published by one instance to reach
    all connected clients across all instances.
    """

    async def on_task_event(message: dict):
        """Broadcast task events to local WebSocket clients."""
        await redis_manager.broadcast_to_local(message)

    async def on_user_event(message: dict):
        """Broadcast user-specific events."""
        await redis_manager.broadcast_to_local(message)

    # Subscribe to multiple channels
    tasks = [
        redis_manager.subscribe("tasks", on_task_event),
        redis_manager.subscribe("user_events", on_user_event),
    ]

    await asyncio.gather(*tasks)


# Include routers
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(websocket_routes.router, tags=["websocket"])


@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

### Kubernetes Deployment with Redis

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
spec:
  replicas: 3  # Multiple instances
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
    spec:
      containers:
      - name: fastapi
        image: todo-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          value: redis://redis-service:6379
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: database-url
        - name: BETTER_AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: auth-secrets
              key: secret
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: todo-backend-service
spec:
  selector:
    app: todo-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: redis-storage
          mountPath: /data
      volumes:
      - name: redis-storage
        emptyDir: {}

---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  clusterIP: None  # Headless service for Redis
```

### Client Connection with Load Balancer

```typescript
// frontend/lib/config.ts
/**
 * WebSocket URL configuration for load-balanced deployment.
 *
 * Load balancer handles sticky sessions automatically,
 * ensuring client reconnects to same server instance if possible.
 */

export const WS_CONFIG = {
  // Production: Use load balancer URL
  // The load balancer routes new connections and automatically
  // maintains affinity for existing connections
  url: process.env.NEXT_PUBLIC_WS_URL || "wss://api.example.com/ws",

  // Reconnection strategy
  reconnect: {
    enabled: true,
    maxAttempts: 10,
    initialDelay: 1000,
    maxDelay: 30000,
  },
};
```

---

## Architectural Recommendations

### 1. When to Use Each Pattern

| Pattern | Use Case | Pros | Cons |
|---------|----------|------|------|
| **In-Process Manager** | Development, single server | Simple, no external deps | Doesn't scale, single point of failure |
| **Redis Pub/Sub** | Multi-instance, load-balanced | Scalable, resilient, simple | Redis dependency, operational overhead |
| **Kafka** | Event-driven, complex workflows | Durable, replay events | Complex setup, overkill for basic chat |

### 2. Security Best Practices

```python
# Security checklist for WebSocket implementation

# 1. Always use WSS (WebSocket Secure) in production
# 2. Validate JWT tokens before accepting connection
# 3. Use query parameters (safer than exposing in logs/history)
# 4. Implement per-message authentication checks
# 5. Rate limit WebSocket connections per user
# 6. Log all WebSocket events for audit trail
# 7. Implement heartbeat to detect stale connections
# 8. Validate message payloads
# 9. Use environment variables for secrets
# 10. Implement graceful shutdown (close all connections before restart)
```

### 3. Performance Optimization

```python
# backend/src/websocket/optimized_manager.py
from asyncio import Semaphore
from typing import Set

class OptimizedConnectionManager:
    """
    Connection manager with performance optimizations.
    """

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        # Limit concurrent connections per instance
        self.connection_semaphore = Semaphore(1000)
        # Group connections by room/topic for targeted broadcasting
        self.rooms: dict[str, Set[WebSocket]] = {}

    async def broadcast_to_room(self, room: str, message: dict):
        """
        Broadcast only to users in specific room.

        Reduces message overhead vs broadcasting to all users.
        """
        if room not in self.rooms:
            return

        failed = []
        for connection in self.rooms[room]:
            try:
                await connection.send_json(message)
            except:
                failed.append(connection)

        for connection in failed:
            await self.disconnect(connection)

    async def join_room(self, websocket: WebSocket, room: str):
        """Add connection to room."""
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(websocket)

    async def leave_room(self, websocket: WebSocket, room: str):
        """Remove connection from room."""
        if room in self.rooms:
            self.rooms[room].discard(websocket)
            if not self.rooms[room]:
                del self.rooms[room]
```

### 4. Monitoring and Debugging

```python
# backend/src/websocket/metrics.py
from datetime import datetime
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class WebSocketMetrics:
    """Track WebSocket connection metrics."""

    def __init__(self):
        self.connections_count = 0
        self.messages_sent = 0
        self.messages_received = 0
        self.errors_count = 0
        self.start_time = datetime.utcnow()

    def record_connect(self):
        """Record new connection."""
        self.connections_count += 1
        logger.info(f"Total connections: {self.connections_count}")

    def record_disconnect(self):
        """Record disconnection."""
        self.connections_count -= 1

    def record_message_sent(self):
        """Record sent message."""
        self.messages_sent += 1

    def record_message_received(self):
        """Record received message."""
        self.messages_received += 1

    def record_error(self):
        """Record error."""
        self.errors_count += 1

    def get_stats(self) -> Dict:
        """Get current statistics."""
        uptime = datetime.utcnow() - self.start_time
        return {
            "active_connections": self.connections_count,
            "total_messages_sent": self.messages_sent,
            "total_messages_received": self.messages_received,
            "errors": self.errors_count,
            "uptime_seconds": uptime.total_seconds(),
        }


# Global metrics instance
metrics = WebSocketMetrics()


# In FastAPI endpoint
@app.get("/metrics/websocket")
async def websocket_metrics():
    """Get WebSocket metrics."""
    return metrics.get_stats()
```

---

## Testing WebSocket Implementation

### Server-Side Tests (pytest)

```python
# backend/tests/test_websocket.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_websocket_requires_auth():
    """Test that WebSocket rejects unauthenticated connections."""
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/tasks"):
            pass


def test_websocket_with_valid_token():
    """Test WebSocket connection with valid JWT token."""
    token = "valid-jwt-token"

    with client.websocket_connect(f"/ws/tasks?token={token}") as websocket:
        # Send message
        websocket.send_json({"type": "ping"})

        # Receive response
        data = websocket.receive_json()
        assert data["type"] == "pong"


def test_websocket_broadcast():
    """Test that message is broadcast to all connections."""
    token = "valid-jwt-token"

    # Create two connections
    with client.websocket_connect(f"/ws/tasks?token={token}") as ws1:
        with client.websocket_connect(f"/ws/tasks?token={token}") as ws2:
            # Send message from first connection
            ws1.send_json({"type": "message", "data": "Hello"})

            # Both should receive it
            data1 = ws1.receive_json()
            data2 = ws2.receive_json()

            assert data1["type"] == "message"
            assert data2["type"] == "message"
```

### Client-Side Tests (Jest)

```typescript
// frontend/__tests__/websocket.test.ts
import { WebSocketClient } from "@/lib/websocket";

describe("WebSocketClient", () => {
  it("should handle automatic reconnection", async () => {
    const client = new WebSocketClient(
      "ws://localhost:8000/ws/tasks",
      "valid-token"
    );

    await client.connect();
    expect(client.isConnected()).toBe(true);

    // Simulate disconnection
    client.disconnect();
    expect(client.isConnected()).toBe(false);

    // Attempt reconnection
    await client.connect();
    expect(client.isConnected()).toBe(true);
  });

  it("should handle exponential backoff on failed reconnection", async () => {
    const client = new WebSocketClient(
      "ws://localhost:8000/ws/tasks",
      "invalid-token"
    );

    const startTime = Date.now();

    try {
      await client.connect();
    } catch (error) {
      const elapsed = Date.now() - startTime;
      // Should have retried with delays
      expect(elapsed).toBeGreaterThan(1000);
    }
  });
});
```

---

## Deployment Checklist

- [ ] JWT secret configured in environment
- [ ] Redis connection tested in staging
- [ ] WebSocket endpoints have authentication
- [ ] Heartbeat mechanism implemented
- [ ] Client reconnection logic tested
- [ ] Load balancer supports WebSocket (sticky sessions optional)
- [ ] Monitoring/metrics collection configured
- [ ] Error handling and logging in place
- [ ] Database connection pooling configured
- [ ] CORS headers allow WebSocket upgrade
- [ ] WSS (secure) used in production
- [ ] Tests passing (unit + integration)

---

## References

- [FastAPI WebSockets Documentation](https://fastapi.tiangolo.com/advanced/websockets/)
- [Starlette WebSocket API](https://starlette.io/websockets/)
- [Broadcaster Library (Redis Pub/Sub)](https://github.com/encode/broadcaster)
- [fastapi-websocket-pubsub Package](https://pypi.org/project/fastapi-websocket-pubsub/)
- [WebSocket Protocol (RFC 6455)](https://tools.ietf.org/html/rfc6455)
- [OWASP WebSocket Security](https://owasp.org/www-community/vulnerabilities/WebSocket_Protocol)
