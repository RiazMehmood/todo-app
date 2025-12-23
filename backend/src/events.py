"""
Event publishing for Kafka integration via Dapr Pub/Sub (Phase V).

This module handles publishing events to Kafka topics through Dapr's Pub/Sub API.
All task operations publish events for:
- Audit trail (task-events topic)
- Real-time sync (task-updates topic)
- Recurring task processing (recurring-tasks topic)
- Reminders (reminders topic)
"""

import httpx
import os
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Dapr configuration
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_PUBSUB_NAME = "kafka-pubsub"
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"

# Feature flag for Kafka (disable if Dapr/Kafka not available)
KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "false").lower() == "true"


async def publish_event(topic: str, event_data: Dict[str, Any]) -> bool:
    """
    Publish event to Kafka topic via Dapr Pub/Sub.

    Args:
        topic: Kafka topic name (task-events, reminders, task-updates, recurring-tasks)
        event_data: Event payload as dictionary

    Returns:
        True if published successfully, False otherwise
    """
    if not KAFKA_ENABLED:
        logger.debug(f"Kafka disabled. Skipping event publish to {topic}: {event_data}")
        return False

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            url = f"{DAPR_BASE_URL}/v1.0/publish/{DAPR_PUBSUB_NAME}/{topic}"
            response = await client.post(url, json=event_data)
            response.raise_for_status()

            logger.info(f"Published event to {topic}: {event_data.get('event_type')}")
            return True

    except httpx.TimeoutException:
        logger.error(f"Timeout publishing to {topic}")
        return False
    except httpx.HTTPError as e:
        logger.error(f"HTTP error publishing to {topic}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error publishing to {topic}: {e}")
        return False


async def publish_task_created(task_data: Dict[str, Any], user_id: str):
    """
    Publish task creation event.

    Args:
        task_data: Task data dictionary
        user_id: User ID who created the task
    """
    event = {
        "event_type": "created",
        "task_id": task_data["id"],
        "user_id": user_id,
        "task_data": task_data,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "source": "backend-api",
            "version": "1.0"
        }
    }

    await publish_event("task-events", event)


async def publish_task_updated(task_id: int, user_id: str, task_data: Dict[str, Any], changes: Dict[str, Any]):
    """
    Publish task update event.

    Args:
        task_id: Task ID
        user_id: User ID who updated the task
        task_data: Full task data after update
        changes: Dictionary of fields that changed
    """
    # Publish to task-events for audit trail
    audit_event = {
        "event_type": "updated",
        "task_id": task_id,
        "user_id": user_id,
        "task_data": task_data,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "source": "backend-api",
            "version": "1.0",
            "changes": changes
        }
    }
    await publish_event("task-events", audit_event)

    # Publish to task-updates for real-time sync
    sync_event = {
        "event_type": "task_updated",
        "task_id": task_id,
        "user_id": user_id,
        "changes": changes,
        "timestamp": datetime.utcnow().isoformat()
    }
    await publish_event("task-updates", sync_event)


async def publish_task_completed(task_id: int, user_id: str, task_data: Dict[str, Any], is_recurring: bool):
    """
    Publish task completion event.

    Args:
        task_id: Task ID
        user_id: User ID who completed the task
        task_data: Full task data
        is_recurring: Whether this is a recurring task
    """
    event = {
        "event_type": "completed",
        "task_id": task_id,
        "user_id": user_id,
        "task_data": task_data,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "source": "backend-api",
            "version": "1.0",
            "is_recurring": is_recurring
        }
    }

    await publish_event("task-events", event)


async def publish_task_deleted(task_id: int, user_id: str, task_data: Dict[str, Any]):
    """
    Publish task deletion event.

    Args:
        task_id: Task ID
        user_id: User ID who deleted the task
        task_data: Task data before deletion
    """
    event = {
        "event_type": "deleted",
        "task_id": task_id,
        "user_id": user_id,
        "task_data": task_data,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "source": "backend-api",
            "version": "1.0"
        }
    }

    await publish_event("task-events", event)


async def publish_recurring_task_completed(
    task_id: int,
    parent_task_id: Optional[int],
    user_id: str,
    recurrence_pattern: str,
    recurrence_interval: int,
    recurrence_days: Optional[list],
    next_occurrence: str,
    recurrence_end_date: Optional[str],
    task_data: Dict[str, Any]
):
    """
    Publish recurring task completion event for processing by Recurring Task Service.

    Args:
        task_id: Completed task ID
        parent_task_id: Parent recurring task ID (or None if this is the parent)
        user_id: User ID
        recurrence_pattern: daily/weekly/monthly
        recurrence_interval: Every N days/weeks/months
        recurrence_days: Days of week for weekly pattern
        next_occurrence: ISO timestamp for next occurrence
        recurrence_end_date: ISO timestamp for recurrence end (or None)
        task_data: Full task data
    """
    event = {
        "event_type": "recurring_task_completed",
        "task_id": task_id,
        "parent_task_id": parent_task_id if parent_task_id else task_id,
        "user_id": user_id,
        "recurrence_pattern": recurrence_pattern,
        "recurrence_interval": recurrence_interval,
        "recurrence_days": recurrence_days,
        "next_occurrence": next_occurrence,
        "recurrence_end_date": recurrence_end_date,
        "task_data": task_data,
        "timestamp": datetime.utcnow().isoformat()
    }

    await publish_event("recurring-tasks", event)


async def publish_reminder(
    task_id: int,
    user_id: str,
    title: str,
    description: Optional[str],
    due_date: str,
    remind_before_minutes: int,
    priority: str,
    tags: Optional[list]
):
    """
    Publish reminder event for notification service.

    Args:
        task_id: Task ID
        user_id: User ID
        title: Task title
        description: Task description
        due_date: ISO timestamp of due date
        remind_before_minutes: Minutes before due date to remind
        priority: Task priority (high/medium/low)
        tags: Task tags
    """
    event = {
        "event_type": "reminder_due",
        "task_id": task_id,
        "user_id": user_id,
        "title": title,
        "description": description,
        "due_date": due_date,
        "remind_before_minutes": remind_before_minutes,
        "priority": priority,
        "tags": tags,
        "timestamp": datetime.utcnow().isoformat()
    }

    await publish_event("reminders", event)


def sync_publish_event(topic: str, event_data: Dict[str, Any]) -> bool:
    """
    Synchronous wrapper for publish_event (for non-async contexts).

    Args:
        topic: Kafka topic name
        event_data: Event payload

    Returns:
        True if published successfully, False otherwise
    """
    if not KAFKA_ENABLED:
        logger.debug(f"Kafka disabled. Skipping event publish to {topic}")
        return False

    try:
        with httpx.Client(timeout=5.0) as client:
            url = f"{DAPR_BASE_URL}/v1.0/publish/{DAPR_PUBSUB_NAME}/{topic}"
            response = client.post(url, json=event_data)
            response.raise_for_status()

            logger.info(f"Published event to {topic}: {event_data.get('event_type')}")
            return True

    except Exception as e:
        logger.error(f"Error publishing to {topic}: {e}")
        return False
