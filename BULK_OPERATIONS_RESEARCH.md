# SQLAlchemy/SQLModel Bulk Operations Research
## Transaction Handling for PostgreSQL with 500+ Tasks

**Date**: December 23, 2025
**Target Stack**: FastAPI + SQLModel (SQLAlchemy 2.0) + PostgreSQL
**Focus**: Partial failure handling, transaction rollback strategies, progress reporting

---

## Executive Summary

This research document provides battle-tested patterns for handling bulk operations on 500+ database records with:
- **Partial failure tolerance**: 50 succeed, 50 fail - capture both outcomes
- **Transaction safety**: Atomic commits vs. partial progress savepoints
- **Progress tracking**: Real-time reporting for long-running operations
- **Detailed error reporting**: Task-level failure information with reasons

---

## 1. Handling Partial Failures in Bulk Operations

### Problem Statement
When updating/deleting 100 tasks:
- Tasks 1-50 succeed
- Tasks 51-100 fail (e.g., due to constraints, validation)
- **Question**: How do we capture which succeeded and which failed?

### Strategy 1: Item-Level Try-Catch (Recommended for User-Facing Operations)

**Pros**: Users know exactly what failed and why
**Cons**: Slower (N database round trips), but acceptable for <5000 items

```python
# File: backend/src/services/bulk_task_service.py
from sqlmodel import Session, select
from sqlalchemy import delete
from typing import List, Dict, Any, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BulkTaskService:
    """Handle bulk operations with partial failure tracking."""

    @staticmethod
    def bulk_delete_with_fallback(
        session: Session,
        user_id: str,
        task_ids: List[int],
        batch_size: int = 50
    ) -> Dict[str, Any]:
        """
        Delete tasks with item-level error tracking.

        Example: Deleting 100 tasks where 50 fail due to constraints.
        Returns: {"deleted": 50, "failed": 50, "failures": [...]}
        """
        results = {
            "deleted": [],
            "failed": [],
            "errors": []
        }

        # Process in batches to avoid memory issues
        for i in range(0, len(task_ids), batch_size):
            batch = task_ids[i:i+batch_size]

            for task_id in batch:
                try:
                    # Attempt to delete single task
                    task = session.query(Task).filter(
                        Task.id == task_id,
                        Task.user_id == user_id
                    ).first()

                    if not task:
                        results["failed"].append({
                            "task_id": task_id,
                            "reason": "Task not found or unauthorized"
                        })
                        continue

                    # Check for dependent records (e.g., reminders)
                    # that might prevent deletion
                    session.delete(task)
                    session.commit()
                    results["deleted"].append(task_id)
                    logger.info(f"Deleted task {task_id} for user {user_id}")

                except IntegrityError as e:
                    session.rollback()
                    results["failed"].append({
                        "task_id": task_id,
                        "reason": f"Constraint violation: {str(e)}"
                    })
                    logger.warning(f"Failed to delete task {task_id}: {str(e)}")

                except Exception as e:
                    session.rollback()
                    results["failed"].append({
                        "task_id": task_id,
                        "reason": f"Unexpected error: {str(e)}"
                    })
                    logger.error(f"Error deleting task {task_id}: {str(e)}")

        return {
            "success": True,
            "summary": {
                "total": len(task_ids),
                "deleted": len(results["deleted"]),
                "failed": len(results["failed"]),
                "success_rate": f"{(len(results['deleted'])/len(task_ids)*100):.1f}%"
            },
            "deleted_ids": results["deleted"],
            "failures": results["failed"]
        }

    @staticmethod
    def bulk_update_with_fallback(
        session: Session,
        user_id: str,
        updates: List[Dict[str, Any]],  # [{"id": 1, "completed": True}, ...]
        batch_size: int = 50
    ) -> Dict[str, Any]:
        """
        Update tasks with individual validation and error tracking.

        Example: Bulk mark 100 tasks as complete - track which ones failed.
        """
        results = {
            "updated": [],
            "failed": [],
            "validation_errors": []
        }

        for idx, update in enumerate(updates):
            task_id = update.get("id")

            try:
                # Validate input
                if not task_id:
                    results["validation_errors"].append({
                        "index": idx,
                        "reason": "Missing task_id"
                    })
                    continue

                # Fetch task
                task = session.query(Task).filter(
                    Task.id == task_id,
                    Task.user_id == user_id
                ).first()

                if not task:
                    results["failed"].append({
                        "task_id": task_id,
                        "index": idx,
                        "reason": "Task not found or unauthorized"
                    })
                    continue

                # Apply updates with validation
                if "title" in update:
                    title = update["title"]
                    if not title or len(title) > 200:
                        raise ValueError("Title must be 1-200 characters")
                    task.title = title

                if "completed" in update:
                    task.completed = update["completed"]

                if "description" in update:
                    desc = update["description"]
                    if desc and len(desc) > 1000:
                        raise ValueError("Description max 1000 characters")
                    task.description = desc

                # Update timestamp
                task.updated_at = datetime.utcnow()

                session.add(task)
                session.commit()
                session.refresh(task)

                results["updated"].append({
                    "task_id": task_id,
                    "title": task.title,
                    "completed": task.completed
                })

            except ValueError as e:
                session.rollback()
                results["validation_errors"].append({
                    "task_id": task_id,
                    "index": idx,
                    "reason": str(e)
                })

            except IntegrityError as e:
                session.rollback()
                results["failed"].append({
                    "task_id": task_id,
                    "index": idx,
                    "reason": f"Constraint violation: {str(e)}"
                })

            except Exception as e:
                session.rollback()
                results["failed"].append({
                    "task_id": task_id,
                    "index": idx,
                    "reason": f"Error: {str(e)}"
                })

        return {
            "success": True,
            "summary": {
                "total": len(updates),
                "updated": len(results["updated"]),
                "failed": len(results["failed"]),
                "validation_errors": len(results["validation_errors"])
            },
            "updated_tasks": results["updated"],
            "failures": results["failed"],
            "validation_errors": results["validation_errors"]
        }
```

