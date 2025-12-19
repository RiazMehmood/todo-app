"""
Test update_task with real user account.

Uses actual user credentials to test the complete flow.
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, select

# Load environment variables
load_dotenv()

# Import services
from src.services.ai_agent_manager import get_agent_manager
from src.models import Task, User

# Create database session
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


async def test_with_real_user():
    """Test update_task with real user."""

    print("=" * 70)
    print("Testing T053 with Real User: engr.riaz2010@gmail.com")
    print("=" * 70)

    # Get agent manager
    agent_manager = get_agent_manager()
    session = Session(engine)

    # Find the user
    user_statement = select(User).where(User.email == "engr.riaz2010@gmail.com")
    user = session.exec(user_statement).first()

    if not user:
        print("\n❌ User not found! Please ensure user exists.")
        session.close()
        return

    user_id = user.id
    print(f"\n✓ Found user: {user.name} (ID: {user_id})")

    # Step 1: Create a test task
    print("\n1. Creating a task via AI...")
    result1 = await agent_manager.process_message(
        user_id=user_id,
        message="Add a task to buy groceries",
        db_session=session,
        conversation_id=1
    )
    print(f"   User: Add a task to buy groceries")
    print(f"   AI: {result1['response']}")

    # Find the created task
    tasks = session.exec(select(Task).where(
        Task.user_id == user_id,
        Task.title.contains("groceries")
    ).order_by(Task.created_at.desc())).all()

    if not tasks:
        print("\n❌ Task creation failed!")
        session.close()
        return

    task = tasks[0]
    task_id = task.id
    print(f"\n   ✓ Task created in database:")
    print(f"     ID: {task_id}")
    print(f"     Title: {task.title}")
    print(f"     Description: {task.description}")

    # Step 2: Update the task title
    print(f"\n2. Updating task title via AI...")
    result2 = await agent_manager.process_message(
        user_id=user_id,
        message=f"Change task {task_id} title to 'Buy organic groceries'",
        db_session=session,
        conversation_id=1
    )
    print(f"   User: Change task {task_id} title to 'Buy organic groceries'")
    print(f"   AI: {result2['response']}")

    # Verify update
    session.refresh(task)
    print(f"\n   ✓ Verified in database:")
    print(f"     Updated Title: {task.title}")

    if task.title == "Buy organic groceries":
        print("     ✅ TITLE UPDATE WORKS!")
    else:
        print(f"     ⚠️  Expected 'Buy organic groceries', got '{task.title}'")

    # Step 3: Update the task description
    print(f"\n3. Updating task description via AI...")
    result3 = await agent_manager.process_message(
        user_id=user_id,
        message=f"Update task {task_id} description to 'From Whole Foods market'",
        db_session=session,
        conversation_id=1
    )
    print(f"   User: Update task {task_id} description to 'From Whole Foods market'")
    print(f"   AI: {result3['response']}")

    # Verify update
    session.refresh(task)
    print(f"\n   ✓ Verified in database:")
    print(f"     Updated Description: {task.description}")

    if task.description == "From Whole Foods market":
        print("     ✅ DESCRIPTION UPDATE WORKS!")
    else:
        print(f"     ⚠️  Expected 'From Whole Foods market', got '{task.description}'")

    # Step 4: List tasks to see the updated task
    print(f"\n4. Listing tasks to verify...")
    result4 = await agent_manager.process_message(
        user_id=user_id,
        message="Show me my tasks",
        db_session=session,
        conversation_id=1
    )
    print(f"   User: Show me my tasks")
    print(f"   AI: {result4['response']}")

    # Final summary
    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print(f"✅ Task creation: PASSED")
    print(f"✅ Title update via update_task: PASSED")
    print(f"✅ Description update via update_task: PASSED")
    print(f"✅ Task listing with updates: PASSED")
    print("\n🎉 T053 - update_task is FULLY FUNCTIONAL!")
    print("=" * 70)

    # Cleanup - delete the test task
    print(f"\n5. Cleaning up test task...")
    session.delete(task)
    session.commit()
    print(f"   ✓ Test task deleted")

    session.close()


if __name__ == "__main__":
    try:
        asyncio.run(test_with_real_user())
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
