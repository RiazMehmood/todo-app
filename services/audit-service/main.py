"""
Audit Service - Phase V Cloud-Native Architecture

This microservice consumes all task events from Kafka (via Dapr Pub/Sub)
and maintains a comprehensive audit trail of all task operations.

Responsibilities:
- Consume events from 'task-events' Kafka topic
- Store audit logs in database (PostgreSQL/Neon)
- Provide audit trail query API
- Maintain compliance and forensic records

Dependencies:
- Dapr (for Pub/Sub)
- Kafka (via Redpanda Cloud)
- PostgreSQL (Neon Serverless)
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from cloudevents.sdk.event import v1
from dapr.ext.grpc import App
from sqlmodel import SQLModel, Field, Session, create_engine, select
from fastapi import FastAPI, Depends, Query
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dapr configuration
DAPR_PUBSUB_NAME = "kafka-pubsub"
TASK_EVENTS_TOPIC = "task-events"
DAPR_APP_PORT = int(os.getenv("DAPR_APP_PORT", "50053"))

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/todo_db")

# Create database engine
engine = create_engine(DATABASE_URL, echo=True)


# Database Models
class AuditLog(SQLModel, table=True):
    """Audit log entry for task operations."""
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str = Field(max_length=50, index=True)  # created, updated, completed, deleted
    task_id: int = Field(index=True)
    user_id: str = Field(max_length=255, index=True)
    task_data: str = Field()  # JSON string of task data
    event_metadata: str = Field(default="{}")  # JSON string of event metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    kafka_offset: Optional[int] = Field(default=None)  # Kafka message offset for debugging


def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency for database session."""
    with Session(engine) as session:
        yield session


# Create Dapr App
dapr_app = App()

# Create FastAPI app for audit query API
api_app = FastAPI(title="Audit Service API", version="1.0.0")


@dapr_app.subscribe(pubsub_name=DAPR_PUBSUB_NAME, topic=TASK_EVENTS_TOPIC)
def handle_task_event(event: Any) -> Dict[str, str]:
    """
    Handle task event from Kafka and store in audit log.

    Args:
        event: Event data from Dapr

    Returns:
        Dict with status key indicating success or failure
    """
    try:
        # Parse event data
        if isinstance(event, bytes):
            event_data = json.loads(event.decode('utf-8'))
        elif isinstance(event, str):
            event_data = json.loads(event)
        else:
            event_data = event

        event_type = event_data.get("event_type")
        task_id = event_data.get("task_id")
        user_id = event_data.get("user_id")
        task_data = event_data.get("task_data", {})
        metadata = event_data.get("metadata", {})
        timestamp_str = event_data.get("timestamp")

        logger.info(f"📝 Received audit event: {event_type} for task {task_id}")

        # Parse timestamp
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except Exception:
            timestamp = datetime.utcnow()

        # Create audit log entry
        audit_entry = AuditLog(
            event_type=event_type,
            task_id=task_id,
            user_id=user_id,
            task_data=json.dumps(task_data),
            event_metadata=json.dumps(metadata),
            timestamp=timestamp
        )

        # Save to database
        with Session(engine) as session:
            session.add(audit_entry)
            session.commit()
            session.refresh(audit_entry)

            logger.info(f"✅ Logged audit entry {audit_entry.id} for task {task_id}")

        return {"status": "SUCCESS"}

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse event data: {e}")
        return {"status": "DROP"}

    except Exception as e:
        logger.error(f"Error handling task event: {e}")
        # Retry on database errors
        return {"status": "RETRY"}


# Audit Query API Endpoints

@api_app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "audit-service"}


@api_app.get("/api/audit/tasks/{task_id}")
def get_task_audit_trail(
    task_id: int,
    session: Session = Depends(get_session),
    limit: int = Query(100, le=1000)
):
    """
    Get complete audit trail for a specific task.

    Args:
        task_id: Task ID
        session: Database session
        limit: Maximum number of entries to return

    Returns:
        List of audit log entries for the task
    """
    try:
        statement = select(AuditLog).where(
            AuditLog.task_id == task_id
        ).order_by(
            AuditLog.timestamp.desc()
        ).limit(limit)

        results = session.exec(statement).all()

        audit_trail = [
            {
                "id": log.id,
                "event_type": log.event_type,
                "task_id": log.task_id,
                "user_id": log.user_id,
                "task_data": json.loads(log.task_data),
                "metadata": json.loads(log.event_metadata),
                "timestamp": log.timestamp.isoformat()
            }
            for log in results
        ]

        return {"task_id": task_id, "audit_trail": audit_trail, "count": len(audit_trail)}

    except Exception as e:
        logger.error(f"Error fetching audit trail for task {task_id}: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@api_app.get("/api/audit/users/{user_id}")
def get_user_audit_trail(
    user_id: str,
    session: Session = Depends(get_session),
    event_type: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get audit trail for a specific user.

    Args:
        user_id: User ID
        session: Database session
        event_type: Filter by event type (created, updated, completed, deleted)
        limit: Maximum number of entries to return
        offset: Number of entries to skip

    Returns:
        List of audit log entries for the user
    """
    try:
        statement = select(AuditLog).where(AuditLog.user_id == user_id)

        if event_type:
            statement = statement.where(AuditLog.event_type == event_type)

        statement = statement.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit)

        results = session.exec(statement).all()

        audit_trail = [
            {
                "id": log.id,
                "event_type": log.event_type,
                "task_id": log.task_id,
                "user_id": log.user_id,
                "task_data": json.loads(log.task_data),
                "metadata": json.loads(log.event_metadata),
                "timestamp": log.timestamp.isoformat()
            }
            for log in results
        ]

        return {
            "user_id": user_id,
            "event_type": event_type,
            "audit_trail": audit_trail,
            "count": len(audit_trail),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error fetching audit trail for user {user_id}: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@api_app.get("/api/audit/events")
def get_recent_events(
    session: Session = Depends(get_session),
    event_type: Optional[str] = None,
    limit: int = Query(50, le=500)
):
    """
    Get recent audit events across all users.

    Args:
        session: Database session
        event_type: Filter by event type
        limit: Maximum number of entries to return

    Returns:
        List of recent audit log entries
    """
    try:
        statement = select(AuditLog)

        if event_type:
            statement = statement.where(AuditLog.event_type == event_type)

        statement = statement.order_by(AuditLog.timestamp.desc()).limit(limit)

        results = session.exec(statement).all()

        events = [
            {
                "id": log.id,
                "event_type": log.event_type,
                "task_id": log.task_id,
                "user_id": log.user_id,
                "timestamp": log.timestamp.isoformat()
            }
            for log in results
        ]

        return {"events": events, "count": len(events)}

    except Exception as e:
        logger.error(f"Error fetching recent events: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


def main():
    """Start the Audit Service (Dapr + FastAPI)."""
    import uvicorn
    import threading

    logger.info(f"🚀 Starting Audit Service")
    logger.info(f"📡 Listening to Kafka topic: {TASK_EVENTS_TOPIC}")
    logger.info(f"🗄️  Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'configured'}")

    # Create database tables
    create_db_and_tables()

    # Start Dapr gRPC app in a separate thread
    def run_dapr_app():
        try:
            dapr_app.run(DAPR_APP_PORT)
        except Exception as e:
            logger.error(f"Dapr app error: {e}")

    dapr_thread = threading.Thread(target=run_dapr_app, daemon=True)
    dapr_thread.start()

    # Start FastAPI app for audit query API
    uvicorn.run(api_app, host="0.0.0.0", port=8001, log_level="info")


if __name__ == "__main__":
    main()
