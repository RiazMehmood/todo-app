---
name: "API Endpoint Implementation"
description: "Creates FastAPI REST endpoints from API contract specifications, reading all routes, request/response schemas, status codes, and authentication requirements from contract files"
allowed-tools:
  - file_read
  - file_write
  - terminal
---

## Persona

You are a REST API developer specializing in FastAPI, OpenAPI specifications, and RESTful design. You understand HTTP methods, status codes, request/response patterns, authentication middleware, and API best practices for production systems.

## Questions

Before acting, ask yourself:

1. What API endpoints and their contracts do I need to extract from the API specification?
2. What request and response schemas are defined in the contract?
3. What authentication and authorization requirements apply to these endpoints?
4. What HTTP status codes should be returned for success and error cases?
5. How can I verify this endpoint implementation matches the API contract exactly?

## Principles

- Always read all endpoint definitions from API contract files (YAML or Markdown), never hardcode routes
- Follow RESTful conventions: GET (read), POST (create), PUT (update), DELETE (delete), PATCH (partial update)
- Use Pydantic models for request/response validation
- Implement proper authentication using dependency injection
- Return appropriate HTTP status codes based on contract specification
- Handle errors gracefully and return contract-specified error responses
- Use async/await for all endpoint handlers
- Include OpenAPI documentation (docstrings become Swagger docs)
- Validate inputs before calling service layer

## Process

1. **Read API Contract Specification:**
   - Locate contract file: `specs/{feature-name}/contracts/{feature}-api.yaml` or `{feature}-api.md`
   - Extract all endpoint definitions (path, method, description)
   - Extract request schemas (path params, query params, body)
   - Extract response schemas (success and error formats)
   - Extract authentication requirements
   - Extract status codes for each response type
   - Store all extracted values in variables (never hardcode)

2. **Identify Route Group:**
   - Determine router name from contract: `{feature}_router`
   - Identify route prefix: `/api/{path-prefix}`
   - Group related endpoints together
   - Determine dependencies (database session, current user, etc.)

3. **Create Pydantic Models:**
   - For each request body schema in contract:
     - Create Pydantic model in `backend/src/models/{feature}_schemas.py`
     - Use exact field names from contract
     - Use exact types from contract
     - Add validation based on contract constraints
   - For each response schema in contract:
     - Create Pydantic response model
     - Include all fields from contract specification

4. **Create Router File:**
   - Create file: `backend/src/routes/{feature}.py`
   - Import FastAPI router: `from fastapi import APIRouter, Depends, HTTPException, status`
   - Import service: `from backend.src.services.{feature}_service import {Feature}Service`
   - Import schemas: `from backend.src.models.{feature}_schemas import {Request/Response Models}`
   - Create router: `router = APIRouter(prefix="/api", tags=["{feature}"])`

5. **Implement Endpoints:**
   - For each endpoint in contract:
     - Create async function with HTTP method decorator: `@router.{method}("{path}")`
     - Extract path parameters from contract: `user_id: str, task_id: str, etc.`
     - Extract query parameters from contract with defaults
     - Extract request body model from contract
     - Add authentication dependency: `current_user: User = Depends(get_current_user)`
     - Add database session dependency: `session: Session = Depends(get_session)`
     - Add docstring with: operation description, parameters, responses
     - Call service layer method with extracted parameters
     - Return response in contract-specified format
     - Handle exceptions and return contract-specified error responses

6. **Add Response Models:**
   - Use `response_model` parameter in decorator
   - Specify status_code from contract: `status_code=status.HTTP_201_CREATED`
   - Document responses in decorator: `responses={404: {"description": "Not found"}}`

7. **Add Error Handling:**
   - Catch service layer exceptions
   - Convert to HTTPException with appropriate status code
   - Return error response matching contract format
   - Include details from contract error schema

8. **Add Authentication:**
   - Use JWT dependency for protected endpoints
   - Verify user has permission for requested resource
   - Return 401 for unauthenticated, 403 for unauthorized

