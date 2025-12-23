"""
Utility functions for Phase V features.

This module contains helper functions for:
- Recurring task calculations
- JSON serialization for tags
- Query building for filters and search
"""

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
    """
    Calculate the next occurrence for a recurring task.

    Args:
        pattern: "daily", "weekly", or "monthly"
        interval: Every N days/weeks/months
        recurrence_days: Days of week for weekly pattern (e.g., ["monday", "friday"])
        current_date: Current date/time

    Returns:
        Next occurrence datetime
    """
    if pattern == "daily":
        return current_date + timedelta(days=interval)

    elif pattern == "weekly":
        if not recurrence_days:
            # Default to same day of week
            return current_date + timedelta(weeks=interval)

        # Map day names to weekday numbers (0=Monday, 6=Sunday)
        day_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }

        # Get target weekday numbers
        target_weekdays = sorted([day_map[day.lower()] for day in recurrence_days])

        # Find next occurrence
        current_weekday = current_date.weekday()
        days_ahead = 0

        # Find next matching day this week
        for target_day in target_weekdays:
            if target_day > current_weekday:
                days_ahead = target_day - current_weekday
                break

        # If no day found this week, go to first day next interval week
        if days_ahead == 0:
            days_ahead = (7 - current_weekday) + target_weekdays[0] + (7 * (interval - 1))

        return current_date + timedelta(days=days_ahead)

    elif pattern == "monthly":
        # Same day of month, N months later
        year = current_date.year
        month = current_date.month + interval
        day = current_date.day

        # Handle month overflow
        while month > 12:
            month -= 12
            year += 1

        # Handle day overflow (e.g., Jan 31 -> Feb 28/29)
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
    """
    Convert Task SQLModel to dict with proper JSON deserialization.

    Args:
        task: Task SQLModel instance

    Returns:
        Dictionary with deserialized tags and recurrence_days
    """
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


def get_priority_sort_value(priority: str) -> int:
    """Convert priority string to numeric value for sorting"""
    priority_map = {
        "high": 3,
        "medium": 2,
        "low": 1
    }
    return priority_map.get(priority.lower(), 0)
