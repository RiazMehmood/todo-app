# In-Memory Todo Console Application

A clean, reliable command-line todo application that manages tasks entirely in memory using Spec-Driven Development with Claude Code and Spec-Kit Plus.

## Features

- ✅ Add tasks with title and description
- ✅ View all tasks with clear status indicators
- ✅ Update existing tasks
- ✅ Delete tasks by ID
- ✅ Mark tasks as complete/incomplete

## Prerequisites

- **Python**: 3.13 or higher
- **UV**: Python package manager

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

### 2. Clone and Setup

```bash
git clone <repository-url>
cd todo
uv sync
```

## Usage

### Run the Application

```bash
uv run python src/main.py
```

### Basic Commands

```
add <title> [description]    Add a new task
list                         View all tasks
complete <id>                Toggle task completion
update <id> [title] [desc]   Update task details
delete <id>                  Delete a task
help                         Show available commands
exit                         Quit application
```

### Example Session

```
> add "Buy groceries" "milk, eggs, bread"
✅ Task added successfully! (ID: 1)

> list
=== Your Tasks ===

[1] ❌ Buy groceries
    Description: milk, eggs, bread
    Status: Incomplete

> complete 1
✅ Task #1 marked as complete!

> exit
👋 Thanks for using Todo App!
```

## Project Structure

```
todo/
├── src/
│   ├── models/         # Data models
│   ├── services/       # Business logic
│   └── cli/            # Command-line interface
├── tests/              # Tests (optional)
├── specs/              # Feature specifications
├── pyproject.toml      # UV configuration
└── README.md           # This file
```

## Development

### Code Quality

```bash
# Format code
uv run black src/

# Lint code
uv run ruff check src/

# Type check
uv run mypy src/
```

### Testing (Optional)

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src tests/
```

## Architecture

The application follows clean architecture principles:

- **Models Layer** (`src/models/`): Pure data models with no business logic
- **Services Layer** (`src/services/`): Business logic and CRUD operations
- **CLI Layer** (`src/cli/`): User interface and presentation

**Dependency Flow**: CLI → Services → Models

## Technical Details

- **Language**: Python 3.13+
- **Package Manager**: UV
- **Storage**: In-memory (dict-based, no persistence)
- **Performance**: <100ms per operation for up to 1,000 tasks

## Documentation

- [Feature Specification](specs/001-todo-console-app/spec.md)
- [Implementation Plan](specs/001-todo-console-app/plan.md)
- [Data Model](specs/001-todo-console-app/data-model.md)
- [Quickstart Guide](specs/001-todo-console-app/quickstart.md)
- [Project Constitution](.specify/memory/constitution.md)

## License

See LICENSE file for details.

## Contributing

This project follows Spec-Driven Development. See [CLAUDE.md](CLAUDE.md) for development guidelines.
