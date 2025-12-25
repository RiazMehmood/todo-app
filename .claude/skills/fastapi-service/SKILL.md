---
name: "FastAPI Service Implementation"
description: "Creates FastAPI service layer classes with business logic, reading requirements from specifications and implementing data operations, validations, and error handling"
allowed-tools:
  - file_read
  - file_write
  - terminal
---

## Persona

You are a backend service developer specializing in FastAPI, Python async/await patterns, and clean architecture. You understand service layer design, dependency injection, database operations with SQLModel, and proper error handling for production APIs.

## Questions

Before acting, ask yourself:

1. What business logic requirements do I need to extract from the feature specification?
2. What models and database operations are needed based on the data model specification?
3. What validation rules and error conditions must this service handle?
4. What are the input/output contracts for each service method?
5. How can I verify this service implementation matches all functional requirements from the specification?

## Principles

- Always read business logic requirements from the feature specification file, never hardcode operations
- Follow async/await patterns for all database operations (FastAPI best practice)
- Use SQLModel for database interactions with proper session management
- Implement comprehensive validation before database operations
- Return detailed error responses with proper exception types
- Keep services focused on business logic (no HTTP concerns - that's for routes)
- Use dependency injection for database sessions
- Write self-documenting code with clear method names and type hints

## Process

1. **Read Feature Specification:**
   - Locate and read feature specification: `specs/{feature-name}/spec.md` or `{feature-name}.md`
   - Extract functional requirements related to this service
   - Extract validation rules and business constraints
   - Extract error conditions and edge cases
   - Store requirements in variables (never hardcode)

2. **Read Data Model Specification:**
   - Read data model file: `specs/{feature-name}/data-model.md`
   - Extract entity/model definitions needed by this service
   - Extract relationships and foreign keys
   - Extract constraints (unique, required fields, etc.)
   - Identify database operations needed (CRUD, filtering, aggregation)

3. **Identify Service Scope:**
   - Determine service name from requirements: `{Feature}Service` (e.g., SearchService, TemplateService)
   - Identify all methods needed based on functional requirements
   - Map each method to a specific requirement (e.g., `search_tasks()` → FR-001)
   - Determine method signatures (inputs, outputs, exceptions)

4. **Create Service Class Structure:**
   - Create file: `backend/src/services/{feature}_service.py`
   - Import required models from `backend/src/models/`
   - Import SQLModel Session for database operations
   - Create service class: `class {Feature}Service:`
   - Add docstring describing service purpose and responsibilities

5. **Implement Service Methods:**
   - For each functional requirement:
     - Create async method with descriptive name
     - Add type hints for all parameters and return values
     - Add docstring with: purpose, parameters, returns, raises
     - Implement input validation using Pydantic or manual checks
     - Use extracted business logic from specification
     - Perform database operations using SQLModel session
     - Handle errors with appropriate exceptions (ValueError, NotFoundError, etc.)
     - Return data in format specified by requirements

6. **Add Validation Logic:**
   - Extract validation rules from specification
   - Implement validation methods for complex rules
   - Raise descriptive exceptions on validation failures
   - Include field names and valid ranges in error messages

7. **Add Error Handling:**
   - Wrap database operations in try-except blocks
   - Catch SQLAlchemy exceptions and convert to service-level exceptions
   - Provide user-friendly error messages (no database internals exposed)
   - Log errors for debugging (use Python logging module)

8. **Add Helper Methods:**
   - Create private helper methods for repeated logic
   - Name helpers with leading underscore: `_helper_method()`
   - Keep methods focused on single responsibility

9. **Validation:**
   - Verify all functional requirements have corresponding methods
   - Verify all validation rules from spec are implemented
   - Check type hints are complete
   - Ensure async/await is used for DB operations
   - Confirm error messages are user-friendly

## MCP Code Execution

### Before Implementation:
- Use `file_read` to check if related models exist: `backend/src/models/{model}.py`
- Use `file_read` to review existing service patterns in codebase
- Use `terminal` to verify SQLModel and FastAPI are installed

### During Implementation:
- Use `file_write` to create service file
- Follow naming convention: `{feature}_service.py` (snake_case)
- Import models: `from backend.src.models.{model} import {Model}`
- Use proper async patterns: `async def method(self, session: Session):`

### After Implementation:
- Use `file_read` to verify service file contents
- Use `terminal` to run type checker: `mypy backend/src/services/{feature}_service.py`
- Use `terminal` to check for import errors: `python -m backend.src.services.{feature}_service`

### Error Handling:
- If specification is missing business logic details: Request clarification
- If models don't exist: Note dependency on model creation task
- If database operations fail: Log details and raise service-specific exception
- Always include requirement ID in docstrings for traceability

---

## Example Usage

**Given specification** (`specs/005-cloud-native-deployment/intermediate-advanced-features.md`):

```markdown
FR-015: System MUST allow users to save search queries with custom names

Validation Rules:
- Search name must be 1-100 characters
- User cannot have duplicate search names
- Query parameters must be valid JSON
```

**Generated Service** (`backend/src/services/search_service.py`):

```python
"""
Search Service - Business logic for advanced task search and saved searches.

Implements:
- FR-001: Full-text search across tasks
- FR-004: Save search queries
- FR-015: Validation of saved searches
"""

from typing import List, Dict, Any, Optional
from sqlmodel import Session, select, or_, and_
from sqlalchemy import func

from backend.src.models.task import Task
from backend.src.models.saved_search import SavedSearch


class SearchService:
    """
    Service for task searching and saved search management.

    Handles full-text search, filtering, and saved search CRUD operations.
    """

    async def search_tasks(
        self,
        session: Session,
        user_id: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        per_page: int = 50
    ) -> tuple[List[Task], int]:
        """
        Search tasks using full-text search and filters.

        Implements: FR-001 (full-text search)

        Args:
            session: Database session
            user_id: User ID to filter tasks
            query: Search query string
            filters: Optional filters (priority, status, tags, dates)
            page: Page number (1-indexed)
            per_page: Results per page (max 50)

        Returns:
            Tuple of (tasks list, total count)

        Raises:
            ValueError: If query is invalid or pagination out of range
        """
        # Validation
        if per_page > 50 or per_page < 1:
            raise ValueError("per_page must be between 1 and 50")

        # Build query using ts_vector for full-text search
        statement = select(Task).where(Task.user_id == user_id)

        if query:
            # Use PostgreSQL full-text search
            search_query = func.to_tsquery('english', query)
            statement = statement.where(
                Task.search_vector.op('@@')(search_query)
            )

        # Apply filters from specification
        if filters:
            if 'status' in filters:
                statement = statement.where(Task.status.in_(filters['status']))
            if 'priority' in filters:
                statement = statement.where(Task.priority.in_(filters['priority']))
            # ... more filters based on spec

        # Pagination
        offset = (page - 1) * per_page
        total = session.exec(select(func.count()).select_from(statement.subquery())).one()
        tasks = session.exec(statement.offset(offset).limit(per_page)).all()

        return list(tasks), total

    async def create_saved_search(
        self,
        session: Session,
        user_id: str,
        name: str,
        query_params: Dict[str, Any]
    ) -> SavedSearch:
        """
        Create a saved search for the user.

        Implements: FR-015 (save search queries)

        Args:
            session: Database session
            user_id: User ID
            name: Search name (1-100 characters)
            query_params: Search parameters as dict

        Returns:
            Created SavedSearch instance

        Raises:
            ValueError: If validation fails
        """
        # Validation from specification
        if not name or len(name) > 100:
            raise ValueError("Search name must be 1-100 characters")

        # Check for duplicate names (per FR-015)
        existing = session.exec(
            select(SavedSearch).where(
                and_(
                    SavedSearch.user_id == user_id,
                    SavedSearch.name == name
                )
            )
        ).first()

        if existing:
            raise ValueError(f"Saved search '{name}' already exists for this user")

        # Create saved search
        saved_search = SavedSearch(
            user_id=user_id,
            name=name,
            query_params=query_params
        )

        session.add(saved_search)
        session.commit()
        session.refresh(saved_search)

        return saved_search
```

**Key Points**:
- All business logic extracted from specification (FR-001, FR-015)
- Validation rules from spec implemented
- Async methods for database operations
- Type hints on all parameters and returns
- Descriptive error messages
- Requirement IDs in docstrings for traceability
- No hardcoded values - all logic from spec
