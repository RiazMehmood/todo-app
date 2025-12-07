# CLI Commands Contract: In-Memory Todo Console Application

**Feature**: 001-todo-console-app
**Date**: 2025-12-07
**Purpose**: Define command-line interface contract and interaction patterns

## Command Overview

| Command | Purpose | User Story | Priority |
|---------|---------|------------|----------|
| `add` | Add new task | US1 (P1) | Critical |
| `list` | View all tasks | US1 (P1) | Critical |
| `complete` | Toggle completion status | US2 (P2) | High |
| `update` | Modify task details | US3 (P3) | Medium |
| `delete` | Remove task | US4 (P4) | Medium |
| `help` | Show command help | All | High |
| `exit` | Quit application | All | Critical |

## Command Specifications

### 1. ADD Command

**Purpose**: Create a new task (FR-001, FR-002)

**Syntax**:
```
add <title> [description]
```

**Parameters**:
- `title` (required): Task title (max 200 chars, non-empty)
- `description` (optional): Task description (max 1000 chars)

**Interactive Mode**:
```
> add
Enter task title: Buy groceries
Enter description (optional): milk, eggs, bread
✅ Task added successfully! (ID: 1)
```

**Direct Mode**:
```
> add "Buy groceries" "milk, eggs, bread"
✅ Task added successfully! (ID: 1)

> add "Buy groceries"
✅ Task added successfully! (ID: 1)
```

**Success Response**:
```
✅ Task added successfully! (ID: {id})
```

**Error Responses**:
```
❌ Error: Title cannot be empty. Please provide a task title.
❌ Error: Title too long (max 200 characters).
❌ Error: Description too long (max 1000 characters).
```

**User Story**: US1 (Add and View Tasks - P1)

---

### 2. LIST Command

**Purpose**: Display all tasks (FR-004, FR-005, FR-012)

**Syntax**:
```
list
```

**Parameters**: None

**Success Response (Tasks Exist)**:
```
=== Your Tasks ===

[1] ❌ Buy groceries
    Description: milk, eggs, bread
    Status: Incomplete

[2] ✅ Write report
    Description: Q4 financial summary
    Status: Complete

[3] ❌ Call dentist
    (No description)
    Status: Incomplete

Total: 3 tasks (1 complete, 2 incomplete)
```

**Success Response (Empty List)**:
```
=== Your Tasks ===

No tasks yet. Use 'add' to create your first task!
```

**Error Responses**: None (always succeeds)

**User Story**: US1 (Add and View Tasks - P1)

---

### 3. COMPLETE Command

**Purpose**: Toggle task completion status (FR-006)

**Syntax**:
```
complete <task_id>
```

**Parameters**:
- `task_id` (required): Task identifier (positive integer)

**Interactive Mode**:
```
> complete
Enter task ID: 1
✅ Task #1 marked as complete!
```

**Direct Mode**:
```
> complete 1
✅ Task #1 marked as complete!

> complete 1
✅ Task #1 marked as incomplete!
```

**Success Response**:
```
✅ Task #{id} marked as complete!
✅ Task #{id} marked as incomplete!
```

**Error Responses**:
```
❌ Error: Task #{id} not found. Use 'list' to see all tasks.
❌ Error: Invalid task ID. Please provide a number.
```

**User Story**: US2 (Mark Tasks Complete - P2)

---

### 4. UPDATE Command

**Purpose**: Modify task title and/or description (FR-007, FR-008)

**Syntax**:
```
update <task_id> [new_title] [new_description]
```

**Parameters**:
- `task_id` (required): Task identifier
- `new_title` (optional): New task title
- `new_description` (optional): New description

**Interactive Mode**:
```
> update
Enter task ID: 1
Current title: Buy groceries
Enter new title (press Enter to keep current): Buy more groceries
Current description: milk, eggs, bread
Enter new description (press Enter to keep current): milk, eggs, bread, cheese
✅ Task #1 updated successfully!
```

**Direct Mode**:
```
> update 1 "Buy more groceries" "milk, eggs, bread, cheese"
✅ Task #1 updated successfully!

> update 1 "Buy more groceries"
✅ Task #1 updated successfully!
```

**Success Response**:
```
✅ Task #{id} updated successfully!
```

**Error Responses**:
```
❌ Error: Task #{id} not found. Use 'list' to see all tasks.
❌ Error: Title cannot be empty.
❌ Error: Title too long (max 200 characters).
❌ Error: Description too long (max 1000 characters).
```

**Notes**:
- Completion status is preserved (FR-008)
- Task ID cannot be changed
- At least one field (title or description) must be updated

**User Story**: US3 (Update Tasks - P3)

---

### 5. DELETE Command

**Purpose**: Remove task from list (FR-009)

**Syntax**:
```
delete <task_id>
```

**Parameters**:
- `task_id` (required): Task identifier

**Interactive Mode**:
```
> delete
Enter task ID: 3
Are you sure you want to delete task #3? (y/n): y
✅ Task #3 deleted successfully!
```

**Direct Mode**:
```
> delete 3
Are you sure you want to delete task #3? (y/n): y
✅ Task #3 deleted successfully!
```

**Success Response**:
```
✅ Task #{id} deleted successfully!
```

**Error Responses**:
```
❌ Error: Task #{id} not found. Use 'list' to see all tasks.
❌ Error: Invalid task ID. Please provide a number.
❌ Deletion cancelled.
```

