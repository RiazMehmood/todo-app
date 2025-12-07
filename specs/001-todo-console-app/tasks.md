---
description: "Task list for In-Memory Todo Console Application"
---

# Tasks: In-Memory Todo Console Application

**Input**: Design documents from `/specs/001-todo-console-app/`
**Prerequisites**: plan.md (completed), spec.md (completed), data-model.md (completed), contracts/ (completed)

**Tests**: Tests are OPTIONAL per constitution Principle V. No test tasks included unless explicitly requested.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (per plan.md)
- Paths shown below follow project structure from plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project root directory structure (src/, tests/, specs/)
- [x] T002 Initialize UV project with pyproject.toml for Python 3.13+
- [x] T003 [P] Create src/__init__.py as empty module marker
- [x] T004 [P] Create src/models/__init__.py as empty module marker
- [x] T005 [P] Create src/services/__init__.py as empty module marker
- [x] T006 [P] Create src/cli/__init__.py as empty module marker
- [x] T007 [P] Create tests/__init__.py as empty module marker (optional structure)
- [x] T008 Create README.md with project overview and setup instructions
- [x] T009 Create .gitignore for Python (include __pycache__, *.pyc, .venv/, uv.lock)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T010 Create Task model dataclass in src/models/task.py with id, title, description, completed attributes
- [x] T011 Add Task model validation in __post_init__ (non-empty title, max 200 chars title, max 1000 chars description)
- [x] T012 Create TodoManager class in src/services/todo_manager.py with _tasks dict and _next_id counter
- [x] T013 Implement TodoManager.__init__() to initialize empty task dict and ID counter at 1

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to add tasks with title/description and view all tasks in a formatted list

**Independent Test**: Launch app, add multiple tasks with titles and descriptions, view the complete list. Should show all tasks with IDs, titles, descriptions, and incomplete status by default.

### Implementation for User Story 1

- [x] T014 [P] [US1] Implement TodoManager.add_task(title, description) method in src/services/todo_manager.py
- [x] T015 [P] [US1] Implement TodoManager.list_tasks() method to return all tasks as list in src/services/todo_manager.py
- [x] T016 [US1] Create display formatter in src/cli/display.py for task list output with ✅/❌ indicators
- [x] T017 [US1] Implement format_task_list() function in src/cli/display.py to show ID, title, description, status
- [x] T018 [US1] Handle empty task list case in display.py (show friendly "No tasks yet" message)
- [x] T019 [US1] Create CLI interface class in src/cli/interface.py with command loop
- [x] T020 [US1] Implement 'add' command handler in src/cli/interface.py (prompt for title and description)
- [x] T021 [US1] Implement 'list' command handler in src/cli/interface.py calling list_tasks()
- [x] T022 [US1] Add input validation for 'add' command (reject empty titles, enforce length limits)
- [x] T023 [US1] Add error handling for 'add' command with user-friendly messages
- [x] T024 [US1] Create main.py entry point that instantiates TodoManager and CLI interface
- [x] T025 [US1] Implement main application loop in main.py with menu display
- [x] T026 [US1] Add 'help' command handler in src/cli/interface.py showing all available commands
- [x] T027 [US1] Add 'exit' command handler in src/cli/interface.py to quit application

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently as a working MVP todo app

---

## Phase 4: User Story 2 - Mark Complete (Priority: P2)

**Goal**: Enable users to toggle task completion status between complete and incomplete

**Independent Test**: Add tasks, mark some as complete, verify status indicators change from ❌ to ✅ and vice versa.

### Implementation for User Story 2

- [x] T028 [US2] Implement TodoManager.toggle_completion(task_id) method in src/services/todo_manager.py
- [x] T029 [US2] Add task ID validation in toggle_completion() (check task exists, return False if not found)
- [x] T030 [US2] Implement 'complete' command handler in src/cli/interface.py
- [x] T031 [US2] Add interactive prompt for task ID in 'complete' command
- [x] T032 [US2] Add error handling for invalid task IDs with message "Task #X not found. Use 'list' to see all tasks."
- [x] T033 [US2] Add success messages for toggle ("Task #X marked as complete/incomplete")
- [x] T034 [US2] Update format_task_list() in display.py to ensure ✅/❌ indicators reflect current status

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - full task tracking

---

## Phase 5: User Story 3 - Update Tasks (Priority: P3)

**Goal**: Enable users to modify task titles and descriptions while preserving completion status

**Independent Test**: Add tasks, update their titles and descriptions, verify changes are saved and completion status is unchanged.

### Implementation for User Story 3

- [x] T035 [US3] Implement TodoManager.update_task(task_id, title, description) method in src/services/todo_manager.py
- [x] T036 [US3] Add task ID validation in update_task() (check task exists, return False if not found)
- [x] T037 [US3] Ensure update_task() preserves completion status when updating fields
- [x] T038 [US3] Add title validation in update_task() (non-empty if provided, max 200 chars)
- [x] T039 [US3] Add description validation in update_task() (max 1000 chars if provided)
- [x] T040 [US3] Implement 'update' command handler in src/cli/interface.py
- [x] T041 [US3] Add interactive prompts for task ID, new title, new description in 'update' command
- [x] T042 [US3] Show current values when prompting for updates (e.g., "Current title: X")
- [x] T043 [US3] Allow skipping fields (press Enter to keep current value)
- [x] T044 [US3] Add error handling for invalid task IDs in update command
- [x] T045 [US3] Add error handling for validation failures (empty title, too long, etc.)
- [x] T046 [US3] Add success message "Task #X updated successfully"

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - full editing capability

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P4)

