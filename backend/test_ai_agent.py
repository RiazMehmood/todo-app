#!/usr/bin/env python3.14
"""
Quick test script to verify AI Agent Manager configuration.
Tests that the Gemini API is properly configured via Agents SDK.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_agent():
    """Test AI agent with a simple message."""
    print("=" * 60)
    print("Testing AI Agent Manager with Gemini API")
    print("=" * 60)

    # Import after loading env
    from services.ai_agent_manager import get_agent_manager

    # Get agent manager (singleton)
    agent_manager = get_agent_manager()

    print(f"✓ Agent Manager initialized")
    print(f"  Model: {agent_manager.model}")
    print(f"  API Key: {agent_manager.api_key[:10]}..." if agent_manager.api_key else "  API Key: Not set")
    print()

    # Test simple message (no database operations)
    print("Sending test message: 'Hello, can you help me?'")
    print()

    try:
        # Create a mock database session context
        from unittest.mock import MagicMock
        mock_session = MagicMock()

        # Process message
        result = await agent_manager.process_message(
            user_id="test_user",
            message="Hello, can you help me with my tasks?",
            db_session=mock_session,
            conversation_id=1
        )

        print("✓ Response received:")
        print("-" * 60)
        print(result.get("response", "No response"))
        print("-" * 60)
        print(f"Status: {result.get('status', 'unknown')}")

        if result.get("status") == "error":
            print(f"Error: {result.get('error')}")
            return False

        return True

    except Exception as e:
        print(f"✗ Error processing message: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_agent())

    print()
    print("=" * 60)
    if success:
        print("✅ AI Agent test PASSED")
    else:
        print("❌ AI Agent test FAILED")
    print("=" * 60)

    sys.exit(0 if success else 1)
