"""
Test script for Gemini integration via OpenAI Agents SDK.

This script verifies that the AI Agent Manager is correctly configured
to use Gemini through the AsyncOpenAI client with custom base_url.

Usage:
    python test_gemini_integration.py
"""

import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, Runner, RunConfig, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()


async def test_gemini_integration():
    """Test Gemini integration with OpenAI Agents SDK."""

    print("=" * 60)
    print("Testing Gemini Integration via OpenAI Agents SDK")
    print("=" * 60)

    # Get API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY or OPENAI_API_KEY not found in .env")
        print("Please set your API key in the .env file")
        return

    print(f"\n✓ API Key found: {api_key[:8]}...")

    # Create AsyncOpenAI client with Gemini endpoint
    print("\n1. Creating AsyncOpenAI client with Gemini base URL...")
    external_client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/"
    )
    print("   ✓ AsyncOpenAI client created")

    # Create OpenAI-compatible model wrapper
    print("\n2. Creating OpenAIChatCompletionsModel...")
    model_name = os.getenv("AI_MODEL", "gemini-2.0-flash-exp")
    print(f"   Model: {model_name}")

    model = OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=external_client
    )
    print("   ✓ Model wrapper created")

    # Create run config
    print("\n3. Creating RunConfig...")
    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )
    print("   ✓ RunConfig created")

    # Create a simple test agent
    print("\n4. Creating test agent...")
    agent = Agent(
        name="TestAgent",
        model=model,
        instructions="You are a helpful assistant. Respond concisely."
    )
    print("   ✓ Agent created")

    # Test with a simple message
    print("\n5. Running test message...")
    test_message = "Say 'Hello! Gemini is working via OpenAI Agents SDK!' if you can hear me."
    print(f"   Input: {test_message}")

    try:
        result = await Runner.run(
            starting_agent=agent,
            input=test_message,
            run_config=config
        )

        print(f"\n   ✓ Response received:")
        print(f"   {result.final_output}")

        print("\n" + "=" * 60)
        print("SUCCESS: Gemini integration is working!")
        print("=" * 60)

    except Exception as e:
        print(f"\n   ✗ Error: {str(e)}")
        print("\n" + "=" * 60)
        print("FAILED: Gemini integration has issues")
        print("=" * 60)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_gemini_integration())
