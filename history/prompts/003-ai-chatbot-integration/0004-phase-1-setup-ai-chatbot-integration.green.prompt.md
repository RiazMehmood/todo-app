---
id: 0004
title: Phase 1 Setup AI Chatbot Integration
stage: green
date: 2025-12-16
surface: agent
model: claude-sonnet-4-5
feature: 003-ai-chatbot-integration
branch: 003-ai-chatbot-integration
user: riaz
command: /sp.implement
labels: ["setup", "dependencies", "configuration", "migration"]
links:
  spec: specs/003-ai-chatbot-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/pyproject.toml
  - backend/.env
  - backend/migrations/003_add_chat_tables.sql
  - backend/run_migration.py
  - frontend/package.json
  - frontend/.env.local
  - .gitignore
tests:
  - Manual verification of dependency installation
  - Environment variable configuration check
---

## Prompt

Execute /sp.implement command to begin implementation of AI Chatbot Integration feature (Phase III). Start with Phase 1: Setup tasks including:
- Installing backend dependencies (openai, openai-agents, mcp[cli])
- Installing frontend dependencies (@openai/chatkit-react, react-markdown, @heroicons/react)
- Configuring environment variables for OpenAI API
- Creating database migration for chat tables
- Verifying ignore files

## Response snapshot

Successfully completed Phase 1: Setup for AI Chatbot Integration:

1. **Backend Dependencies Installed**:
   - openai (v2.12.0) - OpenAI Python client
   - openai-agents (v0.6.3) - OpenAI Agents SDK for agent runtime management
   - mcp[cli] (v1.24.0) - Official Model Context Protocol Python SDK
   - websockets (v15.0.1) - For real-time streaming

2. **Frontend Dependencies Installed**:
   - @openai/chatkit-react - Official OpenAI chat UI component
   - react-markdown - For rendering AI responses
   - @heroicons/react - Icons for chat interface

3. **Backend Configuration**:
   - Added OPENAI_API_KEY, OPENAI_MODEL, OPENAI_AGENT_ID to backend/.env
   - Added MCP_SERVER_PORT and CHAT_RATE_LIMIT_PER_USER settings

4. **Frontend Configuration**:
   - Added NEXT_PUBLIC_AI_ENABLED=true to frontend/.env.local
   - Added NEXT_PUBLIC_CHATKIT_API_KEY placeholder

5. **Database Migration Created**:
   - Created migrations/003_add_chat_tables.sql
   - Defines user_preferences, conversations, messages tables (Hackathon Page 18 compliance)
   - Enhances tasks table with AI metadata (created_via_ai, ai_suggested_priority, original_nl_input)
   - Creates all performance indexes
   - Migration file ready to run (requires valid DATABASE_URL and OpenAI API key)

6. **.gitignore Updated**:
   - Added AI/ML patterns (*.pkl, *.model, conversations.db)
   - Added temporary file patterns

## Outcome

- ✅ Impact: Phase 1 Setup complete - all dependencies installed, environment configured, migration created
- 🧪 Tests: Manual verification of dependency installation successful
- 📁 Files: 7 files created/modified (pyproject.toml, .env files, migration, .gitignore)
- 🔁 Next prompts: "Continue with Phase 2: Foundational tasks" or "Run database migration and verify tables"
- 🧠 Reflection: Setup went smoothly. Migration file created but not executed due to missing psycopg2 in Python path. User should run migration manually or install missing dependencies.

## Evaluation notes (flywheel)

- Failure modes observed: Python module path issues with psycopg2/sqlmodel - required fallback to pip install
- Graders run and results (PASS/FAIL): N/A (setup phase)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Continue to Phase 2 foundational tasks or wait for user to provide OpenAI API key
