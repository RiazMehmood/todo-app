"""
Analytics API Routes - RESTful endpoints for analytics, reporting, and time tracking.

Implements endpoints from: specs/005-cloud-native-deployment/contracts/analytics-api.yaml

Endpoints:
- GET /api/{user_id}/analytics/overview - Analytics dashboard overview
- GET /api/{user_id}/analytics/export - Export data (CSV/PDF)
- GET /api/{user_id}/time-entries - List time entries
- POST /api/{user_id}/time-entries - Create time entry (start timer)
- PATCH /api/{user_id}/time-entries/{entry_id} - Update time entry (stop timer)
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from datetime import date, datetime
from pydantic import BaseModel, Field
from io import BytesIO
import logging

try:
    from ..services.analytics_service import AnalyticsService, TimeTrackingService
    from ..services.export_service import ExportService
    from ..models.time_entry import TimeEntry, TimeEntryCreate, TimeEntryUpdate
except ImportError:
    from ..services.analytics_service import AnalyticsService, TimeTrackingService
    from ..services.export_service import ExportService
    from ..models.time_entry import TimeEntry, TimeEntryCreate, TimeEntryUpdate

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["analytics"])

# Service instances
analytics_service = AnalyticsService()
time_tracking_service = TimeTrackingService()
export_service = ExportService()


# ============================================================================
# Request/Response Schemas (from contract)
# ============================================================================

class DateRange(BaseModel):
    """Date range schema."""
    start: str = Field(description="Start date (ISO format)")
    end: str = Field(description="End date (ISO format)")


class MetricsData(BaseModel):
    """Metrics data schema from contract."""
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    average_completion_time_hours: float
    total_time_spent_hours: float


class TasksByPriority(BaseModel):
    """Task distribution by priority."""
    high: int
    medium: int
    low: int


class TasksByStatus(BaseModel):
    """Task distribution by status."""
    completed: int
    in_progress: int
    pending: int


class TaskByTag(BaseModel):
    """Tag count entry."""
    tag: str
    count: int


class CompletionTrendEntry(BaseModel):
    """Completion trend data point."""
    date: str
    completed: int


class AnalyticsOverviewResponse(BaseModel):
    """Analytics overview response schema from contract."""
    date_range: DateRange
    metrics: MetricsData
    tasks_by_priority: TasksByPriority
    tasks_by_status: TasksByStatus
    tasks_by_tag: list[TaskByTag]
    completion_trend: list[CompletionTrendEntry]


class TimeEntriesResponse(BaseModel):
    """Time entries list response schema from contract."""
    time_entries: list[TimeEntry]
    total_time_seconds: int


# ============================================================================
# Analytics Endpoints
# ============================================================================

@router.get(
    "/{user_id}/analytics/overview",
    response_model=AnalyticsOverviewResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Invalid date range"},
        401: {"description": "Unauthorized"},
    },
    summary="Get analytics dashboard overview",
    description="Returns comprehensive metrics and data for analytics dashboard"
)
def get_analytics_overview(
    user_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    session: Session = Depends(lambda: None)  # TODO: Add get_session dependency
):
    """
    Get analytics overview for dashboard.

    Implements: GET /api/{user_id}/analytics/overview from analytics-api.yaml

    Args:
        user_id: User ID from path parameter
        start_date: Start date filter (default: 30 days ago)
        end_date: End date filter (default: today)
        session: Database session (injected)

    Returns:
        AnalyticsOverviewResponse with all analytics data

    Raises:
        HTTPException 400: Invalid date range
        HTTPException 401: User not authenticated
    """
    # TODO: Add authentication check

    try:
        # Parse dates
        start_date_obj = date.fromisoformat(start_date) if start_date else None
        end_date_obj = date.fromisoformat(end_date) if end_date else None

        # Get analytics overview
        overview = analytics_service.get_analytics_overview(
            session=session,
            user_id=user_id,
            start_date=start_date_obj,
            end_date=end_date_obj
        )

        return overview

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating analytics overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate analytics overview"
        )


@router.get(
    "/{user_id}/analytics/export",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Invalid parameters"},
        401: {"description": "Unauthorized"},
    },
    summary="Export analytics data",
    description="Export tasks and analytics data to CSV or PDF format"
)
def export_analytics(
    user_id: str,
    format: str = Query(..., description="Export format (csv or pdf)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    session: Session = Depends(lambda: None)  # TODO: Add get_session dependency
):
    """
    Export analytics data to CSV or PDF.

    Implements: GET /api/{user_id}/analytics/export from analytics-api.yaml

    Args:
        user_id: User ID from path parameter
        format: Export format ('csv' or 'pdf')
        start_date: Start date filter (optional)
        end_date: End date filter (optional)
        session: Database session (injected)

    Returns:
        StreamingResponse with CSV or PDF file

    Raises:
        HTTPException 400: Invalid format or date range
        HTTPException 401: User not authenticated
    """
    # TODO: Add authentication check

    # Validate format
    if format not in ['csv', 'pdf']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'csv' or 'pdf'"
        )

    try:
        # Parse dates
        start_date_obj = date.fromisoformat(start_date) if start_date else None
        end_date_obj = date.fromisoformat(end_date) if end_date else None

        # Generate export
        if format == 'csv':
            content = export_service.generate_csv_export(
                session=session,
                user_id=user_id,
                start_date=start_date_obj,
                end_date=end_date_obj
            )

            # Generate filename
            filename = export_service.get_export_filename('csv', end_date)

            return Response(
                content=content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )

        else:  # PDF
            content = export_service.generate_pdf_export(
                session=session,
                user_id=user_id,
                start_date=start_date_obj,
                end_date=end_date_obj
            )

            # Generate filename
            filename = export_service.get_export_filename('pdf', end_date)

            return Response(
                content=content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameters: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating export: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate export"
        )


# ============================================================================
# Time Tracking Endpoints
# ============================================================================

@router.get(
    "/{user_id}/time-entries",
    response_model=TimeEntriesResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Unauthorized"},
    },
    summary="List time entries",
    description="Get time entries for tasks, optionally filtered by task_id"
)
def list_time_entries(
    user_id: str,
    task_id: Optional[str] = Query(None, description="Filter by task ID"),
    start_date: Optional[str] = Query(None, description="Filter by start date"),
    end_date: Optional[str] = Query(None, description="Filter by end date"),
    session: Session = Depends(lambda: None)  # TODO: Add get_session dependency
):
    """
    List time entries with optional filtering.

    Implements: GET /api/{user_id}/time-entries from analytics-api.yaml

    Args:
        user_id: User ID from path parameter
        task_id: Optional task ID filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        session: Database session (injected)

    Returns:
        TimeEntriesResponse with time entries and total time

    Raises:
        HTTPException 401: User not authenticated
    """
    # TODO: Add authentication check

    try:
        # Parse dates
        start_date_obj = date.fromisoformat(start_date) if start_date else None
        end_date_obj = date.fromisoformat(end_date) if end_date else None

        # Get time entries
        entries, total_seconds = time_tracking_service.get_time_entries(
            session=session,
            user_id=user_id,
            task_id=task_id,
            start_date=start_date_obj,
            end_date=end_date_obj
        )

        return TimeEntriesResponse(
            time_entries=entries,
            total_time_seconds=total_seconds
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameters: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error listing time entries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list time entries"
        )


@router.post(
    "/{user_id}/time-entries",
    response_model=TimeEntry,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Invalid request (ended_at before started_at, task not found)"},
        401: {"description": "Unauthorized"},
    },
    summary="Create time entry (start/stop timer)",
    description="Record time spent on a task"
)
def create_time_entry(
    user_id: str,
    entry_data: TimeEntryCreate,
    session: Session = Depends(lambda: None)  # TODO: Add get_session dependency
):
    """
    Create a new time entry (start timer).

    Implements: POST /api/{user_id}/time-entries from analytics-api.yaml

    Args:
        user_id: User ID from path parameter
        entry_data: Time entry creation data
        session: Database session (injected)

    Returns:
        Created TimeEntry

    Raises:
        HTTPException 400: Invalid request
        HTTPException 401: User not authenticated
    """
    # TODO: Add authentication check

    try:
        # Start timer
        time_entry = time_tracking_service.start_timer(
            session=session,
            user_id=user_id,
            task_id=str(entry_data.task_id),
            started_at=entry_data.started_at,
            description=entry_data.description
        )

        # If ended_at is provided, stop timer immediately
        if entry_data.ended_at:
            time_entry = time_tracking_service.stop_timer(
                session=session,
                user_id=user_id,
                entry_id=str(time_entry.id),
                ended_at=entry_data.ended_at
            )

        return time_entry

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating time entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create time entry"
        )


@router.patch(
    "/{user_id}/time-entries/{entry_id}",
    response_model=TimeEntry,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Invalid request"},
        401: {"description": "Unauthorized"},
        404: {"description": "Time entry not found"},
    },
    summary="Update time entry (stop timer)",
    description="Update an existing time entry, typically to set ended_at when stopping timer"
)
def update_time_entry(
    user_id: str,
    entry_id: str,
    entry_data: TimeEntryUpdate,
    session: Session = Depends(lambda: None)  # TODO: Add get_session dependency
):
    """
    Update a time entry (stop timer).

    Implements: PATCH /api/{user_id}/time-entries/{entry_id} from analytics-api.yaml

    Args:
        user_id: User ID from path parameter
        entry_id: Time entry ID from path parameter
        entry_data: Time entry update data
        session: Database session (injected)

    Returns:
        Updated TimeEntry

    Raises:
        HTTPException 400: Invalid request
        HTTPException 401: User not authenticated
        HTTPException 404: Time entry not found
    """
    # TODO: Add authentication check

    try:
        # Stop timer if ended_at provided
        if entry_data.ended_at:
            time_entry = time_tracking_service.stop_timer(
                session=session,
                user_id=user_id,
                entry_id=entry_id,
                ended_at=entry_data.ended_at
            )
        else:
            # Just update description
            time_entry = session.get(TimeEntry, entry_id)
            if not time_entry or time_entry.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Time entry not found"
                )

            if entry_data.description is not None:
                time_entry.description = entry_data.description
                session.add(time_entry)
                session.commit()
                session.refresh(time_entry)

        return time_entry

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating time entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update time entry"
        )