### Strategy 2: Savepoint-Based Partial Rollback (For Mixed Operations)

**Pros**: Can mix successful commits with captured errors
**Cons**: More complex, database overhead from savepoints

```python
from sqlalchemy import event, text
from contextlib import contextmanager

class BulkTaskServiceWithSavepoints:
    """
    Use database savepoints for nested transaction control.
    Allows partial commits while maintaining parent transaction.
    """

    @staticmethod
    @contextmanager
    def savepoint(session: Session, name: str):
        """
        Context manager for savepoint-based error handling.

        Usage:
            with savepoint(session, "update_block_1"):
                # Update logic here
                # If error: rollback to savepoint, continue outer transaction
        """
        savepoint = session.begin_nested()
        try:
            yield savepoint
        except Exception:
            savepoint.rollback()
            raise

    @staticmethod
    def bulk_delete_with_savepoints(
        session: Session,
        user_id: str,
        task_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Delete tasks using savepoints for partial rollback.

        Outer transaction commits successful deletes even if some fail.
        Each delete is wrapped in a savepoint.
        """
        results = {
            "deleted": [],
            "failed": []
        }

        try:
            for task_id in task_ids:
                try:
                    with session.begin_nested():  # Create savepoint
                        task = session.query(Task).filter(
                            Task.id == task_id,
                            Task.user_id == user_id
                        ).with_for_update().first()  # Lock for safety

                        if not task:
                            raise ValueError("Task not found")

                        session.delete(task)
                        session.flush()  # Execute within savepoint
                        results["deleted"].append(task_id)

                except Exception as e:
                    # Savepoint automatically rolls back on exception
                    results["failed"].append({
                        "task_id": task_id,
                        "reason": str(e)
                    })

            # Outer transaction commits all successful deletes
            session.commit()

        except Exception as e:
            # If something catastrophic happens, rollback everything
            session.rollback()
            return {
                "success": False,
                "error": "Bulk operation failed catastrophically",
                "details": str(e)
            }

        return {
            "success": True,
            "summary": {
                "total": len(task_ids),
                "deleted": len(results["deleted"]),
                "failed": len(results["failed"])
            },
            "deleted_ids": results["deleted"],
            "failures": results["failed"]
        }
```

### Strategy 3: Batch Validation + Single Commit (For Strict Atomicity)

**Pros**: All-or-nothing guarantee, fastest for small batches
**Cons**: One failure rolls back everything

```python
class BulkTaskServiceAtomic:
    """
    Atomic bulk operations - all succeed or all rollback.
    Best for critical operations where consistency is paramount.
    """

    @staticmethod
    def bulk_delete_atomic(
        session: Session,
        user_id: str,
        task_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Delete multiple tasks atomically.
        All deletions succeed or all rollback.
        """

        # Phase 1: Validation (read-only, no transaction)
        validation_errors = []
        tasks_to_delete = []

        for task_id in task_ids:
            task = session.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user_id
            ).first()

            if not task:
                validation_errors.append({
                    "task_id": task_id,
                    "reason": "Not found or unauthorized"
                })
            else:
                tasks_to_delete.append(task)

        # Phase 2: Check constraints
        if len(tasks_to_delete) == 0:
            return {
                "success": False,
                "error": "No valid tasks to delete",
                "validation_errors": validation_errors
            }

        # Phase 3: Atomic deletion
        try:
            session.begin()  # Start explicit transaction

            for task in tasks_to_delete:
                session.delete(task)

            session.commit()  # All-or-nothing

            return {
                "success": True,
                "deleted": len(tasks_to_delete),
                "failed": len(validation_errors),
                "validation_errors": validation_errors
            }

        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "error": str(e),
                "deleted": 0,
                "failed": len(task_ids)
            }
```

