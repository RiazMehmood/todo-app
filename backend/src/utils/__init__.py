"""Utility modules for the backend."""

from .rate_limiter import RateLimiter, chat_rate_limiter, api_rate_limiter

# Phase V utility functions
from datetime import datetime, timedelta
from typing import Optional, List
import json
import calendar


def calculate_next_occurrence(
    pattern: str,
    interval: int,
    recurrence_days: Optional[List[str]],
    current_date: datetime
) -> datetime:
    """Calculate the next occurrence for a recurring task."""
    if pattern == "daily":
        return current_date + timedelta(days=interval)

    elif pattern == "weekly":
        if not recurrence_days:
            return current_date + timedelta(weeks=interval)

        day_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }

        target_weekdays = sorted([day_map[day.lower()] for day in recurrence_days])
        current_weekday = current_date.weekday()
        days_ahead = 0

        for target_day in target_weekdays:
            if target_day > current_weekday:
                days_ahead = target_day - current_weekday
                break

        if days_ahead == 0:
            days_ahead = (7 - current_weekday) + target_weekdays[0] + (7 * (interval - 1))

        return current_date + timedelta(days=days_ahead)

    elif pattern == "monthly":
        year = current_date.year
        month = current_date.month + interval
        day = current_date.day

        while month > 12:
            month -= 12
            year += 1

        max_day = calendar.monthrange(year, month)[1]
        if day > max_day:
            day = max_day

        return current_date.replace(year=year, month=month, day=day)

    else:
        raise ValueError(f"Invalid recurrence pattern: {pattern}")


def serialize_tags(tags: Optional[List[str]]) -> Optional[str]:
    """Convert list of tags to JSON string"""
    if not tags:
        return None
    return json.dumps(tags)


def deserialize_tags(tags_json: Optional[str]) -> Optional[List[str]]:
    """Convert JSON string to list of tags"""
    if not tags_json:
        return None
    try:
        return json.loads(tags_json)
    except json.JSONDecodeError:
        return None


def serialize_recurrence_days(days: Optional[List[str]]) -> Optional[str]:
    """Convert list of days to JSON string"""
    if not days:
        return None
    return json.dumps([day.lower() for day in days])


def deserialize_recurrence_days(days_json: Optional[str]) -> Optional[List[str]]:
    """Convert JSON string to list of days"""
    if not days_json:
        return None
    try:
        return json.loads(days_json)
    except json.JSONDecodeError:
        return None


def build_task_dict_response(task) -> dict:
    """Convert Task SQLModel to dict with proper JSON deserialization."""
    task_dict = {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "priority": task.priority,
        "tags": deserialize_tags(task.tags),
        "due_date": task.due_date,
        "remind_before_minutes": task.remind_before_minutes,
        "reminder_sent": task.reminder_sent,
        "is_recurring": task.is_recurring,
        "recurrence_pattern": task.recurrence_pattern,
        "recurrence_interval": task.recurrence_interval,
        "recurrence_days": deserialize_recurrence_days(task.recurrence_days),
        "recurrence_end_date": task.recurrence_end_date,
        "parent_task_id": task.parent_task_id,
        "created_via_ai": task.created_via_ai,
        "ai_suggested_priority": task.ai_suggested_priority,
        "original_nl_input": task.original_nl_input,
        "created_at": task.created_at,
        "updated_at": task.updated_at
    }
    return task_dict


__all__ = [
    "RateLimiter",
    "chat_rate_limiter",
    "api_rate_limiter",
    "serialize_tags",
    "deserialize_tags",
    "serialize_recurrence_days",
    "deserialize_recurrence_days",
    "calculate_next_occurrence",
    "build_task_dict_response"
]
