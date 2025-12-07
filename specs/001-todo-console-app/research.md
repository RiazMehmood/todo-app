# Research: In-Memory Todo Console Application

**Feature**: 001-todo-console-app
**Date**: 2025-12-07
**Purpose**: Document technical research and decision-making for implementation plan

## Research Tasks

### 1. UV Package Manager Investigation

**Question**: How should we use UV for Python 3.13+ project management?

**Research Findings**:
- UV is a fast, modern Python package manager written in Rust
- Supports pyproject.toml standard (PEP 621)
- Provides dependency resolution and virtual environment management
- Compatible with Python 3.13+
- Commands: `uv init`, `uv add`, `uv sync`, `uv run`

**Decision**: Use UV for all dependency management
**Rationale**:
- Constitution Section 4 explicitly requires UV
- Faster than pip/poetry
- Modern tooling aligns with Python 3.13+
- Simple pyproject.toml configuration

**Alternatives Considered**:
- pip + venv: Rejected (slower, manual venv management)
- poetry: Rejected (UV is specified in constitution)

### 2. In-Memory Storage Strategy

**Question**: What data structure should we use for in-memory task storage?

**Research Findings**:
- Options: List, Dict, OrderedDict, custom data structure
- Performance requirements: <100ms for 1,000 tasks
- Access patterns: Lookup by ID (frequent), iterate all (frequent)

**Decision**: Use `Dict[int, Task]` for task storage
**Rationale**:
- O(1) lookup by task ID (meets performance requirements)
- O(n) iteration for list_all() (acceptable for 1,000 tasks)
- Simple, built-in data structure
- Natural mapping: ID → Task

**Alternatives Considered**:
- List: Rejected (O(n) lookup, need to search for ID)
- OrderedDict: Rejected (unnecessary, dict preserves insertion order in Python 3.7+)
- Custom class: Rejected (YAGNI, dict is sufficient)

**Implementation Details**:
```python
class TodoManager:
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1
```

### 3. ID Generation Strategy

**Question**: How should we generate unique task IDs?

**Research Findings**:
- Requirements: Unique, sequential, user-friendly
- Options: Auto-increment, UUID, timestamp, hash

**Decision**: Sequential integer counter starting from 1
**Rationale**:
- User-friendly (easy to type "complete 1", "delete 3")
- Guaranteed unique in single-session
- Simple to implement and debug
- Matches user mental model

**Alternatives Considered**:
- UUID: Rejected (overkill, not user-friendly for CLI)
- Timestamp: Rejected (not guaranteed unique, harder to type)
- Hash: Rejected (unnecessary complexity)

**Implementation Details**:
```python
def add_task(self, title: str, description: str = "") -> Task:
    task_id = self._next_id
    self._next_id += 1
    task = Task(id=task_id, title=title, description=description)
    self._tasks[task_id] = task
    return task
```

**Edge Case**: Deleted task IDs are not reused (simpler, prevents confusion)

### 4. CLI Interface Pattern

**Question**: What CLI interaction pattern provides the best user experience?

**Research Findings**:
- Pattern options:
  1. Argument-based: `python main.py add "Task title"`
  2. Interactive menu: Numbered options, prompt for input
  3. Hybrid: Menu + direct commands
  4. REPL-style: Command loop

**Decision**: Interactive REPL-style with direct commands
**Rationale**:
- Meets SC-006 (self-documenting, no external docs needed)
- Meets SC-008 (95% first-time user success)
- Supports both novice (menu) and power (direct) users
- Natural for session-based application

**Alternatives Considered**:
- Pure argument-based: Rejected (requires external docs, harder for beginners)
- Pure menu: Rejected (slower for experienced users)

**Implementation Pattern**:
```
=== Todo Application ===
1. Add task
2. List tasks
3. Update task
4. Delete task
5. Mark complete/incomplete
6. Help
7. Exit

Enter command number or type command (e.g., 'add', 'list'):
>
```

### 5. Error Handling Strategy

**Question**: How should we structure error handling to meet FR-011?

**Research Findings**:
- Requirements: Clear, actionable, no internal details
- Error categories: Invalid ID, empty title, invalid command, unexpected errors