---

## 2. SQLAlchemy Transaction Rollback Strategies

### Strategy Matrix

| Strategy | Atomicity | Speed | Error Handling | Use Case |
|----------|-----------|-------|-----------------|----------|
| **Item-level commits** | Per-item | Slow (N trips) | Excellent detail | User-facing, <1000 items |
| **Savepoints** | Partial | Medium | Good | Mixed success/failure acceptable |
| **Atomic batches** | All-or-nothing | Fast | Basic | Critical operations |
| **Batch with retry** | Per-batch | Medium | Good | Idempotent operations |

### Recommended: Hybrid Strategy (Item + Savepoint)

```python
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Callable, Any

class HybridBulkOperationService:
    """
    Combines item-level error tracking with savepoint efficiency.
    Balances performance and error visibility.
    """

    @staticmethod
    def bulk_operation(
        session: Session,
        user_id: str,
        operations: List[Dict[str, Any]],
        operation_fn: Callable,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Generic bulk operation handler with batching and savepoints.

        Args:
            session: Database session
            user_id: User context for isolation
            operations: List of operation dicts
            operation_fn: Callable that takes (session, user_id, op_dict)
            batch_size: Process this many items per batch
        """

        results = {
            "successful": [],
            "failed": [],
            "errors": []
        }

        # Process in batches
        for batch_idx in range(0, len(operations), batch_size):
            batch = operations[batch_idx:batch_idx + batch_size]

            # Each batch gets a savepoint
            try:
                with session.begin_nested():
                    for idx, op in enumerate(batch):
                        try:
                            result = operation_fn(session, user_id, op)
                            results["successful"].append({
                                "index": batch_idx + idx,
                                "operation": op,
                                "result": result
                            })

                        except ValueError as e:
                            # Validation error - record but continue
                            results["failed"].append({
                                "index": batch_idx + idx,
                                "operation": op,
                                "error_type": "validation",
                                "error": str(e)
                            })

                        except IntegrityError as e:
                            # Database constraint - record but continue
                            session.rollback()
                            results["failed"].append({
                                "index": batch_idx + idx,
                                "operation": op,
                                "error_type": "constraint",
                                "error": str(e)
                            })

                        except Exception as e:
                            # Unexpected error
                            results["failed"].append({
                                "index": batch_idx + idx,
                                "operation": op,
                                "error_type": "unexpected",
                                "error": str(e)
                            })

                    # Commit batch if all items successful
                    if not results["failed"]:
                        session.commit()

            except Exception as e:
                # Batch-level error
                results["errors"].append({
                    "batch": batch_idx,
                    "error": str(e)
                })

        # Final commit for outer transaction
        session.commit()

        return {
            "success": len(results["failed"]) == 0,
            "summary": {
                "total": len(operations),
                "successful": len(results["successful"]),
                "failed": len(results["failed"]),
                "success_rate": f"{(len(results['successful'])/len(operations)*100):.1f}%"
            },
            "results": results
        }
```

---

## 3. Progress Reporting for Long-Running Bulk Operations

### Challenge
Updating 500 tasks takes 10-60 seconds. How do we report progress to the user in real-time?

### Solution 1: WebSocket Progress Updates (Recommended)

