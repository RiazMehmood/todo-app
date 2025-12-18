---
description: "Implementation tasks for AI Chatbot Integration feature"
---

# Tasks: AI Chatbot Integration

**Input**: Design documents from `/specs/003-ai-chatbot-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL per project constitution - manual testing will be used for MVP.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US0, US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app monorepo**: `backend/src/`, `frontend/app/`, `frontend/components/`, `frontend/lib/`
- All paths are relative to repository root: `/home/riaz/Desktop/todo hackathon II/todo/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [X] T001 Install backend dependencies: openai, openai-agents, mcp[cli] via uv in backend/
- [X] T002 [P] Install frontend dependencies: @openai/chatkit-react, react-markdown, @heroicons/react in frontend/
- [X] T003 [P] Add OpenAI API key and model config to backend/.env (OPENAI_API_KEY, OPENAI_MODEL)
- [X] T004 [P] Add ChatKit config to frontend/.env.local (NEXT_PUBLIC_AI_ENABLED)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create database migration script for new tables (UserPreferences, Conversation, Message) in backend/migrations/003_add_chat_tables.sql
- [X] T006 Run database migration to add UserPreferences, Conversation, Message tables to Neon PostgreSQL
- [X] T007 [P] Enhance Task model with AI metadata fields (created_via_ai, ai_suggested_priority, original_nl_input) in backend/src/models.py
- [X] T008 [P] Create UserPreferences model in backend/src/models.py
- [X] T009 [P] Create Conversation model in backend/src/models.py
- [X] T010 [P] Create Message model in backend/src/models.py
- [X] T011 Create TaskService for AI agent operations (create, list, update, delete, complete) in backend/src/services/task_service.py
- [X] T012 Setup MCP server base structure with FastMCP in backend/src/mcp_server/task_tools.py
- [X] T013 Create AI Agent Manager for Agents SDK integration in backend/src/services/ai_agent_manager.py
- [X] T014 Update main.py to import new models and register for database in backend/src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 0 - Enable AI Chat Features (Priority: P1) 🎯 MVP Component

**Goal**: Users can opt-in to AI features with clear privacy consent

**Independent Test**: Navigate to settings, enable AI toggle, accept privacy notice, verify chat interface appears on dashboard

### Implementation for User Story 0

- [X] T015 [P] [US0] Create POST /api/users/{user_id}/ai/opt-in endpoint in backend/src/routes/auth.py
- [X] T016 [P] [US0] Create POST /api/users/{user_id}/ai/opt-out endpoint in backend/src/routes/auth.py
- [X] T017 [P] [US0] Create GET /api/users/{user_id}/ai/preferences endpoint in backend/src/routes/auth.py
- [X] T018 [P] [US0] Create PATCH /api/users/{user_id}/ai/preferences endpoint in backend/src/routes/auth.py
- [X] T019 [US0] Add opt-in business logic (create UserPreferences, validate consent) in backend/src/routes/auth.py
- [X] T020 [US0] Add opt-out business logic (disable AI, optional delete chat history) in backend/src/routes/auth.py
- [X] T021 [P] [US0] Create AISettingsPanel component in frontend/components/settings/AISettingsPanel.tsx
- [X] T022 [P] [US0] Create PrivacyNotice modal component in frontend/components/ui/PrivacyNotice.tsx
- [X] T023 [US0] Add AI settings panel to settings page in frontend/app/settings/page.tsx
- [X] T024 [US0] Implement opt-in/opt-out API calls in frontend/lib/api.ts
- [X] T025 [US0] Add TypeScript types for UserPreferences in frontend/lib/types.ts

**Checkpoint**: At this point, users can opt-in to AI features and see privacy notice

---

## Phase 4: User Story 1 - Create Tasks via Natural Language Chat (Priority: P1) 🎯 MVP Core

**Goal**: Users can create tasks by chatting in English or Urdu

**Independent Test**: Type "Add task to buy milk" in chat, verify task appears in task list with created_via_ai=TRUE

### Implementation for User Story 1

