# Reusable Skills & Intelligence

This document captures reusable patterns, components, and intelligence for the Todo Console Application project and similar Python CLI applications.

---

## Table of Contents

1. [Architectural Patterns](#architectural-patterns)
2. [CLI Command Patterns](#cli-command-patterns)
3. [Validation Patterns](#validation-patterns)
4. [Error Handling Patterns](#error-handling-patterns)
5. [Display Formatting Patterns](#display-formatting-patterns)
6. [Data Management Patterns](#data-management-patterns)
7. [Development Workflow](#development-workflow)
8. [Testing Patterns](#testing-patterns)

---

## Architectural Patterns

### Three-Layer Clean Architecture

**Pattern**: Separate concerns into models, services, and interface layers

```
src/
├── models/          # Domain entities (Task)
├── services/        # Business logic (TodoManager)
└── cli/            # User interface (TodoCLI, display)
```

**Benefits**:
- Clear separation of concerns
- Easy to test each layer independently
- Business logic independent of UI
- Easy to swap CLI for GUI/API later

**Usage**:
- Models: Pure data structures with validation
- Services: CRUD operations and business rules
- CLI: User interaction and display formatting

---

## CLI Command Patterns

### Interactive Prompt Pattern

**Pattern**: Commands trigger interactive prompts rather than taking arguments

```python
def handle_command(self):
    """Handle interactive command with prompts."""
    print()
    value = input("Enter value: ").strip()

    # Validate
    if not value:
        print("❌ Error: Value cannot be empty.")
        return

    # Execute
    try:
        result = self.service.do_operation(value)
        print(f"✅ Success message! (ID: {result.id})")
    except ValueError as e:
        print(f"❌ Error: {str(e)}")
```

**Benefits**:
- User-friendly for beginners
- Clear step-by-step guidance
- Validation at each step
- Consistent error messaging

**When to Use**: Simple CLI apps where users prefer guided interaction

---

### Command Router Pattern

**Pattern**: Central command dispatcher with handler methods

```python
def run(self):
    """Main command loop."""
    while self.running:
        try:
            command = input("> ").strip().lower()

            if not command:
                continue

            if command in ["exit", "quit", "q"]:
                self.handle_exit()
            elif command == "add":
                self.handle_add()
            elif command == "list":
                self.handle_list()
            # ... more commands
            else:
                print(f"❌ Error: Unknown command '{command}'.")
        except KeyboardInterrupt:
            self.handle_exit()
        except Exception as e:
            print(f"❌ Error: {str(e)}")
```

**Benefits**:
- Centralized error handling
- Easy to add new commands
- Graceful KeyboardInterrupt handling
- Consistent command processing

---

## Validation Patterns

### Model-Level Validation with Dataclass

**Pattern**: Use `__post_init__` for validation in dataclasses

```python
from dataclasses import dataclass

@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False

    def __post_init__(self):
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")
        if len(self.description) > 1000:
            raise ValueError("Task description cannot exceed 1000 characters")
```

**Benefits**:
- Validation runs automatically on instantiation
- Consistent validation across all creation paths
- Clear error messages
- Type hints for IDE support

**When to Use**: Any domain model that needs validation

---

### CLI-Level Pre-Validation

**Pattern**: Validate user input before passing to service layer

```python
def handle_add(self):
    """Handle the 'add' command."""
    title = input("Enter task title: ").strip()

    # Pre-validate
    if not title:
        print("❌ Error: Title cannot be empty. Please provide a task title.")
        return

    if len(title) > 200:
        print("❌ Error: Title too long (max 200 characters).")
        return

    # Proceed to service layer
    try:
        task = self.manager.add_task(title, description)
        print(f"✅ Task added successfully! (ID: {task.id})")
    except ValueError as e:
        print(f"❌ Error: {str(e)}")
```

**Benefits**:
- Fast feedback to user
- User-friendly error messages
- Prevents invalid data from reaching service layer
- Double validation (defense in depth)

---

## Error Handling Patterns

### Graceful Error Messages

**Pattern**: Convert technical errors to user-friendly messages

```python
try:
    result = self.service.operation(data)
    print(f"✅ Success message!")
except ValueError as e:
    print(f"❌ Error: {str(e)}")
except KeyError:
    print(f"❌ Error: Item not found. Use 'list' to see all items.")
except Exception as e:
    print(f"❌ Error: Something went wrong. {str(e)}")
```

**Guidelines**:
- Use ✅ for success, ❌ for errors
- Provide actionable guidance ("Use 'list' to see...")
- Keep messages concise and clear
- Log technical details if needed (not shown to user)

---

### Safe ID Lookup Pattern

**Pattern**: Validate entity existence before operations

```python
def get_task(self, task_id: int) -> Optional[Task]:
    """Get task by ID, return None if not found."""
    return self._tasks.get(task_id)

def operation(self, task_id: int) -> bool:
    """Perform operation on task."""
    task = self.get_task(task_id)
    if not task:
        return False

    # Perform operation
    task.completed = True
    return True
```

**Benefits**:
- Explicit None handling
- Clear success/failure indication
- No exceptions for expected cases (not found)
- Caller can provide appropriate error message

---

## Display Formatting Patterns

### List Formatter Pattern

**Pattern**: Dedicated formatter functions for consistent display

```python
def format_task_list(tasks: List[Task]) -> str:
    """Format task list with consistent styling."""
    if not tasks:
        return "\n=== Your Tasks ===\n\nNo tasks yet. Use 'add' to create your first task!\n"

    output = ["\n=== Your Tasks ===\n"]

    for task in tasks:
        status_icon = "✅" if task.completed else "❌"
        output.append(f"[{task.id}] {status_icon} {task.title}")
        output.append(f"    Description: {task.description or '(No description)'}")
        output.append(f"    Status: {'Complete' if task.completed else 'Incomplete'}")
        output.append("")  # Blank line

    # Summary
    completed = sum(1 for t in tasks if t.completed)
    output.append(f"Total: {len(tasks)} tasks ({completed} complete, {len(tasks)-completed} incomplete)")

    return "\n".join(output)
```

**Benefits**:
- Consistent formatting across the app
- Easy to update styling in one place
- Handles empty state gracefully
- Provides summary information

---

### Box Drawing Pattern

**Pattern**: Use Unicode box-drawing characters for visual appeal

```python
help_text = """
╔═══════════════════════════════════════╗
║     Todo Application Help             ║
╚═══════════════════════════════════════╝

Available Commands:
  ...
"""
```

**Characters**:
- `╔ ╗ ╚ ╝` - Corners
- `═` - Horizontal line
- `║` - Vertical line
- `✅ ❌` - Status indicators
- `👋` - Friendly icons

---

## Data Management Patterns

### In-Memory Dict Storage

**Pattern**: Use dictionary for O(1) lookups with separate ID counter

```python
class TodoManager:
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(self, title: str, description: str = "") -> Task:
        task_id = self._next_id
        task = Task(id=task_id, title=title, description=description)
        self._tasks[task_id] = task
        self._next_id += 1
        return task

    def list_tasks(self) -> List[Task]:
        return list(self._tasks.values())
```

**Benefits**:
- O(1) lookups by ID
- Sequential user-friendly IDs
- Simple and efficient for small datasets
- Easy to replace with database later

**When to Use**: Prototypes, small applications, in-memory caching

---

### Sequential ID Generation

**Pattern**: Simple counter for user-friendly IDs

```python
def add_entity(self, data) -> Entity:
    entity_id = self._next_id
    entity = Entity(id=entity_id, **data)
    self._storage[entity_id] = entity
    self._next_id += 1  # Never decrement, even on delete
    return entity
```

**Benefits**:
- Predictable, easy to remember IDs
- No ID reuse (important for data integrity)
- Simple to implement
- Works well for user-facing applications

---

## Development Workflow

### Spec-Driven Development Flow

**Workflow**:
1. Create constitution (principles and standards)
2. Write feature specification (requirements, user stories)
3. Create implementation plan (architecture, decisions)
4. Break down into tasks (actionable, testable)
5. Implement incrementally (MVP first, then enhancements)
6. Document with PHRs (prompt history records)

**Commands**:
```bash
/sp.constitution  # Create project constitution
/sp.specify       # Create feature specification
/sp.plan          # Create implementation plan
/sp.tasks         # Generate task breakdown
/sp.implement     # Execute tasks
/sp.phr           # Create prompt history record
```

---

### Incremental Delivery Strategy

**Pattern**: Build in phases with independent testing

```
Phase 1: Setup → Foundation ready
Phase 2: Foundational → Core models and services
Phase 3: User Story 1 (MVP) → Test independently → DEPLOY ✅
Phase 4: User Story 2 → Test independently → DEPLOY ✅
Phase 5: User Story 3 → Test independently → DEPLOY ✅
Phase 6: User Story 4 → Test independently → DEPLOY ✅
Phase 7: Polish → Final refinements
```

**Benefits**:
- Early value delivery
- Independent testing of features
- Reduced risk
- Clear milestones

---

## Testing Patterns

### Manual Testing Checklist

**Pattern**: Document test scenarios for each user story

```markdown
## User Story 1 - Add and View Tasks

**Test Scenario 1**: Add task with title and description
- Launch app
- Type 'add'
- Enter title: "Buy groceries"
- Enter description: "Milk, eggs, bread"
- Verify: "✅ Task added successfully! (ID: 1)"

**Test Scenario 2**: View tasks
- Type 'list'
- Verify: Shows [1] with title, description, ❌ status

**Test Scenario 3**: Empty task list
- Launch fresh app
- Type 'list'
- Verify: "No tasks yet. Use 'add' to create your first task!"
```

**When to Use**: Small projects where tests are optional (per constitution)

---

### Edge Case Testing

**Common Edge Cases**:
- Empty strings
- Maximum length strings (200 chars title, 1000 chars description)
- Unicode characters (emoji, non-Latin scripts)
- Special characters (quotes, newlines, tabs)
- Large datasets (100+ items)
- Boundary conditions (ID: 0, negative IDs)
- Concurrent operations (if applicable)

---

## Reusable Code Snippets

### Generic CRUD Manager Template

```python
from typing import Dict, List, Optional, TypeVar, Generic

T = TypeVar('T')

class CRUDManager(Generic[T]):
    """Generic CRUD manager for in-memory storage."""

    def __init__(self):
        self._items: Dict[int, T] = {}
        self._next_id: int = 1

    def create(self, item: T) -> T:
        item.id = self._next_id
        self._items[self._next_id] = item
        self._next_id += 1
        return item

    def read(self, item_id: int) -> Optional[T]:
        return self._items.get(item_id)

    def read_all(self) -> List[T]:
        return list(self._items.values())

    def update(self, item_id: int, updated_item: T) -> bool:
        if item_id not in self._items:
            return False
        self._items[item_id] = updated_item
        return True

    def delete(self, item_id: int) -> bool:
        if item_id not in self._items:
            return False
        del self._items[item_id]
        return True
```

---

## Agent Skills

### When to Create Skills

Create reusable skills when:
1. **Pattern repeats 3+ times** across features
2. **Complex workflow** that can be templated
3. **Domain-specific knowledge** worth capturing
4. **Cross-cutting concern** (logging, validation, formatting)

### Potential Skills for This Project

1. **CLI Command Generator**: Template for creating new CLI commands
2. **CRUD Operation Generator**: Template for add/update/delete operations
3. **Validation Rule Generator**: Template for common validation patterns
4. **Display Formatter**: Template for consistent list/detail displays
5. **Interactive Prompt Builder**: Template for multi-step user input flows

---

## Best Practices Summary

### Code Quality
- ✅ Use type hints everywhere
- ✅ Follow PEP 8 style guide
- ✅ Keep functions small and focused
- ✅ Validate at boundaries (user input, model creation)
- ✅ Use dataclasses for domain models

### Architecture
- ✅ Separate models, services, and interface
- ✅ Keep business logic in service layer
- ✅ Make UI layer thin (just formatting and routing)
- ✅ Design for replaceability (CLI → GUI/API)

### User Experience
- ✅ Provide clear, actionable error messages
- ✅ Use visual indicators (✅ ❌ 👋)
- ✅ Show help text for unknown commands
- ✅ Handle Ctrl+C gracefully
- ✅ Include summaries (task counts, etc.)

### Development Process
- ✅ Start with constitution and spec
- ✅ Build MVP first, then enhance
- ✅ Test each user story independently
- ✅ Document decisions in ADRs
- ✅ Create PHRs for learning

---

## References

- **Constitution**: `.specify/memory/constitution.md`
- **Specification**: `specs/001-todo-console-app/spec.md`
- **Implementation Plan**: `specs/001-todo-console-app/plan.md`
- **Task Breakdown**: `specs/001-todo-console-app/tasks.md`
- **Code Standards**: PEP 8, Clean Architecture principles

---

**Last Updated**: 2025-12-07
**Version**: 1.0.0
**Maintainer**: Todo App Development Team
