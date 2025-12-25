"""
Analytics Service - Business logic for analytics, metrics, and time tracking.

Implements:
- FR-028: Analytics dashboard with completion trends
- FR-029: Task distribution charts (priority, status, tags)
- FR-030: Time tracking with start/stop timer
- FR-031: Metrics calculation (total tasks, completion rate, avg time)
- FR-037: Analytics queries completing within 2 seconds (NFR)
- FR-038: Time tracking persistence across page refreshes
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlmodel import Session, select, func, and_, or_
from datetime import datetime, date, timedelta
from collections import Counter
import logging

try:
    from ..models import Task
    from ..models.time_entry import TimeEntry
except ImportError:
    from ..models import Task
    from ..models.time_entry import TimeEntry

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for analytics calculations, metrics, and time tracking.

    Provides comprehensive analytics data for dashboards, reports, and insights.
    """

    @staticmethod
    def calculate_metrics(
        session: Session,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive analytics metrics for date range.

        Implements: FR-031 (calculate metrics)

        Args:
            session: Database session
            user_id: User ID
            start_date: Start date (default: 30 days ago)
            end_date: End date (default: today)

        Returns:
            Dictionary with metrics:
                - total_tasks: int
                - completed_tasks: int
                - completion_rate: float (0-100)
                - average_completion_time_hours: float
                - total_time_spent_hours: float

        Raises:
            ValueError: If date range is invalid
        """
        # Default date range: last 30 days
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Validate date range
        if start_date > end_date:
            raise ValueError("start_date must be before or equal to end_date")

        # Convert dates to datetime for comparison
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        # Total tasks in date range
        total_tasks_stmt = select(func.count(Task.id)).where(
            and_(
                Task.user_id == user_id,
                Task.created_at >= start_datetime,
                Task.created_at <= end_datetime
            )
        )
        total_tasks = session.exec(total_tasks_stmt).one()

        # Completed tasks
        completed_tasks_stmt = select(func.count(Task.id)).where(
            and_(
                Task.user_id == user_id,
                Task.status == "completed",
                Task.created_at >= start_datetime,
                Task.created_at <= end_datetime
            )
        )
        completed_tasks = session.exec(completed_tasks_stmt).one()

        # Completion rate
        completion_rate = (completed_tasks / total_tasks * 100.0) if total_tasks > 0 else 0.0

        # Average completion time (created_at to updated_at for completed tasks)
        completed_tasks_query = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.status == "completed",
                Task.created_at >= start_datetime,
                Task.created_at <= end_datetime
            )
        )
        completed_task_list = session.exec(completed_tasks_query).all()

        total_completion_hours = 0.0
        completion_count = 0
        for task in completed_task_list:
            if task.updated_at and task.created_at:
                delta = task.updated_at - task.created_at
                total_completion_hours += delta.total_seconds() / 3600
                completion_count += 1

        average_completion_time_hours = (
            total_completion_hours / completion_count if completion_count > 0 else 0.0
        )

        # Total time spent (from time entries)
        time_entries_stmt = select(func.sum(TimeEntry.elapsed_seconds)).where(
            and_(
                TimeEntry.user_id == user_id,
                TimeEntry.started_at >= start_datetime,
                TimeEntry.started_at <= end_datetime,
                TimeEntry.elapsed_seconds.is_not(None)
            )
        )
        total_seconds = session.exec(time_entries_stmt).one() or 0
        total_time_spent_hours = total_seconds / 3600.0

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round(completion_rate, 2),
            "average_completion_time_hours": round(average_completion_time_hours, 2),
            "total_time_spent_hours": round(total_time_spent_hours, 2)
        }

    @staticmethod
    def get_completion_trend(
        session: Session,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get daily completion trend data.

        Implements: FR-028 (completion trends), FR-073 (trend method)

        Args:
            session: Database session
            user_id: User ID
            start_date: Start date (default: 30 days ago)
            end_date: End date (default: today)

        Returns:
            List of dicts with 'date' and 'completed' count

        Raises:
            ValueError: If date range is invalid
        """
        # Default date range
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        if start_date > end_date:
            raise ValueError("start_date must be before or equal to end_date")

        # Get all completed tasks in range
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        completed_tasks_query = select(Task.updated_at).where(
            and_(
                Task.user_id == user_id,
                Task.status == "completed",
                Task.updated_at >= start_datetime,
                Task.updated_at <= end_datetime
            )
        )
        completed_tasks = session.exec(completed_tasks_query).all()

        # Count by date
        completion_by_date = Counter()
        for task_updated_at in completed_tasks:
            if task_updated_at:
                completion_date = task_updated_at.date()
                completion_by_date[completion_date] += 1

        # Build result with all dates in range
        result = []
        current_date = start_date
        while current_date <= end_date:
            result.append({
                "date": current_date.isoformat(),
                "completed": completion_by_date.get(current_date, 0)
            })
            current_date += timedelta(days=1)

        return result

    @staticmethod
    def get_tasks_by_priority(
        session: Session,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, int]:
        """
        Get task count distribution by priority level.

        Implements: FR-029 (task distribution), FR-074 (priority aggregation)

        Args:
            session: Database session
            user_id: User ID
            start_date: Start date filter (optional)
            end_date: End date filter (optional)

        Returns:
            Dict with priority counts: {"high": 10, "medium": 20, "low": 15}
        """
        # Build query
        query = select(Task.priority, func.count(Task.id)).where(
            Task.user_id == user_id
        )

        # Apply date filter if provided
        if start_date and end_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.where(
                and_(
                    Task.created_at >= start_datetime,
                    Task.created_at <= end_datetime
                )
            )

        query = query.group_by(Task.priority)

        results = session.exec(query).all()

        # Convert to dict with default values
        priority_counts = {"high": 0, "medium": 0, "low": 0}
        for priority, count in results:
            if priority in priority_counts:
                priority_counts[priority] = count

        return priority_counts

    @staticmethod
    def get_tasks_by_status(
        session: Session,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, int]:
        """
        Get task count distribution by status.

        Implements: FR-029 (task distribution), FR-074 (status aggregation)

        Args:
            session: Database session
            user_id: User ID
            start_date: Start date filter (optional)
            end_date: End date filter (optional)

        Returns:
            Dict with status counts: {"completed": 50, "in_progress": 10, "pending": 5}
        """
        query = select(Task.status, func.count(Task.id)).where(
            Task.user_id == user_id
        )

        if start_date and end_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.where(
                and_(
                    Task.created_at >= start_datetime,
                    Task.created_at <= end_datetime
                )
            )

        query = query.group_by(Task.status)

        results = session.exec(query).all()

        # Convert to dict with default values
        status_counts = {"completed": 0, "in_progress": 0, "pending": 0}
        for status, count in results:
            if status in status_counts:
                status_counts[status] = count

        return status_counts

    @staticmethod
    def get_tasks_by_tag(
        session: Session,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get task count distribution by tag.

        Implements: FR-029 (task distribution), FR-074 (tag aggregation)

        Args:
            session: Database session
            user_id: User ID
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            limit: Maximum number of tags to return (default: 10)

        Returns:
            List of dicts: [{"tag": "work", "count": 80}, ...]
            Sorted by count descending
        """
        # Get all tasks in range
        query = select(Task.tags).where(Task.user_id == user_id)

        if start_date and end_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.where(
                and_(
                    Task.created_at >= start_datetime,
                    Task.created_at <= end_datetime
                )
            )

        tasks = session.exec(query).all()

        # Count tags
        tag_counter = Counter()
        for tags_list in tasks:
            if tags_list:
                for tag in tags_list:
                    tag_counter[tag] += 1

        # Convert to list of dicts, sorted by count
        result = [
            {"tag": tag, "count": count}
            for tag, count in tag_counter.most_common(limit)
        ]

        return result

    @staticmethod
    def get_analytics_overview(
        session: Session,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get complete analytics overview for dashboard.

        Implements: Complete analytics overview (FR-028, FR-029, FR-031)

        Args:
            session: Database session
            user_id: User ID
            start_date: Start date (default: 30 days ago)
            end_date: End date (default: today)

        Returns:
            Complete analytics overview dict matching API schema
        """
        # Default dates
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Gather all analytics data
        metrics = AnalyticsService.calculate_metrics(
            session, user_id, start_date, end_date
        )

        tasks_by_priority = AnalyticsService.get_tasks_by_priority(
            session, user_id, start_date, end_date
        )

        tasks_by_status = AnalyticsService.get_tasks_by_status(
            session, user_id, start_date, end_date
        )

        tasks_by_tag = AnalyticsService.get_tasks_by_tag(
            session, user_id, start_date, end_date
        )

        completion_trend = AnalyticsService.get_completion_trend(
            session, user_id, start_date, end_date
        )

        return {
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "metrics": metrics,
            "tasks_by_priority": tasks_by_priority,
            "tasks_by_status": tasks_by_status,
            "tasks_by_tag": tasks_by_tag,
            "completion_trend": completion_trend
        }


class TimeTrackingService:
    """
    Service for time tracking operations.

    Handles timer start/stop, time entry CRUD, and time aggregation.
    """

    @staticmethod
    def start_timer(
        session: Session,
        user_id: str,
        task_id: str,
        started_at: Optional[datetime] = None,
        description: Optional[str] = None
    ) -> TimeEntry:
        """
        Start a new timer for a task.

        Implements: FR-030 (start timer), FR-075 (start_timer method)

        Args:
            session: Database session
            user_id: User ID
            task_id: Task ID
            started_at: Start time (default: now)
            description: Optional work description

        Returns:
            Created TimeEntry with timer running (ended_at = None)

        Raises:
            ValueError: If task doesn't exist or doesn't belong to user
        """
        # Verify task exists and belongs to user
        task = session.get(Task, task_id)
        if not task or task.user_id != user_id:
            raise ValueError("Task not found or does not belong to user")

        # Create time entry
        if not started_at:
            started_at = datetime.utcnow()

        time_entry = TimeEntry(
            task_id=task_id,
            user_id=user_id,
            started_at=started_at,
            description=description
        )

        session.add(time_entry)
        session.commit()
        session.refresh(time_entry)

        logger.info(f"Timer started: user={user_id}, task={task_id}, entry={time_entry.id}")

        return time_entry

    @staticmethod
    def stop_timer(
        session: Session,
        user_id: str,
        entry_id: str,
        ended_at: Optional[datetime] = None
    ) -> TimeEntry:
        """
        Stop a running timer.

        Implements: FR-030 (stop timer), FR-075 (stop_timer method)

        Args:
            session: Database session
            user_id: User ID
            entry_id: TimeEntry ID
            ended_at: End time (default: now)

        Returns:
            Updated TimeEntry with calculated elapsed_seconds

        Raises:
            ValueError: If entry doesn't exist, doesn't belong to user, or already stopped
        """
        # Get time entry
        time_entry = session.get(TimeEntry, entry_id)

        if not time_entry or time_entry.user_id != user_id:
            raise ValueError("Time entry not found or does not belong to user")

        if time_entry.ended_at:
            raise ValueError("Timer already stopped")

        # Stop timer
        if not ended_at:
            ended_at = datetime.utcnow()

        if ended_at <= time_entry.started_at:
            raise ValueError("ended_at must be after started_at")

        time_entry.ended_at = ended_at
        time_entry.elapsed_seconds = time_entry.calculate_elapsed()

        session.add(time_entry)
        session.commit()
        session.refresh(time_entry)

        logger.info(f"Timer stopped: entry={entry_id}, elapsed={time_entry.elapsed_seconds}s")

        return time_entry

    @staticmethod
    def get_time_entries(
        session: Session,
        user_id: str,
        task_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Tuple[List[TimeEntry], int]:
        """
        Get time entries with optional filtering.

        Implements: FR-075 (get_time_entries method)

        Args:
            session: Database session
            user_id: User ID
            task_id: Filter by task ID (optional)
            start_date: Filter entries started after this date (optional)
            end_date: Filter entries started before this date (optional)

        Returns:
            Tuple of (time_entries list, total_time_seconds)
        """
        # Build query
        query = select(TimeEntry).where(TimeEntry.user_id == user_id)

        if task_id:
            query = query.where(TimeEntry.task_id == task_id)

        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            query = query.where(TimeEntry.started_at >= start_datetime)

        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.where(TimeEntry.started_at <= end_datetime)

        # Get entries
        entries = session.exec(query).all()

        # Calculate total time
        total_seconds = sum(
            entry.elapsed_seconds for entry in entries
            if entry.elapsed_seconds is not None
        )

        return list(entries), total_seconds
