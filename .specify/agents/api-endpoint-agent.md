# API Endpoint Agent

**Purpose**: Specialized agent for creating FastAPI REST endpoints with authentication

**Trigger**: Use when you need to:
- Create new API endpoints
- Add CRUD operations for entities
- Implement authentication and validation
- Connect endpoints to service layer

## Agent Configuration

```yaml
name: api-endpoint-agent
description: Create FastAPI REST endpoints with authentication and validation
capabilities:
  - Generate Pydantic request/response models
  - Create CRUD endpoint handlers
  - Add authentication dependencies
  - Implement validation and error handling
tools:
  - Read (for existing routes)
  - Write (for new endpoints)
  - Edit (for updating routes)
context_files:
  - backend/src/routes/*.py
  - backend/src/middleware/auth.py
  - templates/backend/api-endpoint-template.py
```

## How to Use

### Creating CRUD Endpoints for New Entity

**Prompt**:
```
Create REST API endpoints for a "notifications" entity with:
- POST /api/notifications - Create notification
- GET /api/notifications - List user's notifications
- GET /api/notifications/{id} - Get notification by ID
- PATCH /api/notifications/{id} - Mark as read
- DELETE /api/notifications/{id} - Delete notification

All endpoints should require authentication and enforce user isolation.
```

**Agent Will**:
1. Read API endpoint template
2. Create Pydantic request/response models
3. Implement all 5 CRUD endpoints
4. Add authentication dependency
5. Add user isolation checks
6. Add validation and error handling
7. Add OpenAPI documentation
8. Register router in main.py

### Creating Custom Endpoint

**Prompt**:
```
Create POST /api/notifications/mark-all-read endpoint that marks all
user's notifications as read. Should return count of updated notifications.
```

**Agent Will**:
1. Create request model (if needed)
2. Create response model with count field
3. Implement endpoint handler
4. Add authentication
5. Call service layer method
6. Add error handling
7. Document endpoint

## Example Output

```python
# backend/src/routes/notifications.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from sqlmodel import Session

from middleware.auth import get_current_user
from db import get_session

router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"]
)

class CreateNotificationRequest(BaseModel):
    message: str

class NotificationResponse(BaseModel):
    id: int
    user_id: str
    message: str
    read: bool
    created_at: str

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    request: CreateNotificationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Create a new notification for the authenticated user."""
    from services.notification_service import NotificationService

    service = NotificationService(db)
    result = service.create_notification(
        user_id=current_user["user_id"],
        message=request.message
    )

    return result

@router.get("/", response_model=List[NotificationResponse])
async def list_notifications(
    unread_only: bool = False,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """List notifications for authenticated user."""
    from services.notification_service import NotificationService

    service = NotificationService(db)
    result = service.list_notifications(
        user_id=current_user["user_id"],
        unread_only=unread_only,
        limit=limit
    )

    return result["notifications"]

# ... more endpoints
```

## Best Practices

1. **Authentication**: Always use Depends(get_current_user) for protected endpoints
2. **User Isolation**: Verify user_id matches authenticated user
3. **Validation**: Use Pydantic models for request/response validation
4. **Error Handling**: Return appropriate HTTP status codes
5. **Documentation**: Add docstrings and OpenAPI examples
6. **Service Layer**: Keep routes thin, logic in service layer

## Common Patterns

### User-Specific Resource Endpoint

```python
@router.get("/api/users/{user_id}/resources")
async def get_user_resources(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Verify user_id matches authenticated user
    if user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    # ... implementation
```

### Pagination Pattern

```python
@router.get("/api/resources")
async def list_resources(
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Validate pagination
    if limit < 1 or limit > 500:
        raise HTTPException(status_code=400, detail="limit must be 1-500")

    # ... implementation
    return {
        "resources": results,
        "total": total_count,
        "limit": limit,
        "offset": offset
    }
```

## Related Patterns

- [API Endpoint Template](../templates/backend/api-endpoint-template.py)
- [Service Template](../templates/backend/service-template.py)
- [Authentication Pattern](../knowledge/patterns/authentication-pattern.md)
