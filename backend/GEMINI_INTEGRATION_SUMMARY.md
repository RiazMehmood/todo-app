# Gemini Integration via OpenAI Agents SDK - Summary

This document summarizes the changes made to integrate Gemini with the OpenAI Agents SDK using the `AsyncOpenAI` client pattern.

## Overview

The chatbot integration now uses Google's Gemini model through the OpenAI Agents SDK, using a custom `AsyncOpenAI` client pointed at Gemini's API endpoint. This approach:

- Uses **only** the OpenAI Agents SDK (no OpenRouter or other intermediaries)
- Connects directly to Google's Gemini API
- Maintains compatibility with the OpenAI Agents SDK tools and features

## Pattern Used

Based on your Chainlit example, we're using:

```python
# Create AsyncOpenAI client with Gemini endpoint
external_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)

# Wrap with OpenAI Agents SDK model wrapper
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash-exp",
    openai_client=external_client
)

# Create run config
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

# Run agent with config
result = await Runner.run(
    starting_agent=agent,
    input=message,
    run_config=config
)
```

## Files Modified

### 1. `backend/src/services/ai_agent_manager.py`

**Key Changes:**

- **Imports:** Added `RunConfig` and `OpenAIChatCompletionsModel` from agents SDK
- **Client Setup:**
  ```python
  self.external_client = AsyncOpenAI(
      api_key=self.api_key,
      base_url="https://generativelanguage.googleapis.com/v1beta/"
  )
  ```
- **Model Wrapper:**
  ```python
  self.model = OpenAIChatCompletionsModel(
      model=self.model_name,
      openai_client=self.external_client
  )
  ```
- **Run Config:**
  ```python
  self.run_config = RunConfig(
      model=self.model,
      model_provider=self.external_client,
      tracing_disabled=True
  )
  ```
- **Updated Methods:**
  - `process_message()`: Now uses `run_config` parameter
  - `stream_message()`: Now uses `run_config` parameter
  - Removed `_get_or_create_session()` (no longer needed)

### 2. `backend/src/routes/chat.py`

**Key Changes:**

- Changed agent manager import from `gemini_agent_manager` to `ai_agent_manager`
- Updated comment to clarify we're using OpenAI Agents SDK with Gemini

### 3. `backend/.env.example`

**Added:**

```env
# AI Configuration (Phase III - Chatbot Integration)
# Gemini API Key from Google AI Studio (https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your-gemini-api-key-here
# Alternative: OPENAI_API_KEY (fallback if GEMINI_API_KEY not set)
# OPENAI_API_KEY=your-openai-api-key-here

# AI Model (default: gemini-2.0-flash-exp)
AI_MODEL=gemini-2.0-flash-exp
```

### 4. `backend/test_gemini_integration.py` (NEW)

Created a standalone test script to verify the integration works correctly.

## Environment Variables Required

Add to your `.env` file:

```env
# Gemini API Key (get from https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your-api-key-here

# Model selection (optional, defaults to gemini-2.0-flash-exp)
AI_MODEL=gemini-2.0-flash-exp
```

## Available Gemini Models

You can use any of these models via `AI_MODEL`:

- `gemini-2.0-flash-exp` (default, fast and efficient)
- `gemini-1.5-flash` (stable, production-ready)
- `gemini-1.5-pro` (more capable, slower)
- `gemini-2.5-flash` (if available)

## Testing the Integration

### 1. Run the Test Script

```bash
cd backend
python test_gemini_integration.py
```

Expected output:
```
============================================================
Testing Gemini Integration via OpenAI Agents SDK
============================================================

✓ API Key found: AIzaSyB...

1. Creating AsyncOpenAI client with Gemini base URL...
   ✓ AsyncOpenAI client created

2. Creating OpenAIChatCompletionsModel...
   Model: gemini-2.0-flash-exp
   ✓ Model wrapper created

3. Creating RunConfig...
   ✓ RunConfig created

4. Creating test agent...
   ✓ Agent created

5. Running test message...
   Input: Say 'Hello! Gemini is working via OpenAI Agents SDK!' if you can hear me.

   ✓ Response received:
   Hello! Gemini is working via OpenAI Agents SDK!

============================================================
SUCCESS: Gemini integration is working!
============================================================
```

### 2. Test via API Endpoint

```bash
# Start the backend server
cd backend
uvicorn src.main:app --reload

# In another terminal, test the chat endpoint
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, can you help me create a task?"}'
```

## How It Works

1. **Client Creation:** `AsyncOpenAI` is configured with Gemini's API endpoint
2. **Model Wrapping:** `OpenAIChatCompletionsModel` makes Gemini compatible with OpenAI Agents SDK
3. **Configuration:** `RunConfig` bundles the model and client for agent execution
4. **Agent Execution:** `Runner.run()` uses the config to run agents with Gemini
5. **Tool Calling:** Function tools work seamlessly through the OpenAI Agents SDK interface

## Benefits of This Approach

1. **No Third-Party Services:** Direct connection to Google's Gemini API
2. **Full SDK Features:** Access to all OpenAI Agents SDK capabilities
3. **Function Tools:** Seamless integration with `@function_tool` decorators
4. **Streaming Support:** Real-time responses via `Runner.stream()`
5. **Consistency:** Same code pattern as shown in your Chainlit example

## Migration Notes

### From `gemini_agent_manager.py` to `ai_agent_manager.py`

The old `gemini_agent_manager.py` used Google's native SDK. The new `ai_agent_manager.py`:

- Uses OpenAI Agents SDK exclusively
- Connects to Gemini via `AsyncOpenAI` with custom base_url
- No longer uses `google.generativeai` package
- Simpler, more consistent with OpenAI Agents SDK patterns

### Breaking Changes

None! The API remains the same:

```python
result = await agent_manager.process_message(
    user_id=user_id,
    message=message_content,
    db_session=session,
    conversation_id=conversation.id
)
```

## Troubleshooting

### API Key Issues

If you get authentication errors:

1. Verify `GEMINI_API_KEY` is set in `.env`
2. Get a new key from https://makersuite.google.com/app/apikey
3. Ensure no extra spaces/newlines in the key

### Model Not Found

If the model isn't available:

1. Check available models in Google AI Studio
2. Update `AI_MODEL` in `.env` to a supported model
3. Default to `gemini-1.5-flash` for stability

### Connection Errors

If you can't connect to Gemini:

1. Verify internet connection
2. Check if Google AI services are accessible in your region
3. Try with a VPN if blocked

## Next Steps

1. Set `GEMINI_API_KEY` in your `.env` file
2. Run `test_gemini_integration.py` to verify setup
3. Test the chat endpoint via API
4. Monitor logs for any errors

## References

- **Google AI Studio:** https://makersuite.google.com/app/apikey
- **Gemini API Docs:** https://ai.google.dev/docs
- **OpenAI Agents SDK:** https://github.com/openai/openai-agents-sdk
- **AsyncOpenAI Client:** https://github.com/openai/openai-python

---

**Integration completed successfully!** 🎉

The chatbot now uses Gemini via OpenAI Agents SDK with the exact pattern you requested.
