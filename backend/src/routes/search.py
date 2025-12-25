"""
Search API Routes

Provides endpoints for:
- Advanced task search with full-text search and filters
- Saved search CRUD operations
- Search suggestions/autocomplete
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from ..db import get_session
from ..middleware.auth import verify_jwt
from ..models import Task
from ..models.saved_search import (
    SavedSearch,
    SavedSearchCreate,
    SavedSearchUpdate,
    SavedSearchResponse
)
from ..services.search_service import SearchService

router = APIRouter(dependencies=[Depends(verify_jwt)])


# === Task Search Endpoint ===

@router.post("/{user_id}/tasks/search")
def search_tasks(
    user_id: str,
    request: Request,
    session: Session = Depends(get_session),
    query: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    sort_by: str = Query("relevance", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=1000, description="Results per page")
):
    """
    **Advanced Task Search**

    Performs full-text search across task titles and descriptions with optional filters.

    **Features:**
    - Full-text search with boolean operators (AND, OR, NOT)
    - Multi-criteria filtering (status, priority, tags, dates)
    - Relevance ranking with ts_rank()
    - Pagination support

    **Search Query Syntax:**
    - Implicit AND: `urgent meeting` → finds tasks with both words
    - Explicit AND: `urgent AND meeting`
    - OR operator: `project OR task`
    - NOT operator: `urgent NOT spam`
    - Phrase search: Use implicit AND for now

    **Filters:**
    - `status`: Array of statuses ['pending', 'in_progress', 'completed']
    - `priority`: Array of priorities ['low', 'medium', 'high']
    - `tags`: Array of tags (any match)
    - `created_after`: ISO datetime string
    - `created_before`: ISO datetime string
    - `due_after`: ISO datetime string
    - `due_before`: ISO datetime string
    - `date_filter`: Predefined ranges ('last_7_days', 'last_30_days', 'last_90_days', 'custom_range')

    **Sort Options:**
    - `relevance`: Sort by search relevance (default when query provided)
    - `created_at`: Sort by creation date
    - `updated_at`: Sort by last update
    - `due_date`: Sort by due date
    - `priority`: Sort by priority level

    **Returns:**
    - `tasks`: Array of matching tasks
    - `total`: Total number of matches (for pagination)
    - `page`: Current page number
    - `per_page`: Results per page
    - `total_pages`: Total pages available
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot search other user's tasks"
        )

    # Perform search
    try:
        tasks, total_count = SearchService.search_tasks(
            session=session,
            user_id=user_id,
            query=query,
            filters=filters or {},
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page
        )

        # Calculate pagination metadata
        total_pages = (total_count + per_page - 1) // per_page  # Ceiling division

        return {
            "tasks": tasks,
            "total": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


# === Saved Searches Endpoints ===

@router.get("/{user_id}/saved-searches", response_model=List[SavedSearchResponse])
def get_saved_searches(
    user_id: str,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    **Get All Saved Searches**

    Retrieves all saved searches for the authenticated user.

    **Returns:**
    List of saved searches with query parameters and metadata.
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot access other user's saved searches"
        )

    # Query saved searches
    statement = select(SavedSearch).where(
        SavedSearch.user_id == user_id
    ).order_by(SavedSearch.created_at.desc())

    saved_searches = session.exec(statement).all()

    return saved_searches


@router.get("/{user_id}/saved-searches/{search_id}", response_model=SavedSearchResponse)
def get_saved_search(
    user_id: str,
    search_id: UUID,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    **Get Saved Search by ID**

    Retrieves a specific saved search.

    **Returns:**
    Saved search details with query parameters.
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot access other user's saved searches"
        )

    # Query saved search
    saved_search = session.get(SavedSearch, search_id)

    if not saved_search or saved_search.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Saved search not found"
        )

    return saved_search


