"""Command-line interface for the todo application."""

from src.services.todo_manager import TodoManager
from src.cli.display import format_task_list


class TodoCLI:
    """Command-line interface for managing todos."""

    def __init__(self, manager: TodoManager):
        """
        Initialize CLI with a TodoManager instance.

        Args:
            manager: TodoManager instance to use for operations
        """
        self.manager = manager
        self.running = True

    def handle_add(self):
        """Handle the 'add' command to create a new task."""
        print()
        title = input("Enter task title: ").strip()

        # Validate title
        if not title:
            print("❌ Error: Title cannot be empty. Please provide a task title.")
            return

        if len(title) > 200:
            print("❌ Error: Title too long (max 200 characters).")
            return

        description = input("Enter description (optional): ").strip()

        # Validate description
        if len(description) > 1000:
            print("❌ Error: Description too long (max 1000 characters).")
            return

        try:
            task = self.manager.add_task(title, description)
            print(f"✅ Task added successfully! (ID: {task.id})")
        except ValueError as e:
            print(f"❌ Error: {str(e)}")

    def handle_list(self):
        """Handle the 'list' command to display all tasks."""
        tasks = self.manager.list_tasks()
        print(format_task_list(tasks))

    def handle_complete(self):
        """Handle the 'complete' command to toggle task completion status."""
        print()
        task_id_input = input("Enter task ID to toggle completion: ").strip()

        # Validate input is a number
        try:
            task_id = int(task_id_input)
        except ValueError:
            print("❌ Error: Task ID must be a number.")
            return

        # Toggle completion
        success = self.manager.toggle_completion(task_id)

        if success:
            # Get the task to show current status
            task = self.manager._tasks.get(task_id)
            if task:
                status = "complete" if task.completed else "incomplete"
                print(f"✅ Task #{task_id} marked as {status}.")
        else:
            print(f"❌ Error: Task #{task_id} not found. Use 'list' to see all tasks.")

    def handle_update(self):
        """Handle the 'update' command to modify task title and/or description."""
        print()
        task_id_input = input("Enter task ID to update: ").strip()

        # Validate input is a number
        try:
            task_id = int(task_id_input)
        except ValueError:
            print("❌ Error: Task ID must be a number.")
            return

        # Get the task to show current values
        task = self.manager._tasks.get(task_id)
        if not task:
            print(f"❌ Error: Task #{task_id} not found. Use 'list' to see all tasks.")
            return

        # Show current values and prompt for updates
        print(f"\nCurrent title: {task.title}")
        new_title = input("Enter new title (or press Enter to keep current): ").strip()

        print(f"Current description: {task.description if task.description else '(No description)'}")
        new_description = input("Enter new description (or press Enter to keep current): ").strip()

        # Check if user wants to update anything
        if not new_title and not new_description:
            print("ℹ️  No changes made.")
            return

        # Prepare update parameters
        title_to_update = new_title if new_title else None
        description_to_update = new_description if new_description else None

        # Update task
        try:
            success = self.manager.update_task(task_id, title_to_update, description_to_update)
            if success:
                print(f"✅ Task #{task_id} updated successfully.")
            else:
                print(f"❌ Error: Task #{task_id} not found. Use 'list' to see all tasks.")
        except ValueError as e:
            print(f"❌ Error: {str(e)}")

    def handle_delete(self):
        """Handle the 'delete' command to remove a task."""
        print()
        task_id_input = input("Enter task ID to delete: ").strip()

        # Validate input is a number
        try:
            task_id = int(task_id_input)
        except ValueError:
            print("❌ Error: Task ID must be a number.")
            return

        # Check if task exists
        task = self.manager._tasks.get(task_id)
        if not task:
            print(f"❌ Error: Task #{task_id} not found. Use 'list' to see all tasks.")
            return

        # Show task details and ask for confirmation
        print(f"\nTask to delete: [{task_id}] {task.title}")
        confirmation = input("Are you sure? (y/n): ").strip().lower()

        # Handle confirmation response
        if confirmation == 'y':
            success = self.manager.delete_task(task_id)
            if success:
                print(f"✅ Task #{task_id} deleted successfully.")
            else:
                print(f"❌ Error: Task #{task_id} not found. Use 'list' to see all tasks.")
        else:
            print("ℹ️  Deletion cancelled.")

    def handle_help(self):
        """Handle the 'help' command to show available commands."""
        help_text = """
╔═══════════════════════════════════════╗
║     Todo Application Help             ║
╚═══════════════════════════════════════╝

Available Commands:

  add
    Add a new task with optional description
    Example: Type 'add' and follow the prompts

  list
    Show all tasks with their status
    Example: list

  complete
    Toggle task completion status (complete ↔ incomplete)
    Example: Type 'complete' and enter the task ID

  update
    Edit task title and/or description
    Example: Type 'update' and enter the task ID
    Tip: Press Enter to keep current values unchanged

  delete
    Remove a task permanently
    Example: Type 'delete' and enter the task ID
    Note: You'll be asked to confirm before deletion

  help
    Show this help message
    Example: help

  exit (or quit, q)
    Quit the application
    Example: exit

Tips:
  - Task IDs are shown in square brackets [1], [2], etc.
  - Use 'list' to see your tasks and their IDs
  - Completed tasks show ✅, incomplete tasks show ❌
  - 'complete' command toggles status - use it to mark done or undo
  - 'update' preserves completion status when editing
  - 'delete' requires confirmation - be careful!
  - All commands can be typed directly or selected from menu
"""
        print(help_text)

    def handle_exit(self):
        """Handle the 'exit' command to quit the application."""
        print("\n👋 Thanks for using Todo App! Your tasks will be lost (in-memory only).")
        print("Goodbye!\n")
        self.running = False

    def run(self):
        """Run the main command loop."""
        # Display welcome message
        print("\n" + "=" * 50)
        print("   In-Memory Todo Console Application")
        print("=" * 50)
        print("\nType 'help' for available commands, 'exit' to quit.\n")

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
                elif command == "complete":
                    self.handle_complete()
                elif command == "update":
                    self.handle_update()
                elif command == "delete":
                    self.handle_delete()
                elif command == "help":
                    self.handle_help()
                else:
                    print(f"❌ Error: Unknown command '{command}'. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\n")
                self.handle_exit()
            except Exception as e:
                print(f"❌ Error: Something went wrong. {str(e)}")
