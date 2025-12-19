---
id: 0003
title: Regenerate Phase III tasks with hackathon compliance
stage: tasks
date: 2025-12-16
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-ai-chatbot-integration
branch: 002-todo-web-app
user: riaz
command: /sp.tasks
labels: ["task-generation", "hackathon-compliance", "chatkit", "agents-sdk", "mcp-sdk"]
links:
  spec: specs/003-ai-chatbot-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-ai-chatbot-integration/tasks.md
tests:
  - Manual testing per project constitution
---

## Prompt

User initiated `/sp.tasks` command to generate implementation tasks for Phase III AI Chatbot Integration feature.

**Context**: After updating all Phase III specifications for strict Hackathon II compliance, the existing tasks.md file referenced incorrect technologies (custom React UI, OpenAI Functions, lightweight MCP pattern) and needed complete regeneration with the correct technology stack:
- OpenAI ChatKit (`@openai/chatkit-react`)
- OpenAI Agents SDK (`openai-agents`)
- Official MCP Python SDK (`mcp[cli]`)

**Input documents**:
- plan.md - Implementation plan with correct tech stack
- spec.md - Feature specification with 5 user stories (US0-US4)
- data-model.md - Database schema with Conversation, Message, UserPreferences tables
- contracts/chat-api.yaml - API contracts with hackathon-required endpoints
- research.md - Technology research and decisions
- quickstart.md - Setup and development guide

**Requirements**:
- Organize tasks by user story for independent implementation and testing
- Use strict checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
- Include all 5 user stories: US0 (Opt-in), US1 (Create), US2 (Query), US3 (Update/Delete), US4 (Voice)
- Mark parallel opportunities with [P]
- Provide clear MVP scope and incremental delivery strategy

## Response snapshot

Successfully regenerated tasks.md with 86 tasks organized across 8 phases:

**Phase Structure**:
1. **Setup (4 tasks)**: Install dependencies (openai-agents, mcp[cli], @openai/chatkit-react), configure environment
2. **Foundational (10 tasks)**: Database migration (Conversation + Message tables), create models, setup MCP server, Agents SDK integration
3. **US0 - Opt-in (11 tasks)**: Privacy consent flow, AI settings panel, opt-in/opt-out endpoints
4. **US1 - Create Tasks via Chat (18 tasks)**: MCP tools (add_task, list_tasks), Agents SDK task agent, ChatKit integration, conversation management - **MVP CORE**
5. **US2 - Query Tasks (7 tasks)**: Enhanced MCP list_tasks, query intent handling, task list formatting
6. **US3 - Update/Delete (12 tasks)**: MCP tools (complete_task, delete_task, update_task), confirmation dialogs, ambiguity handling
7. **US4 - Voice Input (8 tasks)**: Web Speech API, VoiceInput component, microphone button - **BONUS +200 points**
8. **Polish (16 tasks)**: Rate limiting, error handling, logging, Urdu testing, responsive design

**Key Features**:
- ✅ All tasks reference correct packages (ChatKit, Agents SDK, MCP SDK)
- ✅ Database schema matches Page 18 requirements (Conversation + Message tables)
- ✅ API endpoints include hackathon-required POST /api/{user_id}/chat
- ✅ MCP tools include all 5 required tools (add_task, list_tasks, complete_task, delete_task, update_task)
- ✅ Each user story has clear goal and independent test criteria
- ✅ 28 tasks marked [P] for parallel execution
- ✅ MVP scope defined: Phases 1-4 (43 tasks) for Basic Level 200/200 points
- ✅ Full feature: All 86 tasks for 500/500 points (Basic + Urdu + Voice bonuses)

**Implementation Strategy**:
- Week 1: Setup + Foundational + US0 + US1 (T001-T043) → MVP ready
- Week 2: US2 + US3 (T044-T062) → Basic Level complete (200 points)
- Week 3: US4 + Polish (T063-T086) → All bonuses (500 points total)

## Outcome

- ✅ Impact: Phase III implementation tasks completely regenerated with correct hackathon-compliant technology stack. Tasks now reference OpenAI ChatKit, Agents SDK, and Official MCP SDK instead of custom implementations.
- 🧪 Tests: Manual testing approach per project constitution. Each user story includes independent test criteria.
- 📁 Files: Updated specs/003-ai-chatbot-integration/tasks.md (replaced 86 old tasks with 86 new hackathon-compliant tasks)
- 🔁 Next prompts: Run `/sp.implement` to begin implementation phase, or user may create reusable skills/subagents as requested
- 🧠 Reflection: Task regeneration was necessary due to initial technology choices not matching strict hackathon requirements. All 7 specification documents are now aligned with correct tech stack, ready for implementation.

## Evaluation notes (flywheel)

- Failure modes observed: Initial task generation referenced custom implementations instead of required official SDKs. Fixed by reading updated specification documents and generating tasks based on correct technology stack.
- Graders run and results (PASS/FAIL): Format validation PASS - all 86 tasks follow strict checklist format with checkbox, ID, optional [P] and [Story] labels, and file paths
- Prompt variant (if applicable): Standard /sp.tasks workflow with correct specification inputs
- Next experiment (smallest change to try): Consider adding sub-tasks within complex tasks (e.g., T028 "Create task agent" could break down into agent creation, function tool registration, instruction configuration)