@router.post("/{user_id}/saved-searches", response_model=SavedSearchResponse, status_code=201)
def create_saved_search(
    user_id: str,
    search_data: SavedSearchCreate,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    **Create Saved Search**

    Saves a search query for quick access.

    **Request Body:**
    - `name`: User-friendly name (1-100 chars, unique per user)
    - `query_params`: Dict with query, filters, sorting preferences

    **Example:**
    ```json
    {
      "name": "High Priority Work Tasks",
      "query_params": {
        "query": "urgent meeting",
        "filters": {
          "status": ["pending", "in_progress"],
          "priority": ["high"],
          "tags": ["work"]
        },
        "sort_by": "due_date",
        "sort_order": "asc"
      }
    }
    ```

    **Returns:**
    Created saved search with generated ID.
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot create saved search for other user"
        )

    # Check for duplicate name
    existing = session.exec(
        select(SavedSearch).where(
            SavedSearch.user_id == user_id,
            SavedSearch.name == search_data.name
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Saved search with name '{search_data.name}' already exists"
        )

    # Create saved search
    saved_search = SavedSearch(
        user_id=user_id,
        name=search_data.name,
        query_params=search_data.query_params
    )

    session.add(saved_search)
    session.commit()
    session.refresh(saved_search)

    return saved_search


@router.put("/{user_id}/saved-searches/{search_id}", response_model=SavedSearchResponse)
def update_saved_search(
    user_id: str,
    search_id: UUID,
    search_data: SavedSearchUpdate,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    **Update Saved Search**

    Updates name or query parameters of a saved search.

    **Request Body:**
    - `name`: New name (optional)
    - `query_params`: New query parameters (optional)

    **Returns:**
    Updated saved search.
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot update other user's saved searches"
        )

    # Get saved search
    saved_search = session.get(SavedSearch, search_id)

    if not saved_search or saved_search.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Saved search not found"
        )

    # Update fields
    if search_data.name is not None:
        # Check for duplicate name (excluding current search)
        existing = session.exec(
            select(SavedSearch).where(
                SavedSearch.user_id == user_id,
                SavedSearch.name == search_data.name,
                SavedSearch.id != search_id
            )
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Saved search with name '{search_data.name}' already exists"
            )

        saved_search.name = search_data.name

    if search_data.query_params is not None:
        saved_search.query_params = search_data.query_params

    # Update timestamp
    saved_search.updated_at = datetime.utcnow()

    session.add(saved_search)
    session.commit()
    session.refresh(saved_search)

    return saved_search


@router.delete("/{user_id}/saved-searches/{search_id}")
def delete_saved_search(
    user_id: str,
    search_id: UUID,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    **Delete Saved Search**

    Permanently deletes a saved search.

    **Returns:**
    Success message with deleted search ID.
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot delete other user's saved searches"
        )

    # Get saved search
    saved_search = session.get(SavedSearch, search_id)

    if not saved_search or saved_search.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Saved search not found"
        )

    # Delete
    session.delete(saved_search)
    session.commit()

    return {
        "message": "Saved search deleted successfully",
        "id": str(search_id)
    }


@router.post("/{user_id}/saved-searches/{search_id}/execute")
def execute_saved_search(
    user_id: str,
    search_id: UUID,
    request: Request,
    session: Session = Depends(get_session),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=1000)
):
    """
    **Execute Saved Search**

    Runs a saved search and returns results.

    **Returns:**
    Search results using saved query parameters with pagination.
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot execute other user's saved searches"
        )

    # Get saved search
    saved_search = session.get(SavedSearch, search_id)

    if not saved_search or saved_search.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Saved search not found"
        )

    # Extract query parameters
    query_params = saved_search.query_params
    query = query_params.get("query")
    filters = query_params.get("filters", {})
    sort_by = query_params.get("sort_by", "relevance")
    sort_order = query_params.get("sort_order", "desc")

    # Execute search
    try:
        tasks, total_count = SearchService.search_tasks(
            session=session,
            user_id=user_id,
            query=query,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page
        )

        total_pages = (total_count + per_page - 1) // per_page

        return {
            "saved_search_name": saved_search.name,
            "saved_search_id": str(saved_search.id),
            "tasks": tasks,
            "total": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute saved search: {str(e)}"
        )


# === Search Suggestions Endpoint ===

@router.get("/{user_id}/search/suggestions")
def get_search_suggestions(
    user_id: str,
    request: Request,
    session: Session = Depends(get_session),
    prefix: str = Query(..., min_length=1, max_length=50),
    type: str = Query("tags", description="Suggestion type: tags or titles")
):
    """
    **Get Search Suggestions**

    Provides autocomplete suggestions for search input.

    **Query Parameters:**
    - `prefix`: Text prefix to match (e.g., "wor" for "work")
    - `type`: Suggestion type ('tags' or 'titles')

    **Returns:**
    List of matching suggestions (max 20).
    """
    # Verify user_id matches authenticated user
    if request.state.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot access other user's suggestions"
        )

    suggestions = SearchService.get_search_suggestions(
        session=session,
        user_id=user_id,
        prefix=prefix,
        suggestion_type=type
    )

    return {
        "suggestions": suggestions,
        "prefix": prefix,
        "type": type
    }
