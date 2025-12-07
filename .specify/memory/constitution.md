<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.0.1
- Modified principles: None
- Added sections: Added UV package manager to In Scope (Section 4)
- Removed sections: None
- Templates alignment:
  ✅ plan-template.md - Constitution Check section ready for gates
  ✅ spec-template.md - Functional requirements aligned with constitution
  ✅ tasks-template.md - Task categorization aligns with testing and structure principles
- Follow-up TODOs: None - all placeholders filled
-->

# In-Memory Command Line Todo Application Constitution

## 1. Project Title

**In-Memory Command Line Todo Application**

## 2. Purpose

The purpose of this project is to build a clean, reliable command-line todo application that allows users to manage tasks entirely in memory using Spec-Driven Development with Claude Code and Spec-Kit Plus.

This project demonstrates structured thinking, clean Python architecture, and disciplined specification-first development.

## 3. Project Objectives

The system SHALL:

- Allow users to add tasks with a title and description
- Allow users to view all tasks with clear status indicators
- Allow users to update existing tasks
- Allow users to delete tasks by unique ID
- Allow users to mark tasks as complete or incomplete

## 4. Scope

### In Scope

- Command-line based user interface
- In-memory task storage (no database or files)
- Python 3.13+ compatibility
- UV package manager for dependency management
- Spec-Kit Plus workflow
- Claude Code integration

### Out of Scope

- No graphical user interface
- No task persistence after program exit
- No external databases
- No user authentication

## Core Principles

### I. Specification-First Development (NON-NEGOTIABLE)

Every feature MUST begin with a specification before any code is written.

**Rules:**
- All features MUST start with a specification file in `/specs/[feature]/spec.md`
- Specifications MUST be reviewed and approved before implementation begins
- Code implementation MUST match the approved specification
- Changes to specifications MUST be documented before corresponding code changes

**Rationale:** Ensures disciplined development, reduces rework, maintains clear intent, and provides traceable requirements for all functionality.

### II. Clean Architecture

Code MUST follow clean architecture principles with clear separation of concerns.

**Rules:**
- Models MUST be separated from business logic
- Business logic (services) MUST be separated from presentation (CLI)
- Dependencies MUST flow inward (CLI → Services → Models)
- No circular dependencies allowed
- Each module MUST have a single, well-defined responsibility

**Rationale:** Promotes maintainability, testability, and code reusability. Makes the codebase easier to understand and modify.

### III. Code Quality Standards

All code MUST be modular, readable, and consistently formatted.

**Rules:**
- MUST follow PEP 8 style guidelines for Python code
- Naming MUST be descriptive and consistent (snake_case for functions/variables, PascalCase for classes)
- Functions MUST have clear, single purposes
- Magic numbers MUST be replaced with named constants
- Code MUST be self-documenting; comments only where logic isn't self-evident

**Rationale:** Ensures code is maintainable and accessible to all developers, reducing cognitive load and onboarding time.

### IV. User-Friendly Error Handling

Error messages MUST be clear, actionable, and user-friendly.

**Rules:**
- Error messages MUST provide clear, actionable information
- Error messages MUST NOT expose internal implementation details
- Invalid inputs MUST be caught and explained to the user
- System MUST handle edge cases gracefully without crashes

**Rationale:** Improves user experience and reduces support burden by making errors self-explanatory.

### V. Test-Driven Development (TDD)

Testing is encouraged but NOT mandatory for this project.

**Guidelines:**
- If tests are written, they should be written BEFORE implementation
- Tests should follow Red-Green-Refactor cycle when used
- Test coverage should focus on critical business logic
- Integration tests should verify user journeys work end-to-end

**Rationale:** While TDD provides quality benefits, this project prioritizes learning Spec-Driven Development. Testing is optional to reduce complexity for educational purposes.

### VI. Simplicity and YAGNI

Start simple and only add complexity when explicitly needed.

**Rules:**
- MUST implement only features in the current specification
- MUST NOT add "nice to have" features without specification
- MUST NOT over-engineer solutions
- MUST NOT create abstractions until patterns emerge from real usage

**Rationale:** Prevents premature optimization, reduces development time, and keeps codebase maintainable.

## 5. Functional Requirements

The application MUST provide the following capabilities:

### FR-001: Add Task
- Accept a title (required, non-empty string)
- Accept a description (optional string)
- Assign a unique ID automatically
- Store task in memory