```python
# File: backend/src/routes/bulk_operations.py
from fastapi import APIRouter, WebSocket, Depends, HTTPException
from fastapi.responses import JSONResponse
import asyncio
import json
from typing import List

router = APIRouter(prefix="/api/bulk", tags=["bulk"])

class ProgressReporter:
    """Track and broadcast progress for bulk operations."""

    def __init__(self, total: int):
        self.total = total
        self.processed = 0
        self.succeeded = 0
        self.failed = 0
        self.start_time = datetime.utcnow()

    def update(self, succeeded: bool = True):
        self.processed += 1
        if succeeded:
            self.succeeded += 1
        else:
            self.failed += 1

    def get_progress(self) -> Dict[str, Any]:
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        rate = self.processed / elapsed if elapsed > 0 else 0
        remaining = self.total - self.processed
        eta_seconds = remaining / rate if rate > 0 else 0

        return {
            "total": self.total,
            "processed": self.processed,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "percentage": round((self.processed / self.total) * 100, 1),
            "rate": round(rate, 2),  # items per second
            "elapsed_seconds": round(elapsed, 1),
            "eta_seconds": round(eta_seconds, 1)
        }

@router.websocket("/ws/bulk-delete/{operation_id}")
async def websocket_bulk_delete(
    websocket: WebSocket,
    operation_id: str
):
    """
    WebSocket endpoint for real-time progress updates.

    Client connects and receives progress messages every 500ms.
    """
    await websocket.accept()

    try:
        # Get operation from memory/cache
        operation = get_operation_from_cache(operation_id)

        if not operation:
            await websocket.send_json({
                "error": "Operation not found"
            })
            await websocket.close()
            return

        # Send progress until complete
        while operation.get("status") != "complete":
            progress = operation.get("reporter").get_progress()

            await websocket.send_json({
                "type": "progress",
                "progress": progress,
                "status": operation.get("status")
            })

            await asyncio.sleep(0.5)  # Update every 500ms

        # Send final result
        await websocket.send_json({
            "type": "complete",
            "result": operation.get("result"),
            "progress": operation.get("reporter").get_progress()
        })

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "error": str(e)
        })
    finally:
        await websocket.close()

@router.post("/delete-tasks")
async def bulk_delete_tasks(
    user_id: str,
    task_ids: List[int],
    session: Session = Depends(get_session),
    request: Request = Depends(verify_jwt)
) -> JSONResponse:
    """
    Initiate bulk delete operation.
    Returns operation_id for progress tracking via WebSocket.
    """

    if request.state.user_id != user_id:
        raise HTTPException(status_code=403)

    operation_id = generate_operation_id()
    reporter = ProgressReporter(len(task_ids))

    # Start background task
    operation = {
        "id": operation_id,
        "status": "processing",
        "reporter": reporter,
        "result": None
    }
    store_operation_in_cache(operation_id, operation)

    # Run bulk operation in background
    asyncio.create_task(
        _bulk_delete_background(
            operation_id, user_id, task_ids, session, reporter
        )
    )

    return {
        "operation_id": operation_id,
        "message": "Bulk delete started. Monitor progress via WebSocket.",
        "ws_url": f"/api/bulk/ws/bulk-delete/{operation_id}"
    }

async def _bulk_delete_background(
    operation_id: str,
    user_id: str,
    task_ids: List[int],
    session: Session,
    reporter: ProgressReporter
):
    """Background task for bulk deletion."""

    operation = get_operation_from_cache(operation_id)
    failed_ids = []

    try:
        for task_id in task_ids:
            try:
                task = session.query(Task).filter(
                    Task.id == task_id,
                    Task.user_id == user_id
                ).first()

                if task:
                    session.delete(task)
                    session.commit()
                    reporter.update(succeeded=True)
                else:
                    reporter.update(succeeded=False)
                    failed_ids.append(task_id)

            except Exception as e:
                session.rollback()
                reporter.update(succeeded=False)
                failed_ids.append(task_id)
                logger.error(f"Error deleting task {task_id}: {e}")

        # Store result
        operation["status"] = "complete"
        operation["result"] = {
            "deleted": reporter.succeeded,
            "failed": reporter.failed,
            "failed_ids": failed_ids
        }

    except Exception as e:
        operation["status"] = "error"
        operation["result"] = {"error": str(e)}
        logger.error(f"Bulk operation {operation_id} failed: {e}")
```

### Solution 2: Server-Sent Events (Alternative)

```python
from fastapi.responses import StreamingResponse

@router.post("/delete-tasks-streaming")
async def bulk_delete_streaming(
    user_id: str,
    task_ids: List[int],
    session: Session = Depends(get_session)
):
    """
    Stream progress updates using Server-Sent Events (SSE).
    Simpler than WebSocket for one-directional updates.
    """

    async def event_generator():
        reporter = ProgressReporter(len(task_ids))

        for idx, task_id in enumerate(task_ids):
            try:
                task = session.query(Task).filter(
                    Task.id == task_id,
                    Task.user_id == user_id
                ).first()

                if task:
                    session.delete(task)
                    session.commit()
                    reporter.update(succeeded=True)
                else:
                    reporter.update(succeeded=False)

            except Exception as e:
                session.rollback()
                reporter.update(succeeded=False)
                logger.error(f"Error: {e}")

            # Send progress every 10 items or at the end
            if (idx + 1) % 10 == 0 or idx == len(task_ids) - 1:
                progress = reporter.get_progress()
                yield f"data: {json.dumps(progress)}\n\n"
                await asyncio.sleep(0.1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### Solution 3: Status Polling (Simple but Less Efficient)

```python
import uuid
from datetime import datetime, timedelta

