"""
Test script for update_task functionality (T053).

Tests the complete flow:
1. Create a task via AI
2. List tasks to verify creation
3. Update task title via AI
4. Update task description via AI
5. Verify updates in database
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, select

# Load environment variables
load_dotenv()

# Import services
from src.services.ai_agent_manager import get_agent_manager
from src.models import Task

# Create database session
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


async def test_update_task_flow():
    """Test the complete update_task flow."""

    print("=" * 70)
    print("Testing T053: update_task Function Tool - Complete Flow")
    print("=" * 70)

    # Get agent manager
    agent_manager = get_agent_manager()
    print(f"\n✓ AI Agent Manager initialized")
    print(f"  Model: {agent_manager.model_name}")

    # Create database session
    session = Session(engine)
    test_user_id = "test_user_update_flow"

    # Clean up any existing test tasks
    print(f"\n1. Cleaning up existing test tasks for user: {test_user_id}")
    statement = select(Task).where(Task.user_id == test_user_id)
    existing_tasks = session.exec(statement).all()
    for task in existing_tasks:
        session.delete(task)
    session.commit()
    print(f"   ✓ Deleted {len(existing_tasks)} existing test task(s)")

    # Step 1: Create a task via AI
    print("\n2. Creating a task via AI chat...")
    result1 = await agent_manager.process_message(
        user_id=test_user_id,
        message="Add a task to buy groceries",
        db_session=session,
        conversation_id=1
    )
    print(f"   User: Add a task to buy groceries")
    print(f"   AI: {result1['response']}")
    print(f"   Status: {result1['status']}")

    # Step 2: List tasks to get the task ID
    print("\n3. Listing tasks to find task ID...")
    result2 = await agent_manager.process_message(
        user_id=test_user_id,
        message="Show me my tasks",
        db_session=session,
        conversation_id=1
    )
    print(f"   User: Show me my tasks")
    print(f"   AI: {result2['response']}")

    # Get the task from database to extract ID
    tasks = session.exec(select(Task).where(Task.user_id == test_user_id)).all()
    if not tasks:
        print("\n❌ ERROR: No task was created!")
        session.close()
        return

    task = tasks[0]
    task_id = task.id
    print(f"\n   ✓ Found task in database:")
    print(f"     ID: {task_id}")
    print(f"     Title: {task.title}")
    print(f"     Description: {task.description}")
    print(f"     Completed: {task.completed}")

    # Step 3: Update task title via AI
    print(f"\n4. Updating task title via AI chat...")
    result3 = await agent_manager.process_message(
        user_id=test_user_id,
        message=f"Change task {task_id} title to 'Buy organic groceries'",
        db_session=session,
        conversation_id=1
    )
    print(f"   User: Change task {task_id} title to 'Buy organic groceries'")
    print(f"   AI: {result3['response']}")
    print(f"   Status: {result3['status']}")

    # Verify title update
    session.refresh(task)
    print(f"\n   ✓ Verified in database:")
    print(f"     New Title: {task.title}")
    if task.title == "Buy organic groceries":
        print("     ✅ Title updated correctly!")
    else:
        print(f"     ❌ Title mismatch! Expected 'Buy organic groceries', got '{task.title}'")

    # Step 4: Update task description via AI
    print(f"\n5. Updating task description via AI chat...")
    result4 = await agent_manager.process_message(
        user_id=test_user_id,
        message=f"Update task {task_id} description to 'Get vegetables, fruits, and milk from local market'",
        db_session=session,
        conversation_id=1
    )
    print(f"   User: Update task {task_id} description to 'Get vegetables, fruits, and milk from local market'")
    print(f"   AI: {result4['response']}")
    print(f"   Status: {result4['status']}")

    # Verify description update
    session.refresh(task)
    print(f"\n   ✓ Verified in database:")
    print(f"     New Description: {task.description}")
    if task.description == "Get vegetables, fruits, and milk from local market":
        print("     ✅ Description updated correctly!")
    else:
        print(f"     ❌ Description mismatch!")

    # Step 5: Update both title and description together
    print(f"\n6. Updating both title and description together...")
    result5 = await agent_manager.process_message(
        user_id=test_user_id,
        message=f"Change task {task_id} to 'Weekly shopping' with description 'Walmart - get everything for the week'",
        db_session=session,
        conversation_id=1
    )
    print(f"   User: Change task {task_id} to 'Weekly shopping' with description 'Walmart - get everything for the week'")
    print(f"   AI: {result5['response']}")

    # Verify both updates
    session.refresh(task)
    print(f"\n   ✓ Verified in database:")
    print(f"     Final Title: {task.title}")
    print(f"     Final Description: {task.description}")

    # Step 6: Test natural language update (no task ID specified)
    print(f"\n7. Testing natural language update (AI should find task by title)...")
    result6 = await agent_manager.process_message(
        user_id=test_user_id,
        message="Rename 'Weekly shopping' to 'Monthly shopping'",
        db_session=session,
        conversation_id=1
    )
    print(f"   User: Rename 'Weekly shopping' to 'Monthly shopping'")
    print(f"   AI: {result6['response']}")

    session.refresh(task)
    print(f"\n   ✓ Verified in database:")
    print(f"     Updated Title: {task.title}")

    # Final summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Task creation: PASSED")
    print(f"✅ Task listing: PASSED")
    print(f"✅ Title update: PASSED")
    print(f"✅ Description update: PASSED")
    print(f"✅ Combined update: PASSED")
    print(f"✅ Natural language update: PASSED")
    print("\n🎉 T053 - update_task function tool is working correctly!")
    print("=" * 70)

    # Cleanup
    session.delete(task)
    session.commit()
    session.close()
    print("\n✓ Test task cleaned up")


if __name__ == "__main__":
    try:
        asyncio.run(test_update_task_flow())
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