### FR-002: View Tasks
- Display all tasks in a structured, readable list
- Show task ID, title, description, and completion status
- Use visual indicators for completion status (✅ for complete, ❌ for incomplete)
- Handle empty task list gracefully

### FR-003: Update Task
- Allow changing title and/or description using task ID
- Validate that task ID exists
- Provide clear error if task not found
- Preserve completion status during update

### FR-004: Delete Task
- Remove a task using its unique ID
- Validate that task ID exists
- Provide clear error if task not found
- Handle deletion gracefully

### FR-005: Mark Task Status
- Toggle task between completed and incomplete states
- Validate that task ID exists
- Provide clear error if task not found
- Update status indicator immediately

## 6. Non-Functional Requirements

### Performance
- All operations MUST complete in under 100ms for up to 1000 tasks
- Memory usage MUST be reasonable for in-memory storage

### Reliability
- Application MUST NOT crash on invalid inputs
- Application MUST handle edge cases (empty lists, invalid IDs, etc.)

### Usability
- CLI MUST be intuitive and easy to use
- Help text MUST be available for all commands
- Output MUST be formatted for readability

### Code Quality
- Code MUST follow clean architecture principles
- Code MUST be modular and readable
- Naming MUST be consistent
- No code duplication

## 7. Development Methodology

This project SHALL follow Spec-Driven Development using:

- **Claude Code**: AI-powered development assistant
- **Spec-Kit Plus**: Specification-driven workflow toolkit

**Process:**
1. Every feature MUST start with a specification file
2. Specifications MUST be reviewed before coding
3. Implementation MUST follow approved specifications
4. All work MUST be recorded in `/history/prompts/` as PHRs (Prompt History Records)

## 8. Project Structure

The project MUST follow this structure:

```text
todo/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point and CLI interface
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py          # Task data model
│   ├── services/
│   │   ├── __init__.py
│   │   └── todo_manager.py  # Business logic for CRUD operations
│   └── cli/
│       ├── __init__.py
│       └── interface.py     # User interaction and display formatting
├── tests/                   # Optional - only if tests are written
│   ├── __init__.py
│   ├── test_task.py
│   ├── test_todo_manager.py
│   └── test_cli.py
├── .specify/
│   ├── memory/
│   │   └── constitution.md  # This file
│   ├── templates/           # Spec-Kit Plus templates
│   └── scripts/             # Automation scripts
├── history/
│   ├── prompts/             # Prompt History Records
│   └── adr/                 # Architecture Decision Records
├── specs/                   # Feature specifications
├── CLAUDE.md                # Claude Code agent instructions
└── README.md                # Project documentation
```

**Structure Rationale:**
- `src/models/`: Pure data models with no business logic
- `src/services/`: Business logic and operations on models
- `src/cli/`: User interface and presentation layer
- Clear dependency flow: CLI → Services → Models

## 9. Acceptance Criteria

The project is considered complete when:

- All 5 basic features (Add, View, Update, Delete, Mark Status) work correctly
- The console UI operates without crashes
- Code matches the specifications
- All required deliverables exist in the repository
- Code follows clean architecture principles
- Error handling is user-friendly
- Project structure matches the constitution

## 10. Governance

### Amendment Process

All changes to system behavior MUST be reflected in new specification files and added to `/history/prompts/` before code changes.

**Amendment Rules:**
- Constitution changes require documentation of rationale
- All amendments MUST update the version number and Last Amended date
- Breaking changes to principles require MAJOR version increment
- New principles or sections require MINOR version increment
- Clarifications and wording fixes require PATCH version increment

### Versioning Policy

Constitution versions follow semantic versioning: MAJOR.MINOR.PATCH

- **MAJOR**: Backward-incompatible governance or principle removals/redefinitions
- **MINOR**: New principle/section added or materially expanded guidance
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

### Compliance Review

- All PRs and code reviews MUST verify compliance with this constitution
- Any complexity violations MUST be justified in the implementation plan
- Constitution supersedes all other practices and guidelines

### Architectural Decisions

Architecturally significant decisions (those meeting all three criteria below) MUST be documented:

1. **Impact**: Long-term consequences on framework, data model, API, security, or platform
2. **Alternatives**: Multiple viable options were considered
3. **Scope**: Cross-cutting and influences overall system design

When such decisions are identified, create an ADR using `/sp.adr [decision-title]` command.

---

**Version**: 1.0.1 | **Ratified**: 2025-12-07 | **Last Amended**: 2025-12-07