# In-memory operation cache (use Redis for production)
_operations_cache = {}

@router.post("/delete-tasks-async")
async def bulk_delete_async(
    user_id: str,
    task_ids: List[int]
) -> JSONResponse:
    """Start bulk operation, return operation_id for polling."""

    operation_id = str(uuid.uuid4())

    _operations_cache[operation_id] = {
        "user_id": user_id,
        "task_ids": task_ids,
        "status": "pending",
        "reporter": ProgressReporter(len(task_ids)),
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=1)
    }

    # Start background processing
    asyncio.create_task(
        _process_bulk_delete(operation_id, user_id, task_ids)
    )

    return {
        "operation_id": operation_id,
        "poll_url": f"/api/bulk/status/{operation_id}"
    }

@router.get("/status/{operation_id}")
async def get_operation_status(operation_id: str) -> JSONResponse:
    """Poll for operation status and progress."""

    operation = _operations_cache.get(operation_id)

    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")

    return {
        "operation_id": operation_id,
        "status": operation["status"],
        "progress": operation["reporter"].get_progress(),
        "result": operation.get("result")
    }

async def _process_bulk_delete(
    operation_id: str,
    user_id: str,
    task_ids: List[int]
):
    """Background bulk delete task."""

    operation = _operations_cache[operation_id]
    operation["status"] = "processing"

    try:
        for task_id in task_ids:
            # ... delete logic ...
            operation["reporter"].update(succeeded=True)

        operation["status"] = "complete"
        operation["result"] = {
            "summary": operation["reporter"].get_progress()
        }

    except Exception as e:
        operation["status"] = "failed"
        operation["result"] = {"error": str(e)}
```

---

## 4. Best Practices for Error Reporting

### Comprehensive Error Response Schema

```python
from pydantic import BaseModel
from enum import Enum

class ErrorType(str, Enum):
    VALIDATION = "validation"
    CONSTRAINT = "constraint"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    UNEXPECTED = "unexpected"

class TaskError(BaseModel):
    task_id: int
    index: int
    error_type: ErrorType
    message: str
    details: Optional[str] = None
    field: Optional[str] = None  # For validation errors

class BulkOperationResponse(BaseModel):
    """
    Structured response for bulk operations with detailed error info.
    """
    success: bool
    operation_id: str

    summary: Dict[str, int]  # {total, succeeded, failed, ...}

    successful_ids: List[int]
    errors: List[TaskError]  # Detailed per-item errors

    # Aggregated error statistics
    error_summary: Dict[str, int]  # {validation: 5, constraint: 3, ...}

    # Performance metrics
    duration_seconds: float
    items_per_second: float

class DetailedErrorReport(BaseModel):
    """For detailed error inspection."""
    error_type: ErrorType
    message: str
    context: Dict[str, Any]  # e.g., {"constraint": "foreign_key", "table": "tasks"}
    recoverable: bool
    suggested_action: Optional[str] = None
```

### Implementation

```python
class ErrorReporter:
    """Collect and format detailed operation errors."""

    def __init__(self):
        self.errors: List[TaskError] = []
        self.error_counts: Dict[str, int] = {}

    def add_validation_error(
        self,
        task_id: int,
        index: int,
        message: str,
        field: Optional[str] = None
    ):
        """Add validation error."""
        error = TaskError(
            task_id=task_id,
            index=index,
            error_type=ErrorType.VALIDATION,
            message=message,
            field=field
        )
        self.errors.append(error)
        self.error_counts[ErrorType.VALIDATION] = \
            self.error_counts.get(ErrorType.VALIDATION, 0) + 1

    def add_constraint_error(
        self,
        task_id: int,
        index: int,
        db_error: str
    ):
        """Add database constraint error."""

        # Parse constraint type from database error
        constraint_type = self._parse_constraint_type(db_error)

        error = TaskError(
            task_id=task_id,
            index=index,
            error_type=ErrorType.CONSTRAINT,
            message=f"Database constraint violation: {constraint_type}",
            details=db_error
        )
        self.errors.append(error)
        self.error_counts[ErrorType.CONSTRAINT] = \
            self.error_counts.get(ErrorType.CONSTRAINT, 0) + 1

    def add_authorization_error(
        self,
        task_id: int,
        index: int,
        user_id: str
    ):
        """Add authorization error."""
        error = TaskError(
            task_id=task_id,
            index=index,
            error_type=ErrorType.AUTHORIZATION,
            message=f"User {user_id} not authorized to modify task {task_id}"
        )
        self.errors.append(error)
        self.error_counts[ErrorType.AUTHORIZATION] = \
            self.error_counts.get(ErrorType.AUTHORIZATION, 0) + 1

    def _parse_constraint_type(self, db_error: str) -> str:
        """Parse constraint type from PostgreSQL error."""
        if "foreign key" in db_error.lower():
            return "foreign_key"
        elif "unique" in db_error.lower():
            return "unique"
        elif "not null" in db_error.lower():
            return "not_null"
        elif "check" in db_error.lower():
            return "check"
        else:
            return "unknown"

    def get_summary(self) -> Dict[str, int]:
        """Get error summary by type."""
        return dict(self.error_counts)

    def get_errors(self) -> List[TaskError]:
        """Get all errors."""
        return self.errors

    def has_errors(self) -> bool:
        """Check if any errors occurred."""
        return len(self.errors) > 0