**Goal**: Enable users to remove tasks from the list by ID

**Independent Test**: Add multiple tasks, delete specific ones by ID, verify they no longer appear in list and other tasks remain.

### Implementation for User Story 4

- [x] T047 [US4] Implement TodoManager.delete_task(task_id) method in src/services/todo_manager.py
- [x] T048 [US4] Add task ID validation in delete_task() (check task exists, return False if not found)
- [x] T049 [US4] Ensure deleted task IDs are not reused (ID counter only increments)
- [x] T050 [US4] Implement 'delete' command handler in src/cli/interface.py
- [x] T051 [US4] Add interactive prompt for task ID in 'delete' command
- [x] T052 [US4] Add confirmation prompt before deletion ("Are you sure? (y/n)")
- [x] T053 [US4] Handle confirmation response (delete only if 'y', cancel if 'n')
- [x] T054 [US4] Add error handling for invalid task IDs in delete command
- [x] T055 [US4] Add success message "Task #X deleted successfully"
- [x] T056 [US4] Add cancellation message "Deletion cancelled" if user says no

**Checkpoint**: All user stories should now be independently functional - complete CRUD operations

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T057 [P] Add menu display with numbered options (1. Add task, 2. List tasks, etc.) in src/cli/interface.py
- [ ] T058 [P] Implement menu-driven input (accept both numbers and command names)
- [ ] T059 [P] Add task count summary to menu ("Current tasks: X (Y complete, Z incomplete)")
- [ ] T060 [P] Add box drawing characters to menu for visual appeal (╔═══╗ style)
- [ ] T061 [P] Improve error messages across all commands for consistency
- [ ] T062 [P] Add input sanitization for special characters and unicode support
- [ ] T063 [P] Add command aliases ('quit', 'q' for exit)
- [ ] T064 [P] Update README.md with usage examples and command reference
- [ ] T065 [P] Add quickstart section to README.md with UV installation steps
- [ ] T066 [P] Test application with 100+ tasks to verify performance (<2s for list)
- [ ] T067 [P] Test application with edge cases (empty titles, very long strings, unicode)
- [ ] T068 Verify all success criteria from spec.md are met
- [ ] T069 Verify all acceptance scenarios from spec.md pass
- [ ] T070 Final code review for PEP 8 compliance and clean architecture

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (uses existing Task model)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories (uses existing TodoManager)
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - No dependencies on other stories (uses existing TodoManager)

### Within Each User Story

- Models before services (but Task model is in Foundational phase)
- Services before CLI
- Core implementation before polish
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003-T009)
- Task model (T010-T011) can run in parallel with TodoManager skeleton (T012-T013)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within US1: T014-T015 can run in parallel, T016-T018 can run in parallel
- All Polish tasks marked [P] can run in parallel (T057-T067)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# After Foundational phase, launch these in parallel:
Task T014: Implement add_task() method
Task T015: Implement list_tasks() method

# Then these in parallel:
Task T016: Create display formatter
Task T017: Implement format_task_list()
Task T018: Handle empty list case

# Then continue with CLI tasks in sequence (since they depend on each other)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T013)
3. Complete Phase 3: User Story 1 (T014-T027)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready (you have a working todo app!)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! ✅)
3. Add User Story 2 → Test independently → Deploy/Demo (Task tracking ✅)
4. Add User Story 3 → Test independently → Deploy/Demo (Full editing ✅)
5. Add User Story 4 → Test independently → Deploy/Demo (Complete CRUD ✅)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T014-T027)
   - Developer B: User Story 2 (T028-T034)
   - Developer C: User Story 3 (T035-T046)
   - Developer D: User Story 4 (T047-T056)
3. Stories complete and integrate independently
4. All developers work on Polish together

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Summary

- **Total Tasks**: 70
- **Setup (Phase 1)**: 9 tasks
- **Foundational (Phase 2)**: 4 tasks (BLOCKING)
- **User Story 1 (P1)**: 14 tasks (MVP)
- **User Story 2 (P2)**: 7 tasks
- **User Story 3 (P3)**: 12 tasks
- **User Story 4 (P4)**: 10 tasks
- **Polish (Phase 7)**: 14 tasks
- **Parallel Opportunities**: 20 tasks can run in parallel
- **Independent Stories**: All 4 user stories are independently implementable after Foundational phase

---

## Suggested MVP Scope

**Minimum Viable Product (MVP)**: Complete through User Story 1 (P1)

This gives you a working todo application that can:
- Add tasks with titles and descriptions
- View all tasks in a formatted list
- See task IDs and completion status
- Use help command to learn available commands
- Exit the application gracefully

**Estimated MVP Tasks**: 27 tasks (Setup + Foundational + US1)

**Recommended First Milestone**: T001-T027 (MVP)
**Recommended Second Milestone**: T028-T034 (Add task completion tracking)
**Full Feature Set**: T001-T070 (Complete CRUD + Polish)
