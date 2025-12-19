"""
FastAPI Endpoint Template - API Route Pattern

This template demonstrates the pattern for creating REST API endpoints
with FastAPI, including authentication, validation, and error handling.

Usage:
1. Copy this template
2. Define your routes and handlers
3. Add authentication and validation
4. Connect to service layer for business logic
5. Return standardized responses

Example from Phase II & III:
- routes/auth.py, routes/tasks.py, routes/chat.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from sqlmodel import Session
import logging

# Import authentication and database dependencies
from middleware.auth import get_current_user
from db import get_session

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/RESOURCE_NAME",
    tags=["Resource Name"]
)


# ========================================
# 1. Request/Response Models (Pydantic)
# ========================================

class CreateEntityRequest(BaseModel):
    """Request model for creating an entity."""
    required_field: str = Field(..., min_length=1, max_length=200, description="Required field")
    optional_field: Optional[str] = Field(None, max_length=1000, description="Optional field")

    @validator('required_field')
    def validate_required_field(cls, v):
        """Custom validation for required_field."""
        if not v.strip():
            raise ValueError('required_field cannot be empty or whitespace')
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "required_field": "Example value",
                "optional_field": "Optional example"
            }
        }


class EntityResponse(BaseModel):
    """Response model for entity data."""
    id: int
    user_id: str
    required_field: str
    optional_field: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user-123",
                "required_field": "Example",
                "optional_field": "Optional",
                "created_at": "2025-12-16T10:00:00Z",
                "updated_at": "2025-12-16T10:00:00Z"
            }
        }


class ListEntitiesResponse(BaseModel):
    """Response model for listing entities."""
    entities: List[EntityResponse]
    total: int
    limit: int
    offset: int


class UpdateEntityRequest(BaseModel):
    """Request model for updating entity."""
    required_field: Optional[str] = Field(None, min_length=1, max_length=200)
    optional_field: Optional[str] = Field(None, max_length=1000)


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str

    class Config:
        schema_extra = {
            "example": {"detail": "Error message description"}
        }


# ========================================
# 2. CREATE Endpoint
# ========================================

@router.post(
    "/",
    response_model=EntityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new entity",
    description="Create a new entity for the authenticated user",
    responses={
        201: {"description": "Entity created successfully"},
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def create_entity(
    request: CreateEntityRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Create a new entity.

    - **required_field**: Required field description (1-200 chars)
    - **optional_field**: Optional field description (max 1000 chars)
    """
    try:
        # Import service
        from services.entity_service import EntityService

        # Initialize service
        service = EntityService(db)

        # Call service method
        result = service.create_entity(
            user_id=current_user["user_id"],
            required_field=request.required_field,
            optional_field=request.optional_field
        )

        logger.info(f"Entity {result['id']} created for user {current_user['user_id']}")

        return result["data"]

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating entity: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ========================================
# 3. READ Endpoints
# ========================================