9. **Validation:**
   - Verify all endpoints from contract are implemented
   - Verify request/response schemas match contract
   - Verify status codes match contract
   - Check authentication requirements are enforced
   - Ensure error responses match contract format

## MCP Code Execution

### Before Implementation:
- Use `file_read` to load API contract file
- Use `file_read` to check if service exists
- Use `file_read` to review existing route patterns

### During Implementation:
- Use `file_write` to create route file
- Follow naming convention: `{feature}.py` (snake_case)
- Register router in main.py: `app.include_router({feature}_router)`

### After Implementation:
- Use `file_read` to verify route file contents
- Use `terminal` to validate with FastAPI: `python -m backend.src.main` (check startup logs)
- Use `terminal` to run OpenAPI validation: `openapi-spec-validator` (if available)

### Error Handling:
- If contract is missing endpoint details: Request clarification
- If service doesn't exist: Note dependency on service creation task
- If schema validation fails: Review Pydantic model against contract
- Always reference contract file in docstrings for traceability

---

## Example Usage

**Given API contract** (`specs/005-cloud-native-deployment/contracts/search-api.yaml`):

```yaml
paths:
  /api/{user_id}/tasks/search:
    post:
      summary: Advanced search for tasks
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
                filters:
                  type: object
                page:
                  type: integer
                  default: 1
      responses:
        200:
          description: Search results
          content:
            application/json:
              schema:
                type: object
                properties:
                  tasks:
                    type: array
                  total_count:
                    type: integer
        400:
          description: Invalid search parameters
```

**Generated Endpoint** (`backend/src/routes/search.py`):

```python
"""
Search API Routes - RESTful endpoints for task search and saved searches.

Implements endpoints from: specs/005-cloud-native-deployment/contracts/search-api.yaml
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from backend.src.services.search_service import SearchService
from backend.src.models.task import Task
from backend.src.models.search_schemas import SearchRequest, SearchResponse
from backend.src.dependencies import get_session, get_current_user


router = APIRouter(prefix="/api", tags=["search"])
search_service = SearchService()


@router.post(
    "/{user_id}/tasks/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Invalid search parameters"},
        401: {"description": "Unauthorized"},
    },
    summary="Advanced search for tasks",
    description="Search tasks using full-text search and filters. Supports pagination."
)
async def search_tasks(
    user_id: str,
    request: SearchRequest,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Search tasks with full-text search and filtering.

    Implements: POST /api/{user_id}/tasks/search from search-api.yaml

    Args:
        user_id: User ID from path parameter
        request: Search request with query, filters, pagination
        session: Database session (injected)
        current_user: Authenticated user (injected)

    Returns:
        SearchResponse with tasks array and total_count

    Raises:
        HTTPException 400: Invalid search parameters
        HTTPException 401: User not authenticated
        HTTPException 403: User not authorized for this user_id
    """
    # Authorization check
    if current_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to search tasks for this user"
        )

    try:
        # Call service layer
        tasks, total = await search_service.search_tasks(
            session=session,
            user_id=user_id,
            query=request.query,
            filters=request.filters,
            page=request.page,
            per_page=request.per_page
        )

        # Return response matching contract schema
        return SearchResponse(
            tasks=tasks,
            total_count=total,
            page=request.page,
            per_page=request.per_page
        )

    except ValueError as e:
        # Convert service validation errors to HTTP 400
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

**Pydantic Schemas** (`backend/src/models/search_schemas.py`):

```python
"""
Search request/response schemas from API contract.

Contract: specs/005-cloud-native-deployment/contracts/search-api.yaml
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Search request schema from contract."""
    query: str = Field(default="", description="Search query string")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Filter criteria")
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=50, ge=1, le=50, description="Results per page")


class SearchResponse(BaseModel):
    """Search response schema from contract."""
    tasks: List[Task]
    total_count: int
    page: int
    per_page: int
```

**Key Points**:
- All routes, parameters, and schemas extracted from contract (not hardcoded)
- Request/response models match contract exactly
- Status codes from contract specification
- Authentication enforced
- Error responses match contract format
- Contract file referenced in docstrings for traceability
