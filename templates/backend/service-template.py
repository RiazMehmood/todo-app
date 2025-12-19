"""
Service Layer Template - Business Logic Pattern

This template demonstrates the pattern for creating service classes that
handle business logic in the FastAPI backend.

Usage:
1. Copy this template
2. Define service methods for your domain
3. Keep logic separate from API routes
4. Handle validation, database operations, and business rules
5. Return standardized results

Example from Phase II & III:
- task_service.py, chat_service.py, ai_agent_manager.py
"""

from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ServiceTemplate:
    """
    Service class for handling DOMAIN_NAME business logic.

    This service provides methods for:
    - Creating ENTITY
    - Reading/querying ENTITY
    - Updating ENTITY
    - Deleting ENTITY
    - Additional business operations

    Attributes:
        db: Database session
        config: Optional configuration dictionary
    """

    def __init__(self, db: Session, config: Optional[Dict[str, Any]] = None):
        """
        Initialize service with database session.

        Args:
            db: SQLModel database session
            config: Optional configuration (API keys, settings, etc.)
        """
        self.db = db
        self.config = config or {}
        logger.info(f"{self.__class__.__name__} initialized")

    # ========================================
    # CREATE Operations
    # ========================================

    def create_entity(
        self,
        user_id: str,
        required_field: str,
        optional_field: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new entity for the user.

        Args:
            user_id: User ID (for multi-user isolation)
            required_field: Required field description
            optional_field: Optional field description

        Returns:
            Dictionary with created entity data:
            {
                "id": int,
                "status": "created",
                "data": {...}
            }

        Raises:
            ValueError: If validation fails
            Exception: For database errors
        """
        try:
            # 1. Validate inputs
            if not user_id:
                raise ValueError("user_id is required")
            if not required_field or len(required_field) < 1:
                raise ValueError("required_field must not be empty")

            # 2. Business logic validation
            # Example: Check for duplicates, limits, permissions
            # existing = self._check_duplicate(user_id, required_field)
            # if existing:
            #     raise ValueError("Entity already exists")

            # 3. Create entity
            from models import YourModel

            entity = YourModel(
                user_id=user_id,
                required_field=required_field,
                optional_field=optional_field
            )

            # 4. Save to database
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)

            logger.info(f"Entity {entity.id} created for user {user_id}")

            # 5. Return standardized response
            return {
                "id": entity.id,
                "status": "created",
                "data": self._entity_to_dict(entity)
            }

        except ValueError as e:
            logger.warning(f"Validation error creating entity: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating entity: {str(e)}")
            self.db.rollback()
            raise

    # ========================================
    # READ Operations
    # ========================================

    def get_entity_by_id(
        self,
        user_id: str,
        entity_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get entity by ID (with user isolation).

        Args:
            user_id: User ID for isolation
            entity_id: Entity ID to retrieve

        Returns:
            Entity data dictionary or None if not found

        Raises:
            ValueError: If entity doesn't belong to user
        """
        try:
            from models import YourModel

            entity = self.db.get(YourModel, entity_id)

            if not entity:
                return None

            # Multi-user isolation check
            if entity.user_id != user_id:
                raise ValueError("Access denied: entity belongs to different user")

            return self._entity_to_dict(entity)

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving entity {entity_id}: {str(e)}")
            raise

    def list_entities(
        self,
        user_id: str,
        filter_field: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List entities for user with optional filtering.

        Args:
            user_id: User ID for isolation
            filter_field: Optional filter value
            limit: Maximum results to return
            offset: Results to skip (pagination)

        Returns:
            {
                "entities": [list of entity dicts],
                "total": total count,
                "limit": limit used,
                "offset": offset used
            }
        """
        try:
            from models import YourModel

            # Build query
            query = select(YourModel).where(YourModel.user_id == user_id)

            # Apply filters
            if filter_field:
                query = query.where(YourModel.some_field == filter_field)

            # Get total count (before pagination)
            total_query = query
            total = len(self.db.exec(total_query).all())

            # Apply pagination
            query = query.limit(limit).offset(offset)

            # Execute query
            entities = self.db.exec(query).all()

            logger.info(f"Listed {len(entities)} entities for user {user_id}")

            return {
                "entities": [self._entity_to_dict(e) for e in entities],
                "total": total,
                "limit": limit,
                "offset": offset
            }

        except Exception as e:
            logger.error(f"Error listing entities: {str(e)}")
            raise

    # ========================================
    # UPDATE Operations
    # ========================================

    def update_entity(
        self,
        user_id: str,
        entity_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update entity fields.

        Args:
            user_id: User ID for isolation
            entity_id: Entity ID to update
            updates: Dictionary of fields to update

        Returns:
            Updated entity data

        Raises:
            ValueError: If validation fails or entity not found
        """
        try:
            from models import YourModel

            # Get entity with isolation check
            entity = self.db.get(YourModel, entity_id)
            if not entity:
                raise ValueError(f"Entity {entity_id} not found")
            if entity.user_id != user_id:
                raise ValueError("Access denied")

            # Validate updates
            allowed_fields = {"required_field", "optional_field"}
            for field in updates:
                if field not in allowed_fields:
                    raise ValueError(f"Field '{field}' cannot be updated")

            # Apply updates
            for field, value in updates.items():
                setattr(entity, field, value)

            entity.updated_at = datetime.utcnow()

            # Save
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)

            logger.info(f"Entity {entity_id} updated for user {user_id}")

            return self._entity_to_dict(entity)

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating entity {entity_id}: {str(e)}")
            self.db.rollback()
            raise

    # ========================================
    # DELETE Operations
    # ========================================

    def delete_entity(
        self,
        user_id: str,
        entity_id: int
    ) -> Dict[str, Any]:
        """
        Delete entity (soft or hard delete).

        Args:
            user_id: User ID for isolation
            entity_id: Entity ID to delete

        Returns:
            {
                "id": entity_id,
                "status": "deleted"
            }

        Raises:
            ValueError: If entity not found or access denied
        """
        try:
            from models import YourModel

            # Get entity with isolation check
            entity = self.db.get(YourModel, entity_id)
            if not entity:
                raise ValueError(f"Entity {entity_id} not found")
            if entity.user_id != user_id:
                raise ValueError("Access denied")

            # Hard delete (or use soft delete by setting deleted_at field)
            self.db.delete(entity)
            self.db.commit()

            logger.info(f"Entity {entity_id} deleted for user {user_id}")

            return {
                "id": entity_id,
                "status": "deleted"
            }

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error deleting entity {entity_id}: {str(e)}")
            self.db.rollback()
            raise

    # ========================================
    # Helper Methods
    # ========================================

    def _entity_to_dict(self, entity) -> Dict[str, Any]:
        """Convert entity model to dictionary."""
        return {
            "id": entity.id,
            "user_id": entity.user_id,
            "required_field": entity.required_field,
            "optional_field": entity.optional_field,
            "created_at": entity.created_at.isoformat() if entity.created_at else None,
            "updated_at": entity.updated_at.isoformat() if entity.updated_at else None
        }

    def _check_duplicate(self, user_id: str, field_value: str) -> bool:
        """Check if duplicate exists for user."""
        from models import YourModel

        query = select(YourModel).where(
            YourModel.user_id == user_id,
            YourModel.required_field == field_value
        )
        existing = self.db.exec(query).first()
        return existing is not None


# ========================================
# Example: Real Service from Phase III
# ========================================

class ChatService:
    """Service for handling chat operations."""

    def __init__(self, db: Session, openai_api_key: str):
        self.db = db
        self.openai_api_key = openai_api_key

    def process_message(
        self,
        user_id: str,
        message_text: str,
        conversation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process user message and return AI response.

        Returns:
            {
                "conversation_id": int,
                "user_message": {...},
                "ai_response": {...},
                "tool_calls": [...]
            }
        """
        try:
            # 1. Get or create conversation
            from models import Conversation, Message

            if conversation_id:
                conversation = self.db.get(Conversation, conversation_id)
                if not conversation or conversation.user_id != user_id:
                    raise ValueError("Invalid conversation")
            else:
                conversation = Conversation(user_id=user_id)
                self.db.add(conversation)
                self.db.commit()
                self.db.refresh(conversation)

            # 2. Save user message
            user_msg = Message(
                user_id=user_id,
                conversation_id=conversation.id,
                role="user",
                content=message_text
            )
            self.db.add(user_msg)
            self.db.commit()

            # 3. Process with AI (using Agents SDK)
            # ai_response = await self.agent.run(message_text, context={...})

            # 4. Save AI message
            # ai_msg = Message(...)
            # self.db.add(ai_msg)
            # self.db.commit()

            # 5. Return result
            return {
                "conversation_id": conversation.id,
                "user_message": {...},
                "ai_response": {...},
                "tool_calls": []
            }

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            self.db.rollback()
            raise


# ========================================
# Best Practices
# ========================================

# 1. Separation of Concerns:
#    - Service handles business logic
#    - Routes handle HTTP concerns (request/response)
#    - Models handle data structure

# 2. Multi-User Isolation:
#    - ALWAYS require user_id parameter
#    - ALWAYS check user_id in queries
#    - NEVER allow cross-user data access

# 3. Error Handling:
#    - Use try/except blocks
#    - Rollback database on errors
#    - Log errors for debugging
#    - Raise meaningful exceptions

# 4. Validation:
#    - Validate all inputs
#    - Check business rules
#    - Return clear error messages

# 5. Testing:
#    - Unit test each service method
#    - Test with different user contexts
#    - Test validation and error cases
#    - Mock database for speed