@router.get(
    "/{entity_id}",
    response_model=EntityResponse,
    summary="Get entity by ID",
    responses={
        200: {"description": "Entity found"},
        404: {"model": ErrorResponse, "description": "Entity not found"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"}
    }
)
async def get_entity(
    entity_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Get entity by ID (with user isolation)."""
    try:
        from services.entity_service import EntityService

        service = EntityService(db)
        result = service.get_entity_by_id(
            user_id=current_user["user_id"],
            entity_id=entity_id
        )

        if not result:
            raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

        return result

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving entity {entity_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/",
    response_model=ListEntitiesResponse,
    summary="List entities",
    responses={
        200: {"description": "Entities listed successfully"},
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
async def list_entities(
    filter_field: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    List entities for authenticated user.

    - **filter_field**: Optional filter value
    - **limit**: Maximum results (default: 100, max: 500)
    - **offset**: Results to skip for pagination (default: 0)
    """
    try:
        # Validate pagination
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=400, detail="limit must be 1-500")
        if offset < 0:
            raise HTTPException(status_code=400, detail="offset must be >= 0")

        from services.entity_service import EntityService

        service = EntityService(db)
        result = service.list_entities(
            user_id=current_user["user_id"],
            filter_field=filter_field,
            limit=limit,
            offset=offset
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing entities: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ========================================
# 4. UPDATE Endpoint
# ========================================

@router.patch(
    "/{entity_id}",
    response_model=EntityResponse,
    summary="Update entity",
    responses={
        200: {"description": "Entity updated successfully"},
        400: {"model": ErrorResponse, "description": "Validation error"},
        404: {"model": ErrorResponse, "description": "Entity not found"},
        403: {"model": ErrorResponse, "description": "Access denied"}
    }
)
async def update_entity(
    entity_id: int,
    request: UpdateEntityRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Update entity fields."""
    try:
        # Build updates dictionary (only include provided fields)
        updates = {}
        if request.required_field is not None:
            updates["required_field"] = request.required_field
        if request.optional_field is not None:
            updates["optional_field"] = request.optional_field

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        from services.entity_service import EntityService

        service = EntityService(db)
        result = service.update_entity(
            user_id=current_user["user_id"],
            entity_id=entity_id,
            updates=updates
        )

        logger.info(f"Entity {entity_id} updated for user {current_user['user_id']}")

        return result

    except HTTPException:
        raise
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        elif "Access denied" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating entity {entity_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ========================================
# 5. DELETE Endpoint
# ========================================

@router.delete(
    "/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete entity",
    responses={
        204: {"description": "Entity deleted successfully"},
        404: {"model": ErrorResponse, "description": "Entity not found"},
        403: {"model": ErrorResponse, "description": "Access denied"}
    }
)
async def delete_entity(
    entity_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Delete entity."""
    try:
        from services.entity_service import EntityService

        service = EntityService(db)
        service.delete_entity(
            user_id=current_user["user_id"],
            entity_id=entity_id
        )

        logger.info(f"Entity {entity_id} deleted for user {current_user['user_id']}")

        # 204 No Content - no return value
        return None

    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        elif "Access denied" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting entity {entity_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ========================================
# Example: Real Endpoint from Phase III
# ========================================

@router.post(
    "/{user_id}/chat",
    summary="Send chat message (Hackathon Required)",
    responses={
        200: {"description": "AI response with tool calls"},
        403: {"description": "AI features not enabled"}
    }
)
async def send_chat_message(
    user_id: str,
    request: dict,  # {"conversation_id": int?, "message": str}
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Send message to AI assistant (HACKATHON REQUIRED endpoint).

    Returns:
        {
            "conversation_id": int,
            "response": str,
            "tool_calls": [...]
        }
    """
    try:
        # Verify user_id matches authenticated user
        if user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")

        # Check AI enabled
        from services.chat_service import ChatService

        service = ChatService(db, openai_api_key="...")
        result = service.process_message(
            user_id=user_id,
            message_text=request["message"],
            conversation_id=request.get("conversation_id")
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ========================================
# Best Practices
# ========================================

# 1. Authentication:
#    - Use Depends(get_current_user) for protected endpoints
#    - Verify user_id in path matches authenticated user
#    - Return 401 for missing auth, 403 for wrong user

# 2. Validation:
#    - Use Pydantic models for request/response
#    - Add custom validators for business rules
#    - Return 400 for validation errors

# 3. Error Handling:
#    - Catch specific exceptions first
#    - Map to appropriate HTTP status codes
#    - Log errors for debugging
#    - Return user-friendly error messages
#    - Don't expose internal details in production

# 4. Response Models:
#    - Always define response_model
#    - Provide examples in schema_extra
#    - Document in docstring
#    - Use consistent field naming

# 5. HTTP Status Codes:
#    - 200: OK (GET, PATCH)
#    - 201: Created (POST)
#    - 204: No Content (DELETE)
#    - 400: Bad Request (validation)
#    - 401: Unauthorized (not authenticated)
#    - 403: Forbidden (authenticated but access denied)
#    - 404: Not Found
#    - 500: Internal Server Error

# 6. Documentation:
#    - Add summary and description
#    - Document all responses
#    - Provide examples
#    - Use tags for grouping
#    - Keep docstrings concise

# 7. Service Layer:
#    - Keep routes thin (validation + service call)
#    - Business logic in service layer
#    - Database operations in service
#    - Return serialized data from service
