"""Main entry point for the todo application."""

from src.services.todo_manager import TodoManager
from src.cli.interface import TodoCLI


def main():
    """Main application entry point."""
    # Create TodoManager instance
    manager = TodoManager()

    # Create and run CLI
    cli = TodoCLI(manager)
    cli.run()


if __name__ == "__main__":
    main()
