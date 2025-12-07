"""Display formatting for the CLI."""

from typing import List
from src.models.task import Task


def format_task_list(tasks: List[Task]) -> str:
    """
    Format a list of tasks for display in table format.

    Args:
        tasks: List of Task objects to display

    Returns:
        Formatted string with task table or empty message
    """
    if not tasks:
        return "\n=== Your Tasks ===\n\nNo tasks yet. Use 'add' to create your first task!\n"

    # Calculate column widths
    id_width = max(len(str(task.id)) for task in tasks)
    id_width = max(id_width, 2)  # Minimum width for "ID"

    title_width = max(len(task.title) for task in tasks)
    title_width = max(title_width, 5)  # Minimum width for "Title"
    title_width = min(title_width, 40)  # Maximum width for title

    desc_width = 50  # Fixed width for description

    # Build table
    output = ["\n╔═══════════════════════════════════════════════════════════════════════════════════╗"]
    output.append("║                              YOUR TODO TASKS                                      ║")
    output.append("╠════╦════╦══════════════════════════════════════════╦═════════════════════════════════╣")

    # Header row
    header = f"║ {'ID':<{id_width}} ║ St ║ {'Title':<{title_width}} ║ {'Description':<{desc_width}} ║"
    output.append(header)
    output.append("╠════╬════╬══════════════════════════════════════════╬═════════════════════════════════╣")

    # Task rows
    for task in tasks:
        status_icon = "✅" if task.completed else "❌"

        # Truncate title if too long
        title = task.title[:title_width] if len(task.title) > title_width else task.title

        # Truncate description if too long
        desc = task.description if task.description else "(No description)"
        desc = desc[:desc_width] if len(desc) > desc_width else desc

        # Format row
        row = f"║ {task.id:<{id_width}} ║ {status_icon}  ║ {title:<{title_width}} ║ {desc:<{desc_width}} ║"
        output.append(row)

    # Bottom border
    output.append("╚════╩════╩══════════════════════════════════════════╩═════════════════════════════════╝")

    # Summary
    completed_count = sum(1 for t in tasks if t.completed)
    incomplete_count = len(tasks) - completed_count
    output.append(f"\nTotal: {len(tasks)} tasks | ✅ Complete: {completed_count} | ❌ Incomplete: {incomplete_count}\n")

    return "\n".join(output)