**Notes**:
- Confirmation prompt prevents accidental deletion
- Deleted task IDs are not reused

**User Story**: US4 (Delete Tasks - P4)

---

### 6. HELP Command

**Purpose**: Display available commands (FR-013)

**Syntax**:
```
help
```

**Parameters**: None

**Success Response**:
```
=== Todo Application Help ===

Available Commands:

  add <title> [description]
    Add a new task with optional description
    Example: add "Buy groceries" "milk, eggs, bread"

  list
    Show all tasks with their status
    Example: list

  complete <task_id>
    Toggle task completion status
    Example: complete 1

  update <task_id> [title] [description]
    Update task title and/or description
    Example: update 1 "New title" "New description"

  delete <task_id>
    Delete a task (with confirmation)
    Example: delete 3

  help
    Show this help message
    Example: help

  exit
    Quit the application
    Example: exit

Tips:
  - Task IDs are shown in square brackets [1], [2], etc.
  - Use 'list' to see your tasks and their IDs
  - Completed tasks show ✅, incomplete tasks show ❌
  - All commands can be typed directly or selected from menu
```

**Error Responses**: None (always succeeds)

**User Story**: All (supports SC-006)

---

### 7. EXIT Command

**Purpose**: Quit the application

**Syntax**:
```
exit
quit
q
```

**Parameters**: None

**Success Response**:
```
👋 Thanks for using Todo App! Your tasks will be lost (in-memory only).
Goodbye!
```

**Error Responses**: None (always succeeds)

**Notes**:
- Aliases: `exit`, `quit`, `q`
- No data persistence (FR-015)

**User Story**: All

---

## Menu Interface

### Main Menu

```
╔═══════════════════════════════════════╗
║     In-Memory Todo Application        ║
╚═══════════════════════════════════════╝

Current tasks: 3 (1 complete, 2 incomplete)

[1] Add task
[2] List tasks
[3] Mark complete/incomplete
[4] Update task
[5] Delete task
[6] Help
[7] Exit

Enter command number or type command:
>
```

### Menu Behavior

- **Option Selection**: User can type number (1-7) or command name
- **Invalid Input**: Show error and re-display menu
- **After Command**: Return to menu (except exit)
- **Ctrl+C**: Same as exit command

## Input Parsing Rules

### General Rules

1. Commands are case-insensitive: `ADD` = `add` = `Add`
2. Leading/trailing whitespace is ignored
3. Multiple spaces between arguments treated as single space
4. Quotes group multi-word arguments: `"Buy groceries"` = single argument
5. Empty commands (just Enter) re-display menu

### Argument Parsing

**With Quotes**:
```
add "Buy groceries" "milk, eggs, bread"
→ title: "Buy groceries"
→ description: "milk, eggs, bread"
```

**Without Quotes**:
```
add Buy groceries
→ title: "Buy"
→ description: "groceries"
```

**Interactive Prompts**:
```
> add
Enter task title: Buy groceries
→ title: "Buy groceries" (full line)
```

## Error Handling Contract

### Error Message Format

```
❌ Error: {specific_problem}. {helpful_suggestion}.
```

### Error Categories

| Error Type | Message Pattern | Example |
|------------|----------------|---------|
| Invalid ID | Task #{id} not found. Use 'list' to see all tasks. | ❌ Error: Task #99 not found. Use 'list' to see all tasks. |
| Empty Title | Title cannot be empty. Please provide a task title. | ❌ Error: Title cannot be empty. Please provide a task title. |
| Too Long | {field} too long (max {limit} characters). | ❌ Error: Title too long (max 200 characters). |
| Invalid Command | Unknown command '{cmd}'. Type 'help' for available commands. | ❌ Error: Unknown command 'foo'. Type 'help' for available commands. |
| Invalid Input | Invalid {input_type}. {expected_format}. | ❌ Error: Invalid task ID. Please provide a number. |

### Success Message Format

```
✅ {action} successful! [additional info]
```

## Performance Contract

| Operation | Max Response Time | Constraint |
|-----------|------------------|------------|
| add | 100ms | For any task count |
| list | 2s | For up to 100 tasks |
| list | 1s | For up to 1,000 tasks |
| complete | 100ms | For any task count |
| update | 100ms | For any task count |
| delete | 100ms | For any task count |
| help | 100ms | Always |
| exit | 500ms | Always |

## Accessibility

- **Visual Indicators**: Use unicode symbols (✅ ❌) for status
- **Clear Hierarchy**: Headers, spacing, indentation
- **Colorblind-Friendly**: Don't rely solely on color
- **Screen Reader**: Text-based output works with screen readers

## Testing Contract

### Acceptance Test Scenarios

Each command must pass its acceptance scenarios from spec.md:

- **US1**: Add + View (FR-001, FR-002, FR-004, FR-005)
- **US2**: Mark Complete (FR-006)
- **US3**: Update (FR-007, FR-008)
- **US4**: Delete (FR-009)

### Edge Case Testing

- Empty title: Reject with error
- Invalid ID: Reject with error
- Very long input: Reject with error
- Unicode characters: Accept and display correctly
- Empty task list: Show friendly message
- Rapid commands: All succeed within performance limits

---

**Contract Status**: ✅ Complete
**All commands specified**: Yes
**Error handling defined**: Yes
**Ready for**: Implementation