# Usage in bulk operation
def bulk_update_tasks_with_detailed_reporting(
    session: Session,
    user_id: str,
    updates: List[Dict[str, Any]]
) -> BulkOperationResponse:
    """Example bulk update with comprehensive error reporting."""

    start_time = datetime.utcnow()
    reporter = ErrorReporter()
    successful_ids = []

    try:
        for idx, update in enumerate(updates):
            task_id = update.get("id")

            # Validation
            if not task_id:
                reporter.add_validation_error(
                    task_id=0,
                    index=idx,
                    message="Missing required field",
                    field="id"
                )
                continue

            if "title" in update:
                title = update["title"]
                if not title or len(title) > 200:
                    reporter.add_validation_error(
                        task_id=task_id,
                        index=idx,
                        message="Title must be 1-200 characters",
                        field="title"
                    )
                    continue

            # Authorization check
            task = session.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user_id
            ).first()

            if not task:
                reporter.add_authorization_error(
                    task_id=task_id,
                    index=idx,
                    user_id=user_id
                )
                continue

            # Update
            try:
                for key, value in update.items():
                    if key == "id":
                        continue
                    if hasattr(task, key):
                        setattr(task, key, value)

                task.updated_at = datetime.utcnow()
                session.add(task)
                session.commit()
                successful_ids.append(task_id)

            except IntegrityError as e:
                session.rollback()
                reporter.add_constraint_error(
                    task_id=task_id,
                    index=idx,
                    db_error=str(e)
                )
            except Exception as e:
                session.rollback()
                reporter.add_constraint_error(
                    task_id=task_id,
                    index=idx,
                    db_error=f"Unexpected error: {str(e)}"
                )

    finally:
        session.close()

    duration = (datetime.utcnow() - start_time).total_seconds()

    return BulkOperationResponse(
        success=not reporter.has_errors(),
        operation_id=generate_operation_id(),
        summary={
            "total": len(updates),
            "succeeded": len(successful_ids),
            "failed": len(reporter.get_errors())
        },
        successful_ids=successful_ids,
        errors=reporter.get_errors(),
        error_summary=reporter.get_summary(),
        duration_seconds=round(duration, 2),
        items_per_second=round(len(updates) / duration, 2) if duration > 0 else 0
    )
```

---

## 5. PostgreSQL-Specific Optimizations

### Connection Pooling Configuration

```python
# src/db.py - Updated for bulk operations
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import QueuePool
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=False,

    # Connection pooling for bulk operations
    poolclass=QueuePool,
    pool_size=10,          # Keep 10 connections ready
    max_overflow=20,       # Allow up to 30 total connections
    pool_pre_ping=True,    # Test connections before use
    pool_recycle=3600,     # Recycle after 1 hour

    # Performance tuning
    connect_args={
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "options": "-c statement_timeout=300000"  # 5-minute statement timeout
    }
)

def get_session_for_bulk():
    """Optimized session for bulk operations."""
    with Session(engine) as session:
        # Disable autoflush for performance
        session.autoflush = False
        yield session
