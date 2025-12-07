# Quickstart Guide: In-Memory Todo Console Application

**Feature**: 001-todo-console-app
**Date**: 2025-12-07
**Purpose**: Developer setup and getting started guide

## Prerequisites

- **Python**: 3.13 or higher
- **UV**: Python package manager
- **Git**: For cloning repository
- **Operating System**: Linux, macOS, or Windows

## Installation

### 1. Install UV

**Linux/macOS**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell)**:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify Installation**:
```bash
uv --version
# Should output: uv X.X.X
```

### 2. Clone Repository

```bash
git clone <repository-url>
cd todo
```

### 3. Verify Branch

```bash
git branch
# Should show: * 001-todo-console-app
```

## Project Setup

### Initialize UV Project

```bash
# Sync dependencies (will create virtual environment)
uv sync

# Verify Python version
uv run python --version
# Should output: Python 3.13.X
```

## Project Structure

```
todo/
├── src/                     # Source code
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py          # Task data model
│   ├── services/
│   │   ├── __init__.py
│   │   └── todo_manager.py  # Business logic
│   └── cli/
│       ├── __init__.py
│       ├── interface.py     # Command handlers
│       └── display.py       # Output formatting
├── tests/                   # Tests (optional)
├── specs/                   # Feature specifications
│   └── 001-todo-console-app/
│       ├── spec.md          # Requirements
│       ├── plan.md          # Implementation plan
│       ├── data-model.md    # Data structures
│       ├── quickstart.md    # This file
│       └── contracts/
│           └── cli-commands.md
├── .specify/                # Spec-Kit Plus
│   └── memory/
│       └── constitution.md  # Project governance
├── history/                 # Prompt history
├── pyproject.toml           # UV configuration
├── uv.lock                  # UV lock file
├── CLAUDE.md                # Claude Code instructions
└── README.md                # User documentation
```

## Running the Application

### Development Mode

```bash
# Run directly with UV
uv run python src/main.py
```

**Expected Output**:
```
╔═══════════════════════════════════════╗
║     In-Memory Todo Application        ║
╚═══════════════════════════════════════╝

Current tasks: 0 (0 complete, 0 incomplete)

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

### Quick Commands

```bash
# Install UV project
uv sync

# Run application
uv run python src/main.py

# Run tests (if implemented)
uv run pytest

# Format code
uv run black src/

# Type check
uv run mypy src/

# Lint code
uv run ruff check src/
```

## Basic Usage

### Adding Your First Task

```
> add
Enter task title: Buy groceries
Enter description (optional): milk, eggs, bread
✅ Task added successfully! (ID: 1)
```

Or directly:
```
> add "Buy groceries" "milk, eggs, bread"
✅ Task added successfully! (ID: 1)
```

### Viewing Tasks

```
> list
=== Your Tasks ===

[1] ❌ Buy groceries
    Description: milk, eggs, bread
    Status: Incomplete

Total: 1 tasks (0 complete, 1 incomplete)
```

### Marking Complete

```
> complete 1
✅ Task #1 marked as complete!
```

### Getting Help

```
> help
=== Todo Application Help ===
[... help text ...]
```

### Exiting

```
> exit
👋 Thanks for using Todo App! Your tasks will be lost (in-memory only).
Goodbye!
```

## Development Workflow

### 1. Understand the Feature

Read the spec first:
```bash
cat specs/001-todo-console-app/spec.md
```

### 2. Review Architecture

Check implementation plan:
```bash
cat specs/001-todo-console-app/plan.md
cat specs/001-todo-console-app/data-model.md
```

### 3. Implement User Stories

Follow priority order:
1. **P1**: Add and View Tasks (MVP)
2. **P2**: Mark Tasks Complete
3. **P3**: Update Tasks
4. **P4**: Delete Tasks

### 4. Test Manually

For each user story, verify acceptance scenarios from spec.md.

### 5. (Optional) Write Tests

If following TDD approach:
```bash
# Create test file
touch tests/test_task.py

# Run tests
uv run pytest tests/
```

## Configuration

### pyproject.toml

```toml
[project]
name = "todo"
version = "0.1.0"
description = "In-memory command-line todo application"
requires-python = ">=3.13"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.0.0",
    "mypy>=1.5.0",
    "ruff>=0.0.290",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Installing Dev Dependencies

```bash
# Install all dev dependencies
uv sync --all-extras

# Or install individually
uv add --dev pytest black mypy ruff
```

## Troubleshooting

### UV Not Found

**Problem**: `uv: command not found`

**Solution**:
```bash
# Reload shell
source ~/.bashrc  # or ~/.zshrc

# Or add to PATH manually
export PATH="$HOME/.cargo/bin:$PATH"
```

### Python Version Mismatch

**Problem**: Python 3.13+ not available

**Solution**:
```bash
# UV can install Python versions
uv python install 3.13

# Use specific Python version
uv python use 3.13
```

### Module Not Found

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Run from project root
cd /path/to/todo

# Ensure UV environment is active
uv sync

# Run with UV
uv run python src/main.py
```

### Import Errors

**Problem**: `ImportError: attempted relative import beyond top-level package`

**Solution**:
Ensure you're running from project root and using absolute imports:
```python
# Good
from src.models.task import Task

# Bad
from ..models.task import Task
```

## Testing Guide

### Manual Testing Checklist

For each user story, verify all acceptance scenarios:

**US1 - Add and View Tasks**:
- [ ] Add task with title and description
- [ ] Add task with title only
- [ ] View multiple tasks
- [ ] View empty task list

**US2 - Mark Complete**:
- [ ] Mark task as complete
- [ ] Mark task as incomplete (toggle)
- [ ] Try invalid task ID

**US3 - Update**:
- [ ] Update title only
- [ ] Update description only
- [ ] Update both fields
- [ ] Verify completion status preserved

**US4 - Delete**:
- [ ] Delete existing task
- [ ] Try deleting invalid ID
- [ ] Verify other tasks remain

### Automated Testing (Optional)

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src tests/

# Run specific test file
uv run pytest tests/test_task.py

# Run with verbose output
uv run pytest -v
```

## Code Quality

### Formatting

```bash
# Format all Python files
uv run black src/ tests/

# Check formatting
uv run black --check src/ tests/
```

### Linting

```bash
# Run ruff linter
uv run ruff check src/ tests/

# Auto-fix issues
uv run ruff check --fix src/ tests/
```

### Type Checking

```bash
# Run mypy type checker
uv run mypy src/
```

## Next Steps

1. **Read Specification**: Review `specs/001-todo-console-app/spec.md`
2. **Review Architecture**: Check `plan.md` and `data-model.md`
3. **Generate Tasks**: Run `/sp.tasks` to create task breakdown
4. **Start Implementation**: Begin with User Story 1 (P1)
5. **Test Incrementally**: Verify each user story independently

## Resources

- **UV Documentation**: https://github.com/astral-sh/uv
- **Python 3.13 Docs**: https://docs.python.org/3.13/
- **PEP 8 Style Guide**: https://peps.python.org/pep-0008/
- **Constitution**: `.specify/memory/constitution.md`
- **Spec Templates**: `.specify/templates/`

## Support

For issues or questions:
1. Check `specs/001-todo-console-app/` documentation
2. Review constitution principles in `.specify/memory/constitution.md`
3. Consult `CLAUDE.md` for Claude Code integration

---

**Quickstart Status**: ✅ Complete
**Prerequisites**: UV, Python 3.13+, Git
**Ready to**: Start development