**Decision**: Custom error messages with user guidance
**Rationale**:
- Meets Principle IV (User-Friendly Error Handling)
- Each error provides next action
- No stack traces exposed to user

**Implementation Pattern**:
```python
# Bad
raise ValueError("Task not found")

# Good
if task_id not in self._tasks:
    return f"Error: Task #{task_id} not found. Use 'list' to see all tasks."
```

**Error Message Templates**:
- Invalid ID: "Error: Task #{id} not found. Use 'list' to see all tasks."
- Empty title: "Error: Title cannot be empty. Please provide a task title."
- Invalid command: "Error: Unknown command '{cmd}'. Type 'help' for available commands."
- Unexpected: "Error: Something went wrong. Please try again."

### 6. Data Model Design

**Question**: Should Task be a dataclass, NamedTuple, or regular class?

**Research Findings**:
- Options: dataclass, NamedTuple, regular class, dict
- Requirements: Type safety, immutability (partial), simplicity

**Decision**: Use `@dataclass` with default values
**Rationale**:
- Built-in Python 3.7+ feature
- Automatic __init__, __repr__, __eq__
- Type annotations (PEP 8 compliance)
- Mutable (allows updating title/description)
- Clean, minimal code

**Alternatives Considered**:
- NamedTuple: Rejected (immutable, can't update tasks)
- Regular class: Rejected (boilerplate for __init__, __repr__)
- Dict: Rejected (no type safety, error-prone)

**Implementation**:
```python
from dataclasses import dataclass

@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
```

### 7. Output Formatting

**Question**: How should we format task list output for readability?

**Research Findings**:
- Requirements: Visual indicators (✅/❌), structured format, readable
- Options: Table, list, JSON, custom format

**Decision**: Formatted list with visual indicators
**Rationale**:
- Meets FR-004, FR-005 (visual indicators required)
- Console-friendly (no table libraries needed)
- Clear visual hierarchy

**Output Format**:
```
=== Your Tasks ===

[1] ❌ Buy groceries
    Description: milk, eggs, bread

[2] ✅ Write report
    Description: Q4 financial summary

[3] ❌ Call dentist
    (No description)
```

### 8. Input Validation Strategy

**Question**: What validation rules should we enforce?

**Research Findings**:
- FR-014: Reject empty/whitespace-only titles
- FR-010: Validate task IDs exist
- Edge cases: Special characters, unicode, very long strings

**Decision**: Whitelist validation with explicit checks
**Rationale**:
- Security: Prevent unexpected input
- User experience: Clear error messages
- Performance: Fast validation

**Validation Rules**:
```python
# Title validation
def validate_title(title: str) -> bool:
    return bool(title and title.strip())

# ID validation
def validate_task_id(task_id: int) -> bool:
    return task_id in self._tasks

# Length limits (from assumptions)
MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000
```

## Technology Stack Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Language | Python 3.13+ | Constitution requirement |
| Package Manager | UV | Constitution requirement, modern tooling |
| Data Model | @dataclass | Built-in, type-safe, minimal boilerplate |
| Storage | Dict[int, Task] | O(1) lookup, simple, performant |
| CLI Pattern | Interactive REPL | User-friendly, self-documenting |
| Testing | pytest (optional) | Industry standard, optional per constitution |
| Formatting | PEP 8 | Constitution requirement |

## Best Practices Applied

1. **YAGNI**: No external dependencies beyond UV
2. **Clean Architecture**: Three-layer separation (models/services/CLI)
3. **Type Safety**: Type hints throughout (PEP 484)
4. **Error Handling**: User-friendly messages, no exceptions exposed
5. **Performance**: O(1) operations for all ID-based lookups
6. **Simplicity**: Built-in data structures, no frameworks

## Open Questions

None remaining - all technical decisions finalized.

## References

- PEP 8: Python Style Guide
- PEP 621: Storing project metadata in pyproject.toml
- UV Documentation: https://github.com/astral-sh/uv
- Python dataclasses: https://docs.python.org/3/library/dataclasses.html

---

**Research Status**: ✅ Complete
**All decisions documented**: Yes
**Ready for**: Phase 1 design artifacts