```

### Batch Processing for 500+ Items

```python
class BulkTaskServiceOptimized:
    """Optimized for PostgreSQL bulk operations on 500+ items."""

    @staticmethod
    def bulk_delete_optimized(
        session: Session,
        user_id: str,
        task_ids: List[int],
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Delete 500+ tasks efficiently using batched deletes.

        For PostgreSQL:
        - Batch delete reduces transaction overhead
        - Lock contention is reduced
        - Better query plan caching
        """
        from sqlalchemy import delete

        results = {
            "deleted": 0,
            "failed": 0,
            "errors": []
        }

        # Process in batches
        for i in range(0, len(task_ids), batch_size):
            batch_ids = task_ids[i:i + batch_size]

            try:
                # Use bulk delete statement (more efficient than ORM delete)
                stmt = delete(Task).where(
                    Task.id.in_(batch_ids),
                    Task.user_id == user_id
                )

                result = session.execute(stmt)
                session.commit()

                results["deleted"] += result.rowcount

                # Log deletion
                logger.info(
                    f"Deleted {result.rowcount} tasks for user {user_id}"
                )

            except Exception as e:
                session.rollback()
                results["failed"] += len(batch_ids)
                results["errors"].append({
                    "batch": i // batch_size,
                    "error": str(e)
                })
                logger.error(f"Batch delete failed: {e}")

        return {
            "success": results["failed"] == 0,
            "summary": {
                "total": len(task_ids),
                "deleted": results["deleted"],
                "failed": results["failed"]
            },
            "errors": results["errors"]
        }

    @staticmethod
    def bulk_update_optimized(
        session: Session,
        user_id: str,
        updates: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Update 500+ tasks using bulk update statements.

        Alternative to ORM:
        - Uses SQL UPDATE for efficiency
        - Better for repetitive updates (e.g., mark all as complete)
        """
        from sqlalchemy import update

        # Example: Mark all tasks with certain IDs as complete
        task_ids = [u.get("id") for u in updates if u.get("id")]

        try:
            stmt = update(Task).where(
                Task.id.in_(task_ids),
                Task.user_id == user_id
            ).values(
                completed=True,
                updated_at=datetime.utcnow()
            )

            result = session.execute(stmt)
            session.commit()

            return {
                "success": True,
                "updated": result.rowcount,
                "total": len(task_ids)
            }

        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "error": str(e),
                "updated": 0,
                "total": len(task_ids)
            }
```

### Monitoring Long Operations

```python
import logging
from time import time

logger = logging.getLogger(__name__)

class BulkOperationMonitor:
    """Monitor bulk operations for performance and issues."""

    def __init__(self, operation_name: str, total_items: int):
        self.operation_name = operation_name
        self.total_items = total_items
        self.start_time = time()
        self.last_log_time = self.start_time
        self.processed_items = 0
        self.log_interval = 5  # Log every 5 seconds

    def record_item(self):
        """Record processing of one item."""
        self.processed_items += 1

        current_time = time()
        if current_time - self.last_log_time >= self.log_interval:
            elapsed = current_time - self.start_time
            rate = self.processed_items / elapsed
            remaining = self.total_items - self.processed_items
            eta = remaining / rate if rate > 0 else 0

            logger.info(
                f"[{self.operation_name}] "
                f"Progress: {self.processed_items}/{self.total_items} "
                f"({(self.processed_items/self.total_items*100):.1f}%) - "
                f"Rate: {rate:.1f} items/sec - "
                f"ETA: {eta:.0f}s"
            )

            self.last_log_time = current_time

    def finalize(self):
        """Log completion stats."""
        total_time = time() - self.start_time
        final_rate = self.total_items / total_time

        logger.info(
            f"[{self.operation_name}] Complete - "
            f"Processed {self.total_items} items in {total_time:.2f}s "
            f"({final_rate:.1f} items/sec)"
        )
```

---

## 6. Complete Example: Bulk Task Update Endpoint

```python
# File: backend/src/routes/bulk_tasks.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session
from datetime import datetime
from typing import List, Dict, Any

router = APIRouter(prefix="/api/bulk", tags=["bulk-tasks"])

class BulkTaskUpdateRequest(BaseModel):
    task_ids: List[int]
    updates: Dict[str, Any]  # {completed: true, priority: "high"}