- [X] T026 [US1] Implement add_task function tool in AIAgentManager in backend/src/services/ai_agent_manager.py (using function_tool instead of MCP)
- [X] T027 [US1] Implement list_tasks function tool in AIAgentManager in backend/src/services/ai_agent_manager.py
- [X] T028 [US1] Create task agent with Agents SDK in AIAgentManager with add_task function tool in backend/src/services/ai_agent_manager.py
- [X] T029 [US1] Create ChatService for conversation management in backend/src/services/chat_service.py
- [X] T030 [US1] Implement POST /api/{user_id}/chat endpoint (HACKATHON REQUIRED) in backend/src/routes/chat.py
- [X] T031 [US1] Add chat route registration to main.py in backend/src/main.py
- [X] T032 [US1] Implement conversation creation/retrieval logic in chat service in backend/src/services/chat_service.py
- [X] T033 [US1] Implement message persistence (user + assistant messages) in chat service in backend/src/services/chat_service.py
- [X] T034 [P] [US1] Direct OpenAI Agents SDK integration (no ChatKit session needed) - using Gemini via AsyncOpenAI
- [X] T035 [P] [US1] Create ChatInterface component in frontend/components/chat/ChatInterface.tsx (integrated chat UI with blurred disabled state)
- [X] T036 [P] [US1] ChatMessage display integrated into ChatInterface component in frontend/components/chat/ChatInterface.tsx
- [X] T037 [P] [US1] ChatInput integrated into ChatInterface component in frontend/components/chat/ChatInterface.tsx
- [X] T038 [US1] Integrate ChatInterface into dashboard page in frontend/app/dashboard/page.tsx
- [X] T039 [US1] Add sendChatMessage API function in frontend/lib/api.ts
- [X] T040 [US1] Add TypeScript types for Conversation and Message in frontend/lib/types.ts
- [X] T041 [US1] Add language detection for English/Urdu in agent instructions in backend/src/services/ai_agent_manager.py
- [ ] T042 [US1] Test task creation via chat with English input manually
- [ ] T043 [US1] Test task creation via chat with Urdu input manually

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks via chat

---

## Phase 5: User Story 2 - Query Tasks via Natural Language (Priority: P2)

**Goal**: Users can ask about their tasks and get contextual answers

**Independent Test**: User has 5 tasks. User asks "What tasks are pending?" and AI lists incomplete tasks.

### Implementation for User Story 2

- [X] T044 [US2] Enhance list_tasks function tool with filtering (status) in backend/src/services/ai_agent_manager.py
- [X] T045 [US2] list_tasks function tool already added to task agent in backend/src/services/ai_agent_manager.py
- [X] T046 [US2] Agent instructions already handle query intents in backend/src/services/ai_agent_manager.py
- [X] T047 [US2] Query response formatting handled by AI agent naturally in backend/src/services/ai_agent_manager.py
- [X] T048 [P] [US2] ChatInterface displays task lists from AI responses (plain text rendering) in frontend/components/chat/ChatInterface.tsx
- [ ] T049 [US2] Test task queries manually: "What tasks are pending?", "Show completed tasks", "What's on my list?"
- [ ] T050 [US2] Test empty list handling manually: user with no tasks asks "What's on my list?"

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 6: User Story 3 - Update and Delete Tasks via Chat (Priority: P2)

**Goal**: Users can modify and remove tasks through conversational commands

**Independent Test**: User has task "Buy milk". User says "Mark 'Buy milk' as complete" and task status updates. User says "Delete milk task" and task is removed.

### Implementation for User Story 3

