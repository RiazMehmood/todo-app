"""
SearchService

Provides advanced full-text search functionality for tasks using PostgreSQL ts_vector.
Supports:
- Full-text search with boolean operators (AND, OR, NOT)
- Multi-criteria filtering (status, priority, tags, date ranges)
- Relevance ranking using ts_rank()
- Input sanitization to prevent SQL injection
"""

from sqlmodel import Session, select, and_, or_, func, text
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import re

from ..models import Task
from ..config import POSTGRES_SEARCH_LIMIT


class SearchService:
    """
    Service for advanced task search functionality.

    Uses PostgreSQL full-text search with GIN indexes for performance.
    """

    @staticmethod
    def sanitize_search_query(query: str) -> str:
        """
        Sanitize search query to prevent SQL injection.

        Removes potentially harmful characters while preserving search functionality.

        Args:
            query: Raw search query from user

        Returns:
            Sanitized query string safe for ts_query
        """
        if not query:
            return ""

        # Remove special PostgreSQL characters except allowed ones
        # Allowed: letters, numbers, spaces, &, |, !, (, ), :, *
        sanitized = re.sub(r'[^\w\s&|!():*-]', ' ', query)

        # Remove excessive whitespace
        sanitized = ' '.join(sanitized.split())

        # Limit length to prevent DoS
        if len(sanitized) > 200:
            sanitized = sanitized[:200]

        return sanitized

    @staticmethod
    def parse_boolean_operators(query: str) -> str:
        """
        Parse boolean operators from user query and convert to ts_query format.

        Supports:
        - AND: 'urgent AND meeting' -> 'urgent & meeting'
        - OR: 'project OR task' -> 'project | task'
        - NOT: 'urgent NOT spam' -> 'urgent & !spam'
        - Implicit AND: 'urgent meeting' -> 'urgent & meeting'

        Args:
            query: Sanitized search query

        Returns:
            PostgreSQL ts_query compatible string
        """
        if not query:
            return ""

        # Replace boolean operators (case-insensitive)
        query = re.sub(r'\bAND\b', '&', query, flags=re.IGNORECASE)
        query = re.sub(r'\bOR\b', '|', query, flags=re.IGNORECASE)
        query = re.sub(r'\bNOT\b', '!', query, flags=re.IGNORECASE)

        # Split on operators and parentheses
        tokens = re.findall(r'[&|!()]|\w+', query)

        # Add implicit AND between adjacent words
        result = []
        for i, token in enumerate(tokens):
            result.append(token)

            # If current token is a word and next token is also a word, add AND
            if i < len(tokens) - 1:
                current_is_word = re.match(r'\w+', token)
                next_is_word = re.match(r'\w+', tokens[i + 1])

                if current_is_word and next_is_word:
                    result.append('&')

        return ' '.join(result)

    @staticmethod
    def build_date_filter(
        filter_type: str,
        custom_start: Optional[str] = None,
        custom_end: Optional[str] = None
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Build date range filter from filter type.

        Args:
            filter_type: One of 'last_7_days', 'last_30_days', 'last_90_days', 'custom_range'
            custom_start: Start date for custom range (ISO format)
            custom_end: End date for custom range (ISO format)

        Returns:
            Tuple of (start_date, end_date) or (None, None) if invalid
        """
        now = datetime.utcnow()

        if filter_type == "last_7_days":
            return (now - timedelta(days=7), now)
        elif filter_type == "last_30_days":
            return (now - timedelta(days=30), now)
        elif filter_type == "last_90_days":
            return (now - timedelta(days=90), now)
        elif filter_type == "custom_range":
            try:
                start = datetime.fromisoformat(custom_start) if custom_start else None
                end = datetime.fromisoformat(custom_end) if custom_end else None
                return (start, end)
            except (ValueError, TypeError):
                return (None, None)

        return (None, None)

    @staticmethod
    def search_tasks(
        session: Session,
        user_id: str,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "relevance",
        sort_order: str = "desc",
        page: int = 1,
        per_page: int = 50
    ) -> Tuple[List[Task], int]:
        """
        Search tasks with full-text search and filters.

        Args:
            session: Database session
            user_id: User ID to filter tasks
            query: Full-text search query (supports boolean operators)
            filters: Dict with optional filters:
                - status: List[str] - Task statuses
                - priority: List[str] - Task priorities
                - tags: List[str] - Task tags (any match)
                - created_after: str - ISO datetime
                - created_before: str - ISO datetime
                - due_after: str - ISO datetime
                - due_before: str - ISO datetime
                - date_filter: str - Predefined date ranges
            sort_by: Field to sort by ('relevance', 'created_at', 'updated_at', 'due_date', 'priority')
            sort_order: 'asc' or 'desc'
            page: Page number (1-indexed)
            per_page: Results per page (max 1000)

        Returns:
            Tuple of (tasks, total_count)
        """
        filters = filters or {}

        # Start with base query
        statement = select(Task).where(Task.user_id == user_id)

        # Apply full-text search if query provided
        if query and query.strip():
            # Sanitize and parse query
            sanitized_query = SearchService.sanitize_search_query(query)
            ts_query = SearchService.parse_boolean_operators(sanitized_query)

            if ts_query:
                # Use ts_query for full-text search
                # Cast to tsquery and match against search_vector
                statement = statement.where(
                    func.to_tsquery('english', ts_query).op('@@')(Task.search_vector)
                )

        # Apply status filter
        if filters.get("status"):
            statement = statement.where(Task.status.in_(filters["status"]))

        # Apply priority filter
        if filters.get("priority"):
            statement = statement.where(Task.priority.in_(filters["priority"]))

        # Apply tags filter (any tag matches)
        if filters.get("tags"):
            # PostgreSQL array overlap operator &&
            statement = statement.where(
                Task.tags.op('&&')(filters["tags"])
            )

        # Apply date filters
        if filters.get("date_filter"):
            start_date, end_date = SearchService.build_date_filter(
                filters["date_filter"],
                filters.get("custom_start"),
                filters.get("custom_end")
            )
            if start_date:
                statement = statement.where(Task.created_at >= start_date)
            if end_date:
                statement = statement.where(Task.created_at <= end_date)

        # Apply created_at filters
        if filters.get("created_after"):
            try:
                created_after = datetime.fromisoformat(filters["created_after"])
                statement = statement.where(Task.created_at >= created_after)
            except (ValueError, TypeError):
                pass

        if filters.get("created_before"):
            try:
                created_before = datetime.fromisoformat(filters["created_before"])
                statement = statement.where(Task.created_at <= created_before)
            except (ValueError, TypeError):
                pass

        # Apply due_date filters
        if filters.get("due_after"):
            try:
                due_after = datetime.fromisoformat(filters["due_after"])
                statement = statement.where(Task.due_date >= due_after)
            except (ValueError, TypeError):
                pass

        if filters.get("due_before"):
            try:
                due_before = datetime.fromisoformat(filters["due_before"])
                statement = statement.where(Task.due_date <= due_before)
            except (ValueError, TypeError):
                pass

        # Get total count before pagination
        count_statement = select(func.count()).select_from(statement.subquery())
        total_count = session.exec(count_statement).one()

        # Apply sorting
        if sort_by == "relevance" and query and query.strip():
            # Sort by relevance using ts_rank()
            sanitized_query = SearchService.sanitize_search_query(query)
            ts_query = SearchService.parse_boolean_operators(sanitized_query)

            if ts_query:
                # Add relevance score to query
                rank = func.ts_rank(
                    Task.search_vector,
                    func.to_tsquery('english', ts_query)
                )

                if sort_order == "desc":
                    statement = statement.order_by(rank.desc())
                else:
                    statement = statement.order_by(rank.asc())
        elif sort_by == "created_at":
            if sort_order == "desc":
                statement = statement.order_by(Task.created_at.desc())
            else:
                statement = statement.order_by(Task.created_at.asc())
        elif sort_by == "updated_at":
            if sort_order == "desc":
                statement = statement.order_by(Task.updated_at.desc())
            else:
                statement = statement.order_by(Task.updated_at.asc())
        elif sort_by == "due_date":
            if sort_order == "desc":
                statement = statement.order_by(Task.due_date.desc().nulls_last())
            else:
                statement = statement.order_by(Task.due_date.asc().nulls_last())
        elif sort_by == "priority":
            # Custom priority ordering: high > medium > low
            priority_order = {
                'high': 1,
                'medium': 2,
                'low': 3
            }
            if sort_order == "desc":
                statement = statement.order_by(Task.priority.desc())
            else:
                statement = statement.order_by(Task.priority.asc())
        else:
            # Default: sort by created_at desc
            statement = statement.order_by(Task.created_at.desc())

        # Apply pagination
        per_page = min(per_page, POSTGRES_SEARCH_LIMIT)  # Enforce max limit
        offset = (page - 1) * per_page

        statement = statement.offset(offset).limit(per_page)

        # Execute query
        tasks = session.exec(statement).all()

        return (list(tasks), total_count)

    @staticmethod
    def get_search_suggestions(
        session: Session,
        user_id: str,
        prefix: str,
        suggestion_type: str = "tags"
    ) -> List[str]:
        """
        Get autocomplete suggestions for search.

        Args:
            session: Database session
            user_id: User ID to filter tasks
            prefix: Prefix to match (e.g., "wor" for "work")
            suggestion_type: Type of suggestions ('tags', 'titles')

        Returns:
            List of matching suggestions
        """
        if suggestion_type == "tags":
            # Get unique tags from user's tasks that start with prefix
            statement = select(Task.tags).where(
                Task.user_id == user_id
            ).distinct()

            results = session.exec(statement).all()

            # Flatten and filter tags
            all_tags = set()
            for tag_array in results:
                if tag_array:
                    for tag in tag_array:
                        if tag.lower().startswith(prefix.lower()):
                            all_tags.add(tag)

            return sorted(list(all_tags))[:20]  # Limit to 20 suggestions

        return []