@router.post("/tasks/update")
async def bulk_update_tasks(
    user_id: str,
    request_data: BulkTaskUpdateRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    session: Session = Depends(get_session)
) -> JSONResponse:
    """
    Bulk update multiple tasks with detailed error reporting.

    Request:
    {
      "task_ids": [1, 2, 3, ...],
      "updates": {"completed": true, "priority": "high"}
    }

    Response: Detailed summary with per-task error information
    """

    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Validate input
    if not request_data.task_ids:
        raise HTTPException(status_code=400, detail="No task IDs provided")

    if len(request_data.task_ids) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Maximum 1000 tasks per operation"
        )

    operation_id = generate_operation_id()
    monitor = BulkOperationMonitor("bulk_update", len(request_data.task_ids))
    reporter = ErrorReporter()
    successful_ids = []

    try:
        for idx, task_id in enumerate(request_data.task_ids):
            try:
                # Fetch task
                task = session.query(Task).filter(
                    Task.id == task_id,
                    Task.user_id == user_id
                ).first()

                if not task:
                    reporter.add_authorization_error(
                        task_id=task_id,
                        index=idx,
                        user_id=user_id
                    )
                    monitor.record_item()
                    continue

                # Validate updates
                if "title" in request_data.updates:
                    title = request_data.updates["title"]
                    if not title or len(title) > 200:
                        reporter.add_validation_error(
                            task_id=task_id,
                            index=idx,
                            message="Title must be 1-200 characters",
                            field="title"
                        )
                        monitor.record_item()
                        continue

                # Apply updates
                for key, value in request_data.updates.items():
                    if hasattr(task, key):
                        setattr(task, key, value)

                task.updated_at = datetime.utcnow()
                session.add(task)
                session.commit()
                session.refresh(task)

                successful_ids.append(task_id)
                monitor.record_item()

            except IntegrityError as e:
                session.rollback()
                reporter.add_constraint_error(
                    task_id=task_id,
                    index=idx,
                    db_error=str(e)
                )
                monitor.record_item()

            except Exception as e:
                session.rollback()
                reporter.add_constraint_error(
                    task_id=task_id,
                    index=idx,
                    db_error=f"Unexpected: {str(e)}"
                )
                monitor.record_item()

        monitor.finalize()

        duration = (datetime.utcnow() - monitor.start_time).total_seconds()

        return {
            "success": not reporter.has_errors(),
            "operation_id": operation_id,
            "summary": {
                "total": len(request_data.task_ids),
                "succeeded": len(successful_ids),
                "failed": len(reporter.get_errors()),
                "success_rate": f"{(len(successful_ids)/len(request_data.task_ids)*100):.1f}%"
            },
            "successful_ids": successful_ids,
            "errors": [e.dict() for e in reporter.get_errors()],
            "error_summary": reporter.get_summary(),
            "metrics": {
                "duration_seconds": round(duration, 2),
                "items_per_second": round(
                    len(request_data.task_ids) / duration, 2
                ) if duration > 0 else 0
            }
        }

    except Exception as e:
        logger.error(f"Bulk update operation {operation_id} failed: {e}")
        raise HTTPException(status_code=500, detail="Bulk operation failed")

@router.post("/tasks/delete")
async def bulk_delete_tasks(
    user_id: str,
    task_ids: List[int],
    request: Request,
    session: Session = Depends(get_session)
) -> JSONResponse:
    """Bulk delete with item-level error tracking."""

    if request.state.user_id != user_id:
        raise HTTPException(status_code=403)

    return BulkTaskService.bulk_delete_with_fallback(
        session, user_id, task_ids
    )
```

---

## Summary: Decision Matrix

| Requirement | Strategy | Implementation |
|-------------|----------|-----------------|
| **Partial failures OK** | Item-level try-catch | Loop + session.rollback() per item |
| **Atomicity required** | Validate then atomic commit | Two-phase with all-or-nothing |
| **Mixed success/failure** | Savepoints | session.begin_nested() wrapper |
| **Progress tracking** | WebSocket + background task | asyncio + message broadcasting |
| **500+ items** | Batched bulk statements | session.execute(delete().where(...)) |
| **Detailed errors** | ErrorReporter class | Categorize by type (validation, constraint, etc.) |

---

## References

- [SQLAlchemy 2.0 ORM DML Documentation](https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html)
- [Designing Robust Transaction Management with Nested Transactions and Savepoints](https://hevalhazalkurt.com/blog/designing-robust-transaction-management-with-nested-transactions-and-savepoints-in-sqlalchemy/)
- [Unit of Work in SQLAlchemy: How to Handle Transactions Efficiently](https://medium.com/pythoneers/unit-of-work-in-sqlalchemy-how-to-handle-transactions-efficiently-in-2025-7a705cfdcb89)
- [Mastering Transaction Boundaries in Python with SQLAlchemy](https://cevheri.medium.com/mastering-transaction-boundaries-in-python-with-sqlalchemy-and-clean-architecture-principles-10361aaf715e)
- [SQLModel Tutorial: Create Rows](https://sqlmodel.tiangolo.com/tutorial/insert/)
- [SQLModel Tutorial: Update Data](https://sqlmodel.tiangolo.com/tutorial/update/)
- [FastAPI Concurrency and async/await](https://fastapi.tiangolo.com/async/)
- [Handling Long-Running Tasks in FastAPI](https://www.datasciencebyexample.com/2023/08/26/handling-long-running-tasks-in-fastapi-python/)
- [PostgreSQL Batch Operations](https://www.alibabacloud.com/blog/how-does-postgresql-implement-batch-update-deletion-and-insertion_596030)