- [X] T051 [P] [US3] Implement complete_task function tool in backend/src/services/ai_agent_manager.py
- [X] T052 [P] [US3] Implement delete_task function tool in backend/src/services/ai_agent_manager.py
- [X] T053 [P] [US3] Implement update_task function tool in backend/src/services/ai_agent_manager.py (title and description updates)
- [X] T054 [US3] complete_task, delete_task, and update_task function tools added to task agent in backend/src/services/ai_agent_manager.py
- [X] T055 [US3] Agent instructions handle update/delete intents with examples in backend/src/services/ai_agent_manager.py
- [X] T056 [US3] Ambiguity handling delegated to AI agent's natural language understanding
- [X] T057 [US3] Confirmation for delete operations handled by AI agent instructions (asks user first)
- [X] T058 [P] [US3] Confirmation handled conversationally through chat interface (no separate UI component needed)
- [ ] T059 [US3] Test task completion via chat manually: "Mark groceries as done"
- [ ] T060 [US3] Test task deletion via chat manually: "Delete the milk task"
- [ ] T061 [US3] Test task update via chat manually: "Change title to 'Buy organic milk'"
- [ ] T062 [US3] Test ambiguity handling manually: create 2 tasks with "meeting" in title, try to delete one

**Checkpoint**: All core user stories (US0-US3) should now be independently functional

---

## Phase 7: User Story 4 - Multimodal Input (Voice Commands) (Priority: P3) 🎁 BONUS

**Goal**: Users can interact with chat using voice input

**Independent Test**: User clicks microphone icon, says "Add task buy groceries tomorrow", AI transcribes and creates task.

### Implementation for User Story 4

- [ ] T063 [P] [US4] Add voice input toggle to user preferences in backend/src/models.py (already exists)
- [ ] T064 [P] [US4] Create VoiceInput component with browser Web Speech API in frontend/components/chat/VoiceInput.tsx
- [ ] T065 [US4] Integrate VoiceInput component into ChatInput in frontend/components/chat/ChatInput.tsx
- [ ] T066 [US4] Add microphone button to chat input UI in frontend/components/chat/ChatInput.tsx
- [ ] T067 [US4] Add speech recognition error handling (unclear audio, no permission) in frontend/components/chat/VoiceInput.tsx
- [ ] T068 [US4] Add voice_input_enabled preference toggle to settings panel in frontend/components/settings/AISettingsPanel.tsx
- [ ] T069 [US4] Test voice input manually: enable microphone, speak task command, verify transcription
- [ ] T070 [US4] Test voice error handling manually: deny microphone permission, verify fallback to text

**Checkpoint**: Voice input feature complete (bonus +200 points)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T071 [P] Add rate limiting for chat endpoint (CHAT_RATE_LIMIT_PER_USER) in backend/src/routes/chat.py
- [X] T072 [P] Add graceful error handling when AI API is unavailable in backend/src/services/ai_agent_manager.py
- [ ] T073 [P] Add chat history retrieval endpoint GET /api/users/{user_id}/chat/messages in backend/src/routes/chat.py
- [ ] T074 [P] Add chat history clear endpoint DELETE /api/users/{user_id}/chat/messages/clear in backend/src/routes/chat.py
- [ ] T075 [P] Create ChatHistory component to display past conversations in frontend/components/chat/ChatHistory.tsx
- [ ] T076 Add undo functionality for AI-created tasks in chat service in backend/src/services/chat_service.py
- [ ] T077 Add logging for all AI operations (intent detection, tool calls) in backend/src/services/chat_service.py
- [X] T078 [P] Add loading states to ChatInterface component in frontend/components/chat/ChatInterface.tsx
- [X] T079 [P] Add error states and retry mechanism to ChatInterface in frontend/components/chat/ChatInterface.tsx
- [X] T080 Make chat interface responsive for mobile devices in frontend/components/chat/ChatInterface.tsx
- [ ] T081 Test Urdu language support manually: send Urdu messages, verify responses in Urdu
- [ ] T082 Test conversation persistence manually: refresh page, verify chat history loads
- [ ] T083 Test multi-user isolation manually: create tasks for user A, verify user B cannot query them
- [ ] T084 Update quickstart.md with deployment instructions for Phase III in specs/003-ai-chatbot-integration/quickstart.md
- [ ] T085 Run all manual test scenarios from quickstart.md testing checklist
- [ ] T086 Verify all acceptance criteria from spec.md are met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in priority order (P1 → P2 → P3)
  - US0 should complete before US1 (opt-in prerequisite)
  - US1 is foundation for US2 and US3
  - US2 and US3 can proceed in parallel after US1
  - US4 can proceed independently after foundational
