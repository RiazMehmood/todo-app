---
id: 0006
title: Implement User Story 3 - Update Tasks
stage: green
date: 2025-12-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-todo-console-app
branch: master
user: riaz
command: manual
labels: ["user-story-3", "update-command", "phase-5", "crud", "edit-functionality"]
links:
  spec: specs/001-todo-console-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/services/todo_manager.py
  - src/cli/interface.py
  - specs/001-todo-console-app/tasks.md
tests:
  - No tests (optional per constitution Principle V)
---

## Prompt

good move to next step

## Response snapshot

Implemented User Story 3 (Update Tasks functionality) - 12 tasks completed (T035-T046).

**User Story 3 Implementation**

1. **TodoManager Enhancement (src/services/todo_manager.py:67-104)**
   - Implemented `update_task(task_id, title, description)` method
   - Task ID validation (returns False if task not found)
   - Preserves completion status when updating fields
   - Title validation: non-empty if provided, max 200 characters
   - Description validation: max 1000 characters if provided
   - Uses Optional[str] parameters to distinguish between "skip" and "update to empty"
   - Raises ValueError for validation failures

2. **CLI Update Command Handler (src/cli/interface.py:76-118)**
   - Implemented `handle_update()` method with interactive prompts
   - Prompts for task ID with numeric validation
   - Shows current title and description before prompting
   - Interactive prompts: "Enter new title (or press Enter to keep current)"
   - Allows skipping fields - pressing Enter keeps current value
   - Handles case where no changes are made (shows info message)
   - Full error handling for:
     - Invalid task IDs (not found)
     - Non-numeric input
     - Validation failures (empty title, too long, etc.)
   - Success message: "Task #X updated successfully"

3. **Help Text Update (src/cli/interface.py:141-144)**
   - Added 'update' command documentation
   - Explained field skipping behavior (press Enter)
   - Added tip about preserving completion status

4. **Command Router Update (src/cli/interface.py:193-194)**
   - Added 'update' command recognition
   - Integrated into main command loop

All tasks marked as completed [x] in specs/001-todo-console-app/tasks.md.

## Outcome

- ✅ Impact: Users can now edit task titles and descriptions while preserving completion status. Combined with User Stories 1-2, the app provides full CRUD operations except Delete (add, view, complete, update). The interactive prompt pattern maintains UX consistency.
- 🧪 Tests: No tests implemented (optional per constitution Principle V)
- 📁 Files: 3 files modified (todo_manager.py, interface.py, tasks.md)
- 🔁 Next prompts: Implement User Story 4 (Delete Tasks - T047-T056), or test User Story 3 functionality, or proceed to Polish phase
- 🧠 Reflection: Optional parameters pattern (title=None, description=None) elegantly handles partial updates. Showing current values before prompting improves UX. Completion status preservation is critical for data integrity. The "no changes made" info message prevents confusion when user skips all fields.

## Evaluation notes (flywheel)

- Failure modes observed: None - all 12 tasks completed successfully
- Graders run and results (PASS/FAIL): No automated graders run
- Prompt variant (if applicable): Standard implementation following spec and tasks
- Next experiment (smallest change to try): Test update functionality with edge cases (updating only title, only description, both, neither). Verify completion status truly preserved after updates. Test validation edge cases (exactly 200 char title, 1000 char description).