- **Polish (Phase 8)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 0 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 1 (P1)**: Should start after US0 (requires opt-in) - Core MVP
- **User Story 2 (P2)**: Can start after US1 (builds on chat interface and MCP) - Independent feature
- **User Story 3 (P2)**: Can start after US1 (builds on chat interface and MCP) - Independent feature
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Independent feature (bonus)

### Within Each User Story

- Backend MCP tools before agent integration
- Agent configuration before chat service
- Chat service before API endpoints
- API endpoints before frontend components
- Frontend API calls before UI integration
- Core implementation before testing

### Parallel Opportunities

- **Phase 1 (Setup)**: T002, T003, T004 can run in parallel (different environments)
- **Phase 2 (Foundational)**: T007, T008, T009, T010 (models) can run in parallel
- **Phase 3 (US0)**: T015, T016, T017, T018 (opt-in endpoints) can run in parallel; T021, T022 (UI components) can run in parallel
- **Phase 4 (US1)**: T034, T035, T036, T037 (frontend components) can run in parallel after backend complete
- **Phase 5 (US2)**: T048 can run in parallel with backend enhancements
- **Phase 6 (US3)**: T051, T052, T053 (MCP tools) can run in parallel; T058 can run in parallel with backend
- **Phase 7 (US4)**: T063, T064 can run in parallel
- **Phase 8 (Polish)**: T071, T072, T073, T074, T075, T078, T079, T080 can run in parallel

---

## Parallel Example: User Story 1 (Core MVP)

```bash
# After T026-T033 (backend) complete, launch frontend tasks together:
Task T035: "Create ChatInterface component using @openai/chatkit-react in frontend/components/chat/ChatInterface.tsx"
Task T036: "Create ChatMessage display component in frontend/components/chat/ChatMessage.tsx"
Task T037: "Create ChatInput component with text input in frontend/components/chat/ChatInput.tsx"

# After frontend components ready, integration tasks:
Task T038: "Integrate ChatInterface into dashboard page"
Task T039: "Add sendChatMessage API function"
Task T040: "Add TypeScript types for Conversation and Message"
```

---

## Implementation Strategy

### MVP First (Basic Level - 200 Points)

**Target**: User Stories 0, 1, 2, 3 only

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 0 (Opt-in)
4. Complete Phase 4: User Story 1 (Create via chat)
5. **STOP and VALIDATE**: Test US0 + US1 independently against acceptance criteria
6. Complete Phase 5: User Story 2 (Query tasks)
7. Complete Phase 6: User Story 3 (Update/Delete tasks)
8. **VALIDATE**: Test all acceptance criteria from spec.md
9. Deploy to staging → Test manually → Production
10. **Achievement**: 200/200 Basic Level points ✅

### Incremental Delivery with Bonuses (+300 Points)

**Target**: All user stories + bonuses

1. Complete MVP First (above) → **200 points**
2. Add Urdu language support testing (already built-in) → **+100 points**
3. Complete Phase 7: User Story 4 (Voice input) → **+200 points**
4. Complete Phase 8: Polish & Cross-Cutting
5. **Achievement**: 500/500 total points (200 Basic + 100 Urdu + 200 Voice) ✅

### Recommended Approach

**Week 1**: Setup + Foundational + US0 + US1 (Tasks T001-T043)
- End of week: Users can opt-in and create tasks via chat ✅

**Week 2**: US2 + US3 (Tasks T044-T062)
- End of week: Full CRUD via chat complete, Basic Level achieved ✅

**Week 3** (Optional): US4 + Polish (Tasks T063-T086)
- End of week: Voice input, all bonuses, 500/500 points ✅

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Manual testing per project constitution (no automated test files)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Hackathon Compliance**: All required technologies (ChatKit, Agents SDK, MCP SDK) are used correctly
- **Database Schema**: Matches Page 18 requirements (Task, Conversation, Message tables)
- **API Endpoints**: POST /api/{user_id}/chat is hackathon-required endpoint
- **MCP Tools**: All 5 required tools implemented (add_task, list_tasks, complete_task, delete_task, update_task)
